<!-- Fill in every section; write "none" where it does not apply. See docs/review.md for what the owner checks. -->
Closes #N  <!-- or "Refs #N" for one step of a larger issue; the issue-link check needs one of them -->

## What this changes

## Why

## Upstream facts relied on
<!-- upstream file / address and the pinned upstream commit (git -C upstream log -1 --format=%h). Tag [fact]/[inference]/[guess]. -->

## Documentation
<!-- Which docs/ pages changed and what they now say. -->

## Firmware images (only if this builds or changes one; otherwise "none")
- Base image and SHA-256:
- Output `.SFL` name and SHA-256:
- `sfl_encode.py --check` output:
- Update-path functions byte-identical to stock (safety.md D3):
- Lock / option areas byte-identical to stock (safety.md §4):
- Version characters sort below the factory version (D5):
- Way back to stock:

## Radio
<!-- "No radio involved", or: what was done, the owner's approval (date, exact action), backup reference, result. -->

## Checklist
- [ ] Linked an issue in this repository
- [ ] Docs updated (docs-check passes)
- [ ] No firmware, `.SFL`, decoded/patched image, Ghidra database or radio backup committed
- [ ] Nothing written to a radio without the owner's approval for that action
- [ ] Stock-firmware findings reported upstream (label `upstream-finding`), not only here
- [ ] Label `needs-review` added; I will not merge this myself
