# Rules: vlsit-opencore-ip-downloader

Authority: this file is the highest-priority source for the skill. Every rule below is mandatory. `SKILL.md` defines the workflow that satisfies these rules; `references/` holds supporting information and examples that rank below this file. If any other file conflicts with a rule here, follow the rule and report the conflict.

Keywords: MUST and MUST NOT admit no waiver. SHOULD is followed by default and may be deviated from only with a stated reason in the final report.

## A. General

- OCI-001 (MUST): Write all skill output (plans, reports, manifests, script messages, code comments) in precise scientific and engineering English, and distinguish observed results from assumptions. Bilingual English–Vietnamese content is allowed only in README files and documents explicitly designated as user guidelines.
- OCI-002 (MUST): Use the skill only to find and collect existing IP. Do not design a new core.

## B. Required information

- OCI-010 (MUST): Before any download, the request MUST establish (1) the IP type and intended function, standard, or use case, (2) the number of distinct implementations wanted, and (3) the absolute destination folder.
- OCI-011 (MUST): Ask for all missing items in one message and wait for the answer before downloading.
- OCI-012 (MUST NOT): Infer the destination from the current directory, the skill location, or an unrelated earlier task.
- OCI-013 (MUST): Treat a user-supplied count as a target. Report when fewer suitable projects exist. Never invent projects or count mirrors, forks, or repackagings of one upstream project as separate IPs.

## C. Selection and licensing

- OCI-020 (MUST): Use OpenCores as the primary catalog and prefer its official download or the linked upstream repository. Other public repositories MAY be searched only to find more distinct candidates, and those results MUST be labeled external to OpenCores.
- OCI-021 (MUST): Confirm from the project description and the available source or documentation that each candidate implements the requested function. Exclude software-only projects.
- OCI-022 (MUST): Count a project as open source only when its RTL/source is public under a clearly identified open-source license. Preserve the license text and link. A project with a missing or unclear license MUST NOT be counted or called open source; it MAY be listed separately as an unconfirmed candidate.
- OCI-023 (MUST NOT): Download proprietary or access-restricted material.
- OCI-024 (SHOULD): Prefer synthesizable RTL with useful documentation, test collateral, and a clear license.

## D. Download

- OCI-030 (MUST): Download the full project archive or repository snapshot for each selected IP, preserving the upstream directory structure and including all available RTL, packages, file lists, documentation, license notices, testbenches and vectors, build/synthesis scripts, constraints, examples, drivers, project metadata, and declared dependencies.
- OCI-031 (MUST): Follow only links that belong to the selected project's distribution. Do not treat unrelated site pages, external references, or a whole hosting account as project collateral.
- OCI-032 (MUST NOT): Execute downloaded code. Do not run simulation, lint, synthesis, or other tests unless the user asks.

## E. Storage and provenance

- OCI-040 (MUST): Create a separate, descriptively named subfolder per project inside the destination. Check existing files first and never silently overwrite user data. On a name collision choose a new name or ask.
- OCI-041 (SHOULD): Keep the original archive beside its extracted tree. For a repository snapshot, record the exact revision or commit.
- OCI-042 (MUST): Write `DOWNLOAD_INFO.md` in each project folder with the project name, catalog and upstream URLs, download date, revision or archive name, license and license URL, SHA-256 of the archive when available, and unavailable or excluded materials.
- OCI-043 (MUST): Add or update a destination-level `CATALOG.md` listing each selected project with its source, license, and brief description. Preserve existing catalog content and unrelated files.

## F. Evaluation README

