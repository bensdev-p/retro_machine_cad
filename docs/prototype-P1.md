# P1 — printable reference-hardware prototype

This is a detailed enclosure prototype, not a validated production design. It has real panel solids, fastener holes and nut pockets, removable internal mounts, split printing sections, a keyboard carrier, and an engineered *proposed* handle load path. STL exports are intended for test printing. Do not print the entire set until the coupons and selected hardware fit have been checked.

## Design and appearance

The assembled shell is **400 W × 200 H × 220 D mm**. The attached keyboard carrier adds **64 mm** to depth, giving a **400 × 200 × 284 mm** transport envelope excluding screw heads. The handle reaches about Z=234 mm; purchased 6 mm rubber feet make the total standing height approximately 240 mm. The keyboard stays intact and is modeled at its supplied 376.6 × 169.6 × 46.8 mm bounding dimensions.

The palette follows the M Edition direction: neutral light gray shell, charcoal fascia, gray/off-white keys and restrained blue accents. The keyboard shown in the renders is an approximate stock-keyboard visualization, not a reverse-engineered 8BitDo housing or key layout. The screen graphics are illustrative and do not represent running software. Views are rendered from the executed CAD meshes; the Blender lighting and fine shading bevel are presentation effects. The printed CAD has explicit 1.2 mm corner breaks on the principal panel outlines.

The two real drive faceplates remain accessible through recessed openings. No replacement eject mechanism is invented. The carrier places the keyboard's underside toward the computer, with keycaps toward a protective cover and clearance in front of them. Two padded straps cross its underside. Peripheral foam contacts must be checked on the actual housing; the overall keyboard envelope does not establish exactly where a safe housing contact lies.

## Reference hardware and source quality

| Item | Design basis | What remains to verify |
|---|---|---|
| Display | Uploaded October 2026 Raspberry Pi 10-inch Touch Display 2 brief; 248.096 × 166.88 × 15.55 mm, documented outer/inner M2.5 axes | Drawing is approximate. Actual support plane, screw engagement and spacer thickness |
| Keyboard | User-supplied M Edition manufacturer bounding dimensions | Housing profile, knobs, rear controls/ports, contact lands; not available from an inspected drawing |
| Floppy drives | **TEAC FD-235HF class**, nominal 101.6 × 146 × 25.4 mm planning envelope | Exact suffix, bezel protrusions, actual depth, power, read/write condition and USB controller compatibility |
| Pi | Nominal 85 × 56 mm Pi 5 board | Verified board drawing, actual orientation, connector bodies and mounting-edge offsets |
| Cooler | Raspberry Pi Active Cooler reference concept, conservative 60 × 45 × 24 mm allowance | Exact cooler and its installed geometry |
| USB hub | Powered hub allowance **140 × 55 × 28 mm**, adjustable cradle | Select actual hub. Its port face and power inlet determine replacement rear plate geometry |
| USB floppy controllers | Two 76 × 42 × 12 mm allowances under drives | Select/test actual controllers, retain using insulated foam/straps |
| Printer | Primary requested: H2C; all printed parts checked below a **250 mm** maximum extent | H2C usable volume not verified. Nominal 256 mm A1 cube used conservatively; confirm brim/slicer limits |

Attempts to read the 8BitDo, Bambu Lab, TEAC and Raspberry Pi manufacturer websites were blocked by the configured network proxy (HTTP 403). Therefore the new hardware selections above are explicitly **reference choices, not researched-and-verified purchasing recommendations**. The uploaded display document is the mechanical source actually inspected. Nothing requires buying a drive merely because its model name appears in this prototype: first compare the exact seller unit to the central dimensions and test one drive/controller on the Pi.

Use normal PC 1.44 MB disks. Ordinary USB floppy controllers are suitable only after Linux read/write compatibility is demonstrated. A flux controller is not needed for this intended workflow.

## Files and rebuilding

- `parameters.json`, `prototype` section: enclosure, hardware allowances, printer limit, palette, clearances, hardware sizes and selected design parameters.
- `cad/prototype.py`: detailed build123d source and exact rigid-volume interference checks.
- `cad/verify_prototype.py`: independent STEP reimport and binary-STL topology, dimensions and volume checks.
- `cad/render_prototype.py`: Blender renderer, using tessellations from the executed CAD.
- `outputs/prototype/enclosure_assembly.step`: operating enclosure and rigid reference hardware.
- `outputs/prototype/transport_assembly.step`: enclosure plus carrier and stock-keyboard envelope.
- `outputs/prototype/parts/`: individual STEP files in assembly coordinates, and individually oriented STL files translated onto the build plate.
- `outputs/prototype/validation.json` and `export_verification.json`: current parameter hash, measured print bounds and numerical results.
- `outputs/prototype/previews/`: operating, transport, rear, exploded and front views.
- `outputs/prototype/handle_backing_drill_template.dxf`: 2D millimeter outline and hole pattern for the metal bar.
- `outputs/prototype/handle_backing_aluminium.step`: **metal** backing bar; not a printed structural part.
- `outputs/prototype/print_manifest.csv`: filename, material volume, orientation and manufacturing notes.

