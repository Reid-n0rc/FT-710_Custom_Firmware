# Documentation standard

Everything in this repository is documented in detail, so that a reviewer can check it and a new person (or a new agent) can pick
it up without asking. This page says what "documented" means. `tools/check_docs.py` checks the mechanical parts in CI
(`docs-check`); the rest is part of the review ([review.md](review.md)).

## Rules for every change

1. **Docs travel with the change.** A pull request that changes anything outside `docs/` also changes `docs/` (checked).
2. **Evidence tags.** Claims about the radio or its firmware are tagged **[fact]** (seen in code, data, a manual or a measurement,
   with the source), **[inference]** (follows from facts, not seen directly) or **[guess]**.
3. **Upstream citations.** Stock-firmware facts cite upstream: file, section or address, and the pinned commit when it matters
   ([upstream.md](upstream.md)).
4. **Numbers, not adjectives.** "Fails on 3 of 117 channels", not "mostly works". Say what was measured and how.
5. **Plain English.** Short sentences, one idea per paragraph. Define terms on first use or link upstream's glossary.
6. **Diagrams.** Mermaid for flows and structure (about 25 nodes or fewer).
7. **Links.** Relative links inside `docs/` must resolve (checked).

## Project pages (`docs/projects/<name>.md`)

One page per project; it is the source of truth for the design and the plan. It must have these `##` sections, in this order
(checked; the text may say "none yet"):

| Section | Contents |
|---|---|
| `## Summary` | what the project changes for an operator, in a few sentences; the issue link; current status |
| `## Status` | a table of the plan's steps with their state (`todo`, `in progress`, `in review`, `done`, `blocked`) and links to pull requests |
| `## Background` | the upstream facts the project relies on, with citations and the pinned upstream commit |
| `## Design` | what will change, chip by chip; why this approach; alternatives considered and why not |
| `## Delivery and the way back` | how the result is installed (standard SD-card update only), how it complies with [safety.md](safety.md) D1–D8 and §4, and the project's "if something goes wrong" table |
| `## Risks` | each risk with likelihood, impact, mitigation and path back |
| `## Plan` | numbered steps, each with one verifiable result and its test |
| `## Test log` | every offline check and every radio test: date, what was approved and by whom, backup reference, steps, result, surprises |
| `## Decisions` | dated decisions, who made them and why |
| `## Open questions` | what is not known yet, and how each will be answered |

## Patches

Each patch (in the project's directory once one exists) documents:

- the base image: name, version and SHA-256 of the official file;
- every change: address, old bytes, new bytes, and what the change does, with upstream citations;
- how it was verified offline (disassembly of the result, simulation, `sfl_encode.py --check`);
- the safety comparisons: update-path functions and lock/option areas byte-identical to stock ([safety.md](safety.md));
- the SHA-256 of the produced `.SFL` file and its file name (version characters per D5);
- the install steps and the way back to stock.

## Tools

Each script starts with a docstring: what it does, its inputs and outputs, an example command, and what it never does (for example,
"never writes to a radio"). It is listed in the project page or in [docs/README.md](README.md).

## Radio tests

The test log entry for a radio test records:

- the owner's approval: date and the exact action approved;
- the radio's firmware versions before the test (`VE0;`..`VE3;`) and the backup taken (folder and `SHA256SUMS` hash);
- the files installed (names and SHA-256);
- the steps, the observed result, any surprise;
- the restore to stock at the end (D7) and the versions after it.
