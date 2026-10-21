# 视频提示词反推框架

Use this reference after observing the video. The output should feel like a production-ready prompt, not a commentary transcript.

## Core Formula

高质量 AI 视频提示词 =
真实拍摄约束 + 原生手机质感 + 拍摄关系/主体数量 + 可信人物 + 职业身体痕迹 + 本地化场景 + 产品物理细节 + 前 3 秒卖点钩子 + 自然产品显著性 + 画面信息密度 + 流程阶段锁 + 工具/材料身份锁 + 物理效果分布锁 + 可验证动作 + 结果展示 + 0 秒起始口播/声音 + 口播/音频信息密度 + 连续现场声床 + 动作同步音频峰值 + 明确禁用项。

高质量电商带货视频提示词 =
产品卖点 + 前 3 秒产品识别/卖点钩子 + 可信使用场景 + 符合物理/事实的证明动作 + 真实反应/结果 + 购买暗示 + 反扭曲约束。

The guiding question:

如果这是真人拿手机拍，现场到底应该有什么人、什么光、什么声音、什么杂物、什么动作，以及产品如何在镜头里证明自己？

For product-led videos, also ask:

产品在第几秒、哪个画面区域、以多大比例被看见？观众是否在前 3 秒知道卖的是什么，并且在中段证明动作里持续看到产品承担作用？

If the clip is ecommerce, also ask:

如果只看前 3 秒、只听前 3 秒，观众是否已经知道：卖的是什么产品、解决什么痛点、为什么值得继续看？如果答案是否定的，提示词需要把开场改成“产品身份 + 痛点/卖点 + 证明动作开端”的压缩信息包，而不是只写人物、场景或氛围。

Before product prominence, also ask:

到底是谁在拍谁？画面是第一人称、同事手机拍、自拍、固定机位，还是过肩视角？如果参考只有一个人，提示词不能让模型生成“拍摄者自己的腿 + 另一个工人”这种双主体混合视角。

For embodied work scenes, also ask:

这个人看起来真的在干这份活吗？头发、脸、手、手套、衣服、鞋、膝盖、姿势、呼吸和发力方式，有没有被现场的灰尘、汗、碎屑、油污、水汽、热度或重量影响？

For region-specific UGC, also ask:

这个人、说话方式、穿着、工具、工地/街道/室内背景，是否像目标市场里真实存在的人和现场？还是变成了没有地区感的干净模特？

For talking videos, also ask:

参考视频从第 0 秒开始听到什么？如果开场有人说话或有动作声，提示词必须锁定 0.0 秒就开始有声音，不能让模型默认静音开场。

For native UGC texture, also ask:

参考片是手机现场拍到的生活/工地/街头声音和画面，还是干净的生成广告？生成片是否太高清、太稳、太亮、太干净，声音是否像被噪声门切过？

For physical-effect products, also ask:

产品到底制造了什么物理效果？震动、按摩、风、热、压缩、拉力或运动阻力从哪里传到哪里？哪些身体部位、衣物、头发、道具或背景应该一起轻微响应，哪些结构必须保持稳定？如果生成片只让肚子、脸、皮肤或单个物体局部变形，说明提示词缺少效果分布锁。

When the user provides generated attempts that feel wrong, the guiding question changes:

模型把什么东西放大了、删掉了、变干净了、变广告了、变不连续了？这些偏差通常来自提示词里的权重、动词、镜头约束或连续性没有锁住。

For installation or surface-application attempts, also ask:

参考片是在第几秒才进入真正安装？有没有先出现桌面准备、裁剪、揭背膜、小片试贴、喷水、刮平、裁边这些不漂亮但可信的步骤？生成片是否太早把成品大面积贴到目标物上，或者让工具只在空中展示而不接触材料？

Also ask whether the tool and material stayed the same species:

参考片里的小剪刀、短手刮、美工刀、红色标签、平整镜面膜，在生成片里有没有变成长柄清洁刮、银色皱塑料、布、窗帘、金属箔、漂浮黑带，或者其他看似相近但物理用途不同的东西？

When a revised prompt becomes much better, the guiding question changes again:

这次到底是哪几个约束改变了模型的重心？是人物锚点、场景锚点、产品显著性、动作节奏、声音起点、连续性，还是负面约束更精确？哪些只是偶然细节，不该被固化？

For ecommerce attempts, also ask:

购物者看完是否知道产品卖点是什么？证明动作是否可信？背景任务有没有常识错误让人出戏？

For low-density attempts, also ask:

前 3 秒有没有空镜、沉默、泛泛人物入场、只露环境不露产品、只说寒暄不说卖点？音频是不是只有低音量底噪或泛泛环境声，而没有口播信息、动作瞬态和产品证明相关声音？这些都会让“像原片”变成“同题材素材”，但不是高转化短视频。

When the user provides reference prompts, also ask:

这些参考提示词的共同语法是什么？它们通常多长、先写什么、怎么写动作、怎么写口播、怎么写禁用项？最终输出应该像用户的提示词体系，而不是像一个全新的模板。

## Reverse-Engineering Checklist

### 1. Basic Video Envelope

- platform or style: TikTok, Reels, YouTube Shorts, UGC, cinematic, vlog, product demo
- duration: infer exact or approximate seconds
- aspect ratio: 9:16, 16:9, 1:1
- continuity: one-take, fixed camera, handheld follow, multiple shots, cuts
- subtitles, on-screen text, logo, BGM, voiceover
- image quality and finish: low-bitrate phone repost, high-resolution polished render, CCTV, dashcam, webcam, news footage, archival, etc.

### 1.5. Comparison Loop for Failed Generations

If the user provides one or more generated attempts:

