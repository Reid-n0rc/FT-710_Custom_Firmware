# Contributing

Thanks for helping. This repository builds custom firmware features for the Yaesu FT-710 on top of the reverse-engineering in
[Reid-n0rc/FT-710_Firmware](https://github.com/Reid-n0rc/FT-710_Firmware). Most of the work is done by AI agents and reviewed by the
repository owner; human contributions follow the same process.

1. **Read [AGENTS.md](AGENTS.md).** It is the rule book for humans and agents alike, including the hard rules on radios, firmware
   delivery and lock bits.
2. **Start with an issue** (templates: project, task, question). Say what you want to change and why.
3. **Work on a branch or a fork**, with the documentation ([docs/documentation-standard.md](docs/documentation-standard.md)).
4. **Open a pull request** with the template and link the issue (`Closes #N` or `Refs #N`). The `issue-link` and `docs-check` checks
   must pass.
5. **The owner reviews and merges** ([docs/review.md](docs/review.md)). Nobody pushes to `main` directly.

**Facts about the stock firmware** go upstream, to FT-710_Firmware ([docs/upstream.md](docs/upstream.md)).

**Don't touch anyone's radio without asking.** Anything that writes to a radio needs that radio owner's explicit approval each time.
Read [docs/safety.md](docs/safety.md) first.

**Never commit firmware**: no Yaesu download, `.SFL`, decoded or patched image, Ghidra database or radio backup.

Signing commits is welcome but not required.
