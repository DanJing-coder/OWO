# IT asset checkout: record a confirmed handover

This example describes a laptop, a checkout request, and an employee. The
request is approved and the laptop is available, but `handover_confirmed` is
initially `false`. `record_checkout` is blocked until a separate handover
process confirms that the employee received the laptop.

| Snapshot | `record_checkout` | Reason |
|---|---|---|
| [`world.json`](world.json) | `false` | Handover has not happened |
| [`confirmed.json`](confirmed.json) | `true` | Handover is explicitly confirmed |

```sh
owo validate examples/it-asset-checkout/world.json
owo evaluate examples/it-asset-checkout/world.json record_checkout
owo evaluate examples/it-asset-checkout/confirmed.json record_checkout
owo apply examples/it-asset-checkout/confirmed.json record_checkout -o /tmp/owo-checked-out.json
```

The final snapshot marks the laptop `checked_out`, assigns it to `employee_5`,
and marks the request `fulfilled`. OWO does not hand over hardware or update an
asset database. The real asset system must handle identity, approval,
concurrent claims, and the committed checkout record.