1. Build comparable evidence first: contact sheets, matched timestamp frames, or a short shot list for the reference and each attempt.
2. Diagnose differences across these axes:
   - visual hierarchy: what is the real main event, and what did the generated video make too important?
   - camera role: whether first-person, coworker-filmed, selfie, tripod, or over-the-shoulder perspective matches the reference
   - subject count: whether one visible performer became two people, duplicate bodies, camera-wearer legs, or impossible limbs
   - product prominence: whether the product is visible early enough, large enough, and present during the proof action instead of only in the CTA
   - opening hook clarity: whether the first 0-3 seconds identify the product category, pain point or selling point, and proof promise
   - visual information density: whether each short beat carries product identity, pain, proof, result, trust, or CTA instead of empty movement or generic scene-setting
   - native phone texture: whether compression, softness, exposure shifts, close phone distance, accidental crops, and imperfect framing match the reference
   - process phase timing: whether prep, cutting, peeling, wetting, first contact, smoothing, trimming, and reveal happen in the same order and at similar relative timing
   - tool and material identity: whether scissors stay scissors, a short hand squeegee stays a short hand squeegee, utility knives stay utility knives, and flat adhesive film stays flat adhesive film rather than foil, cloth, or a cleaning tool
   - tool-contact logic: whether scissors, squeegees, knives, scrapers, brushes, rollers, or applicators physically touch the right material with the right force and angle
   - physical-effect distribution: whether vibration, massage, airflow, heat, compression, balance, or resistance originates from the product and spreads through the correct contact points
   - reflective-surface artifacts: whether glossy film, mirrors, glass, metal, or screens accidentally introduce faces, duplicate bodies, camera operators, or wrong reflected rooms
   - scene density: clutter, dirt, wall/ground texture, background objects, local markers, imperfect edges
   - camera geometry: height, distance, lens feel, cropping, handheld shake, subject partially out of frame
   - action causality: whether each action logically causes the next, or the model produced a tidy montage
   - object continuity: whether objects stay worn/held/installed, keep color/scale/position, and do not turn into display props
   - human behavior: gaze, smile, body strain, work focus, timing of talking to camera
   - occupational credibility: whether the person looks like a worker/athlete/cook/mechanic/etc. rather than a clean influencer or office worker in costume
   - body texture: hair flyaways, sweat, pores, dust on clothes, scuffed shoes, dirty gloves or hands, glove continuity, uneven sleeve wrinkles
   - local authenticity: whether identity cues, language/accent, jobsite type, tools, clothing, tattoos, grooming, and behavior fit the target country/market
   - finish: raw phone footage vs polished ad, clean render, cinematic grading, or overly sharp high-production look
   - audio/text: subtitles, watermark, BGM, TTS, dialogue language, environmental sound, whether sound begins at 0.0 seconds or starts late, whether pauses keep room tone or become digital silence, whether visible actions create matching transient peaks
   - audio information density: whether the first spoken phrase and early sounds communicate product, pain, proof, urgency, or trust rather than only ambience or filler
   - factual/physical correctness: impossible tool use, wrong assembly, impossible body movement, object penetration, melting/morphing, product effects beyond plausible claims
   - selling point clarity: whether the product's main benefit is visible, tested, and tied to the shopper's pain point
3. Attribute the likely prompt causes:
   - over-weighted product wording caused product-display behavior
   - over-corrected realism or task wording buried the product, turning the ad into a generic work tutorial
   - product visibility wording was too aggressive, so the model created fake first-person POV knees, billboard-like product framing, or two bodies in one scene
   - no camera-role lock let "low-angle close-up" become first-person POV even though the reference was coworker-filmed
   - no subject-count lock let the model add another worker or duplicate the same worker's body
   - no product visibility budget let the model show the product only at the beginning or end, not during the proof action
   - no first-3-second hook let the model spend the opening on a face, room, task, or beauty shot before the viewer understands what is being sold
   - no information-density plan let the model create low-value beats: empty walking, silent handling, repeated product beauty shots, or generic lifestyle montage
   - vague "UGC/realistic" wording let the model choose a clean influencer demo
   - character details were too generic, so the model created salon hair, smooth skin, clean clothes, clean hands, and office-worker body language
   - local identity was underspecified, so the model created a location-neutral clean presenter instead of a person who belongs to the observed market and jobsite
   - missing glove/hand locks let the model switch between gloves and bare hands, or make hands too clean for the task
   - audio was described too generally, so the model delayed speech, muted the opening, generated mouth movement without voice, or made visible actions nearly silent
   - opening dialogue was too generic, so the clip began with greetings or ambience instead of product/pain-point information
   - audio bed was not specified, so the model noise-gated pauses and removed room tone/action texture between speech bursts
   - action-synchronized sound was not specified, so the model created generic quiet ambience instead of distinct scissors, peel, scrape, tap, motor, or squeegee transients that match the frame
   - raw phone texture was underspecified, so the output became a polished, high-bitrate, well-lit product render
   - missing continuity locks let worn items become handheld props
   - missing process-phase locks let the model jump straight to the finished installation, skip the unglamorous prep, or repeat the same glossy display beat
   - missing tool/material identity locks let the model substitute a different tool or material that looks plausible but changes the event, such as a window-cleaning squeegee instead of a tint applicator, or crumpled silver foil instead of flat mirror film
   - missing tool-contact locks let cutters, squeegees, scissors, or scrapers float near the object instead of doing physical work
   - missing physical-effect locks let the model make one body part wobble or morph while feet, legs, clothing, shoulders, hair, and the product stay unnaturally still
   - missing reflective-surface locks let a hands-only product demo reveal a face, torso, selfie angle, or extra person in the reflection
   - too many perfect steps made the model center the process like a tutorial
   - secondary-task instructions were too complex, so the model spent attention on pipe/tool mechanics and made physical errors
   - broad negative constraints missed the actual failure mode
   - no domain logic let the model invent a wrong installation, wrong tool, fake test, or impossible product effect
   - product benefit was implied but not proven, so the result looked like generic lifestyle footage
4. Revise by changing the prompt's center of gravity, not just adding more adjectives. Lead with the lived event, lock object states, timestamp the action beats, and add only targeted negatives.
5. For ecommerce revisions, make the product benefit explicit but not fake: define the pain point, show a real use case, include one proof close-up, and keep the task mechanically believable. Rewrite the first 0-3 seconds first, because if that beat does not identify the product and selling point, later improvements usually cannot save the clip.

### 1.6. Success Pattern Loop

Use this when the user provides a successful, usable, or much-improved generation.

Compare the successful clip against the reference and earlier failed attempts, then classify what improved:

- character anchor: distinctive identity, age, job, clothing, tattoos, dirt, grooming, posture, and speech rhythm now match the reference better
- scene anchor: location, construction materials, clutter, light direction, background depth, and imperfect phone framing now carry the same local reality
- product/effect anchor: product remains on-body/in-hand/installed, appears early enough, and the effect happens at the same rhythm and physical distribution as the reference
- action anchor: the clip follows a simple lived event instead of a generic product demo or over-complex tutorial
- audio anchor: sound starts at 0.0 seconds, mouth movement has voice, environment/action sounds continue under the speech
- negative anchor: exclusions target the actual failure mode rather than bloating the prompt

Then write the learning as a reusable rule:

- keep: constraints that repeatedly moved the output closer
- refine: constraints that worked but still leave small drift
- discard: accidental details that are not part of the reference's essential structure

Example from a successful construction UGC revision:

- keep: "specific US/LatAm worker identity + dusty graphic work shirt + visible neck/forearm tattoos + tool belt + used trowel + 0.0-second jobsite sound + exact slow photochromic timing"
- refine: "frame rate/low-bitrate wording may help texture but does not replace character and audio anchors"
- discard: "extra ad-like CTA or long technical work instructions if the reference is really a quick worker-to-camera demo"

