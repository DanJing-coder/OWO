# Server maintenance: wait for observed health

This example shows how an agent can describe a *proposed* restart without
confusing a planned transition with an observed recovery. The `hosts` relation
connects `server_1` to `catalog_api`.

| Snapshot | Action | Result | Reason |
|---|---|---|---|
| [`world.json`](world.json) | `begin_restart` | `true` | Server is running and maintenance is approved |
| After `begin_restart` | `complete_restart` | `unknown` | `healthcheck_passed` has not been observed |
| [`verified.json`](verified.json) | `complete_restart` | `true` | Restarting state and a passed health check are explicit |

Run from the repository root:

```sh
owo validate examples/server-maintenance/world.json
owo evaluate examples/server-maintenance/world.json begin_restart
owo apply examples/server-maintenance/world.json begin_restart -o /tmp/owo-restarting.json
owo evaluate /tmp/owo-restarting.json complete_restart
owo evaluate examples/server-maintenance/verified.json complete_restart
owo apply examples/server-maintenance/verified.json complete_restart -o /tmp/owo-running.json
```

The evaluation results, in order, are `true`, `unknown`, and `true`.
`verified.json` represents a *separately observed* passed health check. The
`begin_restart` effect only changes the JSON snapshot to `status: restarting`;
it does not call a restart API. A real automation should execute the restart
through its own controlled tool, collect a health-check result, and only then
create the verified snapshot.
