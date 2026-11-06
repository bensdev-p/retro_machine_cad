# P2 internals: bill of materials

This lists everything that goes **inside** the Phosphor luggable (P2 concept). The printed case, hinges and latches are listed at the end and get detailed in P2-detail.

**Status key:** **HAVE** = owned or decided · **CART** = in your Adafruit cart · **CHOOSE** = pick a part to the stated requirement · **OPTIONAL** = nice to have · **VERIFY** = a fact I could not confirm from a source; check it before buying.

I have not picked brands or models where I could not confirm the dimensions. Those items are written as requirements. When you choose a part, send me its datasheet or dimensions and I will fit it in the CAD.

---

## 1. Core computer

| # | Qty | Part | Status | Notes |
|---|---|---|---|---|
| 1.1 | 1 | Raspberry Pi 5 (RAM size is your choice) | HAVE | Mounted on the display's rear 58 × 49 mm M2.5 pattern |
| 1.2 | 1 | Raspberry Pi Active Cooler (official) | CHOOSE | The CAD reserves its envelope plus 22 mm of air before the drawer |
| 1.3 | 1 | Raspberry Pi Touch Display 2, 10.1" | HAVE | The product brief in `docs/reference` lists the DSI ribbon, the GPIO power cable and 8 × M2.5 screws as included. Screw length is not in the brief. |
| 1.4 | 1 | microSD card, 64 GB or larger, A2 class | CHOOSE | The RetroOS POST sample data assumes "SD card 64 GB" |
| 1.5 | 4 | M2.5 standoffs (6 mm) plus screws, Pi to display | CHOOSE | The CAD uses a 6 mm standoff. Check whether the display's included screws suit it. |
| 1.6 | 1 | Raspberry Pi 5 RTC battery (official, plugs into the Pi 5 battery connector) | OPTIONAL | Keeps the clock running while the case is unplugged, which suits a luggable |
| 1.7 | 1 | microSD extension cable to a rear-panel slot | OPTIONAL | The Pi sits behind the screen, so without this you have to open the case to swap cards. Needs a rear-panel cutout. |

## 2. Floppy subsystem

| # | Qty | Part | Status | Notes |
|---|---|---|---|---|
| 2.1 | 2 | Adafruit 6037 Upcycled Sony MPF-920 drive | CART | 146.1 × 101.6 × 25.4 mm, +5 V only, 1.25 W normal operation |
| 2.2 | 2 | Adafruit Floppy FeatherWing (5679) | CART | 50.8 × 22.8 × 13.6 mm. Works only with Feather M4 or RP2040. Drive power is not supplied through it. |
| 2.3 | 2 | Rainbow 34-pin IDC ribbon, 30 cm | CART | One per drive; no twisted cable needed. **VERIFY** which drive-select line the Adafruit firmware uses versus the drive's jumper. |
| 2.4 | 2 | Adafruit Feather RP2040 (4884) | CHOOSE | 50.8 × 22.8 × 7 mm, USB-C. Runs Adafruit's Greaseweazle-compatible firmware. |
| 2.5 | 2 sets | Headers to join each Feather to its FeatherWing | CHOOSE | Header type sets the stack height. The CAD reserves 32 mm; about 38 mm is available. **VERIFY** whether headers come with the boards. |
| 2.6 | 2 | Floppy drive power lead: 4-pin floppy ("Berg") female to wires | CHOOSE | Feeds +5 V/GND from the internal 5 V bus to each drive. The 12 V pin stays unused. |
| 2.7 | 2 | USB-C to USB-A **data** cable, short (15–20 cm, right-angle preferred) | CHOOSE | Feather to internal hub |
| 2.8 | 4 | M2.5 or #2 nylon standoffs plus screws per stack | VERIFY | The Feather and FeatherWing hole size and positions are not sourced yet |
| 2.9 | 8 | Drive mounting screws | VERIFY | The MPF-920 screw thread and hole positions are not sourced yet |
| 2.10 | — | HD 1.44 MB disks, DD 720K disks, one head-cleaning disk | CHOOSE | HD disks for PC formats; DD disks for Amiga and Atari ST |

## 3. Power