### 2. Product or Subject

Describe visible physical facts:

- category, color, shape, material, texture, labels, packaging
- condition: new, dusty, wet, scratched, used, reflective
- scale and how it is held/worn/installed
- for product references: "所有产品细节以参考图为准，强制保留原图物理特征，严禁形变、换款、错色、错 logo。"

Better than "黑色护膝":

"黑色重型硬壳护膝，硬质外壳、厚缓震内垫、魔术贴绑带，表面有灰尘和使用划痕。"

Product hierarchy rule:

- If the reference is a product ad or TikTok Shop style clip, make the product benefit the hero and include a proof moment.
- If the reference is a task or lived scene where the product is only worn, used, or visible, describe the task first and the product second.
- Avoid verbs that change the product's state unless the reference does that. For example, "展示护膝" often makes models put the pad in the hand; use "镜头看到护膝一直绑在膝盖上" or "用手拍一下仍绑在膝盖上的护膝."

For ecommerce, name the selling point in physical terms:

- protection: what impact, abrasion, heat, cold, pressure, or moisture is reduced?
- convenience: what step becomes faster or easier?
- fit/comfort: what part of the body or object stays stable, padded, dry, or adjustable?
- durability: what material resists wear, bending, tearing, stains, or scratches?
- visual appeal: what detail, texture, cut, glow, or before/after state is visible?

Then link the selling point to a proof action. Avoid unsupported claims like "prevents all injury", "instantly repairs", or "works perfectly forever."

### 2.5. Shot Intent Mapping

For close recreation and ecommerce reverse-engineering, map each meaningful shot before writing:

- product identity: exact category, visible model/type, material, condition, reference-image dependency
- shot function: pain point, product reveal, use-case proof, durability proof, comfort/fit proof, result display, trust-building, CTA
- shopper takeaway: what the viewer should understand after that shot
- model risk: what the generator may distort, omit, or misunderstand

Keep this mapping concise. It is for prompt accuracy, not a long creative analysis.

Example:

- kneeling close-up: proves the hard shell contacts rough concrete instead of the knee; risk is the model turning the knee pad into a handheld prop.
- tool close-up: builds real-worker trust; risk is the model inventing incorrect assembly, so simplify or lock the physical logic.

### 2.6. First-3-Second Hook and Information Density

Use this for ecommerce, TikTok Shop, product-led UGC, or any clip meant to sell a product quickly.

Design the opening as a compressed sales packet, not a slow intro:

1. product identity: the viewer can name the category within 3 seconds, e.g. knee pads, window film, washing-machine cleaner, vibration platform, photochromic glasses
2. pain point or benefit: the opening shows or says the problem/benefit in physical terms, e.g. concrete hurts knees, the washer smells, sunlight is harsh, the platform is running
3. proof promise: the first action starts proving the claim, e.g. kneeling onto concrete, dropping tablet into washer, peeling film, stepping into sun, motor vibration
4. audio cue: if audio is present, the first phrase or first action sound carries product/pain/proof information instead of only a greeting, silence, or generic ambience

Write the first 0-3 seconds before the rest of the prompt. A useful opening beat usually combines one visual cue and one audio cue:

- visual: product in the same frame as the pain or use case, not isolated beauty display
- spoken: short, oral, target-language line that names the pain or product benefit
- action sound: a close-mic sound that confirms physical use, such as kneeling thump, scissors click, peel rasp, motor hum, spray, scrape, tap, or fabric stretch

For product-led clips, every 1-3 second beat should carry at least one function:

- product identity
- pain point
- proof action
- result or comparison
- trust/real-user signal
- CTA or purchase cue

Avoid low-density beats unless the reference clearly uses them on purpose: empty walking, room-only establishing shots, silent product handling, generic face-to-camera greetings, repeated beauty shots, or long task steps that do not prove the product. If a task is necessary for realism but not for selling, compress it and keep the product or pain cue in frame.

For audio information density:

- use short lines that a real person would say while doing the action
- make the first line reveal the product or pain: "Concrete floors destroy your knees", "If your washer smells, look at this", "Watch these lenses change in the sun"
- keep continuous room/street/worksite tone under the speech
- pair each visible proof action with a distinct sound transient
- avoid voiceover that starts after the visual hook, low-volume background-only audio, noise-gated gaps, and filler lines that do not advance the sale

### 2.7. Product Prominence Budget

Use this for ecommerce, TikTok Shop, product demos, or any reference where the product is meant to sell even while the scene feels lived-in.

Define a product visibility budget before writing the final prompt:

- first 1-3 seconds: viewer can identify the product category and main benefit or pain point, not just the surrounding task
- proof action: product remains visible while it does the job, e.g. knee pad pressed against concrete while the worker measures, reaches, or tightens
- mid-video: do not hide the product for more than 2-3 seconds unless the reference also does that
- ending: product gets a natural close-up or touch cue, but it should not be the first clear product reveal

For worn products:

- keep the worn product in the same frame as the body strain: knees on concrete, elbow on counter, glove gripping sharp material, shoe stepping in mud
- use low-angle or cropped framing that includes both the product and the task object
- write physical contact, not abstract display: "the hard shell is visibly compressed against broken concrete while she leans forward" is stronger than "show the knee pads"

For product-led videos with a secondary task:

- the task should prove the product, not become the main tutorial
- simplify the task to a few believable actions if the domain is likely to drift
- avoid long tool-only or pipe-only close-ups that hide the product

If a generated attempt made the product too weak, add direct locks:

- product visible in at least 70% of shots
- first frame includes the product large in the lower third
- every work beat keeps the product either centered, foregrounded, touched, or under visible load
- no task-only close-up longer than 2 seconds
- no final-only product reveal

Important: product prominence must not override camera role. If the reference is coworker-filmed, do not write instructions that imply the viewer is wearing the product. Avoid "my knees fill the lower third", "first frame from the wearer's eyes", or "POV of my knee pads" unless the reference is truly first-person. Write "third-person low angle, the worker's knee pads visible on her own knees" instead.

### 3. Scene and Local Reality

Use this formula:

国家地区 + 具体地点 + 时间光线 + 背景道具 + 人群状态 + 不完美痕迹。

Good scene details include:

- ground, wall, furniture, storefront, vehicle, tools, signs, background people
- local markers: US suburb, Miami evening street, Mexican market, American mall
- imperfections: dust, sweat, clutter, noise, crowd blocking, uneven handheld motion

Avoid generic "beautiful background" unless the reference video is clearly staged.

