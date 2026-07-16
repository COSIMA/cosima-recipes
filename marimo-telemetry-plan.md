# Marimo telemetry support — design plan

## Context

cosima-recipes is being ported from Jupyter to marimo (38 notebooks; all 38 convert, 33 with zero
`marimo check` issues). Porting silently breaks usage telemetry.

`access-py-telemetry` collects its data through IPython, loaded from an IPython startup script in the
`analysis3` environment. Under marimo that path is inert:

```python
# access_py_telemetry/__init__.py
ip = get_ipython()   # -> None under marimo (no IPython shell exists)
if ip:               # -> False
    load_ipython_extension(ip)   # never runs; pre_run_cell never registered
```

`ipython>=7.0.0` is a hard dependency, so the import succeeds and nothing raises. Worse,
`ipy_register_func`'s wrapper is a **pure passthrough** — it registers the function *name* and never
sends anything itself; all sending is done by `capture_registered_calls` on `pre_run_cell`. So every
`ipy_register_func`-decorated function emits **exactly zero telemetry under marimo, with no error**.

For a package whose numbers inform resourcing, silently reporting zero usage is worse than crashing.

**Goal:** make `access-py-telemetry` support marimo alongside IPython, preserving the existing
deployment property that *notebooks contain no telemetry code*.

## Approach

marimo ships no IPython and no shim (`grep -rn get_ipython` over marimo 0.23.14 → zero hits), so the
existing hook has no equivalent. The replacement is marimo's `marimo.cell.executor` entry point.

Verified facts (marimo 0.23.14, read from the installed package):

| Fact | Location |
| --- | --- |
| Entry-point group `marimo.cell.executor` | `marimo/_entrypoints/ids.py` |
| `resolve_executor()` loads **one** factory, else `DefaultExecutor` | `marimo/_runtime/executor/evaluator.py:155` |
| Resolved in kernel mode (`marimo edit` / `marimo run`) | `marimo/_runtime/runner/cell_runner.py:196` |
| Resolved in **script mode** (`app.run()`) | `marimo/_runtime/app/script_runner.py:73` |
| `Executor` protocol: `name`, `execute_cell(cell, glbls)`, `execute_cell_async(cell, glbls)` | `marimo/_runtime/executor/executor.py:31` |
| `CellImpl.code: str` — the cell source text | `marimo/_ast/cell.py:158` |
| Env gating `MARIMO_CELL_EXECUTOR_ALLOWLIST` / `_DENYLIST` | `marimo/_entrypoints/registry.py` |

Why this fits: `CellImpl.code` is the direct analogue of IPython's `info.raw_cell`, so the existing
libcst detection logic works essentially unchanged. It is environment-level (entry point in package
metadata), mirroring today's startup-script model — **no notebook changes**. And unlike the IPython
hook it also fires in script mode, so headless/CI execution is covered.

Accepted risks: marimo declares the group *"Internal entrypoints. Not user-facing as the API is not
stable."*; only one executor per environment wins. The latter is acceptable — we own `analysis3`.

---

## Section 1 — `access-py-telemetry`

### 1.1 Split the runtime-agnostic seam in `ast.py`

`capture_registered_calls(info: ExecutionInfo)` immediately does `code = info.raw_cell`, then
`strip_magic()`, then libcst-parses and matches against the registries. Everything after the first
line is just string processing and is already runtime-agnostic.

- Extract the body into `capture_from_source(code: str) -> None`.
- Keep `capture_registered_calls(info)` as a thin IPython adapter → `capture_from_source(info.raw_cell)`.
  Preserves the public name and the `pre_run_cell` signature; no downstream breakage.
- `strip_magic()` stays on the IPython path only — marimo has no magics (they are a hard runtime error
  there, see `marimo/_runtime/runtime.py:863`).
- Keep failing silently on parse errors, as today.

### 1.2 Move IPython imports off the module top-level

`ast.py` and `__init__.py` currently do `from IPython.core.getipython import get_ipython` /
`from IPython.core.interactiveshell import ExecutionInfo, InteractiveShell` at import time. Make these
lazy/guarded so the package is importable in a marimo-only environment, and so `IPython` can later
become an extra rather than a hard dependency.

