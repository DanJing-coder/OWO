# Inventory: preview a single-item reservation

`item_42` is explicitly requested for `order_17`. The `reserve_item` action
checks availability, absence of an existing reservation, approval of the
order, and the directed `requested_for` relation. It then sets `reserved` to
`true` and `reserved_for` to the order ID.

```sh
owo validate examples/inventory/world.json
owo evaluate examples/inventory/world.json reserve_item
owo apply examples/inventory/world.json reserve_item -o /tmp/owo-reserved.json
owo evaluate /tmp/owo-reserved.json reserve_item
owo evaluate /tmp/owo-reserved.json release_item
owo apply /tmp/owo-reserved.json release_item -o /tmp/owo-released.json
```

The evaluation results are `true`, `false`, and `true`. The second reservation
is blocked because the item is already marked reserved. The release action
sets `reserved_for` to JSON `null`, a known value distinct from an absent
property.

This example is suitable for planning, API contract tests, and UI previews.
It is **not** a transactional inventory system: two actors can evaluate the
same snapshot concurrently and both see `true`. A real reservation must use
the database's concurrency controls and confirm the committed result.
