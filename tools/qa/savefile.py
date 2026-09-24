"""Read and write FR/LG flash saves (128 KiB) at the level of SaveBlock1,
SaveBlock2 and PokemonStorage.

A save holds two slots of 14 sectors; the newer slot (higher counter) is the
live one and its sectors are rotated. Each sector carries 3968 bytes of data
and a footer with its id, a checksum, a signature and the slot counter. This
module reads the live slot into three bytearrays, lets the caller edit them,
and writes them back to the same physical sectors with fresh checksums.
"""

import struct

from gamedata import off, const, map_info, Rom, POCKETS, items, item_name

SECTOR_SIZE = 0x1000
DATA_SIZE = 3968
SIGNATURE = 0x08012025
SECTORS_PER_SLOT = 14


def checksum(data):
    s = 0
    for (v,) in struct.iter_unpack('<I', data[:len(data) & ~3]):
        s = (s + v) & 0xFFFFFFFF
    return ((s >> 16) + s) & 0xFFFF


def _chunks(total):
    out = []
    pos = 0
    while pos < total:
        out.append((pos, min(DATA_SIZE, total - pos)))
        pos += DATA_SIZE
    return out


class Blocks:
    """Flags and vars over SaveBlock1/SaveBlock2 bytes, from a save file or
    read out of a running game (eventcheck.py)."""

    def __init__(self, sb1=None, sb2=None):
        self.blocks = {'sb1': bytearray(sb1 or b''), 'sb2': bytearray(sb2 or b'')}

    @property
    def sb1(self):
        return self.blocks['sb1']

    @property
    def sb2(self):
        return self.blocks['sb2']

    def _flag_loc(self, flag):
        flag = const(flag)
        start, count = const('HOENN_FLAGS_START'), const('HOENN_FLAGS_COUNT')
        if start <= flag < start + count:
            return self.sb2, off('sb2.hoennFlags') + (flag - start) // 8, (flag - start) % 8
        if flag >= const('FLAGS_COUNT'):
            raise ValueError('flag %#x is out of range' % flag)
        return self.sb1, off('sb1.flags') + flag // 8, flag % 8

    def flag(self, flag):
        blk, o, bit = self._flag_loc(flag)
        return bool(blk[o] >> bit & 1)

    def set_flag(self, flag, on=True):
        blk, o, bit = self._flag_loc(flag)
        if on:
            blk[o] |= 1 << bit
        else:
            blk[o] &= ~(1 << bit) & 0xFF

    def _trainer_loc(self, trainer):
        # Hoenn trainers are numbered past the flag block; theirs sit in
        # SaveBlock2.hoennTrainerFlags (battle_setup.c, HoennTrainerFlagByte)
        t = const(trainer)
        if t >= const('HOENN_TRAINERS_START'):
            bit = t - const('HOENN_TRAINERS_START')
            return self.sb2, off('sb2.hoennTrainerFlags') + bit // 8, bit % 8
        return self._flag_loc(const('TRAINER_FLAGS_START') + t)

    def trainer_beaten(self, trainer):
        blk, o, bit = self._trainer_loc(trainer)
        return bool(blk[o] >> bit & 1)

    def set_trainer_beaten(self, trainer, on=True):
        blk, o, bit = self._trainer_loc(trainer)
        if on:
            blk[o] |= 1 << bit
        else:
            blk[o] &= ~(1 << bit) & 0xFF

    def _var_loc(self, var):
        var = const(var)
        if const('HOENN_VARS_START') <= var <= const('HOENN_VARS_END'):
            return self.sb2, off('sb2.hoennVars') + (var - const('HOENN_VARS_START')) * 2
        if const('VARS_START') <= var <= const('VARS_END'):
            return self.sb1, off('sb1.vars') + (var - const('VARS_START')) * 2
        raise ValueError('var %#x is not saved' % var)

    def var(self, var):
        blk, o = self._var_loc(var)
        return struct.unpack_from('<H', blk, o)[0]

    def set_var(self, var, value):
        blk, o = self._var_loc(var)
        struct.pack_into('<H', blk, o, const(value) & 0xFFFF)

    # ---------------------------------------------------------- money, bag
    def _key(self):
        return struct.unpack_from('<I', self.sb2, off('sb2.encryptionKey'))[0]

    def money(self):
        return struct.unpack_from('<I', self.sb1, off('sb1.money'))[0] ^ self._key()

    def set_money(self, n):
        struct.pack_into('<I', self.sb1, off('sb1.money'), n ^ self._key())

    def _pocket(self, item):
        """(offset, slot count) of the bag pocket that holds item."""
        field, count = POCKETS[items()[item_name(item)]]
        return off(field), const(count)

    def _slots(self, item):
        o, n = self._pocket(item)
        return [o + 4 * i for i in range(n)]

    def item_count(self, item):
        """How many of item the bag holds (quantities are XORed with the key)."""
        want = const(item_name(item))
        total = 0
        for o in self._slots(item):
            iid, qty = struct.unpack_from('<HH', self.sb1, o)
            if iid == want:
                total += qty ^ (self._key() & 0xFFFF)
        return total

    def set_item(self, item, n):
        """Put exactly n of item in its pocket (0 removes it)."""
        want = const(item_name(item))
        key = self._key() & 0xFFFF
        slots = self._slots(item)
        for o in slots:
            if struct.unpack_from('<H', self.sb1, o)[0] == want:
                struct.pack_into('<HH', self.sb1, o, 0, key)
        if n <= 0:
            self._compact(slots)
            return
        for o in slots:
            if struct.unpack_from('<H', self.sb1, o)[0] == 0:
                struct.pack_into('<HH', self.sb1, o, want, n ^ key)
                return
        raise ValueError('no free slot for %s' % item)

    def _compact(self, slots):
        key = self._key() & 0xFFFF
        kept = [struct.unpack_from('<HH', self.sb1, o) for o in slots]
        kept = [k for k in kept if k[0]]
        for i, o in enumerate(slots):
            struct.pack_into('<HH', self.sb1, o, *(kept[i] if i < len(kept) else (0, key)))

    def fill_items(self, keep_free=()):
        """Fill every empty slot of the ITEMS pocket with a different item, one
        of each, skipping keep_free, so that giving any other item fails."""
        key = self._key() & 0xFFFF
        slots = self._slots('ITEM_POTION')
        have = {struct.unpack_from('<H', self.sb1, o)[0] for o in slots}
        skip = {const(item_name(i)) for i in keep_free}
        spare = [const(k) for k, p in items().items() if p == 'POCKET_ITEMS' and k != 'ITEM_NONE']
        spare = [v for v in spare if v not in have and v not in skip]
        filled = 0
        for o in slots:
            if struct.unpack_from('<H', self.sb1, o)[0] == 0:
                struct.pack_into('<HH', self.sb1, o, spare.pop(0), 1 ^ key)
                filled += 1
        return filled


