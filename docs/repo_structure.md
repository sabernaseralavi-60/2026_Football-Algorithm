# نقشهٔ ریپو — Total Football Optimizer (TFO)

این سند برای ادامهٔ کار روی سیستم محلی (VS Code + افزونهٔ Claude Code) نوشته شده: هر پوشه/فایل چیه، برای چیه، و از کجا شروع کنی.

## ۱. مستندات پروژه (Spec-Kit) — نقشهٔ راه کامل

```
.specify/memory/constitution.md          اصول پروژه (۶ اصل، ۸ گیت کیفیت) — مرجع نهایی هر تصمیم
specs/001-football-algorithm/
├── spec.md                              ۴۵ نیازمندی، ۵ داستان کاربر (P1-P5)، ۱۴ معیار موفقیت
├── plan.md                              معماری فنی، ساختار کد، وابستگی‌ها
├── research.md                          تصمیمات فاز طراحی (R1-R20) با توجیه هرکدوم
├── data-model.md                        ساختار دقیق داده‌ها (Squad، Formation، Manager و...)
├── mechanism-map.md                     جدول کامل ۱۹ مکانیزم ← خانوادهٔ عملگر ← استناد
├── related-work.md                      مرور ادبیات کامل (۱۴ الگوریتم رقیب، با راستی‌آزمایی)
├── tasks.md                             ۱۶۰ تسک پیاده‌سازی (چک‌لیست، T001-T160)
├── contracts/                           ۴ قرارداد فنی (ledger، optimizer، mechanism، results-schema)
└── checklists/requirements.md           چک‌لیست کیفیت مشخصات
```
**اگه می‌خوای بفهمی الان کجای کاریم:** اول `tasks.md` رو باز کن، ببین کدوم چک‌باکس‌ها تیک خوردن.

## ۲. کد اصلی الگوریتم — `src/tfo/`

فقط با NumPy کار می‌کنه، مستقل از هر بنچمارکی. **کاملاً تست‌شده.**

```
src/tfo/
├── registry.py          جدول ۱۹ مکانیزم ↔ خانوادهٔ عملگر ↔ استناد (منبع جدول مقاله)
├── config.py             TFOConfig — تنظیمات، ablate()/homogeneous() برای آزمایش‌های حذفی
├── squad.py              ساختار دادهٔ تیم: Squad، Ball، KeeperArchive، TabuRegister
├── clock.py               MatchClock — فیکسچرها و مرزهای تکرار
├── manager.py             لایهٔ تطبیقی (۴ حالت: BUILD_UP/CONTROL/HIGH_PRESS/CHASING)
├── engine.py              حلقهٔ اصلی الگوریتم (۹ مرحله در هر تکرار)
├── api.py, __init__.py    نقطهٔ ورود عمومی: tfo.minimize(...)
├── archetypes/            ۸ آرکی‌تایپ بازیکن (هرکدوم یک فایل جدا)
└── tactics/               ۱۱ تاکتیک تیمی (فرمیشن، پرسینگ، ضدحمله، VAR، آفساید و...)
```

## ۳. هارنس بنچمارک — `src/tfo_bench/`

اجرای آزمایش، مقایسه با baseline ها، آمار. **این بخش الگوریتم رو اجرا نمی‌کنه، فقط دور و برش رو می‌سازه.**

```
src/tfo_bench/
├── ledger.py, seeds.py         شمارندهٔ دقیق ارزیابی + بذر تصادفی مشترک بین الگوریتم‌ها
├── problems/                   ۴ مجموعه بنچمارک: cec2017.py، cec2022.py، engineering.py، tuning.py
├── algorithms/                 ۹ آداپتور: tfo_adapter، sibling (CA/GA/PSO/GWO)، woa، lshade، cmaes
│   └── vendor/                 کپی فایل الگوریتم شطرنج (فقط برای استفادهٔ baseline، فقط‌خواندنی)
├── runner.py, records.py       اجرای آزمایش‌ها + نوشتن CSV نتایج
├── audit.py, stats.py          ممیزی صحت داده + آمار (Wilcoxon/Holm/Friedman)
└── manifest.py                 ثبت محیط اجرا (نسخهٔ کتابخانه‌ها، سخت‌افزار) برای بازتولیدپذیری
```

