# Mode Memory Startup for SwitchPatch 29.33 (Simos18, S50)

Key on with Race (or any profile) left selected and the engine is in that profile before you
crank. Without this, the MK7 head unit shows the remembered profile but tells the engine
"Normal" until you press the selector once, so the ECU runs Normal until you do. Measured on a
2016 Golf R: coordinator target 2 from key-on, Race latched only after the first press.

**Status: v1.0, verified** on one car (MK7 Golf R, 8V0906259K, SwitchPatch 29.33, push-to-pass
v1.1): key on in Race after a real key-off, coordinator still sending Normal, ECU already in Race
before cranking, engine started in Race. Selector, map switching and the drive were normal.

## Dependencies

Not standalone. The patch checks the first three by refusing to apply if the bytes it expects
are not there.

| Dependency | Why |
|---|---|
| Simos18 **S50** box code (`SC800S50`, 8V0906259K / 5G0906259x family), 4 MB bin | Every address is S50: the drive-mode plausibility routine `DrvModSwt` at file `0x14B600`, its RAM, and the switchpatch stubs below. |
| **`SL PATCH.29.33 - S50`** (switchleg SwitchPatch 29.33) already applied | The remembered mode lives in the switchpatch's own NVM block. The patch hooks its three NVM stubs (restore `0x131100`, save `0x131120`, default `0x131134`) and uses the high byte of the switchpatch's map-index halfword, which the switchpatch itself never touches. Other switchpatch versions lay the stubs out differently. |
| Blank flash at file `0x132E80..0x132F3D` (190 bytes) | Where the four routines live. It is the free space after the push-to-pass block; nothing in the BinToolz S50 set writes there. |
| **Full flash** (ASW) after applying | Code is in ASW1. A CAL-only flash will not carry it, and the full flash resets the readiness monitors. |
| BinToolz, or stock Python 3 with the `btp_apply.py` in the repo root | To apply, check or remove the `.btp`. |
| A car whose driving profile reaches the engine through the Charisma coordinator (MK7 with Driving Profile Selection) | That is the signal the patch overrides at key-on. On a car without profile selection the coordinator value is 0 and the patch does nothing. |

**Not** dependencies: push-to-pass (checked, the patch applies to a switchpatch-only bin and to a
switchpatch + push-to-pass bin; the two share no bytes), any XDF, any setting. There is nothing to
configure and no CAL byte is written, so the patch is settings-free and stacks on any tune built on
switchpatch 29.33.

## Applying it

BinToolz: One Click Patch, ADD, pick your bin, pick `JB ModeMemory v1.0 - S50.btp`. CHECK and
REMOVE work, the patch carries the original bytes.

Without BinToolz:

```
python ../btp_apply.py add    "JB ModeMemory v1.0 - S50.btp" mybin.bin -o mybin_modemem.bin
python ../btp_apply.py check  "JB ModeMemory v1.0 - S50.btp" mybin_modemem.bin
python ../btp_apply.py remove "JB ModeMemory v1.0 - S50.btp" mybin_modemem.bin -o mybin_back.bin
```

## What it does

- At every ECU reset it notes the first value the head unit sends. While that value does not
  change, it feeds `DrvModSwt` the mode the engine last ran in instead. So Race left selected
  means Race before cranking.
- The first selector press releases it for the rest of that key cycle. From then on the head
  unit owns the mode, including a later return to the key-on mode.
- At shutdown it saves the mode the engine actually latched (1 to 5) in the high byte of the
  switchpatch's NVM halfword. The switchpatch stubs only read and write the low byte, so a revert
  to a plain switchpatch bin sees its map index unchanged; the mode is simply forgotten.
- Saved mode 0 (first key cycle after flashing, or after the switchpatch's NVM default), or a
  head-unit value outside 1 to 5 (no CAN yet): the patch passes the head-unit value through and
  the ECU behaves exactly as stock.

## Testing it

First start after flashing behaves as stock, by design: nothing is saved yet. Drive once in Race,
key off properly (long enough for the head unit to reboot, a few minutes), then key on in Race and
log before cranking. Pass, with the drive-mode PIDs from the plan:

| PID | Address | Expect |
|---|---|---|
| Coordinator raw | `0xD0019F34` | 2 (head unit still says Normal) |
| Cord latched | `0xD001BCAC` | 3 |
| LF_DRIV_MOD | `0xD000C4BB` | 8 |
| STATE_DRIV_MOD | `0xD000C4C2` | 3 |

Then one selector press and back: everything must follow the head unit.

## Worth knowing

- **The head unit disagrees with the ECU** until you press the selector: it thinks Normal, the
  ECU answers Race. On the test car the cluster showed nothing. If yours throws a driving-profile
  warning, say so; a variant that overrides one stage later and answers Normal is possible.
- **Quick restarts** (engine off, key back on within seconds) never needed the patch: the head
  unit stays up and keeps sending the profile. The patch matters after a real key-off.
- **It remembers the engine's last mode, not the head unit's display.** They agree in practice,
  because the head unit remembers the same thing.
- **Push-to-pass** is unaffected. It switches map slots; this switches the driving profile. The two
  live in different RAM and different flash.

Not affiliated with switchleg or BinToolz. Provided as is. You are flashing your own ECU.