With the pinned Python environment installed as documented in the main README:

```sh
./rebuild-prototype.sh
```

To regenerate images with **Blender 4.3.2**:

```sh
blender -b -t 4 -P cad/render_prototype.py
```

The renderer uses CPU Cycles. The supplied environment lacks OpenImageDenoise, so denoising is disabled. Render source contains all lighting/camera settings. Earlier layout scripts and outputs remain for historical comparison; use `outputs/prototype` for P1.

## Printing and fit coupons

Use PLA for the first fit set. Start with 0.20 mm layers, a 0.4 mm nozzle, four walls and approximately 25% infill as provisional settings. Structural clamps/cage supports may need more walls or local solid infill after slicing. These are starting settings, not validated strength settings. Consider PETG for final service-temperature resilience after a real thermal test; PLA can soften in hot environments.

Print these **seven coupons first**:

1. `TEST_screen_mount`: verify actual M2.5 hardware, support plane and selected spacer. Slots provide 2 mm total vertical adjustment, not compensation for a wrong overall drawing.
2. `TEST_screen_corner`: check bezel/gasket placement and finger access at the active-area corner.
3. `TEST_drive_face`: test bezel fit, disk insertion/removal, eject-button finger access and LED visibility on the purchased drive.
4. `TEST_keyboard_retention`: verify the carrier edge, padding and strap slot against the intact housing. Check knobs/keycaps without forcing contact.
5. `TEST_fasteners`: check M3/M4 screw clearance and captive hex-nut fit. No heat-set inserts are used in this revision.
6. `TEST_alignment_left` and `TEST_alignment_right`: fit a purchased 2 × 8 mm steel dowel, check the 2.3 mm bore and 0.25 mm seam gap.

All STLs are oriented and shifted to Z=0. Most panel faces lie flat on the bed. Side shells print on their external walls. Each drive-cage half prints on its side wall so the shelves grow as upright ribs instead of spanning a large unsupported gap. Carrier halves print protective-face down. Vertical screen supports print on their back faces. Inspect bridges over nut pockets and vent slots in the slicer; local supports may be required. Do not assume that fitting the printer's numeric volume establishes a successful toolpath. Brims must fit in the remaining nominal margin.

The model uses nominal ISO-style M3 and M4 nut dimensions (5.5/7 mm across flats; 2.4/3.2 mm thickness). Pocket dimensions and screw clearances are enlarged in `parameters.json` for a first print. They have not been calibrated to your printer or a purchased hardware batch.

## Hardware list

Quantities below are derived from the modeled joint groups; buy a small spare allowance and verify engagement during assembly.

| Hardware | Starting quantity | Use |
|---|---:|---|
| M3 × 12 mm screws | 22 | Top/base-to-side rails (12), fascia-to-side (4), rear-to-side (6) |
| M3 × 8 mm screws | 48 | Panel seam strips (26), screen feet (4), hub cradle (4), hub plate (4), cable saddle (2), carrier seams (8) |
| M3 × 10 mm screws | 8 | Cage to base (4), cage base seam (4) |
| M3 × 8 mm countersunk screws | 8 | Two drive shelf seam joints; heads must sit flush below drive housing |
| M3 hex nuts | One per M3 joint | Captive pockets; ordinary hex nuts, not heat-set inserts |
| M4 × 25 mm hand-knob screws | 4 | Removable carrier through rim/spacers/fascia into side rails |
| M4 × 20 mm screws | 4 optional | Retain front rim when carrier is removed; verify engagement |
| M4 hex nuts | 4 | Captive carrier/operating-rim joints |
| M4 × 25 mm bolts | 4 | Handle clamps through lid and metal backing bar |
| M4 washers + locking nuts | 8 washers + 4 nuts | Handle through-bolts; check actual stack and thread protrusion |
| M2.5 screen screws/washers/spacers | 4 sets | Select lengths from measured screen boss and bracket stack; no safe universal length asserted |
| 2 × 8 mm steel alignment pins | 4 | Two top and two base seam positions |
| 392 × 60 × 4 mm aluminum flat bar | 1 | Handle reinforcement, drilled as modeled |
| 6 × 30 mm steel crosspins | 2 | Captured in sewn webbing returns outside handle clamps |
| 25 mm webbing | About 0.5 m before trimming | Handle with properly sewn returns; test entire load path |
| 20 mm padded webbing/straps | 2 drive straps, 2 keyboard straps, hub/controller retention as needed | Fit lengths to the actual units; allow adjustment/buckle overlap |
| Insulating/non-marring foam, screen gasket, cable grommet/ties, 6 mm rubber feet | As fitted | Isolate circuit boards, protect housing/glass and lift base screw heads |

