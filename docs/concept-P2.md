# P2 concept: Kaypro-style luggable

P2 replaces the flat P1 "box with a carrier" layout with a massing based on the Kaypro II and Kaypro 10. The P1 files in `outputs/prototype` are still there for reference, but P2 is now the direction for the design.

This is a **concept model**. It sets the overall form, the transport scheme and where the internals go. It is not yet split into printable parts (see "Next steps").

![Operating, charcoal](../outputs/p2/previews/01_operating_charcoal.png)
![Closed for carrying](../outputs/p2/previews/03_closed_carry.png)

## What changed from P1 and why

| Request | P2 answer |
|---|---|
| Kaypro "shielding" around the screen and drives | The front panel sits **56 mm back** inside a hood made by the top, sides and base. An **angled shield ring** (8 mm at 45°) joins the hood walls to the fascia. Inside that, the screen and the drive pair each have their own **angled frustum surround**, like the Kaypro CRT bezel. The glass and drive faces sit another 10 mm back. |
| Keyboard covers the display when closed | The keyboard sits in a **housing that is also the front lid**. In use it lies flat as the keyboard surround. For carrying, you flip it keys-inward. Its rim plugs into the hood, its 400 × 210 base plate becomes the whole front face, and two **side latches** clamp the plate's edges. |
| Not flat | The design has a recessed fascia, angled shrouds, Kaypro 10-style horizontal grooves beside the drives, a ribbed side wrap, top louvres, a recessed handle tub and an inset rear panel. |
| 2 floppies, vertical, side by side | Two drives (Sony MPF920 envelope, 101.6 × 25.4 × 150) stand vertically to the right of the screen, with POWER / A / B LEDs above. |
| USB hub out the back | A hub envelope sits on a shelf above the drive cage. Its ports, plus HDMI, RJ45, USB-C power in and a rocker switch, are on the rear I/O plate. |
| Use empty space for storage | The space behind the screen holds a **rear pull-out drawer**. It has a diskette file on the left (about 26 3.5" disks standing on edge) and an accessory/cable bin on the right. |
| Darker keyboard | The renders use charcoal keycaps. The housing and keyboard envelope are sized from the 8BitDo M Edition dimensions (376.6 × 169.6 × 46.8). |

There are two colourways in the viewer: **charcoal** (Kaypro 10-like) and **classic** (Kaypro II-like off-white with blue).

## Key dimensions (from `outputs/p2/validation.json`)

- Case: **400 W × 210 H × 250 D mm**, plus 6 mm feet.
- Closed, including lid and latches: **426 × 216 × 259 mm**. The raised handle is extra.
- Keyboard unit (lid): 400 × 210 mm plate, about 45 mm tall with the keys and feet.
- Hood opening: 390 × 189 mm. The lid rim has 1 mm clearance per side.
- Fascia plane: 56 mm behind the lip. With the full 46.8 mm keyboard height, the closed keyboard leaves **8.2 mm** to the fascia.
- Screen glass: 66 mm behind the lip. The visible active window is 216.6 × 135.4 mm (Touch Display 2, 10.1").
- Pi 5 sits on the display's inner 58 × 49 M2.5 pattern. Behind the Active Cooler there is a 22 mm air gap before the drawer.
- Operating footprint: about 488 mm deep with the keyboard 28 mm in front of the case.

All of the clearance and interference checks in `validation.json` pass. These cover the closed lid against the front parts, the drawer (in and pulled out) against the internals, the drives, the display/Pi, and the handle in both positions.

## Hardware assumptions to confirm

These are envelopes, not product models:

1. **Sony MPF920 size and mounting.** I used 101.6 × 25.4 × 150 mm. The real side screw positions and front bezel are needed before the cage is detailed. The MPF920 is a 34-pin drive, so it needs a USB floppy controller (a Greaseweazle-class board, 60 × 50 envelope under the drives). One twisted cable serves both A and B.
2. **8BitDo profile.** Only the overall box (376.6 × 169.6 × 46.8) is a real input. The keycaps are an illustrative TKL layout. If you change to a different charcoal keyboard, its height is what sets how deep the fascia sits. Its width and depth set the hood and lid size.
3. **Power.** A 5 V distribution / USB-C PD input envelope (about 70 × 48 × 24) feeds the Pi, the hub and the drives. You still need to choose the actual parts.
4. **USB hub.** The model reserves an 79 × 72 × 26 mm envelope with its ports facing the rear.
5. **Touch near the screen edges.** The 10 mm deep, 45° frustum gives a Kaypro look, but it may make the outermost few mm of the touch area awkward to reach. The depth and slope are parameters (`p2.screen_shroud`).

## Open design questions

- **Handle.** P2 uses a fold-flat bail handle in a top tub, pivoting about 136 mm behind the lip, roughly over the centre of mass with the lid on. A side strap handle is another option.
- **Tilt.** The case sits flat, like the Kaypro. A fold-out rear foot could angle the touchscreen.
- **Keyboard link.** The 8BitDo works over 2.4 GHz or Bluetooth, so there is no fixed cable. There is a USB-C port on the left side for wired use or charging, and a cable notch in the lid rim.
- **Branding.** The case uses the project name "RETRO / M". It deliberately avoids Kaypro marks.

## Next steps (P2-detail)

1. Agree on the form, proportions and colourway.
2. Get real drawings or measurements of the MPF920, the chosen keyboard and the hub.
3. Split the shell, fascia, lid and drawer to fit a 256 mm print bed. P1's seam strips and captive nut pockets can be reused.
4. Design the latch mechanism and the lid-rim alignment features, then print fit coupons.

## Files

- `cad/p2_concept.py`: parametric build123d model. The inputs are in `parameters.json` under `p2`.
- `outputs/p2/p2_operating.step`, `outputs/p2/p2_closed.step`: assemblies for FreeCAD or other CAD tools.
- `outputs/p2/viewer.html`: offline 3D viewer. Open it in any browser to switch between operating, closed, rear/drawer and X-ray views and between the two colourways, and click parts for their notes.
- `outputs/p2/previews/*.png`: renders from the viewer.
- `outputs/p2/validation.json`: dimensions and clearance checks.
- Rebuild with `./rebuild-p2.sh`. This needs the `requirements.lock` venv, and Node with Playwright for the PNGs.
