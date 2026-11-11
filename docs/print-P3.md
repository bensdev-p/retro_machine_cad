# P3 printable v1: print and assembly guide

P3 turns the approved P2 concept (M Edition colourway, Phosphor branding) into printable parts. The shape is unchanged; this stage adds joints, heat-set inserts, printed hardware and the print setup.

- **Generator:** `cad/p3_print.py`. It reuses `cad/p2_concept.py` for the shared geometry.
- **Parameters:** `parameters.json` → `p3`, plus `p2` for the shape.
- **Outputs:** `outputs/p3/`
  - `stl/`: one STL per part, already oriented for printing, plus an inlay STL for each multi-colour part
  - `3mf/`: multi-colour parts, with the part and its inlays as separate bodies
  - `print_manifest.csv`: printer assignment, size, volume and notes for every part
  - `p3_assembly.step`: the full assembly
  - `validation.json`: fit and clearance checks
  - `viewer.html`: Assembled / Closed / Exploded / X-ray views

> **Status: not yet print-tested.** Print the **coupons first** (below). Several inputs are still placeholders; see "Open inputs".

## Printers and part split

Build volumes, from manufacturer pages via search; the scripts keep a 5 mm margin:

| Printer | Volume (mm) | Used for |
|---|---|---|
| H2C | 325 × 320 × 320 (left nozzle); 300 wide with both nozzles; sources disagree on Z (320 vs 325), so 320 is used | The two shell halves |
| X2D | 256 × 256 × 260 single nozzle (235.5 wide with both nozzles) | Large flat parts |
| A1 | 256³ | Bezels, lid halves, rear panels, drawer |
| A1 mini | 180³ | Hinges, latches, handle parts, feet, coupons |

The script picks the **smallest printer that fits** each part in its print orientation (preference order: A1 mini → A1 → X2D → H2C). The result is in `print_manifest.csv`.

**Assignment from this run** (every part fits with the 5 mm margin):
- **H2C:** screen bezel, drawer panel, drawer.
- **A1:** shell halves (210 × 249.5 × 200 mm, which fits since the measured keyboard moved the front forward), lid halves, drive bezel, I/O plate, handle, display bracket.
- **A1 mini:** everything else, including the drive cage, hinges, latches, feet and coupons.

**Front bezels are multi-part prints:** the dark shield and shroud plus the warm-grey grooved face print together as one object. The face is listed as `bezel_*_face` inside the same `.3mf`. This keeps the two-tone look without gluing anything.

**Why the case splits:** it is 400 mm wide, and no bed takes 400 mm. The splits are placed where they read as deliberate or stay hidden:

| Part | Split | Joint |
|---|---|---|
| Shell | Centre seam at `p3.seam_x` = 200 mm | Internal screw blocks (counterbored screw on the left half, insert on the right), 2 dowels through the solid front ring. The front bezel and rear panel also bridge the seam. |
| Front bezel | At the screen/drive divide, hidden by the shroud edge | Each half screws to the shell separately |
| Rear | Drawer panel plus a separate **replaceable I/O plate** | Flat-head M3 into ledge inserts |
| Lid | Centre seam at 200 mm, aligned with the shell seam when closed | 2 splice plates recessed under the keyboard, 2 dowels |

## Multi-colour and branding

**Recommendation: yes, use the AMS.** The wordmarks, model lines, nameplate and diamond are **flush inlays**: separate bodies sitting in matching pockets. Assign them a filament in Bambu Studio. They are always on a face that prints flat:
- **Side wordmarks:** each shell half prints on its outer side, so the logo is on the bed face and comes out smooth and crisp.
- **Closed-lid logo:** the lid halves print on their outer face, so it's also on the bed.
- **Keyboard-deck badge and nameplate:** on the top face of the print.

**In Bambu Studio:**
1. Open the part's `.3mf`. When asked, load it as **a single object with multiple parts**.
2. Give the main part the shell colour, the wordmark the brand colour, and the diamond rings Cobalt, Sky, Aqua and White.
3. For a single-colour printer, use the separate `*__inlay_*.stl` files: print the inlays on their own and press or glue them in.

