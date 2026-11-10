# RFC-0003: Grounded actions and effects

Status: Accepted for v0.1 MVP

Version: 0.1

An action has a unique `id`, optional `precondition`, and an `effects` list.
It is grounded: all entity IDs are literal and refer to declared entities.
A condition is exactly one of a state `fact`, a `relation`, `not`, `all`, or
`any` expression. State tests contain `entity`, `key`, and `equals`; relation
tests contain `subject`, `predicate`, and `object`.

`evaluate_action(world, id)` returns the precondition truth. `apply_action`
MUST apply effects only when truth is `true`; otherwise it MUST raise a
precondition error and leave the input document unchanged. An effect sets one
state property to a scalar `value`. Effects are applied in list order to a
deep copy of the world; later writes to the same property win. Applying an
action does not add a history record and does not change definitions or
relations. Empty effects are allowed. Evaluation and application MUST first
validate the world and reject unknown action IDs.

This MVP does not model simultaneous actions, conflicts between agents,
permissions, timestamps, or physical side effects. Callers own persistence.
