# برنامهٔ ادامهٔ کار — نوشته‌شده برای یه نشست تازهٔ Claude Code روی سیستم محلی

این سند طوری نوشته شده که کافیه بهش لینک بدی یا بگی «طبق `docs/NEXT_STEPS.md` ادامه بده» و یه Claude
تازه (بدون هیچ حافظه‌ای از نشست‌های قبلی) بتونه دقیقاً از همین‌جا ادامه بده، بدون این‌که کاری رو
دوباره انجام بده یا تصمیمی رو که قبلاً گرفته شده دوباره بگیره.

**تاریخ آخرین به‌روزرسانی این سند:** بلافاصله بعد از commit شدن `db0e133` (چک وضعیت با
`git log --oneline -5` رو انجام بده تا مطمئن بشی commit جدیدتری از این سند نیومده).

---

## ۱. وضعیت دقیق الان (قبل از هر کاری این رو تأیید کن)

اجرا کن:
```bash
pytest tests/unit tests/contract tests/integration tests/golden -q
```
باید **277 passed** بده. اگه نداد، قبل از هر کار دیگه‌ای اون رو دیباگ کن — یعنی یه چیزی روی
سیستم محلی فرق داره (نسخهٔ پایتون، وابستگی‌ها).

### چی کامل شده (تأیید‌شده، تست‌شده، commit و push شده)
- **Phase 1 (Setup)** — کامل. تسک‌های T001–T008.
- **Phase 2 (Foundational)** — کامل. تسک‌های T009–T108: کل الگوریتم TFO (۱۹ مکانیزم مستقل و
  قابل‌سوییچ)، هارنس `tfo_bench` (ledger، ۴ مجموعهٔ بنچمارک، ۹ آداپتور الگوریتم)، pipeline ممیزی
  داده، و گیت‌های pre-registration. تگ‌های گیت `prereg-v1` و `tfo-frozen-v1` هر دو زده شدن
  (`git tag -l` رو چک کن؛ اگه با `git clone` عادی گرفتی باید بیان، اگه نیومدن `git fetch --tags`).
- **Phase 3 / User Story 1 (بستهٔ ممیزی داور)** — کامل. تسک‌های T109–T116.
- **`specs/001-football-algorithm/tasks.md`** به‌روز شده: چک‌باکس‌های T001–T116 تیک خوردن،
  چون واقعاً commit شدن (این رو خودم دستی تیک زدم چون قبلاً commit تسک‌ها انجام شده بود ولی
  چک‌باکس‌ها به‌روز نشده بودن — **این فایل الان قابل‌اعتماده**، از این به بعدش رو خودت با هر
  تسکی که تمومش می‌کنی تیک بزن).

### دو باگ واقعی که در این نشست پیدا و رفع شد (نباید دوباره ظاهر بشن، ولی اگه یه‌وقت با یه
مرج یا rebase عجیب برگشتن، این‌ها رو دوباره بخون)
1. **`requirements-lock.txt`**: خط cec2017-py با `#egg=cec2017-py` نصب تمیز رو می‌شکست، چون
   نام واقعی پکیج بالادستی `cec2017`ه نه `cec2017-py` (pip مدرن اسم‌ها رو چک می‌کنه). رفع شد با
   حذف فرگمنت `#egg=`.
2. **`scripts/run_suite.py`**: حالت `--smoke` داشت توی `results/raw/_smoke/` می‌نوشت، ولی
   قرارداد `results-schema.md` §۱ می‌گه `_smoke/` باید هم‌سطح `raw/` باشه (یعنی
   `results/_smoke/`)، نه زیرشاخه‌ش. رفع شد.

### وضعیت Phase 4 / User Story 2 (اجرای بنچمارک اصلی) — **در حال انجام، این‌جا متوقف شده**

`results/raw/main/{cec2017,cec2022,engineering}/` الان یه دیتاست **جزئی و واقعی** (نه smoke)
داره که با ۲ پاس روی یه نشست ابری موقت جمع شده:

