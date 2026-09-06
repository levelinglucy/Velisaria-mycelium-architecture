This folder holds attachable body parts.

Rule: organs should not be executed directly.
They are attached only through launcher.py.

Entrypoint:
- Use `python /home/runner/work/Velisaria-mycelium-architecture/Velisaria-mycelium-architecture/launcher.py` for interactive mode.
- Use `python /home/runner/work/Velisaria-mycelium-architecture/Velisaria-mycelium-architecture/launcher.py --once` for CI smoke-test mode (boot/start/clean-shutdown).

Import policy:
- Runtime modules use the repository's flat sibling-file layout.
- Prefer imports like `from kernel import Kernel` and avoid nested package paths.
