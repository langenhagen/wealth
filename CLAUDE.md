# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

`Wealth` is a personal-finance toolkit built as Jupyter notebooks backed by a
Python library (`src/wealth/`). It imports bank-transaction CSV exports,
categorizes and visualizes them, and provides tools for savings/compound
interest, inflation, pension and investment projections. Everything runs
locally; no data leaves the machine.

The repo distinguishes between:
- The **project** (`wealth` itself, this git repo) — the library and templates.
- A **workspace** — a separate directory (default `~/wealth/workspace`)
  created by `scripts/create-workspace.sh`, containing the user's actual
  notebooks, config and CSV data, kept out of this repo's version control.

## Commands

### Project setup (for developing `wealth` itself)
```bash
scripts/setup.sh --dev          # create .venv, install requirements + requirements-dev.txt
scripts/setup.sh --dev --clean  # same, but wipe .venv first
```
Requires Python >= 3.9. Always run from the repo root.

### Create/refresh a user workspace
```bash
scripts/create-workspace.sh [--dev] [<path/to/workspace>]  # default: ~/wealth/workspace
```
Sets up a separate `.venv`, installs `requirements.txt` (+ dev reqs), and
copies `prototype/` (notebooks, config, csv samples, scripts) into the
workspace. Launch it via the copied `start` script (`workspace/start`),
which activates its venv and runs `jupyter lab`.

### Linting
```bash
scripts/lint-project.sh
```
Runs, in order: Flake8, Pylint, Mypy, Black (`--check`), Isort (`--check-only`),
Vulture (against `src/setup.py` and `src/wealth/`), then Shellcheck against
`scripts/*.sh`. Run with an active venv from the repo root. There is no
single-file shortcut baked in — invoke the individual tool on one file/path
when iterating (e.g. `flake8 src/wealth/track.py`).

### Tests
```bash
pytest src/
```
Tests are colocated with source as `test_*.py` (currently only
`src/wealth/util/test_deepupdate.py`). No pytest config/marker setup beyond
that convention.

### Notebook/workspace hygiene (run inside a workspace, or adapted from `prototype/scripts/`)
```bash
prototype/scripts/clean-notebooks.sh   # strip notebook outputs via nbconvert
prototype/scripts/clean-project.sh     # remove __pycache__, *.pyc, .ipynb_checkpoints
prototype/scripts/validate-yaml-file.sh <file.yml>
```

## Architecture

### Package layout (`src/wealth/`)
- `config.py` — loads workspace-relative `../config/config.yml` (path is
  relative to the *notebook's* working directory, i.e. `<workspace>/notebooks/`),
  deep-merges it over `default` via `wealth.util.deepupdate.deepupdate`, and
  exposes the merged dict as `config`.
  **Gotcha:** `wealth/__init__.py` does `from wealth.config import config`,
  which rebinds the `wealth.config` attribute from the submodule to the
  merged dict itself. So after `import wealth`, `wealth.config` is a `dict`
  (used e.g. as `wealth.config.get("accounts", {})` in `importers/importer.py`),
  not the module — only `from wealth.config import config` or importing the
  submodule directly before package init would give the module.
- `importers/` — bank CSV parsing. `common.py` defines the shared
  `transfer_columns` and helpers (`add_all_data_column`, `to_lower`).
  Per-bank modules (`dkb_giro.py`, `n26_mastercard.py`, `sparkasse_giro.py`)
  each expose `read_csv(path, account_name) -> DataFrame` normalized to
  `transfer_columns`. `importer.py::init()` is the entry point: it scans
  `../csv/*.csv` (again relative to the notebook), maps filenames to an
  importer via regex on the account-name segment
  (`dkb-giro`, `n26-mastercard`, `sparkasse-giro`), concatenates/sorts all
  transactions, injects a per-account opening-offset row (from
  `config["accounts"][name]["offset"]`), classifies each row with
  `util.transaction_type.TransactionType`, and rebuilds a combined
  `all_data` text column used later for regex-based category matching.
- Feature subpackages follow a **logic / ui split**: `categories/` and
  `savings/` each have `logic.py` (pure DataFrame computation) and `ui.py`
  (ipywidgets/matplotlib rendering), wired together by a top-level function
  of the same name as the package (`categories.categories()`,
  `savings.savings()`). `transactions/` follows the same shape without a
  separate `logic.py`. Flat modules (`balance.py`, `expenses.py`,
  `positions.py`, `invest.py`, `inflation.py`, `pension.py`, `track.py`)
  hold both logic and presentation for smaller features.
- `ui/` — shared presentation utilities used across features:
  `display.py` (`display`, `display_side_by_side` for notebook output),
  `format.py` (currency/date/percent formatters, reads `config["currency"]`),
  `styles.py` (pandas Styler CSS snippets), `plot.py` (shared matplotlib
  setup), `layouts.py`/`widgets.py` (shared ipywidgets layout/composition).
- `util/` — generic helpers unrelated to finance: `deepupdate.py` (recursive
  dict merge, has the only test file) and `transaction_type.py`
  (`TransactionType` Flag enum: `IN`/`OUT`/`INTERNAL_IN`/`INTERNAL_OUT`, used
  to classify parsed transactions — distinct from the enum-based
  `TransactionType` in `savings/type.py`, which only knows `DEPOSIT`/`INTEREST`).

### Data flow
CSV exports (named `<year>-<account-name>-*.csv`, account name matched
against `dkb-giro` / `n26-mastercard` / `sparkasse-giro`) live in a
workspace's `csv/` dir → `wealth.importers.init()` parses and normalizes them
into one DataFrame → notebooks in `prototype/notebooks/` (one per feature:
`balance`, `categories`, `expenses`, `inflation`, `invest`, `pension`,
`positions`, `savings`, `track`, `transactions`) call into the corresponding
`wealth` package function, which computes and renders results inline via
ipywidgets/matplotlib.

### Notebooks are templates, not source of truth
`prototype/notebooks/*.ipynb` are copied into new workspaces as starting
points; the actual data and any user notebook edits live only in the
workspace, never in this repo. `prototype/config/config.yml` documents every
supported config key in its header comments (accounts/iban/offset,
capital_gains_taxrate, currency, inflation_rate, retirement.birthday/age).

## Code Style

- Enforced by `.flake8` (max line length 88, max McCabe complexity 8) and
  `[tool.pylint]`/`[tool.isort]` in `pyproject.toml` (isort uses the `black`
  profile; several pylint checks disabled: `C0103`, `R0903`, `R0913`,
  `R0914`, `R0902`).
- Google-style docstrings on (almost) every function, including private
  (`__name` / `_name`) helpers.
- Private module-level helpers use the `__name` (double-underscore) prefix.