For US/LatAm construction or trade UGC, use concrete local markers when visible or desired: unfinished wood framing, cinder block or drywall, orange extension cords, plastic buckets, measuring tape clipped to a belt, used trowels, work trucks outside frame, sun-bleached T-shirts, bilingual English/Spanish speech, and ordinary jobsite mess. Avoid turning the scene into a clean international showroom, an empty architectural render, or a perfectly lit product-demo corner.

For US home UGC, especially TikTok Shop or Reels product clips, use concrete household markers instead of generic "living room": beige or off-white rental walls, gray sectional sofa, carpet or area rug, blinds or vertical blinds, scattered laundry, slippers, plastic water cup, extension cord, power strip, kids' toys, pet hair, wall outlet plates, casual daylight from a side window, and slightly cramped phone framing. Avoid showroom-clean apartments, empty beige walls, perfectly arranged furniture, luxury decor, hotel-room lighting, and influencer studio posture unless the reference shows that.

### 4. Character Credibility

Use this formula:

年龄 + 身份/职业/地域信号 + clothing + body state + emotion + language + relationship to product.

For manual labor or physically specific scenes, expand the formula:

年龄 + 职业年限/地域信号 + 不完美毛发 + 皮肤/汗/灰尘 + 手套或手部状态 + 衣物磨损污渍 + 鞋底/膝盖/肘部受力 + 专注表情 + 符合职业习惯的动作。

Examples:

- 39 岁美国墨西哥裔贴瓷砖工人，胡须、纹身、工服沾水泥灰，用西语口播。
- 25-30 岁美国百货商场女导购，黑色西装，妆容精致，用英语自然推荐。
- 30-45 岁美国普通居家女性，松弛的灰色家居运动套装、白袜、微乱长发、轻微疲态，用随口英语介绍家用健身器材。
- 拍摄者第一人称不露脸，只出现右手和声音。

### 4.2. Occupational Realism Locks

Use this whenever the reference is construction, plumbing, repair, cleaning, cooking, sports, farming, warehouse work, outdoor labor, or any task where the body should show contact with the environment.

Concrete signals to write:

- hair: tied back for safety, loose strands stuck to forehead, imperfect parting, helmet/hat marks, not salon-smooth
- face/skin: light sweat, pores, dust specks, mild fatigue, focused eyes looking at the work more than the lens
- hands: work gloves if appropriate; if bare hands are visible, show dirt in creases, small scratches, dry skin, short nails, no manicure
- clothing: dust on knees/thighs/sleeves, paint or cement marks, wrinkles from kneeling, scuffed boots, tool belt weight, safety glasses with smudges
- posture: weight pressed into knees/elbows/heels, shoulder lean, off-hand bracing the material, small awkward adjustments in cramped space
- behavior: glances at camera are brief; most attention stays on the task until the final CTA or explanation

Bad generic prompt:

"a realistic female construction worker wearing knee pads installs a pipe"

Better:

"a 30-year-old Latina renovation worker with a messy side braid, loose curls stuck to her forehead, smudged clear safety glasses, dusty burgundy sleeves, gray rubberized work gloves, olive work pants with drywall dust across both knees, scuffed brown work boots, and a tool belt pulling one side of her vest down; she keeps her eyes on the pipe and shifts her weight heavily into the knee pads while working on rough concrete"

If a generated attempt looked too clean, add direct negatives:

- no salon-perfect hair, no smooth plastic skin, no influencer smile during work, no clean bare hands, no spotless pants, no pristine boots, no office-worker posture, no fashion-model kneeling, no glossy showroom lighting.

### 4.4. Local Authenticity Locks

Use this when the user says the character does not feel local, or when the reference depends on a specific market such as US, LatAm, Japan, China, Europe, or a local trade scene.

Write the desired identity positively:

- target market and community: "US Southwest / Southern California / Texas jobsite", "Mexican-American or Latino construction worker", "bilingual English-Spanish worksite banter"
- visible local signals: sun-tanned skin, short practical haircut with imperfect edges, neck or forearm tattoos if present in the reference, faded graphic work T-shirt, brown leather tool belt, scuffed tape measure, dusty boots, used trowel, drywall/cement dust
- behavior: brief eye contact with the phone, most attention on the task, casual worker-to-worker tone, small pauses and filler words, not a scripted studio delivery
- language: choose the actual or target language; for US trade UGC, Spanglish or casual American English/Spanish can be more local than neutral narration

Avoid protected-class negative prompts. Do not write "not [ethnicity]". Instead, state the desired local identity, styling, voice, and behavior in enough concrete detail that the model has a clear target.

If generated output looked location-neutral, add direct negatives:

- no generic clean presenter, no showroom model, no office-worker grooming, no K-pop/fashion-influencer hair styling, no perfectly symmetrical beauty face, no pristine T-shirt, no empty render-like jobsite, no polished brand-commercial posture.

### 5. Camera Discipline

Choose one coherent camera plan:

- first-person POV, handheld phone, slight walking shake
- third-person coworker filming, close follow
- fixed tripod-like phone shot, no pan/tilt/zoom
- low-angle close-up tracking knees/hands/product

Be explicit about:

- shot size: close-up, medium, over-the-shoulder, low angle
- movement: light shake, follow, push-in, no movement
- editing: one-take/no cuts or multi-shot sequence
- focus priorities: product details, hands, face, action result

Do not mix mutually exclusive instructions unless recreating a visibly contradictory reference. Resolve conflicts like "固定镜头" vs "手持跟拍".

### 5.2. Camera Role and Subject Count Locks

Use this before writing product visibility rules. The camera role is more important than a generic "make product visible" instruction.

Common roles:

- coworker-filmed: one invisible camera operator films the subject; only the worker's body appears; no camera-wearer legs or hands unless they hold the phone offscreen
- first-person POV: the camera wearer is the subject; their hands/legs may appear; no separate duplicate worker should perform the same task in front
- selfie/vlog: subject holds or faces the phone; framing includes face and torso; product may be tapped or pointed to
- fixed phone/tripod: camera stays in one place; subject moves through frame; no floating POV body parts
- over-the-shoulder: camera is behind or beside the worker; only one worker remains the subject

If the reference is coworker-filmed, write:

"同事手机近距离拍摄同一位女工，拍摄者不入镜；画面里只有这一个女工，没有第一人称膝盖，没有第二个工人，没有重复身体。"

If generated output became fake POV, add:

- no first-person POV, no camera-wearer knees, no viewer's own legs at the bottom, no hands entering from behind camera, no split identity between wearer and worker.

If generated output added people or duplicate bodies, add:

- only one visible person in the entire clip; the same worker's face, vest, gloves, pants, boots, and knee pads remain continuous; no second worker, no extra legs, no duplicate torso, no body crossing in front of the camera.

