<div align="center">
  <h1>Skills-Codex</h1>
  <p><strong>A searchable, deduplicated library of Codex and agent skills.</strong></p>
  <p><a href="#persian">فارسی</a> · <a href="#english">English</a> · <a href="#arabic">العربية</a></p>
</div>

---

<a id="persian"></a>
## فارسی

<div dir="rtl" align="right">
این مخزن، مجموعه‌ای بزرگ از اسکیل‌های Codex و عامل‌های هوش مصنوعی را با فایل‌های همراه، منابع، اسکریپت‌ها و اطلاعات منشأ گردآوری می‌کند. در واردسازی اولیه، ۱٬۰۰۸ مجموعهٔ منبع بررسی شد.
</div>

### آمار واردسازی

- **۵۵٬۳۰۱** فایل `SKILL.md` در منابع پیدا شد.
- **۴۳٬۵۶۶** محتوای یکتا باقی ماند؛ تکراری‌بودن با تطبیق دقیق SHA-256 سنجیده شد.
- **۱۱٬۷۳۵** مورد تکراری دقیق در یک نسخه ادغام شد.
- فایل‌های همراهِ بستهٔ منتخب و **۹۱۲** مجوز سطح منبع حفظ شدند.
- هیچ فایلی به‌دلیل محدودیت ۱۰۰ مگابایتی GitHub حذف نشد.

### جست‌وجو و استفاده

هر ردیف در [`catalog.csv`](catalog.csv) یک محتوای یکتا را معرفی می‌کند. [`skill_sources.csv`](skill_sources.csv) همهٔ محل‌هایی را نشان می‌دهد که آن محتوا در منابع واردشده پیدا شده است؛ [`sources.csv`](sources.csv) نیز نام مجموعه‌های منبع و مجوزهای نگه‌داری‌شده را ثبت می‌کند.

برای جست‌وجو در PowerShell:

```powershell
Import-Csv .\catalog.csv | Where-Object name -Match 'security'
```

