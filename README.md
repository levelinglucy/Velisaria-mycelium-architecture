# Velisara mycelium architecture

An experimental, local-first attachable-body Python agent. Organs are assembled
by `launcher.py`; they should not be executed individually.

The historical root-level upload was flattened, so imports such as
`velisara_agent.bootstrap` and `velisara_agent.organs.registry` did not
resolve. The **maintained alpha package** now lives under `velisara_agent/`,
while the original flat Python files and uploaded state/log/bytecode remain
unchanged, except the root launcher gains cooperative shutdown. The package
does **not** read or migrate archived root-level state.

Run locally with Python 3.11+:

```sh
python launcher.py
python -m unittest discover -s tests -v
```

The live data root defaults to `~/.velisara_agent`. Set
`VELISARA_DATA_HOME` to an isolated directory to trial it without touching
existing data. Run `quit` to exit. No network connection is opened.
Use only copies for migration experiments; do not copy untrusted JSON or
JSONL into live data. A damaged journal refuses awakening instead of silently
extending broken records. An existing PID lock after an interruption requires owner review.

**Development:** This is an **unreleased alpha candidate**. See
[developer notes](./DEV_NOTES.md) for goals, limitations, validation, and
recovery caveats; [changelog](./CHANGELOG.md) for meaningful changes.
