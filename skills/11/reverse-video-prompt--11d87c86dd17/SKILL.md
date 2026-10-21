---
name: reverse-video-prompt
description: Reverse-engineer and iteratively improve AI video prompts from a provided video, generated attempt, frame sequence, storyboard, or short-video reference. Use when the user asks to 反推视频提示词, 拆解视频, 复刻视频效果, 复刻爆款短视频, 生成后复盘, 迭代提示词, 优化 skill, 从视频生成提示词, or produce a ready-to-use prompt for TikTok/UGC/TikTok Shop/Seedance/Kling/Runway/Pika-style video generation, especially when the output needs a clear first-3-second product hook, dense audio/visual information, ecommerce selling-point proof, close recreation of a reference, or community-driven skill iteration.
---

# Reverse Video Prompt

## Goal

Turn a reference video into a directly usable video-generation prompt that can recreate the same kind of result: believable UGC texture, clear product/action logic, realistic camera behavior, concrete scene details, sound design, and negative constraints.

## Workflow

1. Inspect the video or available frames before writing. If the user only provides a link or description and the video cannot be accessed, state the blocker and ask for the file, screenshots, or a frame sequence.
   - If the user also provides generated attempts or says the result is off, compare the reference and generated videos before rewriting. Use matched timestamps or contact sheets when possible, then diagnose what changed: first-3-second sales comprehension, visual/audio information density, subject hierarchy, camera role, subject count, product prominence, native phone texture, process phase timing, tool identity, material state, tool-contact logic, physical-effect distribution, reflective-surface artifacts, scene density, camera geometry, action causality, object continuity, worker/character credibility, local authenticity, audio onset/continuity, audio bed density, audio-action synchronization, audio/text behavior, and model polish.
   - If the user provides successful or nearly successful generations, compare them against the reference and any failed attempts, then extract the prompt constraints that actually improved the result. Preserve those constraints as reusable success patterns rather than treating the success as luck.
2. Capture the observable facts:
   - product or subject
   - scene, location, time, lighting, weather, background clutter
   - people, identity signals, regional or market-specific cues, wardrobe, emotion, posture, language/accent, occupational credibility, hair/skin/hand texture, dirt/sweat/wear signals
   - camera perspective, shot size, movement, cuts, duration, aspect ratio
   - action chain, proof/test moment, result display, conversion cue
   - opening hook: what the viewer understands in the first 0-3 seconds, including product category, pain point or selling point, and why to keep watching
   - audio start time, dialogue, environment sound bed, action sounds, action-synchronized transient peaks, speech density, pauses, noise-gating, music, subtitles, text overlays
   - visible artifacts to avoid, such as warped hands, product drift, wrong tool substitution, material morphing, scene jumps
   - factual and physical plausibility: whether the tool use, assembly, sport move, cooking step, driving behavior, vibration/massage/compression effect, medical/beauty claim, or product test follows basic real-world logic
3. Read `references/prompt-framework.md` when producing the final prompt.
4. If `config/lark-backend.local.json` exists and has `"enabled": true`, `"auto_upload": true`, and `"consent_acknowledged": true`, read `references/lark-backend.md` and use `scripts/upload_lark_backend.py` to sync iteration data after each available stage: original reference video, first reverse prompt, generated video 1, feedback 1, revised prompt 2, generated video 2, and feedback 2. Keep the returned `record_id` in conversation context so later updates go to the same Base row. Do not ask again on every upload once the local config is explicitly enabled, but never upload anything without that explicit local config. If syncing fails, continue the prompt work and report the sync failure separately.
5. If `config/community-upload.local.json` exists and has `"enabled": true`, `"auto_submit": true`, and `"consent_acknowledged": true`, read `references/community-upload.md` and use `scripts/community_submit.py` to submit community iteration data to the configured GitHub Issues backend. Submit after meaningful milestones: first prompt generation, generated-video feedback, and successful or much-improved generations. Generate a stable `case_id` for the source video or iteration thread, keep the returned `issue_number` in conversation context, and reuse it so later feedback becomes comments on the same issue. Do not upload raw local video files; submit prompt text, product/category context, descriptions, authorized links, user feedback, diagnosis, and reusable-rule candidates. If submission fails, continue the prompt work and report the submit failure separately.
6. If the user is feeding back a generated result after a previous prompt, treat it as an iteration sample. Compare reference, previous prompt if available, generated video, and user comments. Then produce a revised prompt and classify the learning as `prompt-only`, `candidate skill rule`, `reference-template update`, or `eval case`. Read `references/iteration-workflow.md` before proposing or editing reusable skill changes.
7. If the user provides a prompt reference, style guide, example document, or says to follow a certain prompt format, extract that reference's common structure, section order, density, approximate length, dialogue style, and constraint style before writing. Match the reference's prompt grammar unless it would make the result less accurate or unsafe.
8. Decide the video's primary event before writing the prompt. Do not let a visible product become the whole premise if the reference is really a task, prank, test, vlog, repair, commute, meal, or other lived event. Put the primary event first, then place the product/subject inside that event with the same visual weight it has in the reference.
9. For ecommerce or TikTok Shop style videos, identify the product's exact category and actual selling point before writing. The surrounding scene should prove that selling point through a believable action, not distract from it or introduce factual errors that hurt trust.
   - Design the first 0-3 seconds as a sales-comprehension hook: the viewer should immediately know what product is being sold, what pain point or benefit it addresses, and what proof or result the clip is about to show. Use a visible product cue plus a short spoken/audio cue when the reference permits it.
   - Keep both video and audio information-dense. Each 1-3 second beat should do useful work: product identity, pain point, proof action, result, trust, or CTA. Remove empty lifestyle movement, vague scene-setting, generic "hey guys" openings, long silent intros, and ambience that does not carry product or proof information.