- یه پاس اول: ۳ تابع دستچین‌شده از هر suite (نماینده از خانواده‌های مختلف تابع) × ۹ الگوریتم
  × ۵ اجرا، با بودجهٔ رسمی `protocol.toml` — برای sanity-check قبل از commit به کل کمپین.
  نتایجش معنادار بود و با فرضیه‌های پیش‌ثبت‌شده در `config/protocol.toml` هم‌خونی داشت:
  - **H1** (TFO بهترین گروه کلاسیک/متوسط — یعنی GA/PSO/GWO/WOA/CA — روی هر ۳ suite): روی
    CEC-2017 واضح تأیید شد (TFO/TFO-static رتبهٔ میانگین ۴.۶۷، بقیهٔ گروه ۵.۳۳ تا ۷.۳۳).
    روی CEC-2022 و مهندسی با این نمونهٔ خیلی کوچیک (۳ تابع، ۵ اجرا) نتیجه مخلوط بود — **این
    هنوز باز نیس، باید با گرید کامل ۳۰-اجراییِ نهایی دوباره بررسی بشه**، فرض نکن جواب رو
    از قبل می‌دونی.
  - **H4** (باخت مورد‌انتظار به L-SHADE و CMA-ES (IPOP)): روی هر ۳ suite تأیید شد — این
    طبق پیش‌بینی خودِ پروتکله، نشونهٔ باگ نیست.
- یه پاس دوم، بزرگ‌تر: تلاش برای همهٔ توابع (۲۹ cec2017 + ۱۲ cec2022×۲بعد + ۷ مهندسی) با
  ۱۰ اجرا (به‌جای عدد نهایی ۳۰) به‌عنوان قدم میانی قبل از کل کمپین ۳۰-اجرایی. این پاس **ناتمام
  موند** چون نشست ابری بعد از ~۲۵ دقیقه بی‌فعالیتی (حتی با وجود ۴ پردازش پرمصرف CPU در پس‌زمینه)
  کاملاً reclaim/reboot شد — این محدودیت مال اون محیط بود، **روی سیستم محلی صدق نمی‌کنه**.

هیچ داده‌ای گم نشده (`runner.py` هر `(algorithm, cell, run)` رو checkpoint می‌کنه)، فقط
کار ناتمومه. الان دقیقاً این وضعیت commit شده‌ست:
- `cec2017`: بخشی از ۲۹ تابع پوشش داده شده (بیشترش فقط F01/F09/F23، بعضی تا ۱۰ اجرا رسیدن،
  بقیه فقط ۵ تا)
- `cec2022`: فقط F01/F05/F12 در D=10، فقط ۵ اجرا (D=20 اصلاً شروع نشده)
- `engineering`: فقط WeldedBeam/PressureVessel/SpeedReducer، فقط ۵ اجرا (۴ مسئلهٔ باقی‌مونده
  اصلاً شروع نشدن)

---

## ۲. قدم بعدی دقیق (این رو همین الان اجرا کن)

چون `runner.py` بر اساس `(algorithm, cell, run)` resume می‌کنه، دستورهای زیر خودشون فقط چیزی
که کم داریم رو اضافه می‌کنن — هیچ‌کدوم از کاری که قبلاً واقعاً انجام شده رو دوباره حساب
نمی‌کنن. با `--workers` برابر تعداد هسته‌های CPU سیستمت اجرا کن.

### گام الف: تکمیل پاس ۱۰-اجرایی روی همهٔ توابع (قدم میانی)
```bash
python scripts/run_suite.py --suite cec2017 --dim 30 --runs 10 --workers <N>
python scripts/run_suite.py --suite cec2022 --dim 10 --runs 10 --workers <N>
python scripts/run_suite.py --suite cec2022 --dim 20 --runs 10 --workers <N>
for p in WeldedBeam Spring PressureVessel SpeedReducer ThreeBarTruss GearTrain CantileverBeam; do
  python scripts/run_suite.py --suite engineering --functions "$p" --runs 10 --workers <N>
done
python scripts/validate_results.py results/raw/main/cec2017
python scripts/validate_results.py results/raw/main/cec2022
python scripts/validate_results.py results/raw/main/engineering
```
بعد از این، یه نگاه بنداز به رتبه‌بندی‌ها (کد نمونه پایین، بخش ۳) و مطمئن شو H1/H4 هنوز
معنادار به‌نظر می‌رسن، هیچ الگوریتمی خطای غیرمنتظره نمی‌ده، و audit ایرادی نمی‌گیره.