## ۴. تست‌ها — `tests/` (۲۷۷ تست، همه پاس)

```
tests/unit/          یک تست به‌ازای هر مکانیزم (۱۹ فایل) + هستهٔ الگوریتم
tests/contract/      تست قراردادها (هر الگوریتم باید این ۸ قانون رو رعایت کنه)
tests/integration/   تست‌های end-to-end (سوییچ‌پذیری مکانیزم‌ها، بازتولیدپذیری)
tests/golden/        تست مقایسه با مقادیر مرجع شناخته‌شده
```
اجرا: `pytest tests/unit tests/contract tests/integration tests/golden -q`

## ۵. اسکریپت‌های اجرایی — `scripts/`

```
run_suite.py              اجرای اصلی بنچمارک (--suite, --functions, --algorithms, --runs, --budget)
tune.py, pilot.py         تنظیم پارامتر + برآورد هزینهٔ محاسباتی قبل از اجرای کامل
audit_preflight.py         ممیزی صحت توابع بنچمارک قبل از اعتماد به نتایج
validate_results.py        اعتبارسنجی فرمت فایل‌های نتیجه
make_mechanism_table.py    رندر خودکار جدول مقاله از registry.py (هیچ‌وقت دستی ننویس)
```

## ۶. تنظیمات و داده — `config/`, `results/`, `docs/`

```
config/protocol.toml        پیش‌ثبت‌نامهٔ کامل آزمایش (بودجه، seed، فرضیه‌های H1-H5) — تگ prereg-v1
config/tfo_frozen.toml       پارامترهای نهایی TFO بعد از tuning — تگ tfo-frozen-v1
results/raw/                 نتایج خام CSV هر اجرا
results/audit/                گزارش ممیزی صحت هر تابع بنچمارک
docs/reviewer_audit_packet.md   بستهٔ ممیزی داور (جدول مکانیزم + توصیف بدون استعاره + ممیزی هم‌پوشانی با CA)
```

## ۷. فایل‌های وابستگی

```
pyproject.toml               تعریف پکیج‌های tfo و tfo_bench
requirements-lock.txt        نسخه‌های دقیق‌پین‌شده (numpy, cec2017-py, opfunu, niapy, cma, ...)
requirements-nodeps.txt      mealpy (باید با --no-deps نصب بشه، طبق research.md R1)
```

---

## راه‌اندازی روی سیستم محلی (VS Code + Claude Code)

```bash
git clone https://github.com/sabernaseralavi-60/2026_Football-Algorithm.git
cd 2026_Football-Algorithm
python -m venv .venv
source .venv/bin/activate        # ویندوز: .venv\Scripts\activate
pip install -r requirements-lock.txt
pip install --no-deps -r requirements-nodeps.txt
pip install -e .
pytest tests/unit tests/contract tests/integration tests/golden -q   # باید 277 passed بده
```

**نکات مهم برای ادامهٔ کار:**
- ۸ فایل PDF مقالات مرجع (که آپلود کرده بودی) در گیت نیستن (عمداً، به‌خاطر کپی‌رایت ناشر — طبق `.gitignore`). اگه لازمشون داری، از دانلودهای خودت کپی کن.
- تگ‌های `prereg-v1` و `tfo-frozen-v1` رو با `git fetch --tags` می‌گیری.
- قبل از هر کار جدید، `specs/001-football-algorithm/tasks.md` رو چک کن ببین کجای ۱۶۰ تسک هستیم.
- گزارش پایلوت آزمایشی (کوچک، فقط برای اطمینان از مسیر درست، نه نتیجهٔ نهایی) در `results/raw/pilot/pilot_report.json` هست.