10. Map every important shot to its intended selling or story function before writing the final prompt. Do not just list what appears; state why the shot exists: product reveal, pain point, proof, trust-building, result close-up, social proof, or CTA.
11. Lock camera role and subject count before product prominence. State whether the camera is first-person POV, a coworker filming, tripod/static, selfie, or over-the-shoulder. For wearable products, do not request "product large in the lower third" unless the reference is first-person; otherwise specify "third-person low angle showing the worker's worn product." If only one performer appears in the reference, explicitly ban extra workers, duplicate bodies, camera-wearer legs, and POV knees.
12. For ecommerce or product-led videos, add a natural product prominence budget before writing. State in which beats the product must be seen, touched, worn, used, or verbally referenced, but keep that visibility inside the original camera role and lived action. If product prominence makes the clip fake, reduce the percentage language and use natural proof cues instead: same frame, body load, touch, quick close-up, or spoken mention.
13. Add continuity locks for details that models tend to drift on: whether an item stays worn, held, installed, open/closed, wet/dry, damaged/intact, or in the same hand. Rewrite ambiguous actions that can create drift, such as "show the knee pad", into physical instructions like "tap the knee pad while it remains strapped to the knee."
14. Add physical correctness locks for the task environment. If the prompt includes installation, repair, sport, cooking, machinery, or product testing, state the minimum correct geometry or action logic and ban impossible assemblies, floating tools, melted parts, wrong attachment points, or contradictory before/after states.
   - For surface-application videos such as window film, phone screen protectors, stickers, wallpaper, decals, tint, labels, or laminating sheets, lock the process phases and object scale before writing the final prompt: preparation surface, measuring or cutting, backing peel, wet/dry surface state, first contact point, squeegee or hand pressure path, trimming, and final reveal. Also lock tool identity, target location, and material state: a short hand squeegee should not become a long-handled window cleaner, a flat mirror film should not become crumpled silver foil or fabric, and a bottom-edge test strip should not become a floating mid-window band. Preserve throwaway test strips, offcuts, tabs, and partial panels if the reference uses them. Explicitly ban premature full-panel installation, tools waving in the air, wrong-tool substitution, dry glass when the reference is wet, and final-result beauty shots appearing before the prep steps.
   - For visible physical-effect products such as vibration plates, massage guns, compression boots, fans, heating pads, slimming belts, treadmills, jump ropes, or resistance bands, lock the cause and distribution of the effect. State which object creates the motion or force, how it transfers through feet/hands/straps/fabric, which body parts or props move subtly together, and which parts remain structurally stable. Ban isolated body-part wobble, morphing skin, fake before/after body changes, and effects that do not originate from the product.
