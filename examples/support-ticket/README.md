# Support ticket: close only after notification is recorded

The `ticket_204` entity is linked to `customer_9` by `submitted_by`. The ticket
is resolved but `customer_notified` is initially `false`, so `close_ticket`
evaluates to `false`. The `record_notification` action changes the local
record; after that, `close_ticket` evaluates to `true`.

```sh
owo validate examples/support-ticket/world.json
owo evaluate examples/support-ticket/world.json close_ticket
owo apply examples/support-ticket/world.json record_notification -o /tmp/owo-notified.json
owo evaluate /tmp/owo-notified.json close_ticket
owo apply /tmp/owo-notified.json close_ticket -o /tmp/owo-closed.json
```

The first evaluation is `false`; the second is `true`. Check
`/tmp/owo-closed.json` to see `status: closed`.

`record_notification` does not send a message. In a real support system, call
it only after an external delivery event has been observed, then persist the
new snapshot through your own application. OWO's `apply` command is useful
for previewing the state transition, not for changing the ticketing system.
