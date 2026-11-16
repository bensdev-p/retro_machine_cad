# Handoff: Phosphor luggable enclosure (state at end of session, 16 Nov 2026)

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
  - 40 print-oriented parts, auto-assigned to the H2C, X2D, A1 and A1 mini (bed sizes sourced).
  - M3 heat-set joints, flush multi-colour logo inlays exported as 3MF parts, two-tone multi-part bezels, and fit coupons.
  - All assembly checks pass. Rebuild with `./rebuild-p3.sh` (about 3 min); the viewer is `outputs/p3/viewer.html`.
- **Internals parts list:** `docs/BOM-P2.md`.

## Decisions made
- **Keyboard:** 8BitDo Retro Mechanical M Edition. Listing size 376.6 × 169.6 × 46.8 mm, confirmed by the user. Measured case edges: front 19.05 mm, rear 38.6 mm. Platform tilt is 0°.
- **Floppy controller:** most likely a **Greaseweazle V4.1**, replacing the Feather + FeatherWing stacks. **The CAD still models two Feather stacks; switching it over is still to do.**
- **Main power switch:** the user is considering an IBM-style "Big Red Switch" (Printables model 459567) on the right side toward the rear. The CAD has a placeholder cutout and keep-out space (`p3.power_switch`).
- **Fasteners:** heat-set inserts. The finish should look polished, not "snapped together".
- **Hardware (last recommendation):**
  - **Buy:** the handle (metal fold-flat), the hinges (small stainless or brass lift-off), the latches (toggle or draw latches, optionally in a printed housing), the feet, and steel pins.
  - **Print:** keyboard clips, drawer rails, and everything visible or cosmetic.
  - The printed versions stay in the CAD until the user picks the bought parts and sends their dimensions.

## Open inputs (ask the user; do not assume dimensions)
1. Dimensions of the bought handle, hinges and latches, once chosen.
2. MPF-920: side and bottom screw positions and thread, rear connector positions, eject-button position, spin-up current.
3. Greaseweazle V4.1: board size and mounting holes.
4. Big Red Switch: the STEP file or dimensions, and which electrical switch it actuates.
5. Heat-set insert brand and size. Coupon C1 tests 3.9 / 4.0 / 4.1 mm holes; currently set to 4.0 mm.
6. Power and I/O parts (BOM section 3/4): the buck converter, input jack, hub, speaker and panel-mount ports.
7. Display mounting-hole thread depth.

## Environment notes
- `adafruit.com`, `learn.adafruit.com`, `bitsavers.org` and `printables.com` could not be fetched in this session: they are outside the allowed network hosts. WebSearch works.
- The Python venv is not committed. `python3.12 -m venv .venv && pip install -r requirements.lock`, then use the rebuild scripts. Previews need Node with the pre-installed Playwright.
- The RetroOS repo (`bensdev-p/RetroOS`) is public. Its `docs/STYLE.md` defines the brand palette, fonts and the "one product, one hand" rule.