**Architecture:** one DC input feeds a master switch and fuse, then a single **5 V bus** powers everything. The Pi 5 takes its power from the bus through a USB-C pigtail cable. Because that supply can't negotiate with the Pi the way an official Pi supply does, two settings tell it to allow full current: `PSU_MAX_CURRENT=5000` in the Pi's EEPROM and `usb_max_current_enable=1` in `config.txt` ([Raspberry Pi white paper](https://pip-assets.raspberrypi.com/categories/685-app-notes-guides-whitepapers/documents/RP-009856-WP-1-USB%20Power%20delivery%20on%20Raspberry%20Pi%205.pdf)). Those settings only remove a software limit, so the 5 V supply must really be able to deliver the current.

| # | Qty | Part | Status | Requirement |
|---|---|---|---|---|
| 3.1 | 1 | External power adapter | CHOOSE | **Option A (recommended):** a 65 W or larger USB-C PD charger with a USB-C PD trigger board set to 20 V. **Option B:** a 12 V DC brick (5 A) with a barrel jack. |
| 3.2 | 1 | Input connector | CHOOSE | A panel-mount USB-C PD trigger (option A) or a panel-mount barrel jack (option B). It must fit the rear I/O plate. |
| 3.3 | 1 | **Master power switch**: rocker, DC rated | CHOOSE | Rated for at least the input voltage and **at least 6 A DC**. It switches the DC input after the jack. The CAD has a provisional 21 × 14 mm cutout, which will change to match the switch's datasheet. An illuminated switch is optional. |
| 3.4 | 1 | Inline fuse and holder on the input | CHOOSE | Just above the full input current: about 4–5 A for 20 V, or 7.5 A for 12 V |
| 3.5 | 1 | **DC-DC buck converter to 5 V, 10 A (50 W) or more** | CHOOSE | Must accept your input voltage. Pick one with mounting holes and a heatsink. The CAD reserves about 61 × 59 × 24 mm. |
| 3.6 | 1 | USB-C pigtail rated for 5 A (USB-C male to wires, 18 AWG or heavier) | CHOOSE | 5 V bus to the Pi 5 |
| 3.7 | 1 | 5 V / GND distribution (terminal block or bus bar) | CHOOSE | Feeds the Pi, hub, both drives, the amp and the LEDs |
| 3.8 | — | Wire: 16 AWG for the 5 V trunk, 18 AWG for branches, 22–24 AWG for signals and LEDs | CHOOSE | Silicone insulation is easiest to route |
| 3.9 | 1 | **Soft power button**: momentary, normally open | CHOOSE | Wired to the Pi 5's **J2** pads, which act like the on-board power button ([element14](https://community.element14.com/products/raspberry-pi/f/raspberry-pi-5-faq/53770/does-the-raspberry-pi-5-have-a-power-button-and-how-does-it-function/214935), [Core Electronics forum](https://forum.core-electronics.com.au/t/raspberry-pi5-power-button/20125)). It lets RetroOS shut down cleanly ("It is now safe to turn off your computer"). The rocker is the hard off. **VERIFY** against the official Pi 5 docs; it also needs a 2-pin header soldered on and a hole in the case. |

**Power budget** (5 V side):

| Load | Figure | Source |
|---|---|---|
| Raspberry Pi 5, including up to 1.6 A total from its USB ports | up to about 25 W | Pi 5 5 V/5 A supply class; white paper above |
| Touch Display 2, 10.1" | 5.1 W | product brief in `docs/reference` |
| 2 × MPF-920 | 2 × 1.25 W normal operation; **spin-up peak unknown** | Sony manual |
| MAX98357A amp (if fitted) | up to 3.2 W into 4 Ω | Adafruit 3006 |
| Hub, 2 × Feather, keyboard dongle, LEDs | estimate about 1.5 W | **estimate, not sourced** |
| **Total** | **about 37 W plus drive spin-up** | → a **50 W or larger** 5 V converter leaves headroom |

## 4. USB and rear I/O

The Pi 5 has 4 USB-A ports: 2 × USB 3, 2 × USB 2.

| # | Qty | Part | Status | Notes |
|---|---|---|---|---|
| 4.1 | 1 | Internal USB 2.0 hub board, **4 ports or more, with its own 5 V power input** | CHOOSE | Powered from the 5 V bus. It connects the two Feathers, the keyboard dongle and the side USB-C port. Upstream to one Pi USB 2 port. The CAD reserves about 79 × 72 × 26 mm above the drives; send me the board's dimensions. |
| 4.2 | 2 | Panel-mount USB 3 extension (USB-A male to female, short) | CHOOSE | Pi USB 3 ports to the rear panel |
| 4.3 | 1 | Panel-mount USB 2 extension | CHOOSE | The Pi's remaining USB 2 port to the rear panel (3 rear USB-A in total) |
| 4.4 | 1 | Panel-mount RJ45 extension (Cat6, short) | CHOOSE | Pi Ethernet to the rear panel |
| 4.5 | 1 | Micro-HDMI male to HDMI female panel-mount cable | OPTIONAL | External monitor |
| 4.6 | 1 | Panel-mount USB-C female to USB-A male (data) | CHOOSE | The case's left-side keyboard port (wired mode and charging), into the hub |

The CAD's rear plate currently shows 4 USB-A openings plus HDMI, RJ45, USB-C power and a rocker. I'll match these to the chosen panel-mount parts in P2-detail.

## 5. Audio

The Pi 5 has no 3.5 mm audio jack, and the RetroOS startup chime needs a speaker.

| # | Qty | Part | Status | Notes |
|---|---|---|---|---|
| 5.1 | 1 | Adafruit MAX98357A I2S 3 W amplifier (3006) | CHOOSE | Mono, I2S. Wired to 5 V, GND, GPIO18 (BCLK), GPIO19 (LRCLK) and GPIO21 (DIN) ([Adafruit 3006](https://www.adafruit.com/products/3006)). RetroOS's `config.txt` will need the matching audio overlay; **VERIFY** it on a Pi 5. |
| 5.2 | 1 | Speaker, 4 Ω or more, about 3 W | CHOOSE | Needs a grille and a mounting spot in the case; send me its size. The top louvres or a side grille are candidates. |
| 5.3 | 1 | USB audio adapter with a headphone jack | OPTIONAL | Plugs into the hub |

## 6. Front panel and status

| # | Qty | Part | Status | Notes |
|---|---|---|---|---|
| 6.1 | 1 | 5 mm LED, red: POWER | CHOOSE | From the 5 V bus through a resistor. The fascia holes are 5.2 mm. |
| 6.2 | 2 | 5 mm LED, green or lime: A and B | CHOOSE | Driven from a spare pin on each Feather (3.3 V) so they show real drive activity |
| 6.3 | 3 | Current-limiting resistors | CHOOSE | Value depends on each LED's forward voltage and current; I'll calculate them once you've picked LEDs |
| 6.4 | — | 2.54 mm Dupont/JST leads, heat-shrink | CHOOSE | |

## 7. Keyboard

| # | Qty | Part | Status | Notes |
|---|---|---|---|---|
| 7.1 | 1 | 8BitDo Retro Mechanical Keyboard M Edition (376.6 × 169.6 × 46.8 mm) | HAVE / deciding | **VERIFY** that it comes with a 2.4 GHz dongle. If it doesn't, use Bluetooth or the side USB-C port. |

## 8. Cooling

| # | Qty | Part | Status | Notes |
|---|---|---|---|---|
| 8.1 | — | Active Cooler (1.2) plus the case's top louvres and left-side vent slots | — | Passive case airflow, sized in the CAD |
| 8.2 | 1 | 40 mm 5 V case fan | OPTIONAL | Add it only if thermal testing shows throttling |

## 9. Fasteners and mounting (the internals side)

| # | Part | Status |
|---|---|---|
| 9.1 | Drive screws: **VERIFY** the MPF-920 thread | — |
| 9.2 | Feather standoffs: **VERIFY** the hole size | — |
| 9.3 | M3 screws and nuts or heat-set inserts for the cage, hub shelf and buck mount; counts come with P2-detail | CHOOSE |
| 9.4 | Cable ties, adhesive cable mounts, Kapton tape | CHOOSE |

## 10. Case hardware (specified in P2-detail)

The lift-off hinge pair; 2 side latches; the fold-flat handle (which needs a steel or aluminium core, see the P1 handle notes); rubber feet (4 on the case, 4 on the lid); drawer rails (printed); keyboard retention clips (printed).

---

## Still open: I need these from you

1. The drive's screw positions and thread, its rear connector positions, its eject-button position, and its spin-up current.
2. The Feather RP2040 and FeatherWing hole positions, and the assembled stack height.
3. Datasheets or dimensions for the parts you choose for 3.1–3.5 and 3.9 (adapter, input connector, rocker switch, fuse, buck converter, soft-power button).
4. Dimensions of the hub board you choose (4.1), and the panel-mount cutouts for 4.2–4.6.
5. Speaker size (5.2) and where you'd like the grille.
6. Whether the keyboard includes a 2.4 GHz dongle (7.1).

Sources for verified figures are listed in [`docs/concept-P2.md`](concept-P2.md), under "Floppy subsystem: verified vs. still needed", and inline above.
