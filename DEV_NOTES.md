# Developer notes — maintained Velisara package

## Development summary

**Goal:** Make the historically flattened Python upload runnable without
overwriting the archived memory and identity, and fail closed on damaged
persistent JSON. **Stage:** proposed unreleased alpha candidate; integration,
validation and publication are tracked separately.

**Current change:** reconstruct the intended `velisara_agent` package
hierarchy and missing daemon base, use a separate opt-in data root, atomic
JSON replacement and exclusive PID locking. Retain original flat source and
uploaded state/log files for provenance.

**Next:** (1) verify CI on the exact PR revision; (2) test clean interactive
startup and corrupt-state refusal on disposable data; (3) assess memory journal
and actual crash/power-loss limitations before any stable release.

**Material limits:** There is no automatic migration of archived root-level
data; old JSONL is not exhaustively validated, and power-loss durability,
cross-process journal consistency, stale-lock recovery, Windows and Pythonista
behaviour are not established. A stale PID file may require manual investigation
and safe deletion. Do not treat a successful synthetic test as a real-use
durability guarantee. The optional organs are placeholders.

## Reconstructed architecture and decision

The original flat archive contained `launcher.py` importing
`velisara_agent.bootstrap`, but the repository had only top-level files.
Organ and daemon relative imports both referenced `.base`, while only the
organ base class was present; `ManagedDaemon` was missing. Running the
historical entrypoint therefore could not reach its intended boot path.

Instead of rewriting original archives or inferring their historical execution,
this candidate creates a conventional package: `config/`, `organs/`,
`daemons/`, plus shared bootstrap/kernel/paths/storage. The missing
`ManagedDaemon` is a small newly reconstructed cooperative background worker.
Historical code is copied where compatible, not claimed as verified original
runtime behaviour.

Runtime data is deliberately separate from the uploaded archive, defaulting to
`~/.velisara_agent`, overridable using `VELISARA_DATA_HOME`. This avoids
silently interpreting tracked root-level files as live state. No automatic
migration is attempted because the archived material's trust/provenance and
completeness have not been verified.

The historical `read_json` returned defaults for malformed JSON, while
`Kernel.awaken` writes identity/state. On live paths this could overwrite
damaged but recoverable data. The maintained package rejects invalid JSON at
boot and writes JSON through same-directory temporary files before replacing.
The existing data is left intact on failure before replacement. Journal
appends are **not** transactional with identity/state updates; real power-loss
and concurrency guarantees remain out of scope.

Lock acquisition now creates its PID file exclusively and removes only a lock
owned by this launcher. We intentionally refuse existing/stale locks rather
than guessing whether a PID has been reused. A future locking design could
use platform-specific OS locks with recovery rules, but needs cross-platform
testing and a clearly specified crash model.

## Testing and release evidence

Run `python -m unittest discover -s tests -v` against disposable
`VELISARA_DATA_HOME`. The GitHub Actions smoke workflow tests Python
3.11/3.12. Record exact tested revision and outcome in the pull request or
private workshop checkpoint after observation—not here in advance.

Stable release requires a runnable clean install, non-destructive refusal of
corrupted JSON, a functioning lock lifecycle, and documented scope/limitations.
Any target device not tested is explicitly **unverified**, not an indefinite
blocker for other platforms. Do not promote if a critical data-loss defect
remains unmitigated.