### گام ب: گسترش به عدد نهایی پیش‌ثبت‌شده (۳۰ اجرا، طبق FR-030)
فقط `--runs 10` رو با `--runs 30` عوض کن، همون دستورها:
```bash
python scripts/run_suite.py --suite cec2017 --dim 30 --runs 30 --workers <N>
python scripts/run_suite.py --suite cec2022 --dim 10 --runs 30 --workers <N>
python scripts/run_suite.py --suite cec2022 --dim 20 --runs 30 --workers <N>
for p in WeldedBeam Spring PressureVessel SpeedReducer ThreeBarTruss GearTrain CantileverBeam; do
  python scripts/run_suite.py --suite engineering --functions "$p" --runs 30 --workers <N>
done
python scripts/validate_results.py results/raw/main/cec2017
python scripts/validate_results.py results/raw/main/cec2022
python scripts/validate_results.py results/raw/main/engineering
```
**تخمین محاسباتی** (از داده‌های واقعی pilot، نه نظری): این کل کمپین حدود ۱۶۶ core-hour طول
می‌کشه (سنجش کامل توی `results/raw/pilot/pilot_report.json`). با N هسته، تقریباً
`166/N` ساعت زمان واقعی. می‌تونی گام الف و ب رو یکی کنی و مستقیم `--runs 30` بزنی؛ گام الف
فقط برای این بود که با نمونهٔ کوچیک‌تر زودتر یه دید واقعی از نتایج بگیریم.

بعد از هر بخشی که تموم شد commit کن (پیام کوتاه، مثلاً «cec2017 main experiment complete,
30 runs»)، تا اگه سیستمت وسط راه خاموش شد یا قطع شد، فقط از همون‌جا resume بشه، نه از صفر.

### گام ج: تکمیل بقیهٔ Phase 4 (T120–T126) — این‌ها هنوز نوشته نشدن
بعد از این‌که دادهٔ خام کامل شد، این اسکریپت‌ها/فایل‌ها طبق
`specs/001-football-algorithm/tasks.md` (T120–T126) باید نوشته بشن — الان وجود ندارن:
- `scripts/analyze.py` (CLI که `src/tfo_bench/analyze.py` رو صدا می‌زنه؛ خودِ کتابخانه موجوده)
- `src/tfo_bench/tables.py`، `src/tfo_bench/figures.py`
- `docs/baseline_footnote.md`
- تست‌های T124، T126

جزئیات دقیق هر تسک توی خودِ `tasks.md` هست؛ همون‌جا رو منبع اصلی بدون.

---

## ۳. کد آماده برای sanity-check سریع نتایج (بعد از هر پاس)

```python
import pandas as pd
for suite in ["cec2017", "cec2022", "engineering"]:
    df = pd.read_csv(f"results/raw/main/{suite}/runs.csv")
    piv = df.groupby(["function_id", "algorithm"])["error"].mean().unstack("algorithm")
    print(suite, piv.rank(axis=1, method="average").mean().sort_values().round(2))
```
انتظار: TFO/TFO-static باید بین بهترین‌های گروه کلاسیک (GA/PSO/GWO/WOA/CA) باشن ولی به
L-SHADE و CMA-ES (IPOP) ببازن — این خودِ H1/H4 پیش‌ثبت‌شده‌ست، نه یه علامت مشکل.

---

## ۴. بعد از Phase 4: نقشهٔ راه باقی‌مونده (T127–T160)

اینا رو **به ترتیب** انجام بده (وابستگی‌هاشون توی `tasks.md`، بخش «Dependencies & Execution
Order» دقیق نوشته شده):

| فاز | چی | تسک‌ها |
|---|---|---|
| Phase 5 (US3) | Ablation (۱۸ تک‌مکانیزم خاموش + ۷ گروهی)، تحلیل توپولوژی فرمیشن (H3) | T127–T135 |
| Phase 6 (US4) | ابزار بازتولیدپذیری، گزارش بودجه، گزارش ممیزی، راهنمای بازتولید | T136–T143 |
| Phase 7 (US5) | تحلیل حساسیت پارامتر، آزمایش epsilon (قید offside) | T144–T151 |
| Phase 8 (Polish) | زمان‌سنجی، ممیزی نهایی، related-work (خوندن کامل SLOCA — هنوز باز)، چک‌لیست ارسال | T152–T160 |

