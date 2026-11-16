# Hardware recommendations (16 Nov 2026)

This is a shopping list for the parts that are still open. Each section gives one recommended part with a link, alternatives where useful, and what I still need from you before I fit the part in the CAD.

**Network note:** WebSearch works in this session, but these hosts could not be opened directly: adafruit.com, pololu.com, mcmaster.com, printables.com, bitsavers.org, millennium.ca and silmoh.com. Figures marked *(listing)* come from retailer listings found by search. Check them against the maker's drawing, or measure the part, before printing anything that depends on them.

**Status key:** **SOURCED** = from the maker's own design data · *(listing)* = retailer listing, not yet checked against a drawing · **MEASURE** = I need you to measure it when it arrives.

---

## 1. Greaseweazle V4.1 (confirmed)

**Plan:** use one board for both drives. In IBM/PC mode the Greaseweazle supports two drives on one ribbon with a twist, and PC drives are strapped DS1, so the twist selects A and B ([Greaseweazle wiki: Drive Select](https://github.com/keirf/greaseweazle/wiki/Drive-Select)). This needs a 3-connector **twisted** PC floppy cable (controller, B, twist, A). You lose simultaneous A→B copying, which one board can't do in any case.

Board geometry is **SOURCED** from the official design files ([Design Files wiki](https://github.com/keirf/greaseweazle/wiki/Design-Files), archive `GW_V41_231112.zip`, KiCad 7 Gerbers dated 22 Jul 2023):

| Item | Value | Source in the archive |
|---|---|---|
| PCB outline | **95.0 × 50.0 mm**, corner radius 3.0 mm | `GW-Edge_Cuts.gbr` |
| Mounting holes | 4 × **Ø2.70 mm** (non-plated), for M2.5 | `GW-NPTH.drl` |
| Hole positions | 7.0 mm in from each short edge, 5.0 mm from the header edge and 10.0 mm from the USB edge. Pitch **81.0 × 35.0 mm** | `GW-NPTH.drl` vs. outline |
| 34-pin header | 2×17 shrouded header, pins along the header long edge, row centred 40.6 mm from the left edge | `picknplace.csv` (J1), `GW-PTH.drl` |
| USB-C | On the opposite long edge, centred 75.0 mm from the left edge (the plug points out of the board edge) | J3 and its two NPTH pegs |
| Drive power header | 4-pin, 2.54 mm pitch, next to the 34-pin header (+5V, GND, NC…) | J4, photo `assembled_example.jpg` |

**Not in the design files** (I need these from the real board, so they are flagged in `parameters.json`): the height of the shrouded header, and the size of the IDC plug on your ribbon cable. The board is mounted on its own small printed **sled**, so if a reseller's board differs from the official design, you reprint only the sled.

**Buy:**
- Greaseweazle V4.1. Tindie seller example: [trilobytesretro](https://www.tindie.com/products/trilobytesretro/greaseweazle-v41-usb-floppy-flux-reader-writer). Check that the listing says "V4.1".
- A twisted 34-pin floppy cable with 3 connectors (controller + 2 drives). It replaces the two straight 30 cm rainbow ribbons in your Adafruit cart.
- The board can power **one** 3.5" drive from its header ([V4.1 Setup](https://github.com/keirf/greaseweazle/wiki/V4.1-Setup)). Feed both drives from the internal 5 V bus instead, and leave the "USB 5V ENABLE" jumper fitted only if the board takes its power from USB.

This removes from the BOM: 2× Feather RP2040, 2× Floppy FeatherWing, the headers, the Feather standoffs and one of the two USB cables.

## 2. Power switch: vintage SMK XT/AT switch in a printed housing

**Part:** [MarVac Electronics listing](https://marvac.com/products/vintage-smk-brand-xt-at-pc-computer-power-switch-dpst-on-off-15a-125v): SMK, DPST ON-OFF, 15 A @ 125 VAC, 10 A @ 250 VAC, 1/4" quick-slide terminals. The listing gives the AC rating only; no DC rating is published. At 12 V and about 5 A, that is a light load for these contacts, but it is not a datasheet rating.

No drawing for this switch exists online, so **I'll design the housing from your measurements**. When it arrives, please measure:
1. Body: width × depth × height (the black block, without the terminals).
2. Mounting ears: hole diameter, centre-to-centre spacing, and ear thickness.
3. Paddle: width, thickness, how far it sticks out above the ears, and its throw (the angle, or the travel at the tip, from OFF to ON).
4. Terminals: how far they stick out below the body. Also tell me whether you'll use straight or right-angle 1/4" spade connectors.
5. Which way ON is: toward the front or the rear of the case.

A phone photo next to a ruler, square to the part, helps too. Until then, the CAD keeps the placeholder cutout on the right side toward the rear (`p3.power_switch`).

## 3. MPF-920 drives (arriving today)

The only official dimensions I could find are the outer size: 101.6 × 25.4 × 144.0 mm and about 430 g, from Sony's manual ([pro.sony PDF 4-668-278-11](https://pro.sony/s3/cms-static-content/operation-manual/4668278111.pdf)). The Sony datasheets that might show the mounting holes are on sites this session can't open ([silmoh.com 98-DS.PDF](https://www.silmoh.com/pezzi2/DS/98-DS.PDF), [millennium.ca](https://www.millennium.ca/products/floppy_tape/Sony_MPF920_1.44MB_Floppy_Disk_Drive.pdf)). If you can download either PDF and add it to `docs/reference/`, I'll read it. Otherwise, please **measure one drive**:
1. Side screw holes: distance from the front face (bezel) to each hole, height from the bottom face, and how many holes per side.
2. Bottom screw holes: X and Y from the front-left corner.
3. Thread: try an M3 screw. Most 3.5" floppy drives use M3, but that's a general rule, not a confirmed MPF-920 figure.
4. Rear connectors: the 34-pin header and the 4-pin power socket, measured from one side and from the bottom.
5. Eject button: its centre and size on the bezel.
6. Does it have a drive-select jumper? Or is it fixed at DS1 (the usual for PC drives)?

## 4. Case hardware

All of these have the maker's CAD or drawings online. Once you choose, send the part number (or the drawing PDF) and I'll fit it.

| Item | Recommendation | Why | What I need |
|---|---|---|---|
| **Latches (×2)** | **Southco 97-30-160-12**: small stainless over-centre draw latch, tab-up; the keeper is sold separately ([Southco](https://southco.com/en_us_int/97-30-160-12), [shop](https://shop.southco.com/en_us/97-30-160-12)). | Small enough for the case sides. A sibling part, 97-30-161-12, is listed at 43 × 12.6 × 7.9 mm and 378 N *(listing, [RS](https://ph.rs-online.com/web/p/door-latches/4474887))*. | The matching keeper's part number and the STEP or drawing from Southco's page |
| Latch alternative | Southco 97-50 series (medium), e.g. 97-50-220-12 ([Southco](https://southco.com/en_us_int/97-50-220-12)), about 79.8 × 22.4 × 14.4 mm *(listing)* | Stronger, but long for this case | — |
| **Hinges (×2)** | **Small stainless lift-off hinges** from [McMaster: stainless lift-off hinges](https://www.mcmaster.com/products/stainless-steel-lift-off-hinges/) (e.g. the narrow-profile lift-off hinges with holes). | The lid lifts off for use as a keyboard base. Pick a hinge about 1–1.5" tall with countersunk holes. | The McMaster part number. I couldn't open McMaster, so send me the drawing (each part page has one). |
| **Handle** | **Penn Elcom spring-loaded surface-mount handle** ([zinc surface-mount spring-loaded handle](https://penn-elcom.com/zinc-surface-mount-spring-loaded-handle-2356)), or a folding pull handle from [McMaster: folding pull handles](https://www.mcmaster.com/folding-pull-handles). | Spring-loaded handles fold flat, don't rattle, and are rated for flight cases. | The part number and drawing. The CAD's handle pocket is 210 mm wide (`p2.handle.pocket_x`), so a handle about 120–200 mm long fits. |
| **Feet (×4 case, ×4 lid)** | **3M Bumpon SJ5009**: 22.3 mm diameter × 10.1 mm tall *(from 3M's Bumpon brochure, [PDF](https://multimedia.3m.com/mws/media/175691O/3mtm-bumpontm-protective-products.pdf))*, set into the 22 mm printed recesses already in the CAD. A smaller Bumpon fits the lid. | Adhesive feet in a recess look finished, and the printed TPU feet stay as a backup. | Nothing. I'll check the 3M sheet when you order. |
| **Pins** | 3 mm and 4 mm steel dowel pins (hinge and latch pivots, handle pivots), or M3/M4 shoulder screws | Already in the CAD | Lengths to come with the final hardware |

## 5. Heat-set inserts

**Recommended: CNC Kitchen M3 inserts** ([M3 standard, M3 × 5.7](https://3djake.com/cnc-kitchen/threaded-inserts-m3-standard), [M3 short, M3 × 3.0](https://www.3djake.com/cnc-kitchen/threaded-inserts-m3-short)). The CNC Kitchen [standard set](https://www.3djake.com/cnc-kitchen/threaded-inserts-set-standard) also covers other sizes. The retailer's table gives:

| Insert | Length | Outer Ø | Hole Ø | Minimum wall |
|---|---|---|---|---|
| M3 standard | 5.7 mm | 4.6 mm | **4.0 mm** | 1.6 mm |
| M3 short | 3.0 mm | 4.6 mm | **4.0 mm** | 1.6 mm |

The 4.0 mm hole is what the CAD already uses (`p3.insert.hole_d`). Equivalent: [ruthex RX-M3x5.7](https://3djake.com/ruthex/threaded-insert-m3-100-pieces) (same 4.6 / 4.0 / 5.7 mm figures in the retailer table). Print coupon C1 (holes of 3.9, 4.0 and 4.1 mm) with your shell filament and tell me which hole worked best.

**Change for you to approve:** `p3.insert_short.depth` is currently 4.2 mm, written for "an insert about 4 mm long". If you buy the CNC Kitchen short insert (3.0 mm), I'll set it to 3.0.

## 6. Power, USB, speaker and panel-mount ports

### Recommended power layout
**12 V brick → panel barrel jack → fuse → SMK switch → 5 V buck → 5 V bus.** A fixed 12 V brick is simpler and more reliable than USB-C PD negotiation, and it keeps the vintage AC-rated switch at a low DC voltage.

| # | Part | Link | Key figures | Status |
|---|---|---|---|---|
| 3.1 | **Mean Well GST60A12-P1J**: 12 V / 5 A (60 W) desktop adapter, 5.5 × 2.1 mm centre-positive plug | [Digi-Key](https://www.digikey.com/en/products/detail/mean-well-usa-inc/GST60A12-P1J/7703712), [datasheet](https://www.meanwellaustralia.com.au/sites/default/files/2024-12/MEAN%20WELL%20GST60A%20DATA%20SHEET.pdf) | 90–264 VAC in; short-circuit, overload, over-voltage and over-temperature protection *(listing)* | Buy (the mains cord may be sold separately, depending on the suffix) |
| 3.2 | **Switchcraft 722A**: panel-mount DC jack, 5.5 mm OD / 2.0 mm pin, 5 A | [Digi-Key](https://www.digikey.com/en/products/detail/switchcraft-inc/722A/109410) | Threaded bushing. **Send me the drawing:** the panel hole and the maximum panel thickness | Buy |
| 3.4 | Inline blade-fuse holder + **7.5 A** fuse on +12 V | any ATO/ATC holder rated for 10 A or more | Just above the 5 A brick limit | Buy |
| 3.5 | **Pololu D42V110F5**: 5 V, 11 A step-down regulator | [Pololu 5671](https://www.pololu.com/product/5671) | 1.25" × 1.7" × 0.355" (31.8 × 43.2 × 9.0 mm), 5–60 V in (the real minimum is higher, because of dropout), 11 A continuous *(search result; Pololu blocked here)*. A sibling board's page gives 4 corner holes for #2/M2, 1.53" × 1.0" apart: **verify on the 5671 dimension diagram** | Buy |
| 3.5 alt. | Mean Well DDR-60G-5: DIN-rail DC-DC, 9–36 V in, 5 V **10.8 A** | [Digi-Key](https://www.digikey.com/en/products/detail/mean-well-usa-inc/DDR-60G-5/8681212) | 52.5 × 90 × 54.5 mm *(listing)*: too tall to go under the drives, so it would need a new spot | Only if you want an enclosed industrial module |

The Pololu is small enough for the existing power reservation under the drives. At about 37 W of load, it runs at about two-thirds of its 11 A rating.

**Still needed from the BOM:** the 5 A USB-C pigtail for the Pi (3.6), the 5 V distribution block (3.7), wire (3.8), and the soft power button wired to the Pi's J2 pads (3.9).

### USB
| # | Part | Link | Key figures |
|---|---|---|---|
| 4.1 | **Adafruit CH334F Mini 4-Port USB Hub Breakout (5997)** | [Adafruit](https://www.adafruit.com/product/5997), [guide](https://learn.adafruit.com/adafruit-ch334f-mini-4-port-usb-hub-breakout/overview) | 31.6 × 20.4 × 4.8 mm, 2.9 g *(listing, consistent across several retailers)*. Small enough to go almost anywhere. **I need to check** its connector types (upstream and downstream) before I route the cables. |

**Simpler option without a hub:** the Pi 5 has four USB ports. Put both USB 3 ports on the rear panel, and use one USB 2 port for the Greaseweazle and the other for the side USB-C keyboard port. The keyboard's 2.4 GHz dongle then goes in a rear port, or you use Bluetooth. That's one fewer board and one fewer 5 V branch, but only 2 rear USB-A ports instead of 3.

### Panel-mount ports (all Adafruit, one consistent "screw ear" style)
| # | Part | Link | Panel fixing *(listing)* |
|---|---|---|---|
| 4.2/4.3 | **Panel Mount USB Cable, A male to A female (908)** ×2 or ×3 | [Adafruit 908](https://www.adafruit.com/product/908) | 2 screws, **30 mm** apart. Listings disagree on the screw (4-40 or M3), so **MEASURE** when it arrives. This is a USB 2.0 cable, which is fine for keyboards, sticks and the drive. |
| 4.4 | **Panel Mount Ethernet Extension Cable (909)** | [Core Electronics ADA909](https://core-electronics.com.au/panel-mount-ethernet-extension-cable.html) | 2 × 4-40 screws, **24 mm** apart; boot 20 × 33 × 28 mm |
| 4.5 | **Panel Mount HDMI Cable, 40 cm (978)** + **Micro-HDMI to HDMI Socket Adapter (1358)** | [Adafruit 978](https://www.adafruit.com/products/978), [Adafruit 1358](https://www.adafruit.com/products/1358) | 2 × 4-40 screws, **26.9 mm** apart |
| 4.6 | **Panel Mount Cable, USB-C to Type A, 30 cm (4053)** | [Adafruit 4053](https://www.adafruit.com/product/4053) | 2 × M3 ears, **20 mm** apart, walls up to 0.25" (6.35 mm) |

Round, nut-fixed alternatives exist, such as the [RJ45 round panel mount (4215)](https://www.adafruit.com/products/4215), which needs a hole of about 30 mm. I've kept to the screw-ear family so the rear plate looks consistent.

### Audio
| # | Part | Link | Key figures *(listing)* |
|---|---|---|---|
| 5.1 | Adafruit MAX98357A I2S amplifier (3006) | [Adafruit 3006](https://www.adafruit.com/products/3006) | already in the BOM |
| 5.2 | **Adafruit Mono Enclosed Speaker, 3 W 4 Ω (3351)** | [Adafruit 3351](https://www.adafruit.com/product/3351) | 70 × 30 × 17 mm, 26.4 g. The mounting-hole figures conflict between sellers (63 × 24 mm with Ø3.4 holes, versus 64 × 31 mm with Ø3.1 holes on the plain-wire version), so **MEASURE**. A sealed box sounds better in a printed case than a bare driver. |
| 5.2 alt. | Adafruit 3" 4 Ω 3 W speaker (1314) | [Adafruit 1314](https://www.adafruit.com/products/1314) | 4 mounting tabs 60 mm apart; louder, but needs a 3" grille |

## 7. Display mounting-hole thread depth

This isn't in the Raspberry Pi product brief. The CAD already avoids depending on it: the display bracket uses the 8 M2.5 screws supplied with the display, and the bosses leave room behind them. When the display is in hand, measure the length of a supplied screw. I'll set the bracket thickness so the screw engages without bottoming out.
