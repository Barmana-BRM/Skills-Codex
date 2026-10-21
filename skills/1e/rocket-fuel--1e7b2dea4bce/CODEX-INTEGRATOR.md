# Codex Integrator: the invocation contract

Every Codex call in this skill goes through these exact patterns. They encode real traps; do not improvise around them. Verified live on codex-cli 0.143.0.

## The non-negotiables (every call)

1. **Prompts go in via a file on stdin** (`- <"$FILE"`), never as an argv string. This kills two traps at once: shell-quoting bugs and the stdin hang (`codex exec` reads stdin in addition to any argv prompt; under a non-TTY harness an unredirected call blocks forever at 0 CPU). If you ever must pass an argv prompt, append `< /dev/null`.
2. `2>/dev/null` always. Codex streams thinking tokens to stderr; they would flood the driving context.
3. **Capture the JSONL stream to a file and parse it after exit.** Never pipe the stream through `grep` directly: `grep -m1` exits at first match, closes the pipe, and can kill Codex mid-run before the output file is written.
4. `--json -o <outfile>`: the answer is read from the `-o` file, the stream file is parsed only for the thread id.
5. **One fresh temp dir per run, fresh filenames per round** (`RUN=$(mktemp -d /tmp/rf.XXXXXX)`). Never reuse an output path across rounds: after a timeout or failure, a reused path serves the PREVIOUS round's verdict and looks exactly like success.
6. Resume by explicit thread id, never `--last`. A wrong session looks exactly like success.
7. Never pin `-m`. Model pins 400 on ChatGPT-account auth. Before round 1, echo the active model if `~/.codex/config.toml` has a `model` line, else say "Codex CLI default".
8. Bash tool `timeout: 600000` (10 min) on every call. Codex writes output only at completion; a killed call is silently empty.
9. `--skip-git-repo-check` on every call (Codex refuses untrusted directories without it).
10. **Snapshot before every call** (the three snapshot lines below, together, in every snippet): status, tracked diff, and untracked-file hashes. If a read-only call changes files anyway: paths that were CLEAN before get reverted; tracked-dirty or untracked paths whose content no longer matches the snapshot get a STOP, not an auto-revert (surface it, let the user judge). Never blanket-revert: the user or the Visionary may have legitimate uncommitted work.

```bash
snap() { git status --porcelain > "$RUN/pre-$1.txt"; git diff > "$RUN/pre-$1.patch";
  git ls-files --others --exclude-standard -z | xargs -0 shasum > "$RUN/pre-$1.sha" 2>/dev/null || true; }
```
11. A stream event complaining about "skills context budget" is benign Codex housekeeping, not a failure.

## Review calls (Same Page Meeting, read-only)

Fresh session:

```bash
RUN=$(mktemp -d /tmp/rf.XXXXXX)
# write the review prompt to "$RUN/prompt-r1.md" first
snap r1
codex exec -s read-only --skip-git-repo-check --json -o "$RUN/out-r1.txt" \
  - <"$RUN/prompt-r1.md" > "$RUN/stream-r1.jsonl" 2>/dev/null
```

After it exits, extract the thread id from the stream file and echo it visibly:

```bash
THREAD_ID=$(grep -m1 '"type":"thread.started"' "$RUN/stream-r1.jsonl" \
  | sed 's/.*"thread_id":"\([^"]*\)".*/\1/')
```

Resume the SAME session for later rounds. THE SAFETY LINE: `resume` rejects `-s`; without `-c sandbox_mode="read-only"` Codex inherits the config default and can WRITE files mid-review.

```bash
snap rN
codex exec resume "$THREAD_ID" -c sandbox_mode="read-only" --skip-git-repo-check --json \
  -o "$RUN/out-rN.txt" - <"$RUN/prompt-rN.md" > "$RUN/stream-rN.jsonl" 2>/dev/null
```

Then Read the round's `-o` file and grep its last line for `VERDICT:`.

## Build calls (rock execution, sandboxed write)

Gate first, in this order:

1. No git repo yet (fresh kickoff): `git init`, then commit ONLY this run's artifacts. Never sweep unrelated pre-existing files into the baseline: they may be secrets or junk. If any exist, list them and ask the user once (commit, stash, or ignore; "ignore" means writing the paths into `.gitignore` and committing it, so the gate actually reads clean).
2. Commit the planning artifacts (plan, VTO, log, issues) before the first build. These baseline commits are part of the machinery: announce them in one line, do not ask. Only CODE commits (rock results) are user-gated. The gate is not "nothing changed", it is "everything is baselined": `git status --porcelain` must be empty when Codex launches, so the build diff is exactly Codex's work and nothing else.
3. Pre-existing dirty files that are not this run's artifacts: stop and ask the user to commit or stash them.