## Fasteners

- **Heat-set inserts:** M3 by default. Hole diameter and depth are `p3.insert`; the starting values (4.0 mm hole, 5.7 mm long insert) **must be checked against the inserts you buy**. Coupon C1 tests three hole sizes.
- **Short inserts** (`p3.insert_short`, about 4 mm long) are used where the wall is only 5 mm thick: the latch bases on the shell sides.
- **Screws:** M3 socket-head for internal joints, M3 flat-head into the rear ledge.
- **Dowels:** 3 mm steel pins.
- **Hinge pin:** 3 mm steel. **Latch pivots:** 3 mm pins or M3 shoulder screws. **Handle:** 8 mm metal rod core, 4 mm steel pivot pins.

None of the joint screws show on the outside, except:
- the flat-head screws on the rear panel (as on the Kaypro),
- the latch-base screws (like real latch hardware),
- the case-floor screws under the drive cage, on the underside.

## Printed hardware

| Part | Notes |
|---|---|
| Hinges | Interleaved knuckle blocks: the middle knuckle is on the case, the end knuckles on the lid, with a 3 mm steel pin. Bolted to the case's solid bottom front ring and to the lid's rear face. |
| Latches | Base plus lever, with a pin pivot. The lever hooks over the closed lid's front edge. |
| Handle | Printed grip over an 8 mm rod, on printed pivot blocks bolted into bosses under the handle tub. **Load-test it before carrying the machine by it.** |
| Feet | TPU, pressed into 1.5 mm recesses (4 on the case, 4 on the lid). |
| Keyboard clips | Swing clips on the keyboard deck. |
| Drive cage | Corner posts with inserts, screwed up from under the case. The drive screw slots are generic for now. |
| Display bracket | Frame on the display's outer M2.5 rear pattern, bolted to bosses on the screen bezel's flange. The glass sits behind the shroud with a small gap; nothing presses on it. |

## Coupons (print these first)

Generated alongside the parts as `coupon_*`:

| | What it tests |
|---|---|
| C1 | Insert holes at 3.9 / 4.0 / 4.1 mm: pick the best one and set `p3.insert.hole_d` |
| C2 | Hinge knuckles and pin fit: print `hinge_case_1` and `hinge_lid_1` (they're small) |
| C3 | Shell seam: screw block and dowel |
| C4 | Top-right lip corner of the shell (check the closed-lid gap against a lid corner) |
| C5 | Inlay colour test: a slice of the side wordmark plus its inlay |
| C6 | Screen-shroud corner and bezel flange insert |
| C7 | Latch base and lever: print `latch_base_left` and `latch_lever_left` |

## Material and colour

PLA is fine for the coupons and a first prototype. For the final build, use **PETG or ASA**, choosing whichever matches the keyboard best now that it has arrived. The colour roles come from `p2.palettes.m_edition`:
- shell: off-white
- fascia and keyboard deck: warm greys
- bezels: dark charcoal
- branding: dark warm grey, plus the four Phosphor blues

## Open inputs (placeholders in the model)

1. **Keyboard:** measured: front edge 19.05 mm and rear edge 38.6 mm (the listing's 376.6 × 169.6 × 46.8 mm is confirmed). The wedge is now 18.9 → 43.1 mm with a 6.6° deck.
2. **MPF-920:** side screw positions and thread (the cage uses long slots for now), rear connector positions, eject button position. Your photos confirm the black bezel, the eject button on the right, the LED on the left, and the 34-pin and power connectors at the rear.
3. **Display:** mounting-hole thread depth. Your estimate of about 25 mm of protrusion is inside the reserved Pi/cooler space.
4. **Greaseweazle V4.1:** board size and mounting holes.
5. **Big Red Switch (Printables 459567):** its STEP or dimensions, and which electrical switch it actuates. The right-side cutout (`p3.power_switch`) is a placeholder, with a keep-out space inside.
6. **Inserts:** the brand, hole diameter and length.
7. Power and I/O parts (see `docs/BOM-P2.md`). The I/O plate is replaceable, so these don't block printing.
