# RarePedigree Studio — Phase 4.16.0 Welcome Experience Report

## Decision

**Accepted.** The application now starts on a responsive, interactive Home page embedded in the
existing `MainWindow`. It reuses the established New/Open/Load/Save workflows and does not create
a second editor, duplicate persistence logic, or alter pedigree data models.

## Baseline and implementation audit

Before this phase, startup displayed only a one-time language dialog and then constructed the
editor directly. There was no persistent Home, recent-project model, Home navigation command, or
startup illustration. The editor and scientific modules were already stable at 164 passing tests.

The retained first-run language dialog still chooses PT-BR or English. After that choice, and on
subsequent runs, `MainWindow` opens on `WelcomeScreen`. Home and editor share a stacked layout so
the editor keeps a valid geometry behind Home; entering the workspace is instantaneous and does
not cause a layout jump.

## Requirement traceability

| Requirement | Implementation | Automated/visual evidence | State |
|---|---|---|---|
| Real integrated Home | `WelcomeScreen` is a page owned by `MainWindow.page_stack` | `test_main_window_starts_on_home_and_can_enter_workspace` | Accepted |
| Brand, tagline and scientific illustration | Qt labels, existing vector logo and `PedigreeIllustration` custom paint widget | captures 01, 02, 04 | Accepted |
| New family | signal delegates to `MainWindow.new_project` and existing wizard | existing project tests + Home signal test | Accepted |
| Open project | signal delegates to canonical `open_project/load_from` | loading/recents integration test | Accepted |
| Recent projects | bounded `QSettings` metadata store; open/remove/clear/unavailable states | four recent-store tests + capture 03 | Accepted |
| Privacy | only title/path/timestamp are stored; removing an entry never deletes its file | privacy and removal tests | Accepted |
| Non-blocking animated entry | 2,800 ms reveal followed by a subtle 4,200 ms idle loop; buttons stay enabled | animation interaction and idle-motion tests | Accepted |
| Reduced motion | final state is applied immediately from `ui/reduce_motion` | reduced-motion test + capture 05 | Accepted |
| Pointer interaction | bounded parallax, nearest-node halo and card icon scale; disabled with reduced motion | pointer and reduced-motion tests + capture 06 | Accepted |
| Home command | File → Home screen, `Ctrl+Shift+H`, existing unsaved-change gate | `show_home` integration | Accepted |
| PT-BR / English | all new visible copy routed through `tr()` | captures 01 and 04 | Accepted |
| Midnight / light | isolated welcome theme selectors and Preferences selector | theme tests + captures 01 and 04 | Accepted |
| 1366 / 1600 / 1920 | proportional split, expanding illustration and wrapped copy | captures 01–04; existing resolution tests | Accepted |
| Keyboard/accessibility | actions are native `QPushButton`s with accessible names/tooltips | action-card unit test | Accepted |
| Existing editor preserved | no domain, layout, rendering, HPO or persistence schema changes | complete 176-test suite | Accepted |

## Files changed

- `src/rarepedigree/ui/home.py`: Home UI, animation and recent-project store.
- `src/rarepedigree/ui/main_window.py`: stacked navigation, Home action, canonical workflow wiring.
- `src/rarepedigree/ui/i18n.py`: PT-BR/English Home strings.
- `src/rarepedigree/ui/theme.py`: Midnight and light Home styling.
- `src/rarepedigree/ui/preferences.py`: functional Home theme preference.
- `tests/unit/test_phase_4_16.py`: nine focused regression tests.
- `scripts/validate_phase_4_16.py`: real-widget capture and performance validation.
- `assets/phase_4_16_0/` and `validation/phase_4_16_0/`: evidence and measurements.

## Performance

Measurements use a fresh Python process with the offscreen Qt platform, from `QApplication`
creation through `MainWindow.show()` and `processEvents()`.

| Metric | Baseline | Phase 4.16.0 |
|---|---:|---:|
| Process to visible | 395.43 ms | 329.16 ms |
| MainWindow construction | 88.62 ms | 79.25 ms |
| Peak RSS | 106.74 MiB | 107.41 MiB |
| Enter editor | not measured | 14.25 ms |
| Open synthetic project | not measured | 17.65 ms |

The measured visible-startup time improved by 16.8%; memory increased by approximately 0.67 MiB.
The actions are enabled on the first visible event, before the decorative animation completes.
The editor remains eagerly constructed to preserve mature widget contracts; introducing lazy editor
construction is not justified by the current 329 ms startup result and would carry broader risk.

## Real visual evidence

- `assets/phase_4_16_0/01_welcome_pt_midnight_1920x1080.png`
- `assets/phase_4_16_0/02_welcome_pt_midnight_1366x768.png`
- `assets/phase_4_16_0/03_recent_projects_pt_1600x900.png`
- `assets/phase_4_16_0/04_welcome_en_light_1600x900.png`
- `assets/phase_4_16_0/05_welcome_reduced_motion_1920x1080.png`
- `assets/phase_4_16_0/06_welcome_pointer_parallax_1600x900.png`

These are direct `QWidget.grab()` results from the real PySide6 application. No screenshot was
composed or manually mocked.

## Validation results

```text
ruff check .
All checks passed!

QT_QPA_PLATFORM=offscreen pytest -q
176 passed
```

The twelve new tests cover storage bounds/deduplication/privacy, safe removal, animation
interactivity, idle and pointer motion, reduced motion, both themes, Preferences persistence,
Home/editor navigation, loading and unavailable recent entries.

## Known constraints

- Evidence was rendered through Qt's offscreen platform, so native window-manager chrome and
  physical-monitor color calibration were not assessed.
- Home offers two scoped visual themes; the pre-existing editor remains on its established
  scientific light theme. This avoids presenting an unvalidated dark scientific canvas.
- Recent paths are intentionally local and may reveal filenames to the current OS account; no path
  or project data leaves the computer.
