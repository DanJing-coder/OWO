# RFC-0002: Open-world state and three-valued truth

Status: Accepted for v0.1 MVP

Version: 0.1

## State interpretation

OWO uses an open-world assumption. Missing facts evaluate to `unknown`; they
MUST NOT be treated as false. A state test compares the known scalar value of
`state[entity][key]` to `equals` using JSON type-sensitive equality. In
particular, Boolean `true` does not equal number `1`. A relation test reads the
explicit Boolean value of its exact directed triple. Missing triples are
`unknown`. Explicit false is false. There is no implicit inverse relation.

## Truth operators

The evaluator returns `true`, `false`, or `unknown` (lowercase on the wire).
`not` swaps true and false and preserves unknown. `all` is false if any member
is false, true if every member is true, otherwise unknown. `any` is true if
any member is true, false if every member is false, otherwise unknown. Empty
`all` is true; empty `any` is false. Evaluation is pure and does not infer new
facts. Truth values follow strong Kleene logic.

| A | B | all(A, B) | any(A, B) |
|---|---|---|---|
| true | unknown | unknown | true |
| false | unknown | false | unknown |
| unknown | unknown | unknown | unknown |

An omitted `precondition` is equivalent to `{"all": []}`. `unknown` never
authorizes an action.
