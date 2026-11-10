# Deployment gate: evaluate readiness before a release

This example links `release_42` to `service_billing`. `plan_deployment` checks
that the release is a candidate, tests passed, change approval was received,
and the target service is healthy. It changes only the *planned* release status
to `ready`. It does not deploy software.

| Snapshot | Action | Result | Reason |
|---|---|---|---|
| [`world.json`](world.json) | `plan_deployment` | `true` | All readiness facts are explicit |
| After `plan_deployment` | `record_deployment` | `unknown` | No deployment outcome has been observed |
| [`observed.json`](observed.json) | `record_deployment` | `true` | A separate deployment system reported success |

Run from the repository root:

```sh
owo validate examples/deployment-gate/world.json
owo evaluate examples/deployment-gate/world.json plan_deployment
owo apply examples/deployment-gate/world.json plan_deployment -o /tmp/owo-release-ready.json
owo evaluate /tmp/owo-release-ready.json record_deployment
owo evaluate examples/deployment-gate/observed.json record_deployment
owo apply examples/deployment-gate/observed.json record_deployment -o /tmp/owo-release-deployed.json
```

The results are `true`, `unknown`, and `true`. An internal deployment tool,
change-management system, CI system, and monitoring system must supply the
facts. Approval and actual deployment authorization remain with those systems.
See the [offline record adapter](../company-internal/README.md) for a runnable
field-mapping example.