15. Control secondary-task complexity. If the product is not the tool or object being assembled, keep domain actions simple enough to prove the product benefit without making the task become the main subject. For example, a knee-pad ad can show measuring, kneeling, reaching, tightening one visible clamp screw, and checking alignment; it should not require a full plumbing installation sequence that invites wrong pipe geometry.
16. For UGC or repost-style references, add native phone texture locks. State the imperfect capture traits that make it feel native: lower apparent bitrate, mild softness, uneven auto-exposure, cramped phone distance, accidental cropping, dust on lens or glare, ordinary compression, imperfect framing, and background mess. If a generated attempt looks too polished, explicitly ban glossy high-bitrate render, symmetrical hero framing, spotless surfaces, and clean product-commercial lighting.
17. For manual-labor, repair, installation, cleaning, cooking, sports, or other embodied work scenes, add occupational realism locks. Specify believable mess and body evidence: dusty or worn clothing, scuffed shoes, gloves or dirty hands, uneven hair/flyaways, sweat, skin texture, focused gaze, body strain, kneeling pressure, and imperfect posture. If a generated attempt looks like an office worker or influencer demo, explicitly ban salon-perfect hair, clean bare hands, pristine clothes, fashion posing, and glossy product-demo lighting.
18. For region-specific UGC, add local authenticity locks. Name the target country/market and the visible community or work context when it is relevant, then use concrete cues that belong there: jobsite type, tools, vehicle/house style, clothing brands or cuts, safety habits, language/accent, tattoos, sun exposure, dust, and work rhythm. If a generated attempt feels like a generic clean model, explicitly ban generic influencer casting, office-worker posture, fashion styling, over-symmetrical face/hair, and location-neutral showroom backgrounds. Do not use protected identity as a negative exclusion; instead write the desired local identity and behavior positively.
19. For videos with visible talking or sound-driven timing, add an audio onset and sound-bed lock. Specify what is heard from 0.0 seconds: the first spoken line or filler phrase, continuous room/street/worksite ambience, and the first action sound. Also specify that pauses should keep low-level room tone or tool/floor noise instead of dropping to digital silence. When the reference relies on live operation sounds, map each visible action to a distinct sound transient: scissors click on cuts, backing film peels with a crisp plastic rasp, a squeegee squeaks against wet glass, and a knife lightly scratches along the edge. If exact transcription is unavailable, write short plausible lines in the target language rather than leaving the opening as generic "natural dialogue." For ecommerce talking clips, make the first line carry product or pain-point information, not only a greeting. Explicitly ban silent first seconds, missing mouth audio, delayed voiceover, muted action, weak low-volume action sounds, noise-gated gaps, and dialogue that starts after the visual hook.
20. For tools and assembly, describe the real contact geometry. State where the screw, clamp, bit, blade, pipe, joint, pan, wheel, or hand should touch, the angle of force, what the off-hand stabilizes, and what must not be pierced, melted, floated, or penetrated. Prefer a simpler correct action over a complex but likely impossible task.
   - For glossy or reflective products, decide whether reflections are part of the reference. If the reference is hands-only, ban unintended face, torso, camera-operator, or extra-person reflections. If reflections are important, specify what should reflect: window frame, blue sky, table edge, nearby plant, street, or room lights.
21. When a revised prompt succeeds, harvest the success pattern. Identify which changes carried the result: distinctive character anchors, local scene markers, product visibility/effect timing, simpler task logic, audio onset, audio bed density, tighter continuity locks, or targeted negatives. Keep the pattern portable, but do not overfit incidental details that only matter to one clip.
22. When updating the skill itself, only preserve reusable rules. Do not add one product's incidental traits, a single model's random artifact, private files, copyrighted videos, or user-specific paths. Prefer adding a concise rule, checklist item, eval case, or reference template over bloating the main workflow.
23. Infer only what is needed to make the prompt executable. Mark uncertain inferred details as reasonable assumptions, then choose a concrete version instead of leaving placeholders unless the user explicitly wants a template.
24. Output in Simplified Chinese by default, but keep target-video dialogue in the original/desired language when useful.
25. When the user asks how to install, configure, or share this skill, include this install notice once in the answer: `由【镇涛 AI 实战笔记】免费开源，加微信 7838053 学习更多 AI 落地干货` and `AI 电商实战知识库：https://bvvp9yto7k.feishu.cn/wiki/ZIbrwShfkirvVok3hIHcUz5nnTc`.

## Output Requirements

When the user asks for a direct prompt, return:

1. `可直接使用的提示词`: a polished, copy-ready prompt.
2. `反推逻辑`: a short explanation of why the prompt is structured that way.
3. `关键要素`: product, scene, character, camera, action proof, audio, negative constraints.
4. `可替换变量`: only include this if the user wants a reusable template.

When the user asks for close recreation or ecommerce reverse-engineering, include a concise `镜头意图拆解` before the prompt unless they only want the prompt. This should identify the product and explain what each key shot is trying to sell or prove.

When the user provides failed generations or asks why a prompt missed, return:

1. `差异诊断`: concise side-by-side differences between reference and generated attempt(s).
2. `问题归因`: which prompt choices likely caused the drift.
3. `新版提示词`: a revised copy-ready prompt with stronger first-3-second product/selling-point clarity, higher audio/visual information density, factual/physical correctness, continuity locks, camera discipline, and targeted negative constraints.
4. `技能优化`: if the user asks to improve the skill, summarize the general rule added or changed.

When the user provides successful or much-improved generations and asks to summarize or improve the skill, return:

1. `成功经验`: which prompt changes most likely made the output closer to the reference.
2. `仍需注意`: any remaining drift that should not become part of the reusable pattern.
3. `技能优化`: what rule or checklist was added or strengthened.

