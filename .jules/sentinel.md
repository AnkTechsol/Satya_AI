## 2025-05-15 - Command Injection in Task Completion Checks
**Vulnerability:** Command injection was possible in `CompletionChecker` because `test_command` from task criteria was executed via `subprocess.run(shell=True)`.
**Learning:** In an agentic system where agents can programmatically create or update tasks, providing shell access in automated checks is extremely dangerous. Even though it breaks support for shell operators (like `&&`, `|`), the security risk of arbitrary execution outweighs the convenience.
**Prevention:** Always use `shell=False` and pass arguments as a list. Use `shlex.split` if you must parse a command string, but be aware it won't support shell-specific features.
