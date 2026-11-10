"""Command-line interface for OWO v0.1."""

import argparse
import json
import sys
from pathlib import Path

from .core import PreconditionError, ValidationError, apply_action, evaluate_action, validate_world


def _read(path):
    if path == "-":
        return json.load(sys.stdin)
    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream)


def _write(value, path):
    serialized = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if path == "-":
        sys.stdout.write(serialized)
    else:
        Path(path).write_text(serialized, encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="owo", description="Open World Ontology v0.1")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="validate an OWO document")
    validate.add_argument("file")
    evaluate = commands.add_parser("evaluate", help="evaluate an action precondition")
    evaluate.add_argument("file")
    evaluate.add_argument("action_id")
    apply = commands.add_parser("apply", help="apply an authorized action")
    apply.add_argument("file")
    apply.add_argument("action_id")
    apply.add_argument("-o", "--output", default="-")
    args = parser.parse_args(argv)
    try:
        world = _read(args.file)
        if args.command == "validate":
            validate_world(world)
            print("valid")
        elif args.command == "evaluate":
            truth = evaluate_action(world, args.action_id)
            _write({"action": args.action_id, "result": truth.value}, "-")
        else:
            _write(apply_action(world, args.action_id), args.output)
    except (ValidationError, PreconditionError) as error:
        print("owo: {}".format(error), file=sys.stderr)
        return 2
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print("owo: {}".format(error), file=sys.stderr)
        return 1
    return 0