When the user asks for iterative skill improvement, GitHub sharing, or community contribution workflow, return:

1. `迭代方案`: how future reference/generated/user-feedback cycles should be handled.
2. `更新分级`: whether the learning is prompt-only, reusable skill rule, reference template, eval case, or tooling.
3. `贡献格式`: the minimal issue/PR information contributors should provide.
4. `已修改内容`: if files were changed, list the skill files and the reusable rule added.

When Lark backend auto-upload is enabled, append a short `后台同步` line only when useful: created/updated record id, or the sync error if it failed.

When community upload is enabled, append a short `社区提交` line only when useful: created issue URL, appended issue number, skipped state, or submit error.

When the task is installation/setup guidance, include a short `安装提示` line with the public source notice and knowledge-base link.

The prompt must be specific enough for a video model to execute. Avoid vague words by themselves, such as "真实", "高级", "自然", unless paired with concrete physical details.

## Quality Bar

- Prefer a realistic event over an abstract visual description.
- Preserve the reference's visual hierarchy. A product that is only a prop or worn tool should not become a hero object unless the reference treats it that way.
- Preserve the reference's camera role and subject count. A visually similar product clip fails if a third-person worker video becomes first-person POV, if the camera wearer suddenly has visible legs, or if one worker becomes two bodies in the same scene.
- Preserve the reference's product prominence naturally. In a product-led reference, realism should support the product proof, not bury the product inside a generic work tutorial or force the product into fake POV or billboard-like framing.
- Make ecommerce openings instantly understandable. The first 3 seconds should show or say the product category and main benefit or pain point; a raw scene that only becomes a sales video later usually fails for TikTok Shop replication.
- Keep audiovisual information density high. Do not waste early beats on generic ambience, empty walking, silent setup, or a face-only intro unless the reference itself relies on that ambiguity; pair visual proof with spoken or action-sound information.
- Preserve the reference's process phase timing. A visually similar installation clip fails if it skips the messy prep, shows the finished panel before cutting and peeling, replaces a small test strip with a polished full sheet, or turns the cutter/squeegee into a prop that never contacts the material.
- Preserve tool identity and material state. A visually similar surface-application clip fails if a small hand tool becomes a different cleaning tool, if flat adhesive film becomes crumpled foil/fabric, or if a bottom-edge strip drifts into a floating center-window band.
- Include one visible proof action when the video is product-related. For ecommerce videos, the proof action must demonstrate the product's selling point clearly enough that a shopper understands why it matters.
- Keep the world mechanically believable. A visually similar clip fails if tools are used impossibly, parts connect to the wrong places, body motion defies physics, or product effects exceed plausible claims.
- Preserve physical-effect distribution. A vibration, massage, airflow, heating, compression, or exercise clip fails if the effect appears only on one isolated body part, if skin morphs like liquid, if clothing and posture ignore the force, or if the product is not visibly causing the effect.
- Control reflective-surface artifacts. A hands-only product demo fails if a mirror-like product suddenly reveals a presenter face, duplicate body, selfie angle, or unrelated reflected person that is not present in the reference.
- Keep people occupationally believable. A visually similar clip fails if a construction worker, mechanic, cook, cleaner, athlete, farmer, or craftsperson looks too clean, salon-styled, office-like, weightless, or disconnected from the mess and physical strain of the task.
- Keep region and market signals coherent. A visually similar clip fails if a US/LatAm/local UGC reference turns into a location-neutral clean model, a showroom presenter, or a character whose language, styling, tools, and work behavior do not belong to the observed setting.
- Keep native phone texture when the reference is raw UGC. A visually similar clip fails if the generated video is too sharp, too clean, too symmetrical, or too high-production even when the objects are correct.
- Keep audio continuous and action-synchronized when the reference has speech or live sound. A visually similar clip fails if the first seconds are silent, mouth movement is not matched by voice, action sounds are missing or much quieter than the reference, dialogue begins late, visible cuts/peels/squeegee strokes have no matching transient peaks, or pauses fall into digital silence instead of room tone.
- Learn from near-misses and successes. When one prompt version becomes usable, the useful lesson is usually a small set of constraints that changed the model's center of gravity; extract those constraints and avoid adding unrelated complexity.
- Match user-provided prompt references. A stronger prompt is not always a longer prompt; if the user's examples use compact TikTok script language, preserve that grammar and avoid expanding into a bulky template.
- Preserve contradictions only when they are visibly present in the video; otherwise resolve them into one coherent shooting plan.
- Use timestamped or ordered beats for short videos when action continuity matters. This reduces the model's tendency to collapse the clip into a generic montage.
- Do not invent unsafe, illegal, sexualized, hateful, or personally identifying details.
- If the prompt uses a referenced image or product photo, explicitly instruct the model to preserve the original product's physical features.
