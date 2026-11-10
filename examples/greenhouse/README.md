# Greenhouse irrigation: react to observed soil state

This world contains a plant bed, a pump, and a water tank. Two directed
relations say which bed the pump irrigates and which pump the tank supplies.
The `start_irrigation` action checks for a dry bed, an idle pump, available
water, and both relations. The `stop_irrigation` action requires a running pump
and a separately observed wet bed.

| Snapshot | Action | Result |
|---|---|---|
| [`world.json`](world.json) | `start_irrigation` | `true` |
| After `start_irrigation` | `stop_irrigation` | `false` while the bed is still recorded as dry |
| [`observed-wet.json`](observed-wet.json) | `stop_irrigation` | `true` |

Run from the repository root:

```sh
owo validate examples/greenhouse/world.json
owo evaluate examples/greenhouse/world.json start_irrigation
owo apply examples/greenhouse/world.json start_irrigation -o /tmp/owo-pump-running.json
owo evaluate /tmp/owo-pump-running.json stop_irrigation
owo evaluate examples/greenhouse/observed-wet.json stop_irrigation
owo apply examples/greenhouse/observed-wet.json stop_irrigation -o /tmp/owo-pump-stopped.json
```

The action effects change only the symbolic `running` property. They do not
switch a physical pump, measure soil moisture, or enforce equipment safety.
`observed-wet.json` represents a fresh sensor observation; a real controller
must use its own hardware interface, safety interlocks, and verified readings.