مقدار ستون `path` به فایل `SKILL.md` می‌رسد؛ کل پوشهٔ همان اسکیل را کپی کنید تا فایل‌های همراهش هم بمانند. اسکیل را در `.agents/skills/<نام-اسکیل>` برای یک پروژه یا در مسیر مهارت‌های کاربر Codex قرار دهید. چند مسیر منبع طولانی است و در ویندوز ممکن است فعال‌کردن پشتیبانی مسیر طولانی Git لازم باشد. راهنمای رسمی: [Codex Skills](https://developers.openai.com/codex/skills) و [استاندارد Agent Skills](https://agentskills.io/specification).

### منشأ و مجوزها

فایل‌های مجوزِ خود اسکیل داخل پوشهٔ آن باقی می‌مانند. مجوزهای سطح ریشهٔ منبع در `source-licenses/` نگه‌داری شده‌اند و در `sources.csv` به منبع مربوط وصل هستند. چون محتوای مجموعه از منابع و مجوزهای گوناگون می‌آید، مجوز واحدی برای کل مخزن اعلام نمی‌شود؛ پیش از استفاده یا بازنشر، مجوز همان اسکیل و منبعش را بررسی کنید. محتوای اسکیل‌ها به‌صورت دستی بازبینی یا تأیید امنیتی نشده است؛ پیش از فعال‌کردن یک اسکیل، دستورها و اسکریپت‌هایش را بخوانید.

**معیار یکتاسازی:** فقط فایل‌های `SKILL.md` با بایت‌های کاملاً یکسان ادغام شده‌اند. نسخه‌هایی که نام یکسان اما محتوای متفاوت دارند حفظ می‌شوند. فایل‌های اسکیل تغییر داده نشده‌اند.

---

<a id="english"></a>
## English

This repository brings together Codex and AI-agent skills with their available references, scripts, assets, and source records. The initial import covered **1,008 source collections**.

### Import at a glance

- **55,301** `SKILL.md` files were found.
- **43,566** unique contents remain, deduplicated by exact SHA-256 match.
- **11,735** exact duplicate occurrences were consolidated.
- Supporting files from the selected package copies and **912** source-level license files were preserved.
- No files were excluded for GitHub’s 100 MB per-file limit.

### Search and use

Each row in [`catalog.csv`](catalog.csv) describes one unique `SKILL.md` content. [`skill_sources.csv`](skill_sources.csv) lists every source location where that content appeared. [`sources.csv`](sources.csv) maps source collections to preserved root-level license files.

Search the catalog in PowerShell:

```powershell
Import-Csv .\catalog.csv | Where-Object name -Match 'security'
```

The `path` column points to a skill’s `SKILL.md`. Copy its whole parent folder to keep any bundled files. For a project-local skill, place it under `.agents/skills/<skill-name>`; for a user-level skill, use the Codex user skills directory. See the [Codex skills guide](https://developers.openai.com/codex/skills) and the [Agent Skills specification](https://agentskills.io/specification). Some bundled paths are long; Windows users may need Git long-path support.

### Sources and licensing

A skill’s own license file stays with its package. Root-level source licenses are stored under `source-licenses/` and mapped in `sources.csv`. The collection contains material from many sources and license terms, so this repository does not declare one license for all contents. Check the license for an individual skill and its source before reuse or redistribution. Skills have not been manually reviewed or security-audited; read their instructions and scripts before enabling them.

**Deduplication rule:** only byte-identical `SKILL.md` files were consolidated. Same-name files with different contents remain separate. Skill files were not edited.

---

<a id="arabic"></a>
## العربية

<div dir="rtl" align="right">
يجمع هذا المستودع مهارات Codex ووكلاء الذكاء الاصطناعي، مع الملفات المرجعية والبرامج النصية والموارد المتاحة وسجلات المصادر. شمل الاستيراد الأولي <strong>1,008</strong> مجموعات مصدر.
</div>

### ملخص الاستيراد

- عُثر على **55,301** ملف `SKILL.md`.
- بقي **43,566** محتوى فريدًا بعد إزالة التكرار بمطابقة SHA-256 الدقيقة.
- دُمجت **11,735** نسخة مكررة مطابقة في نسخة واحدة.
- حُفظت الملفات المساندة للحزم المختارة و**912** ملف ترخيص على مستوى المصدر.
- لم يُستبعد أي ملف بسبب حد GitHub البالغ 100 ميغابايت للملف الواحد.

### البحث والاستخدام

يصف كل صف في [`catalog.csv`](catalog.csv) محتوى `SKILL.md` فريدًا. ويسرد [`skill_sources.csv`](skill_sources.csv) جميع مواقع المصدر التي ظهر فيها هذا المحتوى، بينما يربط [`sources.csv`](sources.csv) مجموعات المصدر بملفات الترخيص المحفوظة.

للبحث في PowerShell:

```powershell
Import-Csv .\catalog.csv | Where-Object name -Match 'security'
```

يشير العمود `path` إلى ملف `SKILL.md`. انسخ مجلد المهارة كاملًا للاحتفاظ بملفاته المرفقة. ضع المهارة الخاصة بالمشروع في `.agents/skills/<اسم-المهارة>`، أو استخدم مجلد مهارات المستخدم في Codex. بعض المسارات المرفقة طويلة؛ قد يحتاج مستخدمو Windows إلى تفعيل دعم المسارات الطويلة في Git. راجع [دليل Codex Skills](https://developers.openai.com/codex/skills) و[مواصفة Agent Skills](https://agentskills.io/specification).

### المصادر والتراخيص

يبقى ملف الترخيص الخاص بالمهارة داخل مجلدها. تُحفظ تراخيص جذر المصدر في `source-licenses/` ويجري ربطها بالمصدر في `sources.csv`. يحتوي هذا المستودع على مواد من مصادر وشروط ترخيص متعددة، لذلك لا يعلن عن ترخيص واحد يشمل كل المحتوى. تحقّق من ترخيص المهارة ومصدرها قبل إعادة الاستخدام أو النشر. لم تُراجع المهارات يدويًا ولم تخضع لتدقيق أمني؛ اقرأ التعليمات والبرامج النصية قبل تفعيلها.

**قاعدة إزالة التكرار:** دُمجت ملفات `SKILL.md` المتطابقة بايتًا فقط. أما الملفات ذات الاسم نفسه والمحتوى المختلف فتبقى منفصلة. لم تُعدّل ملفات المهارات.

---

<p align="center"><sub>Curated with source records · Built for discovery · Shared in Persian, English, and Arabic</sub></p>

