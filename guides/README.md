# Guides

> Guides connect design principles to a complete system, then show how to test and evolve the result.

Start with [SCOPE](scope-method.md), the Systems Workbench method for moving from a user promise to a design that has been probed against its limits. Read the worked example to see each move in context.

| Guide | What it teaches |
|---|---|
| [Seatline: follow a ticket reservation end to end](seatline-end-to-end.md) | Trace a working reservation through code, retry and race exercises, and slow or unavailable dependency scenarios. |
| [SCOPE: a constraint-first design method](scope-method.md) | A repeatable way to specify, estimate, outline, probe, and evolve a design. |
| [SCOPE example: notification delivery](scope-notifications-worked-example.md) | An original worked example covering estimates, idempotency, retries, and deliberate scaling. |
| [Scaling from one user to millions](scaling-to-millions-of-users.md) | How architecture can change as workload and bottlenecks change. |

## How to practice with a guide

Read the prompt and requirements, pause before the worked design, and draw your own first version. Then compare the assumptions, trace one request, and identify a failure that changes what a user sees. If your design differs, explain which constraint led you to a different choice.
