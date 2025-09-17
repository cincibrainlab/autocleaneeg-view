# Testing Guide for Recent CLI Improvements
Quick steps to verify the recent CLI and loader fixes.
## Prep
- Activate the project virtual environment.
- Export env vars before running commands:
  ```bash
  export MNE_USE_NUMBA=false
  export NUMBA_DISABLE_CACHING=1
  ```
## 1. Loader Registry Refresh
1. Launch `python` in the repo root.
2. Run:
  ```python
  from autocleaneeg_view import loaders
  loaders.register_loader('.dummy', lambda path: path)
  '.dummy' in loaders.SUPPORTED_EXTENSIONS
  ```
3. `autocleaneeg-view --list-formats existing.set` should list `.dummy`.
## 2. `--list-formats` Flag
1. Run `autocleaneeg-view --list-formats`.
2. Expect exit code 0 and output beginning with `Supported file extensions:`.
## 3. NeuroNexus Companion Check
1. Stubs: `tmpdir=$(mktemp -d)` plus `touch "$tmpdir"/subject.xdat.json "$tmpdir"/subject_data.xdat "$tmpdir"/subject_timestamp.xdat`.
2. `autocleaneeg-view "$tmpdir"/subject.xdat.json --no-view --diagnose` → three `-> OK` lines.
3. `autocleaneeg-view "$tmpdir"/subject_data.xdat --no-view --diagnose` → three `-> OK` lines; delete the JSON to see `-> MISSING`.
## 4. Full Test Suite (Optional)
Run `MNE_USE_NUMBA=false NUMBA_DISABLE_CACHING=1 python -m pytest` and expect every test to pass.
