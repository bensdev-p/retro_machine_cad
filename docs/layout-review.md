# Milestone 1 — review before detailed design

## Current inputs

User selected the front keyboard carrier. The uploaded Raspberry Pi Touch Display 2 — 10-inch Portrait product brief (October 2026) confirms the product identity, 10.1-inch diagonal, 135.36 × 216.576 mm active area, native 1200 × 1920 pixels and 24-bit RGB. Landscape uses 216.576 × 135.36 mm and 1920 × 1200 pixels. The viewing angle is 85 degrees, with full/half angle convention unspecified.

PDF page 5 (printed page 4) gives a landscape outline of **248.096 × 166.88 mm**, maximum depth **15.55 mm**, corner radius **5 mm**, and centered active-area offsets **15.76 mm**. The solid is a conservative rectangular full-depth envelope, not an exact reproduction of the rounded glass or stepped rear electronics. The drawing explicitly describes its dimensions as approximate reference data, unsuitable for production data. Parameters distinguish manufacturer reference data from physically measured dimensions. Touch access reserves 5 mm around the active area through the 12 mm front recess; exact finger reach needs physical validation.

The brief confirms Pi 5 compatibility, a mini-mini DSI cable, GPIO power cable, eight M2.5 screws and 5.1 W display consumption. The two supply rows (3.3 V at 340 mA and backlight 5 V at 800 mA) are specifications, not an instruction to wire external rails directly. Use the supported supplied display power connection and budget system power for the Pi, cooling and both drives.

The rear drawing shows eight M2.5 positions: an inner 58 × 49 mm pattern in landscape and an outer 160 × 121.8 mm pattern. Coordinates and their dimension-chain derivation are stored centrally in parameters.json. The eight magenta markers show axes only; their rectangular visualization bars are not holes, bosses, screws or fabrication features. Their Y position is a visualization location behind the maximum-depth envelope: it does not establish the actual mounting plane.

The Pi envelope is centered provisionally around the inner mounting pattern, parallel to the display and with cooler facing rear. This is not a mounting-alignment claim: the board-edge offsets, orientation, connector locations and actual Pi hole positions need its own verified drawing. A provisional 6 mm stand-off plus 1.6 mm board, 24 mm cooler and 15 mm airflow reservation occupies 46.6 mm behind the screen envelope, ending at Y=74.15 mm. Drives still set the 205 mm case depth. The gap is conservative, not a selected spacer. Thread engagement, supplied screw lengths and support-plane depth are not established by the brief. The cable reservation above/left of the Pi is not a verified route.

Stock 8BitDo M Edition keyboard: 376.6 × 169.6 × 46.8 mm, supplied manufacturer dimensions. The envelope includes keys and knobs. Future pads must contact measured housing lands only; transport retention and access to rear controls/connectors are not yet established.

Drives are undecided. The current two 145 × 150 × 22 mm boxes are explicit invented placeholders for housed slim USB drives. They sit horizontally one above the other. A legacy drive with USB conversion needs different dimensions, adapter and power allowances, and a compatibility test before choosing it. A slim drive can retain its housing inside a removable cradle with a retro cosmetic bezel; this preserves the original PCB/mechanism alignment. Do not design slot, button or LED apertures until the selected drive is measured.

Pi 5 board uses nominal 85 × 56 × 1.6 mm dimensions, with an invented 60 × 45 × 24 mm cooler allowance. These are not verified against a drawing in this session. Download of the official drawing at https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-mechanical-drawing.pdf returned HTTP 403; Git access to the official documentation repository worked but did not provide that drawing. Therefore no mounting coordinates are specified. Verify the board revision, holes, actual cooler and connector envelopes before mounts. Generic 40 mm exit regions reserve space for connector bodies and bends but do not prove actual cables can bend or be serviced there. DSI and fan wiring, microSD extraction, power-button access, GPIO and port-panel routing remain to model.

Printers: A1, A1 mini, H2C and X2D. Nominal A1 volume is 256³ mm and mini is 180³ mm. Verify slicer limits, brims and toolhead restrictions. H2C/X2D usable volumes are pending; no fit claim is made for those machines. PLA is selected for prototypes. Consider PETG for the eventual shell and handle reinforcement after temperature and load tests. Use shell structure and hardware for rigidity rather than adding arbitrary ballast; transport weight and handle loads must be measured.

External power for v1; battery not required. Future battery or accessories require explicit new allocations, cooling review and weight/load review.

## Derived envelope

Coordinates: X left-to-right, Y front-to-rear, Z up; front exterior at Y=0. Display and drive front faces at Y=12. All dimensions below are millimeters.

| Constraint | Calculation | Result |
|---|---|---:|
| Width | 2 × (3 wall + 10 edge margin) + 248.096 screen + 12 separation + 145 drive | 431.1 |
| Height | 2 × (3 wall + 10 edge margin) + 166.88 screen | 192.9 |
| Depth | 12 recess + 150 drive + 40 rear cable + 3 wall | 205.0 |
| Carrier envelope width | 376.6 + 2 × (4 clearance + 3 wall) | 390.6 |
| Carrier envelope height | 169.6 + 2 × (4 clearance + 3 wall) | 183.6 |
| Carrier additional depth | 46.8 keyboard + 4 clearance + 3 wall + 6 case gap | 59.8 |