### 5.3. Native Phone Texture Locks

Use this when the reference is raw TikTok/UGC, reposted short video, casual phone footage, jobsite phone footage, street footage, or home product sharing.

Observable texture cues to capture:

- apparent quality: low or medium bitrate, mild compression, slightly soft edges, not pristine 4K sharpness
- camera behavior: cramped distance, accidental partial crops, small hand jitter, slight autofocus or exposure adjustment
- light: ordinary window light, ceiling light, construction light, street light, mixed color temperature, blown highlights or dark corners if present
- framing: product and face are useful but not perfectly centered; background clutter is visible; some body parts or tools enter and leave frame awkwardly
- surface reality: dust, lint, drywall chips, fingerprints, smudged glasses, scuffed floor, unclean corners

If a generated attempt looks too polished, add direct locks:

- low-to-medium apparent phone quality, mild platform compression, slightly soft detail, ordinary phone auto-exposure, no cinematic depth of field, no glossy high-bitrate render, no symmetrical hero framing, no spotless surfaces, no clean brand-commercial lighting.

Camera fidelity tips:

- If the reference feels raw, specify low or uneven phone framing: cramped distance, partial cropping, slight focus hunting, ordinary indoor light, mild compression, imperfect composition.
- If the generated attempt became too polished, explicitly ban clean hero framing, symmetrical composition, cinematic push-ins, glossy lighting, and pristine backgrounds.
- If the reference has repeated close-ups of hands or tools, define what must stay in frame and what can be cropped, rather than asking for a generic close-up.

### 6. Action Chain

For product videos, structure the action:

1. Hook: why the camera starts watching.
2. Product reveal: where the product first appears.
3. Proof action: a visible test or use case.
4. Result display: show the after-state close to camera.
5. Natural CTA: point downward, mention cart/link/shop only if the reference does.

Proof action examples:

- tire rolls over knee pad
- scraper scratches glove palm
- worker crawls through mud wearing pads
- perfume is sprayed and another person reacts
- jersey is turned front/back to show pattern

For product videos, the proof action must include the product in-frame. A knee-pad proof is not "install a pipe"; it is "install or measure while both knee pads are visibly carrying body weight on rough concrete." A glove proof is not "cut a box"; it is "the gloved palm grips and resists abrasion while cutting."

For non-product-first videos, preserve the task chain:

1. setup: the practical problem or work position
2. manipulation: hands, tools, body posture, materials
3. constraint: cramped space, dirt, weather, crowd, time pressure, awkward angle
4. check/result: a visible verification, reaction, or changed physical state
5. only then: face-to-camera explanation, punchline, or CTA if the reference has one

Use ordered beats or rough timestamps for clips under 20 seconds when the sequence matters. Keep each beat filmable in 1-4 seconds.

When the product is the real sales subject and the task is only context, use a task complexity budget:

- choose one simple, repeatable domain action that proves the product
- avoid requesting full expert workflows unless the product itself requires that workflow
- keep the camera close enough that the product and task share the same frame
- if the generated attempt produced impossible mechanics, reduce the domain action rather than adding many more technical steps

### 6.2. Process Phase Locks for Surface Application

Use this for window film, phone screen protectors, stickers, wallpaper, decals, tint, labels, laminating sheets, wraps, screen protectors, and any product that is cut, peeled, pressed, scraped, or stuck onto a surface.

First identify the reference's phase order and relative timing:

1. prep surface: table, counter, window sill, floor, or workbench where the product is unrolled, measured, or positioned
2. scale state: full roll, large panel, small test strip, offcut, corner tab, backing layer, or already-installed piece
3. tool action: scissors cut the loose film; fingers peel a corner; spray wets glass; palm tacks the film; squeegee pushes water/air outward; knife trims only the excess edge
4. target surface state: dry, wet, dusty, clean, bubbled, partially covered, or fully covered
5. reveal timing: the final installed surface appears only after the prep, first contact, smoothing, and trimming phases
6. tool/material identity: whether the reference uses small scissors, a short hand squeegee, a utility knife, red peel tabs, flat black mirror film, transparent backing, or a small offcut

For window tint or mirror film, write direct locks:

- do not place a full finished panel on the window before the cutting/peeling shots are complete
- preserve any small bottom-edge test strip or offcut if the reference uses one before the large panel
- keep the backing layer visibly separate from the dark adhesive film during peel shots
- keep the mirror film flat, glossy, black-blue, and sheet-like; do not let it become crumpled silver foil, fabric, curtain material, wrapping paper, or metallic cloth
- preserve the tool species: scissors remain small scissors, the squeegee remains a short handheld applicator, and the utility knife remains a small yellow cutter; do not turn the applicator into a long-handled window-cleaning squeegee
- preserve the target location of test pieces: a bottom-edge or lower-corner strip should not become a floating horizontal band across the middle of the window
- water droplets remain on the glass during squeegee shots; the squeegee blade contacts wet glass and pushes bubbles/water toward an edge
- the utility knife rides along the window-frame edge and trims excess film only; it does not cut the glass, wood frame, hand, or empty air

If a generated attempt became too polished, add:

- no perfect one-step installation, no instant full-window coverage, no repeated beauty shots of a finished window before the work is done, no tool waving in the air, no wrong-tool substitution, no crumpled silver material, no dry-glass squeegee when the reference uses wet application.

### 6.5. Physical and Factual Correctness

Before finalizing, define the minimum real-world logic the model must obey. This is especially important when the reference contains repairs, tools, sports, vehicles, cooking, beauty routines, medical-looking demos, or product stress tests.

Use three kinds of locks:

1. geometry lock: where objects attach, touch, enter, exit, rotate, or rest
2. force/material lock: what bends, compresses, resists, scrapes, absorbs, or stays rigid
3. before/after lock: what visibly changes and what must remain the same

Examples:

