# Changelog

All notable changes to this project will be documented in this file.

## 0.1.3 — Additional EEG formats
- Support BrainVision `.vhdr`, EGI `.mff`/`.raw`, MNE `.fif`, and `.gdf` files.
- Update CLI help, README, and tests to cover new formats.

## 0.1.4 — Modular loader plugins
- Split each EEG format reader into its own plugin module for maintainability.
- Document the plugin registry and update tests accordingly.

## 0.1.2 — Restore default viewer behavior
- Default behavior now opens the MNE-QT Browser when a file is provided.
- Introduce `--view/--no-view` toggle (default: `--view`).
- Keep backward compatibility with explicit `--view`.
- Update README and tests to reflect behavior.

## 0.1.1 — EDF/BDF support and opt-in view
- Add support for viewing `.edf` and `.bdf` files.
- Switched viewing to be opt-in via `--view` (now reverted in 0.1.2).

## 0.1.0 — Initial release
- Basic `.set` file viewing with MNE-QT Browser.