class SaveFile(Blocks):
    def __init__(self, path):
        self.path = path
        with open(path, 'rb') as f:
            self.raw = bytearray(f.read())
        if len(self.raw) < 2 * SECTORS_PER_SLOT * SECTOR_SIZE:
            raise ValueError('%s is not a 128K flash save' % path)
        self.layout = [('sb2', 0, off('sb2'))]
        self.layout += [('sb1', 1 + i, sz) for i, (_, sz) in enumerate(_chunks(off('sb1')))]
        self.layout += [('storage', 5 + i, sz) for i, (_, sz) in enumerate(_chunks(off('storage')))]
        self.slot, self.counter = self._live_slot()
        self.where = {}          # sector id -> physical sector
        for phys in range(self.slot * SECTORS_PER_SLOT, (self.slot + 1) * SECTORS_PER_SLOT):
            sid = struct.unpack_from('<H', self.raw, phys * SECTOR_SIZE + 0xFF4)[0]
            self.where[sid] = phys
        self.blocks = {'sb2': bytearray(off('sb2')), 'sb1': bytearray(off('sb1')),
                       'storage': bytearray(off('storage'))}
        firsts = {'sb2': 0, 'sb1': 1, 'storage': 5}
        for name, sid, size in self.layout:
            base = (sid - firsts[name]) * DATA_SIZE
            phys = self.where[sid]
            self.blocks[name][base:base + size] = self.raw[phys * SECTOR_SIZE:phys * SECTOR_SIZE + size]

    def _live_slot(self):
        best = None
        for slot in (0, 1):
            ok = True
            counter = None
            for phys in range(slot * SECTORS_PER_SLOT, (slot + 1) * SECTORS_PER_SLOT):
                base = phys * SECTOR_SIZE
                sid, cs, sig, cnt = struct.unpack_from('<HHII', self.raw, base + 0xFF4)
                if sig != SIGNATURE:
                    ok = False
                    break
                counter = cnt
            if ok and (best is None or counter > best[1]):
                best = (slot, counter)
        if best is None:
            raise ValueError('%s has no valid save slot' % self.path)
        return best

    def save(self, path=None):
        firsts = {'sb2': 0, 'sb1': 1, 'storage': 5}
        for name, sid, size in self.layout:
            base = (sid - firsts[name]) * DATA_SIZE
            data = bytes(self.blocks[name][base:base + size])
            phys = self.where[sid]
            self.raw[phys * SECTOR_SIZE:phys * SECTOR_SIZE + size] = data
            struct.pack_into('<H', self.raw, phys * SECTOR_SIZE + 0xFF6, checksum(data))
        with open(path or self.path, 'wb') as f:
            f.write(self.raw)

    # ----------------------------------------------------------------- places
    def location(self):
        o = off('sb1.location')
        g, n, w = struct.unpack_from('<bbb', self.sb1, o)
        x, y = struct.unpack_from('<hh', self.sb1, o + off('warp.x'))
        return g, n, w, x, y

    def warp(self, mapname, x, y):
        """Put the player at (x, y) on a map. The layout id goes with it (a save
        whose mapLayoutId belongs to another map loads a black screen), and the
        continue-game warp is armed so CONTINUE enters the map the way a warp
        does, with its map scripts."""
        m = map_info(mapname)
        for field in ('sb1.location', 'sb1.continueGameWarp'):
            o = off(field)
            struct.pack_into('<bbb', self.sb1, o, m['group'], m['num'], -1)
            struct.pack_into('<hh', self.sb1, o + off('warp.x'), x, y)
        struct.pack_into('<hh', self.sb1, off('sb1.pos'), x, y)
        struct.pack_into('<H', self.sb1, off('sb1.mapLayoutId'), m['layout_id'])
        self.sb2[off('sb2.specialSaveWarpFlags')] |= 1   # CONTINUE_GAME_WARP

    # ---------------------------------------------------------------- options
    def fast_battles(self):
        """Battle style SET (no "Will you switch?" after a foe faints), battle
        animations off and fast text. The u16 after optionsButtonMode holds
        textSpeed:3, windowFrameType:5, sound:1, battleStyle:1, sceneOff:1."""
        o = off('sb2.optionsButtonMode') + 1
        v = struct.unpack_from('<H', self.sb2, o)[0]
        v = (v & ~7) | 2            # OPTIONS_TEXT_SPEED_FAST
        v |= 1 << 9 | 1 << 10       # OPTIONS_BATTLE_STYLE_SET, animations off
        struct.pack_into('<H', self.sb2, o, v)

    # ------------------------------------------------------------------ clock
    # The game clock (src/time_of_day.c) is the RTC plus localTimeOffset when
    # the cart has a working RTC, else a virtual clock: six game minutes per
    # minute of play time plus an offset kept in lastBerryTreeUpdate. mGBA
    # runs this ROM without an RTC, so the virtual clock is the one that
    # counts in the QA tools; both are moved so either way agrees.
    def add_days(self, n):
        for field in ('sb2.localTimeOffset', 'sb2.lastBerryTreeUpdate'):
            o = off(field) + off('time.days')
            d = struct.unpack_from('<h', self.sb2, o)[0]
            struct.pack_into('<h', self.sb2, o, d + n)

    def _virtual_offset(self):
        o = off('sb2.lastBerryTreeUpdate')
        days = struct.unpack_from('<h', self.sb2, o + off('time.days'))[0]
        hours = struct.unpack_from('<b', self.sb2, o + off('time.hours'))[0]
        minutes = struct.unpack_from('<b', self.sb2, o + off('time.minutes'))[0]
        return days * 1440 + hours * 60 + minutes

    def _play_minutes(self):
        h = struct.unpack_from('<H', self.sb2, off('sb2.playTimeHours'))[0]
        m = self.sb2[off('sb2.playTimeMinutes')]
        sec = self.sb2[off('sb2.playTimeSeconds')]
        return (h * 60 + m) * 6 + sec // 10

    def clock_minutes(self):
        """The virtual game clock in minutes since day 0, 00:00."""
        return max(0, self._play_minutes() + self._virtual_offset())

    def set_hour(self, hour):
        """Move the virtual clock forward to the next HOUR:00."""
        now = self.clock_minutes()
        target = now - now % 1440 + hour * 60
        if target < now:
            target += 1440
        new = self._virtual_offset() + (target - now)
        days, rest = divmod(new, 1440)
        o = off('sb2.lastBerryTreeUpdate')
        struct.pack_into('<h', self.sb2, o + off('time.days'), days)
        struct.pack_into('<b', self.sb2, o + off('time.hours'), rest // 60)
        struct.pack_into('<b', self.sb2, o + off('time.minutes'), rest % 60)
        return target

    # ------------------------------------------------------------------- dex
    def set_dex(self, species_national, seen=True, owned=True):
        """Seen/owned must agree in all four places or the game treats the
        entry as tampered with (SaveBlock2 pokedex, SaveBlock1 seen1/seen2)."""
        i = species_national - 1
        byte, bit = i // 8, i % 8
        places = []
        if owned:
            places.append((self.sb2, off('sb2.pokedex') + off('dex.owned')))
        if seen:
            places += [(self.sb2, off('sb2.pokedex') + off('dex.seen')),
                       (self.sb1, off('sb1.seen1')), (self.sb1, off('sb1.seen2'))]
        for blk, o in places:
            blk[o + byte] |= 1 << bit

    # ----------------------------------------------------------------- party
    def party_count(self):
        return self.sb1[off('sb1.playerPartyCount')]

    def party_mon(self, slot):
        size = off('pokemon')
        o = off('sb1.playerParty') + slot * size
        return Mon(self.sb1, o)

    def _party_slot(self, slot):
        size = off('pokemon')
        o = off('sb1.playerParty') + slot * size
        return o, size

    def set_lead(self, slot):
        """Swap party SLOT with the first one."""
        a, size = self._party_slot(0)
        b, _ = self._party_slot(slot)
        first = bytes(self.sb1[a:a + size])
        self.sb1[a:a + size] = self.sb1[b:b + size]
        self.sb1[b:b + size] = first

    def keep_party(self, n):
        """Keep only the first n party POKéMON."""
        for slot in range(n, 6):
            o, size = self._party_slot(slot)
            self.sb1[o:o + size] = bytes(size)
        self.sb1[off('sb1.playerPartyCount')] = min(n, self.party_count())

    def set_hp(self, slot, hp):
        o, _ = self._party_slot(slot)
        struct.pack_into('<H', self.sb1, o + 86, hp)

    # ------------------------------------------------------------ PC boxes
    def box_mons(self):
        size = off('boxmon')
        base = off('storage.boxes')
        n = const('TOTAL_BOXES_COUNT') * const('IN_BOX_COUNT')
        return [Mon(self.blocks['storage'], base + i * size) for i in range(n)]

    def fill_boxes(self):
        """Fill every empty PC box slot with a copy of the first party
        POKéMON, so a POKéMON (or EGG) given now has nowhere to go."""
        size = off('boxmon')
        a, _ = self._party_slot(0)
        copy = bytes(self.sb1[a:a + size])
        filled = 0
        for m in self.box_mons():
            if not m.has_species():
                self.blocks['storage'][m.o:m.o + size] = copy
                filled += 1
        return filled


# Gen 3 box data: 4 substructures of 12 bytes in one of 24 orders, XORed with
# personality ^ otId, guarded by a 16-bit sum.
ORDERS = ['GAEM', 'GAME', 'GEAM', 'GEMA', 'GMAE', 'GMEA', 'AGEM', 'AGME', 'AEGM', 'AEMG', 'AMGE', 'AMEG',
          'EGAM', 'EGMA', 'EAGM', 'EAMG', 'EMGA', 'EMAG', 'MGAE', 'MGEA', 'MAGE', 'MAEG', 'MEGA', 'MEAG']


class Mon:
    def __init__(self, blk, o):
        self.blk, self.o = blk, o
        self.personality, self.otid = struct.unpack_from('<II', blk, o)

    def _key(self):
        return self.personality ^ self.otid

    def subs(self):
        raw = self.blk[self.o + 32:self.o + 80]
        key = self._key()
        dec = b''.join(struct.pack('<I', v ^ key) for (v,) in struct.iter_unpack('<I', raw))
        order = ORDERS[self.personality % 24]
        return {c: bytearray(dec[i * 12:(i + 1) * 12]) for i, c in enumerate(order)}

    def put_subs(self, subs):
        order = ORDERS[self.personality % 24]
        dec = b''.join(bytes(subs[c]) for c in order)
        cs = sum(v for (v,) in struct.iter_unpack('<H', dec)) & 0xFFFF
        struct.pack_into('<H', self.blk, self.o + 28, cs)
        key = self._key()
        enc = b''.join(struct.pack('<I', v ^ key) for (v,) in struct.iter_unpack('<I', dec))
        self.blk[self.o + 32:self.o + 80] = enc

    def species(self):
        return struct.unpack_from('<H', self.subs()['G'], 0)[0]

    def has_species(self):
        # BoxPokemon.hasSpecies, outside the encrypted data
        return bool(self.blk[self.o + 19] & 2)

    def is_egg(self):
        return bool(struct.unpack_from('<I', self.subs()['M'], 4)[0] >> 30 & 1)

    def fateful(self):
        # PokemonSubstruct3.modernFatefulEncounter, the top bit of the ribbons
        return bool(struct.unpack_from('<I', self.subs()['M'], 8)[0] >> 31 & 1)

    def level(self):
        return self.blk[self.o + 84]

    def make_strong(self, level, rom=None):
        """Level, experience, IVs 31 and all six stats set together, HP full."""
        rom = rom or Rom()
        subs = self.subs()
        species = struct.unpack_from('<H', subs['G'], 0)[0]
        info = rom.species_info(species)
        struct.pack_into('<I', subs['G'], 4, rom.exp_for_level(info['growthRate'], level))
        ivword = struct.unpack_from('<I', subs['M'], 4)[0]
        ivword = (ivword & 0xC0000000) | 0x3FFFFFFF
        struct.pack_into('<I', subs['M'], 4, ivword)
        evs = list(subs['E'][0:6])
        self.put_subs(subs)
        base = info['base']        # HP Atk Def Spe SpA SpD
        nature = self.personality % 25
        up, down = nature // 5, nature % 5    # over Atk Def Spe SpA SpD
        stats = [(2 * base[0] + 31 + evs[0] // 4) * level // 100 + level + 10]
        for i in range(1, 6):
            v = (2 * base[i] + 31 + evs[i] // 4) * level // 100 + 5
            if up != down:
                if i - 1 == up:
                    v = v * 110 // 100
                elif i - 1 == down:
                    v = v * 90 // 100
            stats.append(v)
        if species == const('SPECIES_SHEDINJA'):
            stats[0] = 1
        o = self.o
        self.blk[o + 84] = level
        struct.pack_into('<I', self.blk, o + 80, 0)                       # status
        # hp, maxHP, attack, defense, speed, spAttack, spDefense
        struct.pack_into('<7H', self.blk, o + 86, stats[0], stats[0], *stats[1:])
        return stats
