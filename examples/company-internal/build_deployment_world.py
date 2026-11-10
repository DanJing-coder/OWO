"""Turn a small export of internal records into an OWO deployment snapshot.

This offline example reads JSON records. Replace the record export with your
own API client, while retaining the explicit field mapping and validation.
"""

import argparse
import json
from pathlib import Path

from owo import validate_world


TEMPLATE = Path(__file__).resolve().parents[1] / "deployment-gate" / "world.json"


def build_world(records):
    world = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    world["state"] = {"release_42": {}, "service_billing": {}}

    def copy_fact(section, source_key, entity, target_key):
        source = records.get(section, {})
        if not isinstance(source, dict):
            raise ValueError("{} must be a JSON object".format(section))
        if source_key in source:
            world["state"][entity][target_key] = source[source_key]

    copy_fact("release", "status", "release_42", "status")
    copy_fact("ci", "tests_passed", "release_42", "tests_passed")
    copy_fact("change", "approval_received", "release_42", "approval_received")
    copy_fact("monitoring", "service_health", "service_billing", "health")
    copy_fact("deployment", "succeeded", "release_42", "deployment_succeeded")
    return validate_world(world)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", type=Path, help="JSON export from source systems")
    args = parser.parse_args()
    try:
        records = json.loads(args.records.read_text(encoding="utf-8"))
        if not isinstance(records, dict):
            raise ValueError("records must be a JSON object")
        world = build_world(records)
    except (OSError, ValueError) as error:
        parser.exit(2, "{}: {}\n".format(parser.prog, error))
    print(json.dumps(world, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
