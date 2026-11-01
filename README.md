# Systems Workbench

> Start with a constraint. Build the smallest design that meets it. Stress it, then evolve it.

Systems Workbench is a hands-on guide to making and defending system design decisions. Learn the forces behind a design, sketch the smallest useful architecture, and test it against load and failure. The material is open, practical, and paired with a local study tutor.

## Why this project exists

System design material often presents a list of components before making the constraints clear. Systems Workbench teaches the reasoning in the other direction: define what must be true, estimate what the system must handle, draw a simple path, and add complexity only when a concrete limit demands it. It combines interview practice with an original decision method, a local-first tutor, and class-level design exercises. Worked examples are starting points to critique, not universal or official answers.

## What you can do here

- **Learn the foundations:** latency, throughput, consistency, availability, databases, communication, and security in [fundamentals](fundamentals/).
- **Understand reusable decisions:** caching, partitioning, replication, messaging, rate limiting, and other [patterns](patterns/).
- **Use one repeatable method:** apply [SCOPE](guides/scope-method.md)—Specify, Calculate, Outline, Probe, Evolve—to unfamiliar design problems.
- **Practice high-level design:** use the [question catalog](questions/), [practice bank](questions/practice-bank.md), and [interview framework](cheat-sheets/interview-framework.md).
- **Practice object-oriented design:** work through class-level problems in [low-level design](low-level-design/).
- **Study real systems:** read [distributed-systems deep dives](deep-dives/) and the [scaling walkthrough](guides/scaling-to-millions-of-users.md).
- **Prepare with company notes:** use the [company guides](companies/) as leads for what to research and rehearse. Interview formats vary by team and change over time; reported questions are not guarantees.
- **Use a local study tutor:** browse, search, quiz, and run mock interviews with the [study assistant](tools/study-assistant/).

## Choose your path

| Your situation | Start here |
|---|---|
| New to system design | [Six-week foundation](roadmaps/6-week-plan.md): learn the vocabulary, then practice one decision at a time. |
| Interview in about two weeks | [Two-week sprint](roadmaps/2-week-plan.md): focus on core patterns and timed practice. |
| Interview in seven days | [One-week triage](roadmaps/1-week-plan.md): prioritize a reliable structure and a few complete rehearsals. |
| Experienced but rusty | [Senior and staff refresher](roadmaps/senior-staff-refresher.md): diagnose gaps, then review only what you need. |
| Want to understand the method first | Read [SCOPE](guides/scope-method.md), then try it on [notification delivery](guides/scope-notifications-worked-example.md). |
| Preparing for class-level design | Follow the [low-level design guide](low-level-design/README.md). |

Each path uses the same rhythm: attempt from a blank page, compare your reasoning with an example, and write down one assumption you would change.

## Run the local study assistant

The assistant runs on your machine. It indexes the repository, provides keyword search without a model, and can use a local Ollama model for semantic retrieval, grounded answers, answer grading, spaced repetition, and mock interviews. Its diagrams include flow playback, and the CAP page has an interactive partition simulator. Mermaid is bundled with the app, so browsing diagrams does not require a CDN.

```bash
cd tools/study-assistant
python3 study_assistant.py build
python3 study_assistant.py serve
```

The app opens at `http://127.0.0.1:8000`. To enable local model features, install [Ollama](https://ollama.com), pull `nomic-embed-text` and a chat model, then rebuild the index. See the [assistant guide](tools/study-assistant/README.md) for configuration and privacy details. To run it in Docker behind the NUC's Caddy proxy, see the [deployment guide](tools/study-assistant/DEPLOYMENT.md).

## Run the reference application

[Seatline](examples/seatline/) is a runnable ticket reservation app. Follow a seat hold through checkout, inventory updates, the transactional outbox, and an idempotent notification worker. It is the concrete companion to the concepts in this guide; the [Seatline README](examples/seatline/README.md) maps each behavior to the code and its study pages. On the NUC, open the [live Seatline demo](https://study.192-168-1-22.sslip.io/seatline/).

## Repository map

| Folder | What it contains |
|--------|------------------|
| [fundamentals/](fundamentals/) | Concepts and constraints behind design choices |
| [patterns/](patterns/) | Reusable architecture techniques |
| [questions/](questions/) | High-level design practice problems |
| [guides/](guides/) | SCOPE method, worked examples, and end-to-end walkthroughs |
| [low-level-design/](low-level-design/) | Object-oriented and class-design exercises |
| [deep-dives/](deep-dives/) | How important distributed systems work |
| [companies/](companies/) | Interview preparation notes by company |
| [cheat-sheets/](cheat-sheets/) | Quick references, comparisons, and flashcards |
| [roadmaps/](roadmaps/) | Study plans for different timelines |
| [tools/study-assistant/](tools/study-assistant/) | Local web app and command-line tutor |
| [resources.md](resources.md) | Further reading and source repositories |

## Sources and credit

Systems Workbench is an independent learning project. Its starting references include:

- [Grokking System Design](https://github.com/design-gurus/grokking-system-design), published by DesignGurus.io.
- [The System Design Primer](https://github.com/donnemartin/system-design-primer), created by Donne Martin and contributors.

Both source repositories publish content under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). This project adds its own method, study paths, examples, exercises, and tools. Where material is directly adapted, the relevant source and changes should be credited. Systems Workbench is not affiliated with or endorsed by either source. See [NOTICE.md](NOTICE.md) for attribution details.

## Contributing

Contributions are welcome. Please write in your own words, cite sources for factual or time-sensitive claims, and label company interview information as reported unless supported by an official source. Start with [CONTRIBUTING.md](CONTRIBUTING.md) and the relevant template.

## License

Learning content is shared under [CC BY 4.0](LICENSE), with source credits and third-party notices described in [NOTICE.md](NOTICE.md). Third-party software and bundled assets may have separate licenses.