This is a compact starting layout for the assumptions, not a global minimum or a fabrication tolerance specification. Final brackets, shell joints, connector plugs, venting and handle reinforcements may enlarge it. Keyboard carrier width and height also participate in the case-size formulas, though the screen/drive arrangement currently dominates. The broad proportions follow the written Kaypro direction; no concept image was available in this conversation.

## Keyboard alternatives

| | A: front carrier | B: separate keyboard |
|---|---|---|
| Case plus carrier W × H × D | 431.1 × 192.9 × 264.8 | Case 431.1 × 192.9 × 205.0 |
| Keyboard | Rotated upright over front | Stock unit carried separately |
| Benefit | One transport assembly; can protect front | Fewer parts, lower carrying load on case |
| Tradeoff | Latches, protected housing contacts, extra depth and load | Requires separate protection/packing |

A is a separate close-fitting carrier, not a whole-width oversized lid. It must be removed for use: it deliberately occupies the front disk-access/touch region while transported. The keyboard has no invented contact points or latches. A is now the selected design direction. B is retained only as a comparison reference. A future handle must transfer load through reinforced base/side structure, not thin front panels. No mouse compartment is included.

## Executed verification and limits

The generator checks 27 valid positive-volume single solids (including eight mounting-axis markers) and compares their bounding boxes to the parameter dimensions. It tests every hardware/hardware pair and hardware versus internal cable, touch and cooler-air reservations using exact B-rep intersections. No positive-volume unwanted intersections were found. The cooler contacts the rear-facing board plane; connector-zone-to-component boundaries intentionally touch. The transported keyboard is also checked against all physical hardware. Internal cable/air reservations are checked against the case interior. Case/carrier containment and active-screen reference overlays are intentional. External disk access volumes are operating-space reservations and are not valid while carrier A is installed.

Front, side, top and three-quarter renders come from tessellated CAD solids, not image-generation artwork. The shell envelope is wireframe for internal inspection; a material-shell cutaway cannot be validated before shell geometry exists. Rendering transparency is illustrative; exact interference assertions are the numerical evidence.

Single-piece case envelope exceeds A1 and A1 mini build volumes. Detailed parts have not been designed or tested in a slicer. In a flat panel plan, A1 could start with two width sections; mini also needs division along the 193/205 mm panel direction. Fastener flanges and alignment tabs require extra margin, so this is not a committed seam layout. H2C/X2D fit is untested. Mount alignment, housing-only keyboard retention, drive operability, cooling, port access, mass and handle capacity remain unverified.

## Next milestone after layout review

1. Measure the display mounting plane and thread engagement against the supplied reference drawing; choose and bench-test two matching drives and any adapters. Obtain verified Pi mechanical drawing and exact cooler/cables.
2. Define fascia, screen bracket, removable two-drive cradles, base, shell sections and rear service panel. Use straight sides, small chamfers, warm gray shell, charcoal recessed fascia and restrained blue accents. Select a folding/strap handle with a reinforced load path.
3. Choose actual screws/inserts from hardware drawings; reserve tool access and determine seams for the chosen printer. Fit clearances remain unverified until printed.
4. Produce screen-corner, drive-opening/eject, keyboard-housing-retention and screw/insert/mating samples. Print and measure them before full shell parts.
5. Export printable STEP and STL/3MF for reviewed parts; validate each part against printer volume with orientation and brim allowances. Prefer broad panel faces on the bed and avoid supports in touch/fit surfaces; exact orientations depend on seams and insert bosses.
6. Provisional assembly sequence: test electronics externally; assemble base and reinforcement; attach Pi/cooler to the verified display rear mounts on the bench; install the complete display/Pi module and drives into removable mounts; route and strain-relieve cables; connect and function-test; fit shell and removable rear; add chosen keyboard carrier. Check screw access and reverse removal at each step. This sequence is not yet geometrically validated.

Planning hardware list: owned keyboard and display, Pi 5, confirmed cooler, two matching drives, appropriate USB and display cables, suitable Pi 5 external power supply, verified handle/strap, fasteners/inserts selected later, and non-marring retention pads selected after housing measurements. Quantities/lengths for fasteners, power distribution, optional powered USB hub and adapter hardware remain open. No final hardware shopping list or load rating is implied.

## Review status

Front carrier selected. Manufacturer reference dimensions and all eight M2.5 axes are now incorporated from the supplied PDF. Source PDF, SHA-256 and rendered physical-specification page are retained in docs/reference and parameters.json. Next mechanical inputs are actual support-plane height, screw lengths/engagement, verified Pi geometry/cooler and drive selection. Do not fabricate final mounts from this approximate envelope alone.
