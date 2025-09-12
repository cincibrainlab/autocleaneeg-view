# Changelog

All notable changes to this project will be documented in this file.

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
