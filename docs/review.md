# Review guide (for the owner)

Every change reaches `main` only through a pull request that the owner reviews and merges. This page is the checklist. The pull
request template mirrors it, so an agent fills in the evidence and the reviewer checks it.

## How merging works

- The branch ruleset on `main` requires a pull request, the `issue-link` and `docs-check` checks, and one approving review.
- Agents use the owner's GitHub account, and GitHub does not let an account approve its own pull request. The owner therefore merges
  with the ruleset's **pull-request bypass** ("Merge without waiting for requirements to be met"). Only use it after the review below.
- Direct pushes to `main` are blocked for everyone, including the owner's account, so an agent can't skip the pull request.
- To get formal approvals later, give agents their own GitHub account (a machine user) with write access; then the owner approves in
  the normal way and the bypass is no longer needed.

## Checklist

### Every pull request
- [ ] It links an issue in this repository (`Closes #N` / `Refs #N`), and the change matches the issue.
- [ ] The documentation explains the change well enough that someone new could follow it ([documentation-standard.md](documentation-standard.md)).
- [ ] Claims about the stock firmware cite upstream (file + pinned commit or address), with [fact]/[inference]/[guess] tags.
- [ ] Nothing forbidden is committed: no firmware, `.SFL`, decoded or patched image, Ghidra database or radio backup.
- [ ] No radio action happened without your approval (the test log says what was approved and when).

### Pull requests that build or change a firmware image
- [ ] **Standard update only:** the image is a `.SFL` built by a committed script from the official download; `sfl_encode.py --check`
      output is in the pull request (D1, D4 in [safety.md](safety.md#32-requirements-for-every-custom-image)).
- [ ] **Update path untouched:** the byte-compare of the update functions against stock is in the pull request (D3).
- [ ] **Locks and options unchanged:** the byte-compare of the option-setting memory, boot headers and bitstream options against stock
      is in the pull request ([safety.md §4](safety.md#4-locks-and-option-settings-never-change)).
- [ ] **Factory file wins:** the custom version characters sort below the factory version (D5).
- [ ] **Way back:** the project page has the "if something goes wrong" table filled in, and the planned first radio test ends with
      reinstalling the factory `.SFL` (D7).
- [ ] Transmit changes keep the radio within licence limits, with a dummy-load test planned.

### Upstream-sync pull requests
- [ ] Read the listed upstream commits. Does any project page cite something that changed? If so, ask for a follow-up issue before
      or after merging.

## When to say no

- Any change to lock bits, option settings, OTP, encryption or debug access: the answer is no ([safety.md §4](safety.md#4-locks-and-option-settings-never-change)).
- Any image that needs a non-standard install path, or that touches the updater.
- Any stock-firmware fact documented only here and not reported upstream.
