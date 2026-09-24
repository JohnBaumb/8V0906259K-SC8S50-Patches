"""Apply, check or remove a BinToolz .btp patch, without BinToolz.

    python btp_apply.py add    "JB P2P v1.1 - S50.btp" mybin.bin [-o out.bin]
    python btp_apply.py check  "JB P2P v1.1 - S50.btp" mybin.bin
    python btp_apply.py remove "JB P2P v1.1 - S50.btp" mybin.bin [-o out.bin]

Stock python, no dependencies. Never writes over the input unless you point -o at it.

Container format ("BinToolz Patch v1.1"), read out of the shipped patches:

    0x00  char[20]  "BinToolz Patch v1.1\\0"
    0x14  char[8]   ECU tag, e.g. "SC800S50"
    0x1C  u32       record count
    0x20  u32       CRC32 of the record area
    0x24  u32       expected bin size
    0x28  ...       zero padding to 0x64
    0x64  records   { u32 offset, u32 length, u8 original[length], u8 patched[length] }

Every byte a patch writes ships with the byte it replaced, which is what makes check
and remove exact rather than a guess.
"""
import argparse, struct, sys, zlib


def load(path):
    b = open(path, "rb").read()
    if b[:19] != b"BinToolz Patch v1.1":
        sys.exit(f"{path}: not a BinToolz Patch v1.1 file")
    ecu = b[0x14:0x1C].rstrip(b"\0").decode("ascii", "replace")
    count, crc, size = struct.unpack_from("<III", b, 0x1C)
    body = b[0x64:]
    if zlib.crc32(body) & 0xFFFFFFFF != crc:
        sys.exit(f"{path}: CRC mismatch, the patch file is damaged")
    recs, off = [], 0
    for _ in range(count):
        a, ln = struct.unpack_from("<II", body, off)
        off += 8
        old, new = body[off:off + ln], body[off + ln:off + 2 * ln]
        off += 2 * ln
        if len(new) != ln or len(old) != ln:
            sys.exit(f"{path}: truncated record")
        recs.append((a, new, old))
    if off != len(body):
        sys.exit(f"{path}: {len(body) - off} trailing bytes, refusing to guess")
    return ecu, size, recs


def state(buf, recs):
    """applied / clean / mixed, judged per record against both byte sets."""
    hits = [bytes(buf[a:a + len(n)]) == n for a, n, _ in recs]
    outs = [bytes(buf[a:a + len(o)]) == o for a, _, o in recs]
    if all(hits):
        return "applied"
    if all(outs):
        return "clean"
    return "mixed"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["add", "check", "remove"])
    ap.add_argument("patch")
    ap.add_argument("bin")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()

    ecu, size, recs = load(a.patch)
    buf = bytearray(open(a.bin, "rb").read())
    print(f"patch: {len(recs)} record(s), ECU {ecu}, expects a {size} byte bin")
    if len(buf) != size:
        sys.exit(f"{a.bin}: {len(buf)} bytes, this patch is for {size}")

    st = state(buf, recs)
    if a.action == "check":
        print({"applied": "PATCHED", "clean": "not patched",
               "mixed": "MIXED, some records match and some do not"}[st])
        return 0 if st in ("applied", "clean") else 2

    if st == "mixed":
        sys.exit("bin matches neither the patched nor the unpatched byte pattern, refusing")
    want = "clean" if a.action == "add" else "applied"
    if st != want:
        print(f"nothing to do, bin is already {'patched' if st == 'applied' else 'unpatched'}")
        return 0

    for off, new, old in recs:
        src, dst = (old, new) if a.action == "add" else (new, old)
        assert bytes(buf[off:off + len(src)]) == src
        buf[off:off + len(dst)] = dst
        print(f"  0x{off:06X}  {len(dst)} bytes")

    out = a.out or (a.bin.rsplit(".", 1)[0] + ("_patched.bin" if a.action == "add" else "_unpatched.bin"))
    open(out, "wb").write(buf)
    print(f"wrote {out}")
    if any(not (0x200000 <= off < 0x280000) for off, _, _ in recs):
        print("FULL FLASH REQUIRED: this patch writes outside the calibration block.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
