"""Validation and deterministic strong-Kleene action evaluation."""

import copy
import json
from enum import Enum
from functools import lru_cache
from importlib import resources

from jsonschema import Draft202012Validator


class ValidationError(ValueError):
    """A document or condition violates OWO v0.1."""


class PreconditionError(ValueError):
    """An action precondition is false or unknown."""


class Truth(str, Enum):
    TRUE = "true"
    FALSE = "false"
    UNKNOWN = "unknown"


@lru_cache(maxsize=1)
def load_schema():
    """Return the packaged Draft 2020-12 world schema."""
    path = resources.files("owo.schemas").joinpath("owo-v0.1.schema.json")
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


@lru_cache(maxsize=1)
def _world_validator():
    return Draft202012Validator(load_schema())


@lru_cache(maxsize=1)
def _condition_validator():
    schema = load_schema()
    return Draft202012Validator({"$ref": "#/$defs/condition", "$defs": schema["$defs"]})


def _schema_error(validator, value):
    error = next(validator.iter_errors(value), None)
    if error is not None:
        location = "/".join(str(part) for part in error.absolute_path)
        raise ValidationError("schema error at /{}: {}".format(location, error.message))


def _json_compatible(value):
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError, OverflowError, RecursionError) as error:
        raise ValidationError("not a finite JSON value: {}".format(error)) from error

    def check(node):
        if isinstance(node, dict):
            for key, child in node.items():
                if not isinstance(key, str):
                    raise ValidationError("JSON object keys must be strings")
                check(child)
        elif isinstance(node, list):
            for child in node:
                check(child)
        elif node is None or isinstance(node, (str, bool, int, float)):
            return
        else:
            raise ValidationError("not a JSON value: {}".format(type(node).__name__))

    check(value)


def _check_condition_references(condition, entity_ids):
    if "fact" in condition:
        entity = condition["fact"]["entity"]
        if entity not in entity_ids:
            raise ValidationError("condition refers to unknown entity: {}".format(entity))
    elif "relation" in condition:
        relation = condition["relation"]
        for endpoint in ("subject", "object"):
            if relation[endpoint] not in entity_ids:
                raise ValidationError("condition refers to unknown entity: {}".format(relation[endpoint]))
    elif "not" in condition:
        _check_condition_references(condition["not"], entity_ids)
    else:
        for child in condition.get("all", condition.get("any", [])):
            _check_condition_references(child, entity_ids)


def validate_world(world):
    """Validate schema and semantic references; return the input on success."""
    _json_compatible(world)
    _schema_error(_world_validator(), world)
    entity_ids = [entity["id"] for entity in world["entities"]]
    entity_set = set(entity_ids)
    if len(entity_ids) != len(entity_set):
        raise ValidationError("duplicate entity id")
    for entity in world["state"]:
        if entity not in entity_set:
            raise ValidationError("state refers to unknown entity: {}".format(entity))
    triples = set()
    for relation in world["relations"]:
        for endpoint in ("subject", "object"):
            if relation[endpoint] not in entity_set:
                raise ValidationError("relation refers to unknown entity: {}".format(relation[endpoint]))
        triple = (relation["subject"], relation["predicate"], relation["object"])
        if triple in triples:
            raise ValidationError("duplicate relation triple: {}".format(triple))
        triples.add(triple)
    action_ids = set()
    for action in world["actions"]:
        if action["id"] in action_ids:
            raise ValidationError("duplicate action id: {}".format(action["id"]))
        action_ids.add(action["id"])
        if "precondition" in action:
            _check_condition_references(action["precondition"], entity_set)
        for effect in action["effects"]:
            if effect["entity"] not in entity_set:
                raise ValidationError("effect refers to unknown entity: {}".format(effect["entity"]))
    return world


def _json_equal(left, right):
    numbers = (int, float)
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if isinstance(left, numbers) and isinstance(right, numbers):
        return left == right
    return type(left) is type(right) and left == right


def _evaluate(world, condition):
    if "fact" in condition:
        fact = condition["fact"]
        properties = world["state"].get(fact["entity"], {})
        if fact["key"] not in properties:
            return Truth.UNKNOWN
        return Truth.TRUE if _json_equal(properties[fact["key"]], fact["equals"]) else Truth.FALSE
    if "relation" in condition:
        requested = condition["relation"]
        for relation in world["relations"]:
            if all(relation[key] == requested[key] for key in ("subject", "predicate", "object")):
                return Truth.TRUE if relation["value"] else Truth.FALSE
        return Truth.UNKNOWN
    if "not" in condition:
        return {Truth.TRUE: Truth.FALSE, Truth.FALSE: Truth.TRUE,
                Truth.UNKNOWN: Truth.UNKNOWN}[_evaluate(world, condition["not"])]
    if "all" in condition:
        values = [_evaluate(world, child) for child in condition["all"]]
        if Truth.FALSE in values:
            return Truth.FALSE
        return Truth.UNKNOWN if Truth.UNKNOWN in values else Truth.TRUE
    values = [_evaluate(world, child) for child in condition["any"]]
    if Truth.TRUE in values:
        return Truth.TRUE
    return Truth.UNKNOWN if Truth.UNKNOWN in values else Truth.FALSE


def evaluate_condition(world, condition):
    """Evaluate a condition after validating the world and expression."""
    validate_world(world)
    _json_compatible(condition)
    _schema_error(_condition_validator(), condition)
    _check_condition_references(condition, {entity["id"] for entity in world["entities"]})
    return _evaluate(world, condition)


def _get_action(world, action_id):
    for action in world["actions"]:
        if action["id"] == action_id:
            return action
    raise ValidationError("unknown action id: {}".format(action_id))


def evaluate_action(world, action_id):
    """Return the action precondition truth value."""
    validate_world(world)
    action = _get_action(world, action_id)
    return _evaluate(world, action.get("precondition", {"all": []}))


def apply_action(world, action_id):
    """Apply an authorized grounded action to a deep copy of the world."""
    validate_world(world)
    action = _get_action(world, action_id)
    truth = _evaluate(world, action.get("precondition", {"all": []}))
    if truth is not Truth.TRUE:
        raise PreconditionError("action {} blocked: {}".format(action_id, truth.value))
    result = copy.deepcopy(world)
    for effect in action["effects"]:
        result["state"].setdefault(effect["entity"], {})[effect["key"]] = copy.deepcopy(effect["value"])
    return result
