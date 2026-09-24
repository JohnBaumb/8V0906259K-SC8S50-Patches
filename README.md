# 8V0906259K / SC8S50 Patches

Add-on patches for Simos18 **S50** (`SC800S50`, 8V0906259K / 5G0906259x) that stack on top of
switchleg's **SwitchPatch 29.33**. They use the same `.btp` format as the
[BinToolz patches](https://github.com/Switchleg1/BinToolz/tree/main/patches), so you add, check and remove them the same way.

| Patch | What it does | XDF needed |
|---|---|---|
| [push-to-pass](push-to-pass/) `JB P2P v1.1 - S50.btp` | Hold the steering wheel cruise + or - button to run a chosen map slot. Let go and it returns to your map. Optional CEL/EPC blink while held. **Only works with cruise off.** | **Yes**: the included XDF adds 3 settings under Switch Patch. Ships off (all 0). |
| [mode-memory-startup](mode-memory-startup/) `JB ModeMemory v1.0 - S50.btp` | At key-on the engine starts in the drive mode it last ran in (for example Race) instead of Normal, without pressing the selector first. | No, there are no settings. |

## How they work

A `.btp` is a list of `{offset, original bytes, patched bytes}` records with a CRC. Applying
checks that every original byte is there, then writes the new ones. That is why CHECK and REMOVE
are exact, and why a patch refuses a bin it doesn't recognize. Each patch hooks switchpatch 29.33
code and puts its own routine in blank ASW flash just after the switchpatch block. The two patches
use separate space (`0x132D44` and `0x132E80`), so you can apply either one or both, in any order.

## Requirements

- A 4 MB S50 bin with **`SL PATCH.29.33 - S50`** already applied. Other box codes or switchpatch
  versions fail the byte check, and nothing gets written.
- A **full flash** (ASW) after applying. CAL-only flashes won't carry the code. Changing the
  push-to-pass settings later can be CAL-only.
- **BinToolz** (One Click Patch > ADD), or plain Python 3 with the included script:

```
python btp_apply.py add    "push-to-pass/JB P2P v1.1 - S50.btp" mybin.bin -o out.bin
python btp_apply.py check  "push-to-pass/JB P2P v1.1 - S50.btp" out.bin
python btp_apply.py remove "push-to-pass/JB P2P v1.1 - S50.btp" out.bin -o back.bin
```

- Push-to-pass only: **map select** enabled in the switchpatch (XDF: Map Switching > UI button,
  `0x27CB28`, tested with 1 = Cruise Resume).
- Push-to-pass only: **TunerPro** with
  `push-to-pass/SC8S50_switchpatch29.33_v1.001+p2p.xdf`. This is the stock 29.33 S50 XDF plus
  three tables: plus map `0x27CB3F`, minus map `0x27CB3E`, lamps `0x27CB3B`. If you have your own
  XDF, you can copy those three `XDFTABLE` entries into it.
- Mode memory: a car with Driving Profile Selection (MK7). Without it, the patch does nothing.

Each folder's README covers the dependencies, testing and caveats. Road tested on one car (MK7
Golf R, 8V0906259K). Not affiliated with switchleg or BinToolz. Use at your own risk: you are
flashing your own ECU.
