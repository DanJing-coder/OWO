"""Executable v0.1 conformance vectors for the schema and reference SDK."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from owo import (
    PreconditionError,
    Truth,
    ValidationError,
    apply_action,
    evaluate_action,
    evaluate_condition,
    load_schema,
    validate_world,
)


ROOT = Path(__file__).resolve().parents[1]
DOOR = json.loads((ROOT / "examples/door/world.json").read_text(encoding="utf-8"))


class SchemaConformance(unittest.TestCase):
    def test_schema_is_valid_and_packaged(self):
        schema = load_schema()
        Draft202012Validator.check_schema(schema)
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertFalse(list(Draft202012Validator(schema).iter_errors(DOOR)))

    def test_invalid_schema_vectors(self):
        vectors = [
            {**DOOR, "owo_version": "0.2"},
            {**DOOR, "extra": 1},
            {**DOOR, "state": {"front_door": {"open": []}}},
            {**DOOR, "actions": [{"id": "bad", "effects": [], "precondition": {"all": {}, "any": []}}]},
            {**DOOR, "relations": [{"subject": "front_door", "predicate": "x", "object": "hall", "value": "true"}]},
        ]
        validator = Draft202012Validator(load_schema())
        for world in vectors:
            with self.subTest(world=world):
                self.assertTrue(list(validator.iter_errors(world)))
                with self.assertRaises(ValidationError):
                    validate_world(world)

    def test_invalid_semantic_vectors(self):
        vectors = []
        duplicate_entity = copy.deepcopy(DOOR)
        duplicate_entity["entities"].append(copy.deepcopy(duplicate_entity["entities"][0]))
        vectors.append(duplicate_entity)
        duplicate_action = copy.deepcopy(DOOR)
        duplicate_action["actions"].append(copy.deepcopy(duplicate_action["actions"][0]))
        vectors.append(duplicate_action)
        duplicate_relation = copy.deepcopy(DOOR)
        duplicate_relation["relations"].append(copy.deepcopy(duplicate_relation["relations"][0]))
        vectors.append(duplicate_relation)
        dangling_relation = copy.deepcopy(DOOR)
        dangling_relation["relations"][0]["object"] = "absent"
        vectors.append(dangling_relation)
        dangling_state = copy.deepcopy(DOOR)
        dangling_state["state"]["absent"] = {}
        vectors.append(dangling_state)
        dangling_condition = copy.deepcopy(DOOR)
        dangling_condition["actions"][0]["precondition"] = {"fact": {"entity": "absent", "key": "open", "equals": False}}
        vectors.append(dangling_condition)
        dangling_effect = copy.deepcopy(DOOR)
        dangling_effect["actions"][0]["effects"][0]["entity"] = "absent"
        vectors.append(dangling_effect)
        dangling_relation_condition = copy.deepcopy(DOOR)
        dangling_relation_condition["actions"][0]["precondition"] = {"relation": {"subject": "front_door", "predicate": "leads_to", "object": "absent"}}
        vectors.append(dangling_relation_condition)
        for world in vectors:
            with self.subTest(world=world):
                self.assertFalse(list(Draft202012Validator(load_schema()).iter_errors(world)))
                with self.assertRaises(ValidationError):
                    validate_world(world)

    def test_non_json_python_values_are_rejected(self):
        non_string_key = copy.deepcopy(DOOR)
        non_string_key["entities"][0]["attributes"][1] = "bad key"
        non_finite = copy.deepcopy(DOOR)
        non_finite["state"]["front_door"]["temperature"] = float("nan")
        for world in (non_string_key, non_finite):
            with self.assertRaises(ValidationError):
                validate_world(world)


class TruthConformance(unittest.TestCase):
    def test_truth_tables(self):
        true = {"fact": {"entity": "front_door", "key": "locked", "equals": False}}
        false = {"fact": {"entity": "front_door", "key": "locked", "equals": True}}
        unknown = {"fact": {"entity": "front_door", "key": "jammed", "equals": False}}
        cases = [
            (true, Truth.TRUE),
            (false, Truth.FALSE),
            (unknown, Truth.UNKNOWN),
            ({"not": unknown}, Truth.UNKNOWN),
            ({"not": false}, Truth.TRUE),
            ({"all": [true, unknown]}, Truth.UNKNOWN),
            ({"all": [false, unknown]}, Truth.FALSE),
            ({"any": [true, unknown]}, Truth.TRUE),
            ({"any": [false, unknown]}, Truth.UNKNOWN),
            ({"all": []}, Truth.TRUE),
            ({"any": []}, Truth.FALSE),
        ]
        for condition, result in cases:
            with self.subTest(condition=condition):
                self.assertEqual(evaluate_condition(DOOR, condition), result)

    def test_json_type_sensitive_equality_and_null(self):
        world = copy.deepcopy(DOOR)
        world["state"]["front_door"]["number"] = 1
        world["state"]["front_door"]["nullable"] = None
        self.assertEqual(evaluate_condition(world, {"fact": {"entity": "front_door", "key": "number", "equals": True}}), Truth.FALSE)
        self.assertEqual(evaluate_condition(world, {"fact": {"entity": "front_door", "key": "nullable", "equals": None}}), Truth.TRUE)

    def test_relation_explicit_false_and_absence(self):
        condition = {"relation": {"subject": "front_door", "predicate": "leads_to", "object": "hall"}}
        self.assertEqual(evaluate_condition(DOOR, condition), Truth.TRUE)
        world = copy.deepcopy(DOOR)
        world["relations"][0]["value"] = False
        self.assertEqual(evaluate_condition(world, condition), Truth.FALSE)
        world["relations"] = []
        self.assertEqual(evaluate_condition(world, condition), Truth.UNKNOWN)


class ActionConformance(unittest.TestCase):
    def test_door_action_is_pure_and_reversible(self):
        original = copy.deepcopy(DOOR)
        self.assertEqual(evaluate_action(DOOR, "open_door"), Truth.TRUE)
        opened = apply_action(DOOR, "open_door")
        self.assertEqual(DOOR, original)
        self.assertTrue(opened["state"]["front_door"]["open"])
        self.assertEqual(evaluate_action(opened, "open_door"), Truth.FALSE)
        self.assertEqual(evaluate_action(opened, "close_door"), Truth.TRUE)
        self.assertEqual(apply_action(opened, "close_door")["state"], DOOR["state"])

    def test_unknown_and_false_block_without_mutation(self):
        for value, expected in [(None, Truth.UNKNOWN), (True, Truth.FALSE)]:
            world = copy.deepcopy(DOOR)
            if value is None:
                del world["state"]["front_door"]["locked"]
            else:
                world["state"]["front_door"]["locked"] = value
            before = copy.deepcopy(world)
            self.assertEqual(evaluate_action(world, "open_door"), expected)
            with self.assertRaises(PreconditionError):
                apply_action(world, "open_door")
            self.assertEqual(world, before)

    def test_unknown_action_rejected(self):
        with self.assertRaises(ValidationError):
            evaluate_action(DOOR, "missing")

    def test_omitted_precondition_and_ordered_effects(self):
        world = copy.deepcopy(DOOR)
        world["actions"].append({
            "id": "set_status",
            "effects": [
                {"entity": "front_door", "key": "status", "value": "first"},
                {"entity": "front_door", "key": "status", "value": "last"},
            ],
        })
        self.assertEqual(evaluate_action(world, "set_status"), Truth.TRUE)
        self.assertEqual(apply_action(world, "set_status")["state"]["front_door"]["status"], "last")
        self.assertNotIn("status", world["state"]["front_door"])


class CliConformance(unittest.TestCase):
    def run_cli(self, *args, input_text=None):
        return subprocess.run([sys.executable, "-m", "owo", *args], input=input_text,
                              capture_output=True, text=True, check=False)

    def test_validate_evaluate_apply(self):
        path = str(ROOT / "examples/door/world.json")
        self.assertEqual(self.run_cli("validate", path).returncode, 0)
        evaluated = self.run_cli("evaluate", path, "open_door")
        self.assertEqual(evaluated.returncode, 0)
        self.assertEqual(json.loads(evaluated.stdout), {"action": "open_door", "result": "true"})
        applied = self.run_cli("apply", path, "open_door")
        self.assertEqual(applied.returncode, 0)
        self.assertTrue(json.loads(applied.stdout)["state"]["front_door"]["open"])
        self.assertEqual(self.run_cli("evaluate", "-", "close_door", input_text=applied.stdout).returncode, 0)

    def test_cli_error_codes_and_output_file(self):
        path = str(ROOT / "examples/door/world.json")
        self.assertEqual(self.run_cli("evaluate", path, "missing").returncode, 2)
        locked = copy.deepcopy(DOOR)
        locked["state"]["front_door"]["locked"] = True
        blocked = self.run_cli("apply", "-", "open_door", input_text=json.dumps(locked))
        self.assertEqual(blocked.returncode, 2)
        self.assertEqual(blocked.stdout, "")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"
            result = self.run_cli("apply", path, "open_door", "-o", str(output))
            self.assertEqual(result.returncode, 0)
            self.assertTrue(json.loads(output.read_text())["state"]["front_door"]["open"])
            self.assertEqual(self.run_cli("validate", str(output)).returncode, 0)
            broken = Path(directory) / "broken.json"
            broken.write_text("{", encoding="utf-8")
            self.assertEqual(self.run_cli("validate", str(broken)).returncode, 1)


if __name__ == "__main__":
    unittest.main()
