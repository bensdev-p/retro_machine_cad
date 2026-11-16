# Handoff: Phosphor luggable enclosure (updated 16 Nov 2026, second session)

Branch: `claude/sharp-gates-zmf806` (not merged; no PR opened). Everything below is committed there.

## What exists
- **P2 concept** (`cad/p2_concept.py`, `docs/concept-P2.md`, `outputs/p2/`): the agreed look.
  - Kaypro-style luggable with an angled shielded front, a slanted case lip, and a hinged wedge keyboard lid that props the case back about 10.9° when open.
  - Two vertical MPF-920 drives, a rear diskette drawer, and a rear I/O plate.
  - **Chosen colourway: "M Edition match"** (`p2.palettes.m_edition`).
  - **Branding:** fictional Phosphor Computer Company.
    - Italic speed-cut "PHOSPHOR" wordmark on the sides, lid and deck.
    - The RetroOS diamond logo appears **only** on the front badges (lid face, deck, nameplate). The user rejected the coloured stripes and does not want the diamond on the sides.
    - The model name is a placeholder: "P-31 Afterglow". "PCC Model 5 Portable" was suggested from the RetroOS lore.
  - The screen shows a redraw of the RetroOS Phosphor BIOS POST screen (`tools/render_post_screen.py`).
- **P3 printable v1** (`cad/p3_print.py`, `docs/print-P3.md`, `outputs/p3/`):
  - 41 print-oriented parts (including the new `gw_sled`), auto-assigned to the H2C, X2D, A1 and A1 mini (bed sizes sourced).
  - M3 heat-set joints, flush multi-colour logo inlays exported as 3MF parts, two-tone multi-part bezels, and fit coupons.
  - All assembly checks pass. Rebuild with `./rebuild-p3.sh` (about 3 min); the viewer is `outputs/p3/viewer.html`.
- **Internals parts list:** `docs/BOM-P2.md`.

## Decisions made
- **Keyboard:** 8BitDo Retro Mechanical M Edition. Listing size 376.6 × 169.6 × 46.8 mm, confirmed by the user. Measured case edges: front 19.05 mm, rear 38.6 mm. Platform tilt is 0°.
- **Floppy controller:** **one Greaseweazle V4.1**, confirmed, driving both drives through a twisted cable. It is modelled in the CAD under the drive cage on a reprintable sled (`gw_sled`). The outline, holes and connector centres come from the official Gerbers (`p2.floppy_controller`). The header/plug height and USB plug space are reservations.
- **Main power switch:** the Big Red Switch is **dropped**. The user plans a vintage SMK XT/AT DPST paddle switch (MarVac listing, 15 A @ 125 VAC) in a **printed housing**. No drawing exists online, so the housing waits for the user's measurements (list in `docs/hardware-recommendations.md` §2). The placeholder cutout (`p3.power_switch`) is still on the right side toward the rear.
- **Fasteners:** heat-set inserts. The finish should look polished, not "snapped together".
- **Hardware (last recommendation):**
  - **Buy:** the handle (metal fold-flat), the hinges (small stainless or brass lift-off), the latches (toggle or draw latches, optionally in a printed housing), the feet, and steel pins.
  - **Print:** keyboard clips, drawer rails, and everything visible or cosmetic.
  - The printed versions stay in the CAD until the user picks the bought parts and sends their dimensions.

## Recommendations given (16 Nov), awaiting the user's choices
See `docs/hardware-recommendations.md`:
- **Power:** 12 V Mean Well GST60A12-P1J, Switchcraft 722A jack, 7.5 A blade fuse, SMK switch, Pololu D42V110F5 (5 V 11 A). The power reservation is now sized for the Pololu (`p2.floppy_controller.power_reserve`).
- **Ports and audio:** Adafruit CH334F hub (or no hub at all); Adafruit 908/909/978+1358/4053 panel-mount cables; Adafruit 3351 enclosed speaker.
- **Inserts:** CNC Kitchen M3 inserts (4.0 mm hole matches the CAD); short M3×3.0 pending (`p3.insert_short.depth` is still 4.2).
- **Case hardware:** Southco 97-30-160-12 latches, McMaster stainless lift-off hinges, Penn Elcom spring-loaded handle, 3M Bumpon SJ5009 feet.

## Open inputs (ask the user; do not assume dimensions)
1. Dimensions of the bought handle, hinges and latches, once chosen.
2. MPF-920: side and bottom screw positions and thread, rear connector positions, eject-button position, spin-up current.
3. Greaseweazle V4.1: board size and holes are DONE (from the Gerbers). Still needed: header/IDC plug height, PCB thickness and the USB cable plug (the board isn't in hand).
4. SMK switch: body, mounting ears, paddle, terminals and ON direction (see the recommendations doc §2).
5. Heat-set insert brand and size. Coupon C1 tests 3.9 / 4.0 / 4.1 mm holes; currently set to 4.0 mm.
6. Power and I/O parts (BOM section 3/4): the buck converter, input jack, hub, speaker and panel-mount ports.
7. Display mounting-hole thread depth.

## Environment notes
- `adafruit.com`, `learn.adafruit.com`, `bitsavers.org`, `printables.com`, `pololu.com`, `mcmaster.com`, `silmoh.com` and `millennium.ca` could not be fetched: they are outside the allowed network hosts. WebSearch and github.com work.
- The Python venv is not committed. `python3.12 -m venv .venv && pip install -r requirements.lock`, then use the rebuild scripts. Previews need Node with the pre-installed Playwright.
- The RetroOS repo (`bensdev-p/RetroOS`) is public. Its `docs/STYLE.md` defines the brand palette, fonts and the "one product, one hand" rule.
