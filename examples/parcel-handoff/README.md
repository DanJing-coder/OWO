# Parcel handoff: require delivery evidence

The world identifies a parcel, courier, and recipient. Relations state that
the courier carries the parcel and the parcel is addressed to the recipient.
The parcel starts `out_for_delivery`. `record_delivery` requires the recipient
to be present and `proof_received` to be explicitly `true`.

| Snapshot | `record_delivery` | Why |
|---|---|---|
| [`world.json`](world.json) | `false` | `proof_received` is explicitly `false` |
| [`confirmed.json`](confirmed.json) | `true` | A separate process supplied delivery proof |

```sh
owo validate examples/parcel-handoff/world.json
owo evaluate examples/parcel-handoff/world.json record_delivery
owo evaluate examples/parcel-handoff/confirmed.json record_delivery
owo apply examples/parcel-handoff/confirmed.json record_delivery -o /tmp/owo-delivered.json
```

The resulting JSON has `status: delivered`. OWO does not authenticate a
recipient, capture a signature, verify proof, or update a shipping system.
The application that receives and checks evidence must create the confirmed
snapshot before recording the transition in its own system.
