# Welcome to Systems Workbench

> Learn to make system design decisions from constraints, then test and explain those decisions.

Start with the user promise. Estimate the workload. Sketch the simplest useful design. Probe its failure modes. Evolve it when a real constraint calls for change.

## The SCOPE method

Use SCOPE on every problem:

1. **Specify** the user outcome and the invariant that must hold.
2. **Calculate** rough traffic, storage, and peak load.
3. **Outline** the simplest end-to-end read and write paths.
4. **Probe** retries, overload, stale data, and component failure.
5. **Evolve** one part of the design when evidence shows a limit.

Read the full [SCOPE guide](../guides/scope-method.md), then work through the [notification delivery example](../guides/scope-notifications-worked-example.md).

## Choose a study path

| Your situation | Recommended path |
|---|---|
| I am new to system design | [Six-week foundation](../roadmaps/6-week-plan.md) |
| My interview is about two weeks away | [Two-week sprint](../roadmaps/2-week-plan.md) |
| My interview is next week | [One-week triage](../roadmaps/1-week-plan.md) |
| I am experienced, but rusty | [Senior and staff refresher](../roadmaps/senior-staff-refresher.md) |

## A useful first exercise

Choose [notification delivery](../guides/scope-notifications-worked-example.md) or a problem from the [question catalog](../questions/). Before opening a walkthrough, write down:

- The promise the system makes to its users.
- One rough estimate that affects its design.
- The first failure that could change what a user sees.

Then compare your assumptions and trade-offs with the walkthrough. A different design can be right when its constraints differ.

## About Systems Workbench

Systems Workbench is an independent learning project for system design interviews and architecture practice. It combines fundamentals, reusable patterns, design exercises, system case studies, company research notes, and a local study tutor. Its focus is explaining why a design fits its constraints, what it costs, and how it behaves when things fail.

The project draws on [Grokking System Design](https://github.com/design-gurus/grokking-system-design) and [The System Design Primer](https://github.com/donnemartin/system-design-primer). It adds project-specific paths, the SCOPE study method, original worked examples, and the local tutor. See [source credits and attribution](../NOTICE.md). Systems Workbench is independent and is not endorsed by either source.

## Study privately on your machine

Browse and search without a model. For local AI answers, install [Ollama](https://ollama.com) and follow the [study tutor setup](../tools/study-assistant/README.md). The tutor uses local model services; configuration and network behavior are explained in its guide.
