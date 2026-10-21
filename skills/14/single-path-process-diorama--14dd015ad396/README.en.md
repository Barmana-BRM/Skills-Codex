# Single-path process diorama

[简体中文](README.md) | [English](README.en.md)

**v0.1.1-rc.1 · Experimental candidate.** Turn a 3–5-step linear process into one integrated miniature world. Follow a road, work surface, or other continuous spatial cue to see an object change through distinct actions. This is neither a panel comic nor an exact engineering diagram.

## Three inspected examples

### Code delivery — five steps

Submission → automated testing → human review → packaging → deployment.

![Code delivery](assets/examples/code.png)

White modules with a red triangle identify the carrier across stages. Packaging adds a transparent case. A separate production edit repaired the review-table track; that edit was not retroactively counted in the original comparison. This is a software metaphor, not a working machine.

### Coffee — four steps

Roasting green beans → grinding → pour-over extraction → serving.

![Coffee preparation](assets/examples/coffee.png)

Beans, grounds, and liquid have different visible states. Grinder output and water/container relationships were inspected. Intermediate transport and the full industrial process are intentionally outside this simplified main line.

### Parcel delivery — three steps

Packing → transport → handoff.

![Parcel delivery](assets/examples/parcel.png)

Blue diagonal tape helps connect the boxes. The initial cycling direction was repaired. Tape placement is not pixel-locked, and loading or parking are not separate illustrated stages.

## Use

Provide the process, aspect ratio, material direction, and lettering preference. The default is one 3:4 image, with at most two targeted revisions. Generate the whole scene together; do not generate each stage separately and stitch them.

> Use $single-path-process-diorama to turn “topic → draft → edit → publish” into one 3:4 paper-and-wood miniature newsroom. Preserve manuscript identity, avoid panels, and use only short station signs if needed. Inspect the finished sequence, actions, and lettering before delivery.

This prompt is a suggested input, not a fourth completed example. More than five mandatory independent steps, or complete branches and loops, require an explicit scope choice rather than silently dropped steps.

For first installation into a destination that does not already exist:

```sh
git clone https://github.com/ZSeven-W/craft-skills.git craft-skills-diorama
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R craft-skills-diorama/skills/single-path-process-diorama "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Back up an existing installation first. The default branch includes this experimental candidate. Alternatively, provide this directory to an assistant and ask it to read SKILL.md without installing it.

## Requirements and delivery

Requires a file-reading assistant, actual image generation, visual inspection, and Python 3.10+ for the standard-library file verifier. Only built-in imagegen generation/editing was exercised. Other models and automatic loading in other clients remain untested. No Midjourney account, proprietary style code, model weights, API credentials, or generation credits are included.

If generation is unavailable, report a prompt-only handoff, not a finished image. If visual inspection or an independent reviewer is unavailable, explicitly distinguish unverified output or self-review from independent acceptance.

Deliver `final.png`, actual `prompt.md`, short `scene-contract.md`, and final-hash-bound `qa.md`. Present the image and a short explanation first. Review both visual coherence and process fidelity at original size and thumbnail size.

```sh
python3 scripts/verify_delivery.py /path/to/outputs --ratio 3:4 --require-all-docs
python3 scripts/verify_delivery.py /path/to/outputs --ratio 3:4 --require-all-docs --review /path/to/review.json
python3 -B -m unittest discover -s tests -p 'test_verify_delivery.py'
```

The optional review JSON has a top-level `reviewed_image_sha256` string. The verifier checks PNG structure/CRC/decompression, ratio, nonempty documents, and hash binding; it does not prove visual quality, semantics, rights, or the truth of QA prose. The 44 unit tests test that shared tool, not image quality. Only `--manifest` writes a report file.

## Evidence and limits

The original three paired image tests yielded two Skill wins and a tie; assertions were 21/21 versus 20/21. One pair per subject is not a success rate or a human study. A failed network edit and separate production repair are recorded rather than counted as successful comparative trials.

This revision's three pre-generation boundary tests compared old and new Skill versions, with no new images. The new version scored 12/12 and the old version 11/12, but the sole disputed criterion concerns whether an extra-wide eight-stage proposal counts as an acceptable alternative. A reasonable alternative interpretation could yield a tie. Do not claim broad improvement from it.

Raw trials and research logs are kept outside this repository. [Validation summary](evals/VALIDATION.md) and [source hashes](evals/sample-origins.json) document their scope; these summaries are not a standalone certification. Bundled routing cases include additional unexecuted checks and must not be presented as completed image trials.

Not suitable for exact branching logic, synchronization, numerical scales, operating procedures, scientific data reconstruction, or pixel-exact identity. File success never replaces looking at the image. The separate cover illustration is not a fourth validated process example.

## License

[Apache-2.0](LICENSE) applies within the project's licensable rights; see [asset scope](ASSET-LICENSE.md). The examples are original AI-generated fictional demonstrations, not private character assets or downloaded source material. No third-party trademark rights or exclusivity are promised. Saving, installing, pushing, merging, and publishing are separate actions.
