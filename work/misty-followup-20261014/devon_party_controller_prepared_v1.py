#!/usr/bin/env python3
"""Prepared QA helpers only; this file never opens an emulator or edits a SAV.

Native integration is pending the actual native-devon-v6.py and current ELF.
The caller must verify a single battle, current PartyMenu offsets/tasks and
the source contract before passing a live emulator to navigate_ui_slot.
"""
from dataclasses import dataclass
from collections import Counter


@dataclass(frozen=True)
class UiMon:
    # gPlayerParty is already in UI order while the battle party menu is open.
    pid: int
    ot: int
    species: int
    hp: int
    egg: bool = False
    bad_egg: bool = False
    checksum_ok: bool = True


def decode_battle_order(packed):
    """UI slot -> battle party index: HIGH nibble first, then LOW nibble."""
    if len(packed) != 3:
        raise ValueError("gBattlePartyCurrentOrder must contain exactly 3 bytes")
    order = tuple(n for b in packed for n in (b >> 4, b & 15))
    if sorted(order) != list(range(6)):
        raise ValueError(("invalid battle party permutation", order))
    return order


def replacement_ui_slots(ui_mons, packed_order, active_battle_indexes,
                         reserved_battle_index=None):
    """Read HP/egg from UI rows, use order only to exclude active battle ids.

    Do not index ui_mons again through the permutation. The game has already
    called UpdatePartyToBattleOrder before displaying these rows.
    """
    if not 1 <= len(ui_mons) <= 6:
        raise ValueError("UI party must contain 1..6 rows")
    order = decode_battle_order(packed_order)
    forbidden = set(active_battle_indexes)
    if any(not 0 <= i < 6 for i in forbidden):
        raise ValueError(("invalid active battle index", forbidden))
    if reserved_battle_index is not None and 0 <= reserved_battle_index < 6:
        forbidden.add(reserved_battle_index)
    return tuple(slot for slot, mon in enumerate(ui_mons)
                 if mon.species != 0 and mon.hp > 0
                 and not mon.egg and not mon.bad_egg and mon.checksum_ok
                 and order[slot] not in forbidden)


def retained_identities(ui_mons):
    """Order-independent evidence preserving even duplicate PID+OT counts."""
    ids = tuple((mon.pid, mon.ot) for mon in ui_mons if mon.species != 0)
    return Counter(ids)


def battle_phase(callback, *, battle_callback, party_callback, overworld,
                 outcome, action_ready=False, choose_mon_ready=False):
    """Leaving BattleMainCB2 is not evidence that a battle has ended."""
    cb = callback & ~1
    if cb == (party_callback & ~1):
        return "party-select" if choose_mon_ready else "party-transition"
    if cb == (battle_callback & ~1):
        return "fight-action" if action_ready else "battle"
    if overworld and outcome != 0:
        return "field-with-result"
    return "unconfirmed-transition"


def navigate_ui_slot(e, target, read_slot, choose_mon_ready, safety_check,
                     *, single_battle_verified, max_inputs=24):
    """Use actual DOWN keys with a read after each; never confirm Cancel.

    This only positions the cursor. It does NOT press A, invoke SEND OUT,
    declare a battle result or touch emulator RAM. Current source/ELF must
    still be checked for the complete menu integration before native use.
    """
    if not single_battle_verified:
        raise ValueError("this prepared navigation only supports a single battle")
    if not 0 <= target < 6:
        raise ValueError("target must be a Pokemon UI slot, never Cancel/Confirm")
    trace = []
    for _ in range(max_inputs + 1):
        safety_check()
        if not choose_mon_ready():
            raise AssertionError(("party selection task not ready", trace))
        slot = read_slot()
        trace.append(slot)
        if slot == target:
            return trace
        if len(trace) > max_inputs:
            break
        e.press("DOWN", hold=2, after=14)
    raise AssertionError(("did not reach verified UI target", target, trace))


