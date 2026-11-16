# Roadmap

Where the integration is heading, by what it will do. Each entry names what has
to exist before it can start. Nothing here is a commitment to a date or an order.

For what the integration does today and what it does not, see the
[README](./README.md) and its [Known limitations](./README.md#known-limitations).

## Zone groups

Split a house into a few zone groups, for example a ground floor and an upper
floor. Each group has its own thermal state in the model, and the number of
groups is not fixed at two: groups are indexed, so a house can have as many as
it needs.

**Needs first:**

- Room-level temperature history, so each group's thermal behaviour can be
  learned from its own measurements.
- Evidence from the room phases planned in round 11 that each group's thermal
  parameters can be told apart from the others' using that history.

## One zone per room

Give each room its own zone, and let the integration write each room's
thermostat target as part of the plan.

**Needs first:**

- The same room-level history and identifiability evidence as zone groups.
- Zone groups, which this builds on.
