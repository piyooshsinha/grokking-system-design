# System Design Learning Lab

> A practical, open learning path for system design interviews, from core concepts to design practice.

This repository brings together system design fundamentals, reusable architecture patterns, interview exercises, and a local study tool. It is built for people who want to understand design decisions, practice explaining trade-offs, and revisit the areas they find difficult.

## Why this project exists

This fork started from the open Grokking System Design repository. It exists to connect its interview practice with the broader topic map of the System Design Primer, then add a local-first study app and an object-oriented design track. The result is one study path for learning concepts, applying them to a design, and practicing how to explain trade-offs. Examples show defensible approaches, not universal or official answers.

## What you can do here

- **Learn the foundations:** latency, throughput, consistency, availability, databases, communication, and security in [fundamentals](fundamentals/).
- **Understand reusable decisions:** caching, partitioning, replication, messaging, rate limiting, and other [patterns](patterns/).
- **Practice high-level design:** use the [question catalog](questions/), [practice bank](questions/practice-bank.md), and [interview framework](cheat-sheets/interview-framework.md).
- **Practice object-oriented design:** work through class-level problems in [low-level design](low-level-design/).
- **Study real systems:** read [distributed-systems deep dives](deep-dives/) and the [scaling walkthrough](guides/scaling-to-millions-of-users.md).
- **Prepare with company notes:** use the [company guides](companies/) as leads for what to research and rehearse. Interview formats vary by team and change over time; reported questions are not guarantees.
- **Use a local study tutor:** browse, search, quiz, and run mock interviews with the [study assistant](tools/study-assistant/).

## A suggested study path

1. Start with the [interview framework](cheat-sheets/interview-framework.md) and [fundamentals](fundamentals/).
2. Learn the [core patterns](patterns/), using the [scaling walkthrough](guides/scaling-to-millions-of-users.md) to see how they combine.
3. Pick a problem from the [question catalog](questions/). State assumptions, sketch a design, and explain the trade-offs before reading the walkthrough.
4. Use the [roadmaps](roadmaps/) to plan your study time, then revisit weak areas with [flashcards](cheat-sheets/flashcards.md) or the study assistant.
5. For class-level design, follow the [low-level design guide](low-level-design/README.md).

## Run the local study assistant

The assistant runs on your machine. It indexes the repository, provides keyword search without a model, and can use a local Ollama model for grounded answers, answer grading, spaced repetition, and mock interviews. Mermaid is bundled with the app, so browsing diagrams does not require a CDN.

```bash
cd tools/study-assistant
python3 study_assistant.py build
python3 study_assistant.py serve
```

The app opens at `http://127.0.0.1:8000`. To enable local model features, install [Ollama](https://ollama.com), pull `nomic-embed-text` and `llama3.2`, and rebuild the index. See the [assistant guide](tools/study-assistant/README.md) for configuration and privacy details.

## Repository map

| Folder | What it contains |
|--------|------------------|
| [fundamentals/](fundamentals/) | Concepts and constraints behind design choices |
| [patterns/](patterns/) | Reusable architecture techniques |
| [questions/](questions/) | High-level design practice problems |
| [low-level-design/](low-level-design/) | Object-oriented and class-design exercises |
| [deep-dives/](deep-dives/) | How important distributed systems work |
| [companies/](companies/) | Interview preparation notes by company |
| [cheat-sheets/](cheat-sheets/) | Quick references, comparisons, and flashcards |
| [roadmaps/](roadmaps/) | Study plans for different timelines |
| [tools/study-assistant/](tools/study-assistant/) | Local web app and command-line tutor |
| [resources.md](resources.md) | Further reading and source repositories |

## Sources and credit

This project was informed by two open learning resources:

- [Grokking System Design](https://github.com/design-gurus/grokking-system-design), published by DesignGurus.io.
- [The System Design Primer](https://github.com/donnemartin/system-design-primer), created by Donne Martin and contributors.

Both source repositories publish content under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). This project reorganizes and extends ideas from those references with its own study paths, exercises, and tools. Where material is directly adapted, the relevant source and changes should be credited. This project is independent and is not affiliated with or endorsed by either source. See [NOTICE.md](NOTICE.md) for attribution details.

## Contributing

Contributions are welcome. Please write in your own words, cite sources for factual or time-sensitive claims, and label company interview information as reported unless supported by an official source. Start with [CONTRIBUTING.md](CONTRIBUTING.md) and the relevant template.

## License

Learning content is shared under [CC BY 4.0](LICENSE), with source credits and third-party notices described in [NOTICE.md](NOTICE.md). Third-party software and bundled assets may have separate licenses.