- OCI-050 (MUST): Add or update `README.md` in the destination, written in English and Vietnamese with consistent technical content. Extend an existing README and preserve unrelated content.
- OCI-051 (MUST): Base every statement on evidence (project README, status notes, changelog, documentation, downloaded source tree). Public information outside the download MAY be used when named as such. State that the assessment is document-based and never present it as measured or verified.
- OCI-052 (MUST): Include a side-by-side comparison covering, per IP: Features, Functions, Status, FPGA capability, and ASIC (tapeout) capability, each as defined in `references/readme_template.md`.
- OCI-053 (MUST): Under Status, quote self-reported caveats (for example "little testing done"). Under FPGA capability, separate "has run" (documented), "has FPGA project files but no reported result", and "no evidence found", and state vendor-primitive portability limits.
- OCI-054 (MUST): Rate ASIC capability on this scale and reproduce the legend in the README:

  | Level | Meaning |
  |---|---|
  | A | Evidence of tapeout or working silicon |
  | B | Technology-independent, reasonably complete RTL that can enter an ASIC flow directly; no silicon evidence found |
  | C | Usable for ASIC only after significant work (verification, PHY/IO, dependencies, missing features) |
  | D | Not suitable for ASIC without a rewrite (FPGA-bound, non-functional, or not RTL) |

- OCI-055 (MUST): Give A only when the evidence concerns this IP. If the evidence applies to an earlier version, a shuttle submission without measured results, or a larger chip containing the block, state that condition. Do not accept "silicon proven" wording when the cited proof is FPGA hardware. Absence of evidence is "no evidence found", not "does not work".
- OCI-056 (MUST): After the table give a short justification of the ratings per IP and a brief selection guide by use case.
- OCI-057 (MUST): End with a **Special notes** section whenever anything applies (license obligations or conflicts, required analog PHY or hard macros, vendor primitives and missing dependencies, missing testbench or documentation and known bugs, download caveats). Omit it only when nothing applies, and do not pad it.

## G. Integrity check and report

- OCI-060 (MUST): Confirm each download completed and that the archive passes its integrity check or listing before extraction. Inspect member paths for unsafe traversal before extracting. Record the SHA-256 when practical. Confirm the extracted tree contains the expected source, documentation, and license files, and report omissions accurately. These are download-integrity checks, not RTL validation.
- OCI-061 (MUST): The final report states the requested count, the number of distinct licensed projects found and downloaded, and the destination. For each project it gives name, source link, license, main materials, and FPGA and ASIC ratings. It points to the README, repeats its key special notes, and identifies external results, missing collateral, unclear licenses, and failed downloads.
- OCI-062 (MUST NOT): Claim the RTL works, synthesizes, or passes tests unless that work was requested and performed.

## H. Self-improvement

- OCI-090 (MUST): When a deterministic, repeatable operation is needed or performed manually a second time, or the model judges it will recur across runs, create a script for it in `scripts/` unless an equivalent script exists. Each script needs a header docstring (purpose, usage, inputs, outputs, exit codes), English messages, Python 3 with only the standard library (a third-party package or another language needs explicit user approval), and no network access or file writes outside user-approved paths.
- OCI-091 (MUST): Test a new script on a real input before registering it. If it cannot be run in the current environment, register it as untested and say so in the report. Register every script in `scripts/README.md` (name, purpose, status).
- OCI-092 (MUST): A script MUST NOT violate any rule in this file (for example, it MUST NOT execute downloaded code, OCI-032).
- OCI-093 (MUST): After completing a task, the model SHOULD record friction it observed (repeated clarification, wrong assumption, missing reference, slow manual step) and MAY improve `SKILL.md`, `references/`, and `scripts/` to remove it. Each change is logged in `references/improvement_log.md` (date, reason, change) and mentioned in the final report.
- OCI-094 (MUST NOT): Edit this file, weaken a rule, or add a waiver without explicit user approval. The model MAY propose new or revised rules at the end of a run, and the user decides.
- OCI-095 (MUST): Keep `SKILL.md` concise. Move bulk detail, templates, and examples to `references/`.
- OCI-096 (MUST): Before the first script call of a run, check that Python 3 is available (`python --version`; on Windows the Microsoft Store shortcut that prints an installation hint does not count). If it is missing, tell the user, propose installing it (for example `winget install Python.Python.3.12` on Windows) and wait for approval before installing anything. Without Python the work may continue by hand and the report MUST say which scripted checks did not run.