def self_test():
    checks = []

    # Non-identity order is the regression case: raw UI1 is alive, raw UI0
    # belongs to active battle id2 and is fainted. Double-permuting loses UI1.
    order = bytes([0x20, 0x13, 0x45])
    assert decode_battle_order(order) == (2, 0, 1, 3, 4, 5)
    rows = [UiMon(102, 77, 9, 0), UiMon(100, 77, 6, 50),
            UiMon(101, 77, 3, 0), UiMon(103, 77, 25, 40, egg=True),
            UiMon(104, 77, 148, 30, bad_egg=True), UiMon(105, 77, 0, 0)]
    assert replacement_ui_slots(rows, order, {2}) == (1,)
    checks.append("non_identity_order_reads_UI_HP_once")
    assert replacement_ui_slots(rows, order, {2}, 0) == ()
    checks.append("reserved_battle_index_is_excluded")
    rows2 = list(rows)
    rows2[3] = UiMon(103, 77, 25, 40, checksum_ok=False)
    assert replacement_ui_slots(rows2, order, {2, 0}) == ()
    checks.append("active_fainted_egg_bad_egg_invalid_empty_are_excluded")
    assert retained_identities(rows) == retained_identities(list(reversed(rows)))
    checks.append("native_party_reordering_preserves_identity_set")
    duplicated = [rows[1], rows[1]]
    assert retained_identities(duplicated)[(100, 77)] == 2
    assert retained_identities(duplicated) != retained_identities([rows[1]])
    checks.append("duplicate_identity_counts_are_preserved")
    for packed in (b"\x00\x00\x00", b"\x01\x23", b"\xf0\x12\x34"):
        try:
            decode_battle_order(packed)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid order accepted")
    checks.append("invalid_order_fails_closed")

    opts = dict(battle_callback=0x080113FC, party_callback=0x08124114,
                overworld=False, outcome=0)
    assert battle_phase(0x08124115, choose_mon_ready=True, **opts) == "party-select"
    assert battle_phase(0x08124115, **opts) == "party-transition"
    assert battle_phase(0x080113FD, action_ready=True, **opts) == "fight-action"
    checks.append("outcome_zero_party_callback_is_not_battle_end")
    assert battle_phase(0x08000001, battle_callback=0x080113FC,
                        party_callback=0x08124114, overworld=True,
                        outcome=1) == "field-with-result"
    assert battle_phase(0x08000001, battle_callback=0x080113FC,
                        party_callback=0x08124114, overworld=True,
                        outcome=0) == "unconfirmed-transition"
    checks.append("field_return_requires_recorded_outcome")

    class FakeKeysOnly:
        def __init__(self, start):
            self.slots = [0, 1, 2, 3, 4, 5, 7]
            self.slot = start
            self.inputs = []

        def press(self, key, **unused):
            assert key == "DOWN", "navigation must not press A/B"
            self.inputs.append(key)
            self.slot = self.slots[(self.slots.index(self.slot) + 1) % len(self.slots)]

        def write(self, *unused):
            raise AssertionError("RAM write prohibited")

    fake = FakeKeysOnly(5)
    trace = navigate_ui_slot(fake, 1, lambda: fake.slot, lambda: True,
                             lambda: None, single_battle_verified=True)
    assert trace == [5, 7, 0, 1] and fake.inputs == ["DOWN"] * 3
    checks.append("cancel_wrap_is_observed_without_confirming_cancel")
    try:
        navigate_ui_slot(fake, 7, lambda: fake.slot, lambda: True,
                         lambda: None, single_battle_verified=True)
    except ValueError:
        pass
    else:
        raise AssertionError("Cancel target accepted")
    checks.append("cancel_target_fails_closed")
    return checks


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps({"logic_checks": self_test(), "native_execution": False,
                          "scope": "prepared helper tests only"}, indent=2))
    else:
        print("PREPARED ONLY: no emulator, ROM build or SAV operation performed")
