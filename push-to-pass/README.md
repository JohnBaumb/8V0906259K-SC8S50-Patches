# Push to pass for SwitchPatch 29.33 (Simos18, S50)

Hold a button, the ECU runs a map slot you choose. Let go, it goes back to the map you were
on. Nothing is committed, nothing needs confirming, and the normal map-switch gesture keeps
working exactly as it does now.

> **Cruise control must be off.** Push-to-pass ignores the buttons while cruise is on, because
> the + and - buttons adjust the set speed then.

**Status: v1.1, road tested** on one car (MK7 Golf R, 8V0906259K, SwitchPatch 29.33): map swap,
restore, both lamps and the silent release all confirmed over several days of driving. Still one
car and one bin; read the testing section before you arm it on yours.

## Dependencies

This is not standalone. Every item below is required, and the patch checks the first three by
refusing to apply if the bytes it expects are not there.

| Dependency | Why |
|---|---|
| Simos18 **S50** box code (`SC800S50`, 8V0906259K / 5G0906259x family), 4 MB bin | Every address in the patch is S50. Other box codes have the same code at different offsets and will fail the byte check. |
| **`SL PATCH.29.33 - S50`** (switchleg SwitchPatch 29.33) already applied | The patch hooks the switchpatch tick at file `0x1321B0`, reuses its `apply()` at `0x8013144E`, its RAM (`0xD000F801..F808`) and its MIL feedback stub at `0x801321E8`. Other switchpatch versions lay these out differently. |
| **Map select** enabled in the switchpatch (XDF: Map Switching > **UI button**, `0x27CB28`; tested with 1 = Cruise Resume) | Push-to-pass rides on the switchpatch's map switching and its + / - map-up / map-down buttons. With map select off there is nothing for it to hook into. |
| Blank flash at file `0x132D44..0x132E78` (308 bytes after the switchpatch block) | Where the routine and lamp function live. No S50 patch in the BinToolz set writes there (HSL, CBRICK, SWG, Immo, FREE SAP, switchpatch 28.12 to 29.33 checked). |
| **Full flash** (ASW) after applying | The code is in ASW1, a CAL-only flash will not carry it. Changing the three settings afterwards is CAL-only. |
| BinToolz, or stock Python 3 with the `btp_apply.py` in the repo root | To apply, check or remove the `.btp`. |
| TunerPro with the included `SC8S50_switchpatch29.33_v1.001+p2p.xdf` | The only way to set which map each button holds and whether the lamps are on. The XDF is the stock 29.33 S50 XDF plus three bytes under **Switch Patch**. |
| The steering wheel's cruise + and - buttons | They are the switchpatch's map-up / map-down buttons. Push-to-pass only reads them while no map-switch gesture is open and cruise control is off. |

## Applying it

With BinToolz, treat it like any other patch: One Click Patch, ADD, pick your bin, pick
`JB P2P v1.1 - S50.btp`. CHECK and REMOVE work too, because the patch carries the original
bytes for everything it writes.

Without BinToolz:

```
python ../btp_apply.py add    "JB P2P v1.1 - S50.btp" mybin.bin -o mybin_p2p.bin
python ../btp_apply.py check  "JB P2P v1.1 - S50.btp" mybin_p2p.bin
python ../btp_apply.py remove "JB P2P v1.1 - S50.btp" mybin_p2p.bin -o mybin_back.bin
```

Stock python, no dependencies. It refuses to touch a bin that matches neither the patched nor
the unpatched byte pattern, so it will not stack on itself or half-apply.

## Settings

Three calibration bytes, defined in the included XDF under **Switch Patch**. The patch itself
never writes them, so applying or removing it leaves your settings alone:

| Setting | Address | Values |
|---|---|---|
| Push to pass map: plus button | `0x27CB3F` | 0 = off, 1 = map 1 ... 5 = map 5 |
| Push to pass map: minus button | `0x27CB3E` | 0 = off, 1 = map 1 ... 5 = map 5 |
| Push to pass lamps | `0x27CB3B` | 0 = off, 1 = on |

Each button can hold its own map, or be off. Plus to map 2 and minus to map 3, plus only, minus
only, whatever you like. Map numbers are the ones the app shows, 1 to 5.

**It ships dormant.** All three bytes are 0, which means off, so out of the box the patch does nothing
at all. Setting either byte arms that button, and since the settings are in calibration, changing
them later is a CAL-only flash. A button pointed at the map you are already on is ignored
completely, no switch, no lamp.