Default build mode is Codex's OWN sandbox with write access to the workspace. Do NOT reach for `--yolo` / `--dangerously-bypass-approvals-and-sandbox` by default: sandboxed mode builds real features, and the bypass flags run an unsandboxed agent, which needs the user's explicit per-run approval.

```bash
snap build   # pre-build.txt must be empty (everything baselined)
codex exec --sandbox workspace-write --full-auto --skip-git-repo-check --json \
  -o "$RUN/build-out.txt" - <"$RUN/contract.md" > "$RUN/stream-build.jsonl" 2>/dev/null
BUILD_THREAD=$(grep -m1 '"type":"thread.started"' "$RUN/stream-build.jsonl" \
  | sed 's/.*"thread_id":"\([^"]*\)".*/\1/')   # fix rounds resume THIS id; echo it visibly
```

If the rock needs network (installing deps), add `-c sandbox_workspace_write.network_access=true` and say so in one line before running. Fix rounds resume the same session with the sandbox forced via `-c`:

```bash
snap fixN
codex exec resume "$BUILD_THREAD" -c sandbox_mode="workspace-write" --skip-git-repo-check --json \
  -o "$RUN/fix-outN.txt" - <"$RUN/fixN.md" > "$RUN/stream-fixN.jsonl" 2>/dev/null
```

## The build contract template

```
GOAL: <one paragraph: what done looks like for THIS rock>
SPEC: Read <actual plan file path>, rock <N>. It is frozen and already
  reviewed. Implement it exactly. If a detail is impossible as written but the
  intent is unambiguous, implement the closest faithful version and report the
  deviation. If the impossibility is MATERIAL (would change behavior, scope, or
  an interface), do not improvise: stop, output `BLOCKED: <reason>` as your
  report, and wait. Do not redesign.
KEY PATHS: <files/dirs to touch, files to read first>
CONSTRAINTS: <do-not-touch list, style rules, deps that must not change>
NON-GOALS: <explicitly out of scope, including every other rock>
PROOF: Run `<PROOF_CMD>` and include its full output in your report.
OUTPUT: End with a report: files changed (one line each: path + what/why),
  the proof output, and any deviations from the spec with reasons.
```

## Level 10 review mechanics (after every build call)

1. `git diff --stat` first. If the diff is large (over ~400 changed lines), review file by file in `--stat` order, skipping lockfiles and generated/vendor output, but always read every hand-written source change in full. Codex's report is a claim, not evidence.
2. Run `PROOF_CMD` yourself. Only your run counts.
3. Findings within the rock's scope: send ONE consolidated fix-round prompt (resume, same session): "Fix these N items, nothing else, re-run the proof." Max 2 fix rounds per rock.
4. Still broken after round 2: the Visionary takes the wheel. Announce it, fix it yourself, note it in the close-out scorecard.
5. Deviations Codex reported: judge each against the Core Focus. Execution-detail deviations stand (the Integrator is the Tie Breaker). Vision or scope deviations get reverted in a fix round, with the reason logged.
6. Commits: user-gated, authored by the driving agent, conventional format. Codex never commits.

## Failure handling

**A call succeeded only if ALL of:** exit code 0, the round's `-o` file exists and is non-empty, and (for meeting rounds) its last line greps a `VERDICT:`. Anything less is a failure, even if the stream showed `thread.started`. Never read a verdict from a file the current round did not freshly write.

- Fresh call fails or times out (no thread id captured): retry ONCE with a fresh session and a new round filename. Do not "resume" a thread that never started.
- Resume call fails or times out: retry ONCE with the same explicit thread id and a new round filename. Second failure: fall back to a fresh session carrying a one-paragraph summary of the meeting so far, and SAY SO to the user in one line (session continuity broke; the round count continues, the new session cannot verify its own prior findings).
- Still failing: stop and surface the error (rerun the identical command WITHOUT `2>/dev/null` to capture stderr). Never silently continue without the review.
- Auth errors: tell the user to run `codex login`. Broken install (`spawn ... ENOENT`): `npm i -g @openai/codex@latest`.
- Prerequisite floor: Codex CLI >= 0.130; contract verified on 0.143.0.