### 1.3 New module: `src/access_py_telemetry/marimo_executor.py`

Do **not** name it `marimo.py` — it works under absolute imports but is needlessly confusing.

```python
from marimo._runtime.executor.executor import DefaultExecutor
from .ast import capture_from_source

class TelemetryExecutor(DefaultExecutor):
    name = "access-py-telemetry"

    def execute_cell(self, cell, glbls):
        capture_from_source(cell.code)
        return super().execute_cell(cell, glbls)

    async def execute_cell_async(self, cell, glbls):
        capture_from_source(cell.code)
        return await super().execute_cell_async(cell, glbls)
```

Note both methods must be covered — async cells bypass `execute_cell` entirely.

`marimo` does **not** need to be a runtime dependency. This module is only ever imported by marimo's
own `EntryPointRegistry` during `resolve_executor()`, so if marimo is absent nothing imports it. Add
it as an extra for tests only:

```toml
[project.optional-dependencies]
marimo = ["marimo>=0.23"]

[project.entry-points."marimo.cell.executor"]
access-py-telemetry = "access_py_telemetry.marimo_executor:TelemetryExecutor"
```

### 1.4 Guard against the mechanism's own silent-failure mode

`resolve_executor()` wraps factory construction in `try/except` and **falls back to `DefaultExecutor`
with only a `LOGGER.warning`**. That reproduces exactly the failure class this whole plan exists to
fix: telemetry silently doing nothing. Mitigations:

- Keep the factory trivial so it cannot realistically raise (all real work inside `execute_cell`).
- Never let `capture_from_source` raise out of `execute_cell` — a telemetry bug must not break a user's
  notebook.
- Add a CI test asserting `resolve_executor()` actually returns `TelemetryExecutor` (see Verification).

### 1.5 Decision required: reactive re-execution semantics

**This is the real design problem, not plumbing.** IPython's `pre_run_cell` fires only on *explicit
user execution*. marimo re-runs cells **reactively**: editing one upstream cell re-triggers every
downstream cell, each firing the executor again. Identical user behaviour therefore yields materially
higher counts under marimo than Jupyter, and the two are not comparable in the same dataset.

Options:

1. **Dedupe per `(SessionID, service, function)`** — record first use per session. Arguably closest to
   the actual intent ("which recipes/functions are used"), and stable against reactive noise. Changes
   semantics relative to the Jupyter path, which records every explicit run.
2. **Record everything, tag the runtime** — add a field (e.g. `runtime: "marimo" | "ipython"`) so
   analysis can segment. Preserves raw data; pushes the problem downstream.
3. **Accept and document the inflation.**

Recommendation: **(2) as a floor — the runtime tag is needed regardless** — plus (1) if the dataset is
meant to be read as usage counts rather than execution counts. Decide before writing code; it changes
the record schema.

### 1.6 Decision required: the `--enable` / `--disable` CLI

`cli.py` implements `--enable/--disable/--status` by editing the **IPython startup profile**. marimo
has no profile: an entry point is live the moment the package is installed. marimo offers
`MARIMO_CELL_EXECUTOR_DENYLIST` as an env-var escape hatch, but wiring `--disable` to it is a
different UX and a different persistence story (shell env vs. a file on disk).

On a shared NCI environment where users reasonably expect `--disable` to mean something, this needs
deciding. Simplest coherent option: have `TelemetryExecutor.execute_cell` consult the package's own
existing config/opt-out state at runtime, so one switch governs both runtimes and `--disable` keeps
working unchanged.

---

## Section 2 — `ACCESS-Analysis-Conda`

Repo layout: `environments/` (`analysis3`, `analysis3-edge`, …), `scripts/`, `modules/`.

- **Add `marimo`** to `environments/analysis3-edge` first, then `environments/analysis3` once the
  telemetry integration has landed and been verified on edge.
- **Bump the `access-py-telemetry` pin** to the first version shipping the entry point. The entry point
  auto-registers on install — **no startup-script work is needed for the marimo path**, in contrast to
  the IPython path.
