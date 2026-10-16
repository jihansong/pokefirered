"""Read-only data model check; no emulator execution and no save modification."""
import argparse, hashlib, json, re, struct
from pathlib import Path
ORDERS = "GAEM GAME GEAM GEMA GMAE GMEA AGEM AGME AEGM AEMG AMGE AMEG EGAM EGMA EAGM EAMG EMGA EMAG MGAE MGEA MAGE MAEG MEGA MEAG".split()
def digest(data):
    return hashlib.sha256(data).hexdigest()
def checksum(data):
    assert len(data) == 48
    return sum(struct.unpack("<24H", data)) & 65535
def crypt(data, pid, ot):
    return struct.pack("<12I", *(v ^ pid ^ ot for v in struct.unpack("<12I", data)))
def plain(mon):
    pid, ot = struct.unpack_from("<II", mon)
    return crypt(mon[32:80], pid, ot)
def valid(mon):
    return checksum(plain(mon)) == struct.unpack_from("<H", mon, 28)[0]
def fixture(order_index):
    chunks = {
        "G": struct.pack("<HHIBBH", 25, 0, 15625, 0, 70, 0),
        "A": struct.pack("<4H4B", 85, 98, 86, 21, 15, 30, 20, 20),
        "E": bytes([6, 12, 18, 24, 30, 36, 0, 0, 0, 0, 0, 0]),
        "M": struct.pack("<BBHII", 0, 1, 0x1210, 0x12345678, 0)}
    pid, ot = 24 * 100000 + order_index, 0x12345678
    data = b"".join(chunks[c] for c in ORDERS[order_index])
    mon = bytearray(80)
    struct.pack_into("<II", mon, 0, pid, ot)
    mon[19] = 2
    struct.pack_into("<H", mon, 28, checksum(data))
    mon[32:] = crypt(data, pid, ot)
    return bytes(mon)
def set_gender(mon, gender):
    mon, data = bytearray(mon), bytearray(plain(mon))
    pid, ot = struct.unpack_from("<II", mon)
    pos = ORDERS[pid % 24].index("M") * 12 + 2
    origin = struct.unpack_from("<H", data, pos)[0]
    struct.pack_into("<H", data, pos, (origin & 0x7fff) | (gender << 15))
    struct.pack_into("<H", mon, 28, checksum(data))
    mon[32:] = crypt(data, pid, ot)
    return bytes(mon)
def change_ot(mon, ot, reencrypt):
    out = bytearray(mon)
    pid = struct.unpack_from("<I", mon)[0]
    data = plain(mon) if reencrypt else None
    struct.pack_into("<I", out, 4, ot)
    if reencrypt:
        out[32:] = crypt(data, pid, ot)
    return bytes(out)
def function_body(source, name):
    m = re.search(r"(?:static\s+)?(?:void|u8|u16)\s+" + name + r"\([^;{}]*\)\s*\{", source)
    assert m, name
    i, depth = m.end(), 1
    while depth:
        depth += (source[i] == "{") - (source[i] == "}")
        i += 1
    return source[m.start():i]
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pokemon-source", type=Path, required=True)
    args = ap.parse_args()
    raw = args.pokemon_source.read_bytes()
    text = raw.decode("utf-8")
    give = function_body(text, "GiveMonToPlayer")
    setter = function_body(text, "SetBoxMonData")
    helper = function_body(text, "SetBoxMonOtIdReencrypt")
    assert "case MON_DATA_OT_ID:\n        SET32(boxMon->otId);" in setter
    assert re.search(r"DecryptBoxMon\(boxMon\);\s*boxMon->otId = otId;\s*EncryptBoxMon\(boxMon\);", helper)
    rows = []
    for n in range(24):
        mon = set_gender(fixture(n), 1)
        old_ot = struct.unpack_from("<I", mon, 4)[0]
        assert valid(mon)
        for delta in (0, 0x00010001, 0x01010101):
            target = old_ot ^ delta
            direct = change_ot(mon, target, False)
            fixed = change_ot(mon, target, True)
            assert valid(fixed) and plain(fixed) == plain(mon)
            assert fixed[28:30] == mon[28:30]
            assert change_ot(fixed, old_ot, True) == mon
            if not delta:
                assert direct == mon and valid(direct)
            rows.append({"order": ORDERS[n], "ot_xor": hex(delta),
                         "direct_valid": valid(direct), "rekey_valid": valid(fixed),
                         "stored": struct.unpack_from("<H", direct, 28)[0],
                         "direct_computed": checksum(plain(direct))})
    foreign = [r for r in rows if r["ot_xor"] != "0x0"]
    assert all(not r["direct_valid"] for r in foreign)
    broken = bytearray(fixture(0)); broken[32] ^= 4; broken = bytes(broken)
    assert not valid(broken)
    preserved = change_ot(broken, 0x89abcdef, True)
    assert not valid(preserved) and plain(preserved) == plain(broken)
    assert preserved[28:30] == broken[28:30]
    report = {"scope": "pure_data_model_not_native_runtime_or_cause_confirmation",
        "source_sha256": digest(raw), "source_unchanged": digest(args.pokemon_source.read_bytes()) == digest(raw),
        "give_uses_plain_ot_setter": bool(re.search(r"SetMonData\(mon,\s*MON_DATA_OT_ID,", give)),
        "cases": len(rows), "foreign_direct_checksum_failures": sum(not r["direct_valid"] for r in foreign),
        "same_ot_controls_valid": all(r["direct_valid"] for r in rows if r["ot_xor"] == "0x0"),
        "all_rekey_payload_and_checksum_preserved": True,
        "already_corrupt_input_not_silently_repaired": True,
        "user_save_read_or_modified": False, "rows": rows}
    print(json.dumps(report, indent=2))
if __name__ == "__main__":
    main()
