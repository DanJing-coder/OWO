# Incident triage: wait for on-call acknowledgement

The incident affects a billing service owned by an on-call team. The alert is
confirmed, but the initial snapshot has no `oncall_acknowledged` fact. The
`start_investigation` precondition is therefore `unknown`, not `false`.

| Snapshot | `start_investigation` | Reason |
|---|---|---|
| [`world.json`](world.json) | `unknown` | No acknowledgement is recorded |
| [`acknowledged.json`](acknowledged.json) | `true` | The on-call response was observed |

```sh
owo validate examples/incident-triage/world.json
owo evaluate examples/incident-triage/world.json start_investigation
owo evaluate examples/incident-triage/acknowledged.json start_investigation
owo apply examples/incident-triage/acknowledged.json start_investigation -o /tmp/owo-investigating.json
```

The last command creates a JSON snapshot with `status: investigating`. OWO
does not page anyone, create an incident ticket, or verify that investigation
actually began. An incident system should provide the acknowledgement event
and retain the authoritative workflow record.