- plumbing: pipes connect end-to-end with visible couplers or clamps; no open pipe floating in midair; no branch entering a sealed wall at the wrong angle; no water flowing through unconnected parts.
- under-sink drain context: the black vertical drain pipe should descend from the sink area; the white PVC trap or branch should attach to a fixed floor/wall stub; each pipe end has one clear mating port; avoid freestanding U-shaped assemblies on the floor unless the reference shows loose parts. Do not create duplicate open pipe mouths, floating black cylinders, extra unattached elbows, or pipe loops with no inlet/outlet.
- drill and fastener: the driver bit stays aligned with the screw head or clamp screw; the drill pushes along the screw axis, not straight down into a pipe wall; the off-hand braces the pipe or clamp away from the spinning bit; no glowing bit, sparks, or drilling through plastic unless the reference actually shows drilling.
- clamp tightening: a band clamp wraps around the joint; the screw sits on the side of the clamp; the drill or screwdriver approaches the side screw, not the open top of a pipe; no long vertical screw suspended beside a pipe; no oversized drill bit inside an open drain.
- wearable protection: the pad stays strapped to the body; impact or kneeling happens on the protected area; straps do not vanish; the body motion stays anatomically plausible.
- cooking: ingredients enter the pan in a sensible order; cooked state changes gradually; utensils do not pass through solid objects.
- beauty: product is applied to the correct surface; before/after is plausible; skin, hair, or fabric does not morph instantly.
- reflective surfaces: decide whether faces, bodies, camera phones, windows, sky, furniture, or lights should appear in the reflection. If the reference is hands-only, ban face/torso/selfie reflections and duplicate people; if the reference relies on reflections, specify exactly what should be reflected.
- surface film: adhesive/backing layers remain two separate sheets during peeling; offcuts stay smaller than full panels; a partially installed strip does not become a full finished window in the next shot unless the reference cuts to that after-state.

If unsure about domain specifics, use a simpler proof action that is obviously credible rather than inventing expert-level technical work.

### 6.6. Physical Effect Distribution Locks

Use this for products whose value is a visible or audible physical effect: vibration plates, massage guns, slimming belts, compression boots, fans, heaters, cooling devices, treadmills, balance boards, jump ropes, resistance bands, posture correctors, or any tool that moves, presses, warms, cools, or pulls the body/object.

First define the effect chain:

1. source: which product part creates the effect, e.g. platform motor, vibrating pad, rotating fan, elastic cord, massage head, heating panel
2. contact path: feet on platform, hands gripping handles, strap around waist, pad touching shoulder, fabric pressed under compression
3. distributed response: which visible parts respond together, e.g. ankles, knees, hips, shoulders, sleeves, drawstrings, hair tips, loose fabric, cord tension, nearby small vibrations
4. stable anchors: product shape, face identity, body proportions, room layout, hands, feet placement, and clothing color remain stable
5. believable limit: the effect is subtle enough for phone footage and does not create medical, slimming, or instant transformation claims

For vibration-platform clips, write direct locks:

- vibration originates from the black platform under both feet; both feet stay planted on the foot pads
- knees, calves, pants fabric, sweatshirt hem, arms, shoulders, and hair tips show tiny synchronized tremors
- the torso has a small whole-body bounce, not a separate belly-only wobble
- the platform hum and slight plastic rattle begin at 0.0 seconds if audio is present
- no liquid-like skin morphing, no isolated stomach shake, no sudden waist-size change, no face distortion, no floating feet, no platform bending or changing shape

For resistance-band clips, write direct locks:

- the band anchors remain attached to the product or fixed point; handles stay in the hands
- cord tension increases as elbows bend and decreases when arms lower
- hands, wrists, elbows, and cord angle move together; no floating handles, disconnected cords, or duplicated straps

### 6.8. Matching User Reference Prompt Style

If the user provides a prompt document or examples, extract a small style profile and follow it:

- opening: whether examples start with "15秒 TikTok..." or a slash title
- section order: product, product features, style, character, scene, action/dialogue, light, sound, negative constraints
- density: compact paragraph script vs many labeled sections
- duration grammar: whether actions are timestamped or written as continuous beats
- dialogue style: language, oral tone, whether each action has a line
- constraint style: embedded in the paragraph or collected at the end
- length: approximate the reference length for similar tasks; do not make the prompt much longer unless needed for safety or physical correctness

When matching a reference prompt, preserve its useful common rules:

- write concrete visual nouns instead of abstract adjectives
- put product and product features early
- make every action visibly filmable
- use one or two strong proof moments rather than many weak proof claims
- include native-language oral dialogue if the reference relies on UGC口播
- keep final CTA natural and platform-specific when the reference is ecommerce

Avoid overfitting accidental mistakes in the reference. Preserve the style, not typos, contradictions, or impossible instructions.

### 7. Audio and Dialogue

Specify concrete sound sources:

- environment: traffic, mall crowd, stadium cheering, workers talking, wind
- action: Velcro, cloth rubbing, footsteps, tool motor, spray nozzle, tire friction
- dialogue: speaker, language, exact lines, tone
- no BGM/subtitles when the goal is raw UGC realism

Dialogue should be short, oral, and context-matched. Avoid brand-commercial wording unless the reference is actually an ad.

#### Audio Onset Lock

For any video where the reference has speech, mouth movement, tool sounds, or an audible hook near the start, specify the opening sound explicitly:

- "0.0 秒立即有现场声，不允许静音开场。"
- "0.0-0.8 秒先听到瓦刀刮灰浆和工人低声开口：'Mira estos lentes...'"
- "口播与嘴型同步；如果人物张嘴，必须同时有对应声音。"
- "前 3 秒持续有环境底噪、动作声和短口播，不要延迟到 3 秒后才开始说话。"

If exact transcription is unavailable, provide plausible short lines in the correct language and cadence. Do not leave talking clips with only "natural dialogue"; that often lets the model drop the opening audio.

When a successful generation fixes an earlier silent opening, preserve the audio pattern explicitly in the next prompt: first-second action sound, first spoken phrase, continuous ambience, and a negative line banning delayed speech. Do not shorten this back to "natural口播" unless silence is acceptable.

#### Audio Bed Continuity Lock

Use this when a generated attempt has quiet gaps, weak ambience, or sounds like clean TTS pasted onto footage.

Write the sound bed as a continuous layer:

- base layer: room tone, street rumble, jobsite hum, crowd murmur, HVAC, wind, or household noise continues under the whole clip
- action layer: tool scrape, cloth rub, footsteps, plastic clicks, Velcro, pipe knocks, floor grit, or product motor appears exactly when the action happens
- speech layer: short imperfect human phrases, breath, filler words, small pauses, not studio narration
- pause behavior: pauses between spoken phrases should keep low-level room tone and small movement sounds; they should not fall into digital silence
- loudness feel: if the reference is phone-recorded speech, keep speech present and close to camera; do not make it much quieter than the action or ambience

If a generated attempt is too quiet or noise-gated, add:

- no noise-gated gaps, no dead-air valleys between phrases, no clean studio voiceover, no muted tool action, no silent middle section, no abrupt audio bed dropouts.

#### Audio-Action Synchronization Lock

Use this when the reference is driven by live operation sounds or when a generated attempt has weak, generic, or mistimed audio.

Map visible actions to audible transients:

- cutting: each visible scissors close should create a short metallic/plastic click
- peeling: backing film should make a crisp plastic rasp exactly as the corner separates
- smoothing: a hand squeegee on wet glass should make a rubber squeak or wet scrape during the stroke
- trimming: a utility knife on film edge should make a light scratch/tick along the frame
- tapping or rubbing: fingers, gloves, cloth, plastic, pipe, or product shell should make small close-mic sounds when they contact

