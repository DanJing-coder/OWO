# RFC-0001: Core world model

Status: Accepted for v0.1 MVP

Version: 0.1

## Scope and wire format

An OWO document is a UTF-8 JSON object with `owo_version` exactly `"0.1"`,
`entities`, `relations`, `state`, and `actions`. The normative JSON Schema is
[`owo-v0.1.schema.json`](../../src/owo/schemas/owo-v0.1.schema.json). Producers
MUST emit only fields defined by the schema. Consumers MUST reject unsupported
versions and schema-invalid documents. Object member order is insignificant.

An entity has an opaque, nonempty `id` and `type`, plus optional `attributes`
containing static JSON values. An ID is unique within a document and is matched
byte for byte after JSON decoding. Entity IDs need not be URIs. `attributes`
are descriptive metadata and are never read by the action evaluator.

A relation is a directed triple (`subject`, `predicate`, `object`) with a
Boolean `value`. `false` explicitly negates a triple; an absent triple is
unknown. A document MUST NOT contain the same triple twice, even with equal
values. Both endpoints MUST identify entities in the document.

`state` maps entity IDs to maps of property names to JSON scalar values
(`null`, Boolean, number, or string). A missing property is unknown; `null` is
a known value. Every state entity ID MUST identify a declared entity. Arrays
and objects are excluded from dynamic state in v0.1.

`actions` is a list of grounded action definitions as specified in RFC-0003.
Action IDs MUST be unique. This version has no parameter binding, inference,
type hierarchy, persistence, or network transport.

## Conformance

Schema validity is necessary but not sufficient: the reference validator also
checks ID uniqueness, endpoint references, state references, action references,
and duplicate relation triples. These semantic checks are normative.