- **Leave the existing IPython startup-script wiring untouched.** The two paths are mutually exclusive
  at runtime (`get_ipython()` is `None` under marimo; no executor is resolved under Jupyter), so
  supporting both requires no mode flag.
- **Assert the `marimo.cell.executor` slot is uncontested.** Only one factory wins per environment —
  `resolve_executor()` picks the first by name, warns, and silently ignores the rest. Check no other
  package in `analysis3` claims the group, and add a build-time check if cheap.

**Open question I could not resolve:** I did not locate where `access-py-telemetry` is pinned, nor
where the IPython startup script is installed (`scripts/install_config.sh` was the most likely
candidate). Confirm both before executing this section.

---

## Section 3 — `cosima-recipes`

**No telemetry code goes here.** Verified: the repo currently contains zero telemetry references —
`grep -ril "telemetry\|access_py_telemetry"` over all notebooks/configs returns nothing. Telemetry
arrives entirely from the environment, and the entry-point design preserves that. If the two sections
above land, the ported notebooks are instrumented with no changes of their own.

The work that *is* required here is the port itself, independent of telemetry:

- Add the 38 converted `.py` files alongside their `.ipynb` originals (no basename collisions; already
  verified).
- Fix the 3 `MB001` unparsable cells — these are IPython-only syntax and are a **hard error** under
  marimo, and `App._maybe_initialize()` (`marimo/_ast/app.py:577`) raises `UnparsableError` for the
  *whole notebook* if any cell is unparsable, so these 3 notebooks are wholly untestable until fixed:
  - `01-Cooking-Tutorials/02-Advanced/intake_to_dask_efficiently_chunking` — `validate_chunkspec?`
    (introspection) and a `%`-magic in "Exercise 2". Note the `?` cell exists to *teach* the IPython
    `?` feature; porting it is an editorial decision, not a mechanical one.
  - `03-Advanced-Recipes/Particle_tracking_with_Parcels` — `dir = ! echo /scratch/$PROJECT/$USER/...`;
    replace with `os.path.expandvars(...)`. Beware: `expandvars` leaves `$PROJECT` literal when unset,
    silently yielding a bad path off-NCI. Also shadows the `dir` builtin today.
- Optionally fix the 2 pre-existing `MF002` latent bugs (`$\degree$`, `$\zeta/f$` in non-raw strings —
  `SyntaxWarning` now, `SyntaxError` on a future Python). These are bugs in the current `.ipynb` files;
  `marimo check` merely surfaced them.
- Add CI running `marimo check --strict`, which validates statically **without NCI data** — something
  the current `test/test_notebooks.py` (nbconvert `ExecutePreprocessor` against `gdata/xp65`) cannot do.

---

## Verification

**access-py-telemetry**

1. Unit: `capture_from_source(code)` sends the same record for a given source string as the existing
   IPython path does for the same `raw_cell`. Golden-test the two adapters against one input.
2. Entry point resolves (guards against §1.4's silent fallback):
   ```python
   from marimo._runtime.executor.evaluator import resolve_executor
   assert resolve_executor().name == "access-py-telemetry"
   ```
3. End-to-end: run a marimo notebook calling a registered function against a local
   `pytest-httpserver` (already a dev dependency) and assert the request arrives. Cover **both**
   `marimo run` (kernel mode) and `python nb.py` (script mode) — the two use different code paths.
4. Async: assert a cell using `await` still emits — `execute_cell_async` is a separate method.
5. Regression: existing IPython tests must pass unchanged.
6. Failure isolation: make `capture_from_source` raise internally, assert the notebook cell still runs.

**ACCESS-Analysis-Conda**

7. Build `analysis3-edge`, launch a marimo notebook, confirm a telemetry record lands.
8. Confirm Jupyter telemetry in the same environment is unchanged (no regression on the IPython path).

**cosima-recipes**

9. `marimo check --strict` passes across all 38 files.
10. Spot-run one ported notebook on NCI (needs `gdata/xp65+ik11+cj50+ol01`) and confirm both that it
    executes and that telemetry is emitted.