If the generated attempt is too quiet, write direct locks:

- action sounds should be close to the phone mic and clearly audible, with small waveform peaks at each cut, peel, scrape, trim, and tap; do not bury them under silence or a very low-volume ambience.
- no generic quiet room tone replacing the action sounds, no action without sound, no sound that arrives before or after the visible contact.

### 8. Negative Constraints

Use only relevant exclusions:

- no subtitles, no BGM, no text overlay
- no studio lighting, no cinematic color grading, no ad-like posing
- no Chinese signs/packaging if target market is US/LatAm
- no product deformation, wrong color, wrong logo, warped hands/fingers
- no scene jump, clothing change, identity change, unrelated people stealing focus
- no cartoon, anime, plastic skin, excessive smoothing

Target negative constraints at observed or likely drift:

- If generated output turned into an ad: no product beauty shot, no influencer smile until the final beat, no clean showroom, no hero pose.
- If generated output looked too polished: add native phone texture locks; ban pristine high-bitrate render, cinematic lighting, perfectly clean surfaces, perfectly centered hero framing, and spotless product-demo composition.
- If generated output buried the product: state a natural product visibility budget inside the correct camera role, put the product in proof-action frames, ban task-only close-ups longer than 2 seconds, and make the product carry visible load or contact.
- If product prominence created fake POV: explicitly restore the camera role and subject count; ban camera-wearer knees, first-person legs, and two-person split identity.
- If a worn item became handheld: item remains worn/installed/attached for the whole clip; do not remove it, hold it up, or display it separately.
- If the scene became too clean: keep dust, scratches, clutter, torn edges, ordinary lighting, and imperfect framing.
- If the worker became too clean: add dusty sleeves, smudged safety glasses, dirty work gloves, scuffed boots, sweat, loose hair strands, tired focused expression, and ban office-clean styling.
- If hands became wrong: lock gloves on both hands for the full work sequence, or specify bare hands with dirt in creases; ban switching between gloves and bare hands unless the reference shows it.
- If audio has dead gaps: specify continuous room tone/action bed, speech density, and pause behavior; ban noise-gated gaps, silent middle sections, and studio-clean voiceover.
- If audio is too weak or generic: map each visible action to a close-mic transient; ban muted scissors, muted peeling, muted squeegee strokes, muted trimming, and delayed or mismatched action sounds.
- If the action became incoherent: no teleporting tools, no changing pipe layout, no repeated impossible assembly, no object scale drift.
- If the opening is low-density: no silent or ambience-only first 3 seconds, no generic "hey guys" opening before product/pain information, no face-only intro that hides the product, no room-only establishing shot, no beauty shot that fails to reveal the selling point.
- If surface-application output skipped prep: no premature full-panel installation, no instant finished surface, no missing backing layer, no missing wet/dry surface state, no floating cutter/squeegee/scissors, no repeated final-window beauty shots before the actual work is shown.
- If surface-application output changed tools or materials: no long-handled cleaning squeegee when the reference uses a short tint applicator, no crumpled foil/fabric/curtain/wrapping paper when the reference uses flat adhesive mirror film, no floating center-window band when the reference shows a bottom-edge strip.
- If a physical-effect product looks fake: no belly-only wobble, no liquid skin, no isolated face/arm shake, no body-size morphing, no product-independent effect, no floating feet or hands, no disconnected resistance cords, no silent motor when the product is visibly running.
- If reflective products created artifacts: no unintended face reflection, torso reflection, camera-operator reflection, duplicate person, selfie angle, or wrong room reflected in mirror/glass/metal/screen surfaces.
- If the secondary task caused physical errors: simplify the task to a credible proof moment and ban the specific wrong geometry, rather than asking for more complex expert steps.
- If the task has factual errors: no wrong connection points, no impossible tool angle, no floating or penetrating objects, no physically impossible before/after, no fake exaggerated result.
- If the product benefit is unclear: no generic lifestyle montage, no unrelated task stealing focus, no beauty shot that fails to show the selling point.
- If the audio carries too little information: no low-volume background-only audio, no delayed product mention, no filler-only opening line, no action without matching sound, no pauses that erase the room tone or proof-action texture.

## Copy-Ready Output Template

```text
【标题】
{时长} {平台/风格} {产品/主题} 视频提示词（{真实感方向}）

【整体核心规范】
真实手机竖屏 {画幅}，{第一/第三人称}，{手持/固定}，{一镜到底/多镜头}。
全片{有/无}字幕，{有/无}背景音乐，保留{环境音、动作音、人物口播}。
整体是{素人 UGC / 真实街拍 / 工地实拍 / 商场顾客视角}质感，不要广告棚拍，不要过度精修。

【原生手机质感】
{低/中码率感、轻微压缩、手机自动曝光/对焦、局促距离、偶然裁切、普通光线、背景杂乱、哪些高制作感必须避免}

【产品/主体】
{产品或主体的可见物理特征、颜色、材质、结构、使用痕迹、参考图一致性要求}

【前三秒卖点钩子】
{0.0-3.0 秒观众如何立刻知道卖的是什么、解决什么痛点/卖点、正在开始什么证明动作；同时写出第一句口播或第一组动作声}

【拍摄关系/主体数量】
{谁拍谁、是否第一人称/同事拍/自拍/固定机位、画面里允许几个人、拍摄者是否入镜、禁止哪些混合视角}

【产品显著性锁定】
{产品第几秒自然出现、如何在正确拍摄关系里可见、是否贯穿证明动作、哪些镜头不能隐藏产品、是否需要产品承重/接触/被触摸}

【流程阶段锁定】
{参考视频的准备/裁剪/揭膜/上墙或接触/刮平/裁边/结果展示顺序；哪些成品镜头不能提前出现；小片、边角料、标签、背膜、湿面等状态如何保持}

【工具/材料身份锁定】
{剪刀、刮板、美工刀、滚筒、喷瓶、膜片、背膜、边角料等必须保持的具体形态；禁止替换成哪些相似但错误的工具或材料}

【场景】
{国家地区、具体地点、时间、光线、天气、背景道具、人群、杂乱程度、不完美细节}

【人物】
{年龄、身份、职业、穿着、状态、表情、语言、是否露脸、与产品关系}

【人物真实度锁定】
{毛发是否凌乱/贴汗、皮肤和护目镜是否有灰尘、手套或手部状态、衣服鞋子污渍磨损、身体受力和职业动作习惯}

【机位】
{视角、距离、角度、运动、对焦对象、是否切镜}

【画面信息密度】
{每 1-3 秒分别承担什么功能：产品身份、痛点、证明动作、结果、信任点、CTA；删除哪些空镜/空动作/无效场景说明}

【画面动作 + 口播】
开场：{可拍摄动作 + 0.0 秒开始的台词/动作声，禁止静音开场}
中段：{证明卖点的动作 + 台词}
结果展示：{测试后结果特写 + 台词}
结尾：{自然购买引导或情绪收束 + 台词}

【卖点证明】
{产品解决的痛点、可见证明动作、证明后的结果、不要夸大的边界}

【连续性锁定】
{人物、服装、道具、产品佩戴/安装状态、场景位置、手持物、已完成/未完成状态必须如何保持一致}

【事实/物理锁定】
{工具和物体如何正确接触、连接、受力或变化；哪些错误动作或错误结构必须避免}

【物理效果分布锁定】
{震动/按摩/风/热/压缩/拉力从产品哪个部件产生，如何通过接触点传到身体或物体，哪些部位和衣物一起轻微响应，哪些结构必须保持稳定，禁止哪些局部形变}

【反光/倒影锁定】
{镜面、玻璃、金属、屏幕中允许反射什么；是否禁止脸、身体、拍摄者、第二个人或错误房间倒影}

【副任务复杂度】
{如果产品不是被维修/安装对象，说明任务只作为证明场景；保留哪些简单动作，禁止哪些复杂流程抢主戏或引发物理错误}

【光线】
{自然光/室内灯/霓虹/施工灯等，以及不要出现的光线风格}

【声音】
{0.0 秒立即开始的环境音 + 连续现场声床 + 具体动作音 + 逐段口播；停顿也保留房间/街头/工地底噪，前 3 秒和中段不得静音；每个可见接触动作对应清楚的近场瞬态声音}

【音频信息密度】
{第一句话如何点明产品/痛点/卖点；哪些动作声证明真实使用；哪些停顿仍保留底噪；禁止泛泛低音量背景声替代口播或动作声}

【负面约束】
不要{字幕/BGM/中文标识/棚拍/产品变形/手指畸形/场景跳变/过度磨皮/无关抢镜等}
```

