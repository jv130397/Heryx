# Welcome Screen — Maintenance Notes

The Home experience lives in `src/rarepedigree/ui/home.py` and is a page of the existing
`MainWindow`; it is not a second application window. `MainWindow.page_stack` keeps Home and the
editor laid out simultaneously, raising one page at a time to avoid geometry jumps.

## Stable extension points

- `WelcomeScreen.newRequested`, `openRequested` and `recentRequested` are the only navigation
  signals. Connect them to canonical application commands; do not implement file I/O in Home.
- `RecentProjectsStore` persists only title, absolute local path and last-opened timestamp in
  `QSettings`. Never add clinical, pedigree or patient data to this metadata.
- `PedigreeIllustration.progress` is the single animation property. Keep the duration between
  1.5 and 2 seconds and leave action buttons enabled throughout.
- Respect `ui/reduce_motion`; the reduced path must render the final state immediately.
- Welcome-specific theme choice is stored in `ui/welcome_theme` (`midnight` or `light`). Add new
  selectors under `QWidget#welcome-screen` to prevent style leakage into the scientific editor.

## Validation

Run:

```bash
ruff check .
QT_QPA_PLATFORM=offscreen pytest -q
QT_QPA_PLATFORM=offscreen python scripts/validate_phase_4_16.py
```

The validator uses real Qt widgets and synthetic project metadata. Generated evidence belongs in
`assets/phase_4_16_0/`; numeric results belong in `validation/phase_4_16_0/`.