هیچ‌کدوم از این اسکریپت‌ها (`run_ablation.py`، `run_sensitivity.py`، `run_epsilon.py`،
`run_timing.py`، `run_takeover.py`، `make_budget_report.py`، `make_audit_report.py`،
`reproduce.sh`) هنوز نوشته نشدن. توی `tasks.md` هر کدوم دقیقاً مشخص شده باید چی پیاده بشه.

**نکتهٔ مهم برای Phase 8 / T157:** `related-work.md` صراحتاً می‌گه متن کامل SLOCA هنوز خونده
نشده و این باید قبل از ارسال مقاله حل بشه — این یه کار باقی‌مونده‌ست، فراموش نکن.

---

## ۵. قواعد ثابت (این‌ها توی کل پروژه عوض نمی‌شن)

- بعد از هر تسک یا گروه منطقی تسک، commit کن (روش خودِ `tasks.md` هم همینه: «Commit after
  each task or logical group»).
- قبل از هر commitِ کد (نه فقط دیتا)، `pytest tests/unit tests/contract tests/integration
  tests/golden -q` رو اجرا کن، باید ۲۷۷+ پاس بشه (با اضافه‌شدن تست‌های جدید Phase 5+، عدد
  بیشتر می‌شه).
- تسک‌های `[P]` مستقل‌ان (فایل جدا، بدون وابستگی به تسک ناتموم) — می‌تونی موازی انجامشون بدی
  یا به چند subagent/session بسپاری.
- `config/protocol.toml` و `config/tfo_frozen.toml` **freeze شدن** (تگ‌های `prereg-v1` و
  `tfo-frozen-v1`) — به هیچ وجه دستی تغییرشون نده؛ `runner.py` خودش `ConfigNotFrozenError`
  می‌ده اگه هش config عوض شده باشه. اگه واقعاً لازم شد چیزی توی این فایل‌ها عوض بشه، اون یه
  تصمیم روش‌شناسی بزرگه، نه یه commit عادی — با کاربر (صاحب پروژه) هماهنگ کن.
- `results/_smoke/` هیچ‌وقت نباید توی تحلیل/آمار استفاده بشه — فقط برای تست دستی pipeline.

---

## ۶. اگه یه Claude تازه این سند رو می‌خونه و کاربر فقط گفته «طبق برنامه ادامه بده»

ترتیب دقیق کاری که باید بکنی:
1. `pytest ... -q` رو اجرا کن، مطمئن شو ۲۷۷+ پاس می‌شه.
2. `git log --oneline -10` بزن ببین از وقتی این سند نوشته شده کامیت جدیدی اومده یا نه (اگه
   اومده، بخش‌های بالا رو با وضعیت واقعی `results/raw/main/*/runs.csv` تطبیق بده، نه صرفاً
   حرف این سند رو باور کن).
3. بخش ۲ (قدم بعدی دقیق) رو شروع کن: گام الف، بعد گام ب.
4. هر بخشی که تموم شد، commit و push کن، و چک‌باکس متناظرش رو توی `tasks.md` تیک بزن.
5. بعد از تکمیل Phase 4 دادهٔ خام، برو سراغ بخش ۲ گام ج (اسکریپت‌های تحلیل)، بعد بخش ۴
   (Phase 5 تا ۸) به ترتیب.
6. اگه به یه تصمیم روش‌شناسی رسیدی که این سند جوابش رو نداره (مثلاً یه فرضیه رد شد و باید
   تصمیم گرفت چیکار کنیم، یا یه بودجهٔ محاسباتی باید عوض بشه) — **متوقف شو و از کاربر بپرس**،
   خودت تصمیم نگیر. تصمیمات محاسباتی/آماری این پروژه از قبل پیش‌ثبت‌نام شدن؛ تغییرشون بدون
   اجازهٔ صریح، پروتکل پیش‌ثبت‌نامی رو خراب می‌کنه.
