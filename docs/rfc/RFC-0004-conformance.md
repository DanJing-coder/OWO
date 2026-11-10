# RFC-0004: Validation, compatibility, and CLI

Status: Accepted for v0.1 MVP

Version: 0.1

The JSON Schema uses Draft 2020-12. A conforming v0.1 producer MUST satisfy
both schema and semantic constraints from RFC-0001. A consumer MUST reject
unknown document fields and unsupported versions; a future version requires
a new schema and explicit migration. No v0.1 extension mechanism is defined.

The Python package exposes `validate_world`, `evaluate_condition`,
`evaluate_action`, and `apply_action`. `validate_world` raises `ValidationError`
on invalid input. The CLI supports `owo validate FILE`,
`owo evaluate FILE ACTION_ID`, and `owo apply FILE ACTION_ID [-o FILE]`.
`-` means standard input for FILE and standard output for `-o`. `evaluate`
emits `{"action": ..., "result": ...}`. `apply` emits a complete JSON world.
Success exits 0, invalid data or blocked actions exit 2, and I/O or JSON
decoding failures exit 1. Diagnostics go to standard error.

The conformance suite contains valid and invalid documents plus truth and
action vectors. Implementations SHOULD run those vectors against the schema
and behavior before claiming v0.1 support. CI runs the reference suite on
Python 3.9 and 3.13 and exercises the Door example through the CLI.