## Compact Ecommerce Script Template

Use this when the user's reference prompts are compact TikTok Shop scripts rather than heavily sectioned templates:

```text
//15秒 TikTok {产品}带货视频脚本｜{场景/卖点}版
产品：{具体产品类别}
产品特点：{颜色、材质、结构、核心卖点}
前三秒钩子：{0-3 秒产品如何入画、痛点/卖点如何被看见或说出、证明动作如何立刻开始、第一句口播/动作声是什么}
拍摄关系/主体数量：{谁拍谁；第一人称/同事拍/自拍/固定机位；只允许几个可见人物；禁止混合视角}
产品显著性：{开场/中段/结尾产品如何在正确拍摄关系里自然可见，证明动作中产品如何承重/接触/发挥作用}
流程阶段：{准备、裁剪、揭膜、接触目标面、刮平、裁边、展示结果的顺序；是否保留小片/背膜/水珠/边角料；禁止过早成片}
工具/材料身份：{工具和材料的具体形态；哪些相似替换必须禁止}
原生手机质感：{低/中码率感、压缩、手持抖动、局促距离、自动曝光、普通光线、杂乱背景、避免广告感}
风格：{地区/平台/UGC质感/镜头方式/一镜到底或剪辑/无字幕无BGM/保留真实声音}
人物：{身份、年龄、地域信号、穿着、状态、与产品关系}
人物真实度：{毛发、脸、手/手套、衣物、鞋、汗/灰尘、身体受力、职业习惯}
场景：{具体地点、环境杂物、光线、不完美痕迹}
信息密度：{每个 1-3 秒短段承担的销售/信任功能；删除空镜、无效入场、低价值重复展示}
画面动作 + 口播：{按视频顺序写连续动作，每个动作对应一个卖点或信任点，口播自然嵌入}
事实/物理锁定：{只写最容易出错的真实逻辑}
物理效果分布：{产品效果的来源、接触路径、身体/衣物/道具的同步响应、稳定项、禁止局部乱形变}
反光/倒影：{允许或禁止的反射内容，尤其是脸、身体、拍摄者、第二个人}
副任务复杂度：{任务只是证明产品的场景，不让教程/维修流程抢主戏}
结尾画面：{产品特写/结果展示/CTA}
声音：{0.0 秒起的连续环境声床、动作音、口播、停顿时的底噪；剪/撕/刮/裁/敲等动作的同步瞬态声；禁止噪声门式静音}
音频信息密度：{第一句点明产品/痛点/卖点；中段口播和动作声持续补充证明；禁止只有低音量环境声或寒暄}
不要：{水印、字幕、BGM、场景跳变、产品形变、物理错误、手指畸形等}
```

## Self-Check Before Finalizing

- Does the prompt describe a filmable event rather than only a mood?
- Is the camera role and subject count locked before product visibility is described?
- Are product details visible and protected against drift?
- Is there a natural product prominence budget that does not create fake POV, duplicate bodies, or billboard-like product framing?
- In the first 3 seconds, can a cold viewer identify what is being sold and why it matters?
- Does the opening combine product identity, pain/benefit, and the start of a proof action rather than only ambience or setup?
- Does every 1-3 second beat carry product, pain, proof, result, trust, or CTA information?
- Are character, language, and location coherent?
- Is there a proof action for product value?
- For installation or surface-application clips, are the process phases in the right order and are final-state shots prevented from appearing too early?
- For installation or surface-application clips, did the tools and material keep their identity instead of drifting into similar but wrong objects?
- For ecommerce, can a shopper identify the product benefit within the first few seconds?
- Are tool use, object contact, assembly geometry, body motion, and before/after states physically believable?
- For physical-effect products, is the effect source, contact path, distributed body/cloth response, and stable anchor clearly locked?
- For reflective products, are unintended faces, duplicate bodies, selfie angles, and wrong-room reflections explicitly controlled?
- If the product is not the task object, is the secondary task simple enough that it will not steal focus or create domain errors?
- Are camera instructions internally consistent?
- Are audio details concrete?
- Does the first spoken phrase or first action sound carry product/pain/proof information?
- Are visible actions mapped to audible transient sounds at the same moment?
- Does audio begin at 0.0 seconds when the reference has speech or action sound?
- Does the audio keep a continuous room/street/worksite bed through pauses instead of dropping into digital silence?
- If the reference is raw UGC, did you specify the actual phone texture rather than only saying "真实"?
- Are negative constraints targeted rather than bloated?
- If there is a successful prior attempt, did you preserve the few constraints that made it work and avoid adding unrelated complexity?
- Can the user paste the prompt into a video model immediately?
