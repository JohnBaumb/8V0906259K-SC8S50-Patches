# 8V0906259K / SC8S50 Patches

Add-on patches for Simos18 **S50** (`SC800S50`, 8V0906259K / 5G0906259x) that stack on top of
switchleg's **SwitchPatch 29.33**. They use the same `.btp` format as the
[BinToolz patches](https://github.com/Switchleg1/BinToolz/tree/main/patches), so you add, check and remove them the same way.

| Patch | What it does | XDF needed |
|---|---|---|
| [push-to-pass](push-to-pass/) `JB P2P v1.1 - S50.btp` | Hold the steering wheel cruise + or - button to run a chosen map slot. Let go and it returns to your map. Optional CEL/EPC blink while held. **Only works with cruise off.** | **Yes**: 3 settings under Switch Patch. Ships off (all 0). |
| [mode-memory-startup](mode-memory-startup/) `JB ModeMemory v1.1 - S50.btp` | At key-on the engine starts in the drive mode it last ran in (for example Race) instead of Normal, without pressing the selector first. **v1.0 users: update**, v1.0 could stay stuck in Race. | No, there are no settings. |
| [rolling-anti-lag-v2](rolling-anti-lag-v2/) `JB RAL V2 v1.0 - S50.btp` | RAL only engages after a deliberate hold (300 ms suggested), Cancel becomes a third button choice, and RAL no longer bucks when it hits its time limit with the button still held. | **Yes**: the hold, Cancel as button 2, and the time limit in seconds, under RAL. Hold and Cancel ship off (0 = stock); the time-limit fix is always on. |
| [launch-control-v2](launch-control-v2/) `JB LC V2 v1.0 - S50.btp` | Launch control limiter mode per map: SwitchPatch (fuel cut) or ME7-style spark cut (**experimental**, read the warning). Launch boost cap in psi, warm-engine gate using the LC oil and coolant minimums, optional exhaust flaps open while holding. | **Yes**: mode per map, caps, spark cut angle and options, under LC. All 0 = SwitchPatch mode, caps off; the temperature gate is always on. |

## How they work

A `.btp` is a list of `{offset, original bytes, patched bytes}` records with a CRC. Applying
checks that every original byte is there, then writes the new ones. That is why CHECK and REMOVE
are exact, and why a patch refuses a bin it doesn't recognize. Each patch hooks switchpatch 29.33
code and puts its own routine in blank ASW flash just after the switchpatch block. The patches
use separate space (`0x132D44`, `0x132E80`, `0x132F40` and `0x132FC0`), so you can apply any of them, in any order.

## Requirements

- A 4 MB S50 bin with **`SL PATCH.29.33 - S50`** already applied. Other box codes or switchpatch
  versions fail the byte check, and nothing gets written.
- A **full flash** (ASW) after applying. CAL-only flashes won't carry the code. Changing the
  settings later can be CAL-only.
- **BinToolz** (One Click Patch > ADD), or plain Python 3 with the included script:

```
python btp_apply.py add    "push-to-pass/JB P2P v1.1 - S50.btp" mybin.bin -o out.bin
python btp_apply.py check  "push-to-pass/JB P2P v1.1 - S50.btp" out.bin
python btp_apply.py remove "push-to-pass/JB P2P v1.1 - S50.btp" out.bin -o back.bin
```

- Push-to-pass only: **map select** enabled in the switchpatch (XDF: Map Switching > UI button,
  `0x27CB28`, tested with 1 = Cruise Resume).
- Push-to-pass, RAL V2 and LC V2: **TunerPro** with `SC8S50_switchpatch29.33_v1.001+JB-patches.xdf`
  (repo root), one XDF for every patch here. It is the stock 29.33 S50 XDF plus each patch's
  settings (titles starting `JB-`), Cancel as RAL button 2, the RAL time limit in seconds, clearer
  names for the SwitchPatch RAL and LC settings, and the factory drive-off torque limiter under
  Launch Control (factory). If you have your own XDF, you can copy those entries into it.
- Mode memory: a car with Driving Profile Selection (MK7). Without it, the patch does nothing.

Each folder's README covers the dependencies, testing and caveats. Road tested on one car (MK7
Golf R, 8V0906259K). Not affiliated with switchleg or BinToolz. Use at your own risk: you are
flashing your own ECU.