Plus and minus are the switchpatch's own map-up and map-down buttons. The patch only looks at
them while no map-switch gesture is open, so it never fights the normal up / down / SET sequence,
and it only engages while cruise control is fully off, because both buttons adjust the set speed
when cruise is on. If you hold one button and then press the other, the second is ignored until
the first is released.

## The lamp indicator

With `0x27CB3B` = 1, the check-engine lamp blinks while you hold plus and the EPC lamp blinks
while you hold minus, the same blink the switchpatch gives you on a map change, for as long as
you hold the button, so you can tell which button is engaged without looking at a laptop. It
works by replacing the switchpatch's own MIL blink stub with a function that behaves identically
when push-to-pass is idle, so normal map-switch feedback is unchanged. The blink is driven by the
lamp transmit itself (one toggle per transmit call), which is why it shows every time; timed
patterns were tried first and the cluster dropped them. Releasing the button is silent: the lamp
just stops, no confirmation flicker. With the byte at 0 the lamps never move.

## Building the map it jumps to

Do this before you arm it, or you will get a surprise.

Out of the box the switchpatch map slots are usually clones of each other, with the feature
flags on in slot 1 and off in the rest. If that is true of your bin, then push-to-pass pointed
at slot 2 does exactly one thing: it turns **off** launch control, no-lift shift, RAL and pops
for as long as you hold the button. Nothing gains power.

So, in the slot you are going to target:

1. **Copy slot 1's flags across**: Enable RAL, Enable NLS, Enable LC. Otherwise those features
   silently switch off under your finger.
2. **Leave Pops enable off, on purpose, for the first test.** See below.
3. **Then** put the actual delta in: the per-map levers are PUT setpoint, Spark modifier,
   Lambda modifier, Torque Request, and the per-map rev and speed limiters.

Build the target as a delta on your daily map, not as a different tune. The swap is
instantaneous, there is no ramp, and the torque model gets no warning.

## Testing it

The first test costs nothing and needs no laptop. Build the target slot as your daily map with
RAL, NLS and LC copied over but **pops left off**, and no power delta at all. Then:

- hold the button, lift off: the exhaust goes quiet
- let go: the pops come back

That proves the button, the map swap and the restore, on a map that cannot hurt anything. Add
the power delta afterwards.

If you log, watch `0xD000F801` (active map), `0xD000F806` (pending, must **not** move) and the
flag mirrors at `0xD000F812` pops, `0xD000F879` RAL, `0xD000F896` NLS, `0xD000F8A0` LC.

## Worth knowing before you drive it

- **No time limit.** It holds as long as you hold the button. This is not an FIA overtake button
  with a budget.
- **Cruise gate.** Engage is refused unless the ECU's cruise state (`0xD001B6CD`) reads 0. A hold
  already in progress still releases if cruise comes on underneath it, so you cannot get stranded
  on the push-to-pass map by turning cruise on. If your car reports a non-zero state with the main
  switch merely on, push-to-pass will refuse with the main switch on; log the `Cruise` PID.
- **Wheel-button map switches still blink the CEL.** The switchpatch's own 2 s feedback is untouched.
  Push-to-pass engage and release do not trigger it; the only lamp activity from push-to-pass
  is the hold indicator above, and only if you turn it on.
- **Interrupting it.** If you open a map-switch gesture while holding the button, the switchpatch
  clears the marker the patch uses, and the car stays on the push-to-pass map until you switch
  manually. Nothing unsafe, but it will look odd.
- **Key off while holding** stores the push-to-pass map as your startup map.

## What it actually does

Both directions go through the switchpatch's own `apply()`, so every per-map flag is re-latched
exactly as a normal map switch would, not just the tables. Engaging enters `apply()` three
instructions in, past its "read the pending slot" prologue, with the target map in `d15`, which
leaves the pending slot holding the map you came from. That is the whole trick, and it is why
the patch needs no RAM of its own for the return address.

It is 308 bytes in blank flash after the switchpatch block, one rewritten jump in the
switchpatch tick, and the two stock calls to the switchpatch MIL stub redirected to the lamp
function (four records). No other S50 patch in the BinToolz set touches that space: HSL, CBRICK, SWG,
Immo, FREE SAP and every switchpatch from 28.12 to 29.33 were checked.

Not affiliated with switchleg or BinToolz. Provided as is, like everything else in this corner
of the hobby. You are flashing your own ECU.