M3 × 8 mm group accounting is: top/base seam strips 16; fascia seam 4; rear seam 6; screen feet 4; hub cradle 4; hub plate 4; cable saddle 2; carrier seam 8 = **48**, plus the separate eight countersunk shelf screws. Thus the actual standard M3 total is 22 + 48 + 8 = **78**, plus eight countersunk = **86 M3 nuts/joints**. Use this group accounting when sourcing; actual head style and washer choice can alter usable screw length.

The hub and controllers must be insulated and restrained. Do not use conductive mounting foam. Provide adequate power for the Pi, display, cooling and both drive motors; the geometry does not demonstrate that a bus-powered hub can supply them. Keep mains conversion outside the enclosure in this revision.

## Installation order and service access

1. Test display/Pi/cooler, then one drive/controller, then both drives simultaneously outside the case. Confirm read/write/eject behavior using an expendable disk.
2. Print and measure coupons; update clearances before main parts. Buy the actual bolts/nuts/straps and compare them with the pocket samples.
3. Prepare the aluminum backing bar, steel pins and sewn handle webbing. Deburr all metal edges and holes. Do not carry installed electronics before proof-load testing.
4. Join base halves with captive-nut seam strips and two alignment pins. Insert nuts before covering access. Attach side shells, installing bottom screws from beneath the base; add rubber feet.
5. Join the drive-cage halves. Use flush countersunk screws at the shelf joints so heads cannot rub drive housings. Bolt the cage into the base. Fit controllers below the drives on insulating pads with straps; maintain access to cables.
6. Bolt the hub cradle to the base, fit the hub and its strap, and route low-voltage cables toward the rear. Ensure the selected hub actually fits the reserved rear port opening; replace the modular plate when necessary.
7. Assemble the display/Pi/cooler module on the bench using verified rear mounting hardware. Fit the screen support rails with measured spacers, washers and safe M2.5 engagement. Never bottom screws in the display bosses or load the glass improperly.
8. Join and fit the fascia. Install a suitable gasket between the screen's non-active border and fascia; bolt the screen rails to base. The detailed Pi placement is still a reference envelope, so verify actual cables and board edges before tightening.
9. Install drives into the cage and fit padded straps around housings/shelves. Check ejection and media access through the fascia. Rear access permits cables and drives to be serviced after removing the rear panels.
10. Fit the front rim with its four **4 mm spacers**, using operating screws or the carrier knobs as appropriate. The spacers prevent the rim from being pulled into the fascia recess.
11. Fit captive nuts, aluminum backing bar, top seam strips, top alignment pins and top halves. Attach screen upper feet and top-to-side screws. Install handle clamps with through-bolts, washers and locking nuts. Webbing loops around 6 mm crosspins outside the clamps provide a positive end stop; do not rely only on friction or glue.
12. Function-test with the rear open. Check connector bend space, cable strain relief, fan operation and screw access. Fit the modular hub plate, power grommet/cable-tie saddle and rear panels. Full tool-clearance sweeps are not modeled; confirm them during this prototype assembly.
13. Join carrier halves. Add foam at confirmed housing contacts and two padded straps across the keyboard underside. Verify a gap to every key and knob, including through the cover seam regions. Attach using four M4 knobs. Remove the carrier for operation; it intentionally obstructs screen/disk access in transport.

Removal reverses the process. Rear panels give access to drive cables, hub and lower controllers. Screen/Pi service requires opening the top, disconnecting cables and removing the bracket fasteners as a module; it is not a claimed tool-less front extraction. Never assume a screw is accessible solely because the solid model has no overlap.

## Handle, cooling and verification boundaries

Proposed load path: sewn webbing returns → steel end-stop crosspins → bolted clamp bars → M4 through-bolts → full-width aluminum bar → side-rail fasteners → side shells → base and internal mounts. The aluminum bar seats in explicit notches in the upper side rails. The computed geometry does not prove the strength of printed nut pockets, layer adhesion, webbing stitching or fasteners. Proof-test with inert mass and inspect deflection/joints before transporting electronics. No load rating is claimed.

Rear and side vents, active-cooler air space and cable keepouts are modeled. Actual temperature, recirculation, dust ingress, fan acoustics and power delivery are untested. Add a case fan or revise vents only after measurements show what is needed.

Exact rigid B-rep intersections are checked across assembled printable parts, hardware envelopes, the transported keyboard, the metal backing and explicit drive/Pi/cooler clearance regions. Face contact at joints is intentional. Flexible straps, decorative legends and visual screw heads are excluded from rigid collision tests. Each exported STEP is reimported; each STL is checked for two-use mesh edges, positive enclosed volume, reasonable agreement with CAD volume and build-volume fit. These tests do not establish tolerances, fatigue strength, print quality or actual cable/service access.

## Estimated material scale

The modeled printed assembly has approximately 2,710 cm³ of CAD polymer volume. At 1.24 g/cm³ that is about 3.36 kg if completely solid; actual slicer mass depends on perimeters, infill, supports and material. Add keyboard, drives, display, metal reinforcement and electronics when estimating carrying weight. This is a substantial prototype, not a lightweight final optimization. Use slicer estimates and measured prototype mass before specifying a handle test load.
