# Contributing to OWO

Thank you for helping make world descriptions understandable and testable across
independent implementations. OWO v0.1 is specification first: the RFCs define
behavior, the JSON Schema defines structure, and the SDK is a reference
implementation.

## Before you start

1. Read the [four RFCs](docs/rfc/RFC-0001-core-model.md), the
   [schema](src/owo/schemas/owo-v0.1.schema.json), and the
   [illustrated Door example](examples/door/README.md).
2. Search existing issues and pull requests for the same proposal.
3. Open an issue for a new concept, semantic change, or compatibility question.
   Describe the use case, a small JSON example, expected evaluation, and any
   ambiguity between independent implementations.

For a protocol change, propose an RFC update before changing the SDK. A change
to v0.1 behavior should state its effect on existing documents and conformance
vectors. New features outside the v0.1 scope belong in a future version
proposal rather than silently changing v0.1 semantics.

## Make a change

1. Create a branch from the latest `main`.
2. Add or update a small valid or invalid example that demonstrates the
   behavior. When semantics change, add a conformance vector that fails before
   implementation.
3. Update the relevant RFC and JSON Schema, then the SDK and CLI as needed.
4. Keep documentation and examples in English. Use JSON for canonical
   documents; do not use executable condition strings.
5. Run the local checks:

   ```sh
   python -m pip install -e '.[test]'
   python -m pytest
   owo validate examples/door/world.json
   owo evaluate examples/door/world.json open_door
   ```

## Open a pull request

Explain the problem, the proposed semantics, and the tests you ran. Link the
issue or RFC discussion when applicable. Keep unrelated changes in separate
pull requests. CI runs the conformance suite on Python 3.9 and 3.13; all checks
should pass before merge.

For documentation and visual changes, include a brief description of what a
reader should learn from the example. Ensure every diagram has descriptive
text nearby and that any shown command or result matches the current SDK.

The repository is licensed under [Apache-2.0](LICENSE). By submitting a
contribution, you agree that it may be distributed under that license.
