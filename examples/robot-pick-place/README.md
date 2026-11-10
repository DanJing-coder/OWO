# Robot pick and place: a symbolic plan

This example describes a robot assigned to move one crate to a packing
station. The initial snapshot says the gripper is empty and the crate is in a
pickup zone. `pick_crate` updates three state facts: the gripper becomes
occupied, the crate location becomes `in_gripper`, and `held_by` becomes
`robot_1`. `place_crate` reverses the gripper and ownership facts while setting
the crate location to `packing_station`.

```sh
owo validate examples/robot-pick-place/world.json
owo evaluate examples/robot-pick-place/world.json pick_crate
owo apply examples/robot-pick-place/world.json pick_crate -o /tmp/owo-picked.json
owo evaluate /tmp/owo-picked.json place_crate
owo apply /tmp/owo-picked.json place_crate -o /tmp/owo-placed.json
owo validate /tmp/owo-placed.json
```

Both evaluations return `true`. This is useful as a planner fixture or a
shared expected interpretation for independent agents. The JSON effects are
predictions, not evidence that a robot moved. A real robot still needs motion
planning, perception, collision avoidance, actuation, and observation.
