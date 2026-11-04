# وضعیت فعلی پروژه Wyckoff W0 — 2026-11-04

> وضعیت پژوهشی/آزمایشی. هیچ نسخه‌ای برای حساب واقعی تأیید نشده است.

## هدف و چارچوب

- پلتفرم: MetaTrader 5؛ نماد اصلی XAUUSD؛ محیط تست گزارش‌شده WMMarkets-Demo.
- H4: زمینهٔ بالادستی و فیلتر اختیاری.
- H1: تشخیص Range، Spring/UTAD، Test و Strength.
- M5: Breakout → Retest → Recovery/Confirmation → Entry.
- خرید: Accumulation/Range → Spring → Test → SOS → LPS → تأیید M5.
- فروش: Distribution/Range → UTAD → Test → SOW → LPSY → تأیید M5.
- ریسک هدف گزارش‌شده 0.5% و RR هدف 2.0 است؛ تحقق ریسک واقعی در هر معامله باید با حجم نهایی و مشخصات قرارداد کنترل شود.

## برآورد پیشرفت

| محور | درصد برآوردی |
|---|---:|
| پیشرفت کلی مهندسی | **55%** |
| اعتبارسنجی استراتژی | **25%** |
| آمادگی عملیاتی | **10%** |

این ارقام برآورد کیفی‌اند و با هم میانگین ساده یا KPI خودکار نیستند. تفصیل: [PROJECT_PROGRESS_ESTIMATE_FA.md](PROJECT_PROGRESS_ESTIMATE_FA.md).

## وضعیت فنی اجزا

| بخش | برآورد | وضعیت |
|---|---:|---|
| استراتژی/قواعد | 65% | بخش زیادی تعریف شده؛ ابهام‌های ساختاری باقی است |
| کدنویسی EA | 85% | نسل‌های سورس و state machine موجود؛ کامپایل نهایی هر نسخه باید مستقل تأیید شود |
| ممیزی H1 | 80% | H1STRUCT Audit اجرا و تحلیل شده |
| ورود M5 | 65% | مسیر اجرا شده؛ دادهٔ معاملاتی کافی نیست |
| MultiAudit | 10% | سورس/SET و بررسی ایستا؛ Compile و Tester تأیید نشده |
| داده | 55% | OHLC و ساخت MTF بررسی؛ محدودیت tick/spread باقی |
| بک‌تست/آمار | 25% | چند تست محدود؛ تعداد معاملات ناکافی |
| ریسک/اجرا | 40% | محاسبات و سفارش ثبت شده؛ گپ/لغزش و fill نیازمند بررسی |
| OOS/Walk-Forward | 0% | انجام نشده/تأیید نشده |
| Forward Demo/Live | 0% | تأیید نشده |

## آخرین اجرای ممیزی H1STRUCT

Journal ارائه‌شده، Expert را `Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_AUDIT.ex5` نشان می‌دهد؛ تیک‌ها 177,991,586 و موجودی نهایی 9,937.56 USD بوده است. در برابر موجودی آغازین 10,000 USD، نتیجهٔ خالص -62.44 USD است؛ یک BUY و یک زیان.

قیف ساختاری گزارش‌شده:
- 67 Range
- 15 Spring و 8 UTAD تأییدشده
- 16 Test
- 6 SOS و 3 SOW
- 4 LPS و 2 LPSY
- 3 M5 breakout، 2 Retest و 1 ورود

هر 9 سیگنال SOS/SOW ممیزی‌شده شکست Swing داخلی بوده‌اند؛ شکست لبهٔ اصلی Range در آن‌ها وجود نداشته است. این موضوع تعریف Strength را به مسئلهٔ اصلی تحقیق تبدیل می‌کند. آزمون Range-edge-only بسیار محدودکننده بوده و هنوز نباید شرط اجباری شود.

## آخرین مسئلهٔ اجرای معامله

ورود BUY در 4729.47 با SL=4712.14 و حجم 0.02؛ ریسک محاسبه‌شده 34.66 USD (حدود 0.347%). خروج ثبت‌شده در 4698.78، یعنی 13.36 دلار قیمت بدتر از SL، و خالص نتیجه -62.44 USD با realizedR=-1.802. باید شکاف بازگشایی پس از تعطیلی آخر هفته با تیک‌ها بررسی شود.

## نسخهٔ تشخیصی بعدی

`Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT.mq5` و SETهای Lookback مبنا=5، SL10 و SL20 در مخزن قرار دارند. اعتبارسنجی ایستا و تطابق SET با 67 ورودی ثبت شده؛ کامپایل MetaEditor و اجرای Strategy Tester هنوز تأیید نشده است.

## تصمیم‌های تثبیت‌شده

1. C2 پایه بدون تغییر حفظ شود.
2. MultiAudit صرفاً diagnostics باشد و Lookbackهای 5/10/20/40 و Pivot را ثبت کند.
3. شکست Swing داخلی، Pivot-zone candidate و Range-edge از هم تفکیک شوند.
4. Creek/Ice هنوز candidate است، نه سطح قطعی معامله.
5. تا تکمیل ممیزی ساختار، RR، ریسک، تلورانس Retest و فیلترهای Spring/UTAD تغییر نکنند.
6. نتیجهٔ یک معامله به‌هیچ‌وجه اثبات edge یا سودآوری نیست.

## اولویت بعدی

Compile واقعی MultiAudit، سپس اجرای SETهای 5/10/20 با یک Expert، بازه و شرایط ثابت؛ بعد مقایسهٔ رویدادهای H1، M5، خروجی معاملات و دادهٔ اجرا. سپس آزمون OOS و Forward Demo.

## مستندات مرجع

- [آرشیو گفتگو و پیشرفت](CHAT_AND_PROJECT_PROGRESS_FA.md)
- [معماری ده‌لایه](PROJECT_ARCHITECTURE_FA.md)
- [برآورد پیشرفت](PROJECT_PROGRESS_ESTIMATE_FA.md)
- [تاریخچه بک‌تست](BACKTEST_HISTORY_FA.md)
- [مرور عمیق H1STRUCT](../reports/20261104_H1STRUCT_MULTI_LOOKBACK_DEEP_REVIEW_FA.md)
- [تحلیل اجرای H1STRUCT](../reports/20261104_H1STRUCT_AUDIT_RUN_ANALYSIS_FA.md)


## Financial ML Core+ و معماری ایجنت‌ها — ثبت 2026-11-04

اولین بررسی BOOT-001 انجام و نتیجه با وضعیت CONDITIONAL ثبت شد: [گزارش تطبیق هویت Baseline W0](../reports/20261104_W0_BASELINE_IDENTITY_FA.md). C2-T030-SB050 Baseline candidate است؛ Freeze نهایی به تطبیق SET اجرای تاریخی و زنجیره EX5/Build وابسته است.

پروتکل پژوهشی Financial ML Core+ و مشخصات **۹ نقش منطقی** در مخزن ثبت شده‌اند:
- یک هماهنگ‌کننده (AGENT_00)
- چهار ایجنت نسخه‌ای (W0، W1، W2، W3)
- چهار ایجنت پشتیبان (AGENT_01 تا AGENT_04)

مستندات:
- [پروتکل Financial ML Core+](FINANCIAL_ML_CORE_PLUS_PROTOCOL_FA.md)
- [رجیستری و System Promptها](../agents/README_FA.md)
- [قراردادهای داده و آزمایش](../contracts/EVENT_AND_CANDIDATE_SCHEMA_FA.md)

**وضعیت دقیق:** این فایل‌ها مشخصات طراحی و Prompt هستند؛ ایجنت‌ها هنوز به‌عنوان سرویس/عامل مستقل مستقر یا فعال نشده‌اند. هیچ بک‌تست، Compile، آموزش HMM/ML یا Forward Demo جدیدی صرفاً با ثبت این اسناد انجام نشده است.

**Gateهای فعلی:** ابتدا Compile و اجرای واقعی MultiAudit؛ سپس تکمیل Event/Candidate Ledger؛ پس از آن Freeze برچسب‌ها و Purged Walk-Forward/Embargo؛ فقط بعد از عبور این مراحل W1 و W2 و سپس W3 وارد آزمایش شوند. W0 باید Baseline ثابت باقی بماند. هیچ نسخه‌ای برای Live تأیید نشده است.


- [برنامه راه‌اندازی و بسته‌های کاری BOOT-001 تا BOOT-007](FINANCIAL_ML_CORE_PLUS_BOOTSTRAP_PLAN_FA.md)
- [مدل استقرار و تحویل Agentها](../agents/EXECUTION_AND_HANDOFF_MODEL_FA.md)
- [قرارداد تحویل Agentها](../contracts/AGENT_HANDOFF_SCHEMA_FA.md)

اولین اقدام اجرایی، BOOT-001 یعنی تطبیق هویت دقیق Baseline است؛ پس از آن BOOT-002 نیازمند Compile و اجرای واقعی MultiAudit در محیط MT5/MetaEditor خواهد بود.


## ممیزی آمادگی داده Financial ML — 2026-11-04

[گزارش کامل آمادگی داده](../reports/20261104_FINANCIAL_ML_DATA_READINESS_AUDIT_FA.md) اضافه شد. Event CSV آرشیوشده C2 مربوط به اجرای 2026-11-03 تا 2026-10-17 است و 65 Range / 15 Test / 6 SOS / 2 SOW دارد. این شمارش با اجرای جداگانه‌ای که گزارش C2 مورخ 2026-11-04 تا 2026-11-04 توصیف می‌کند یکی فرض نمی‌شود؛ CSV آن اجرای جدید در مخزن حاضر نیست.

در سورس C2، SetupID هنگام شناسایی Range افزایش می‌یابد؛ بنابراین شناسه Candidate نیست. قراردادها به schema 1.1-draft ارتقا یافتند و سلسله‌مراتب range_id/cycle_id/attempt_id/candidate_id/legacy_setup_id را مشخص می‌کنند.

**نتیجه آمادگی:** Event Funnel Audit قابل انجام است، اما Dataset supervised و HMM/ML هنوز BLOCKED هستند. فایل خام M1/Tick، Feature Snapshot، Label Outcome و Fold manifest هنوز در مخزن موجود نیستند. W1/W2/W3 تا رفع این کمبودها قفل می‌مانند.


- [ممیزی آمادگی داده و Candidate Identity](../reports/20261104_FINANCIAL_ML_DATA_READINESS_AUDIT_FA.md)
- [گزارش اجرای C2 و تفکیک دو بازه](../reports/20261104_W0_BASELINE_IDENTITY_FA.md)

وضعیت جدید: Event Funnel قابل تحلیل است؛ Event/Candidate schema به 1.1-draft رسیده؛ اما خام M1/Tick، Feature Snapshot و Label Outcome در مخزن حاضر نیستند. W1/W2/W3 همچنان BLOCKED هستند.


## بازبینی ایستای MultiAudit v1.084 — 2026-11-04

[گزارش مقایسه مستقیم v1.083 و v1.084](../reports/20261104_MULTIAUDIT_STATIC_CODE_REVIEW_FA.md) ثبت شد. LCS خطی: 1,767 خط مشترک به‌ترتیب؛ 117 خط افزوده و 4 خط حذف‌شده که فقط metadata هستند. در بازبینی ایستا هیچ خط اجرایی موجود حذف نشده است؛ افزوده‌ها مربوط به لاگ Lookback/Pivot و افزایش history request در حالت انتظار Strength هستند.

این PASS فقط برای Static Review است. Compile در MetaEditor و اجرای MT5 Strategy Tester هنوز انجام/تأیید نشده‌اند؛ وضعیت MultiAudit همچنان منتظر اجرای محیطی است.


- [کارت اجرای MT5 برای BOOT-002](BOOT_002_MULTIAUDIT_RUN_CARD_FA.md)
- [قالب manifest ماشینی هر Run](../experiments/BOOT_002_RUN_MANIFEST_TEMPLATE.json)


### وضعیت CI برای MultiAudit

اولین Preflight مخزن در GitHub Actions با نتیجه success اجرا شده است: [Run 41856290720](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41856290720)، Commit `ec3f92cb94737f63f73c9276827b5f5dac934aaf`. [manifest نتیجه](../experiments/BOOT_002_STATIC_PREFLIGHT_RUN_001.json).

این نتیجه محدود به بررسی ایستای کد/SET/قراردادها است و نه Compile یا Strategy Tester. BOOT-002 تا اجرای واقعی MetaEditor و MT5 باز می‌ماند.


گزارش [دو اجرای موفق Preflight](../reports/20261104_BOOT_002_CI_VERIFICATION_FA.md) نیز ثبت شد. این کنترل فقط static repository validation است؛ BOOT-002 هنوز نیازمند MetaEditor Compile و Strategy Tester برای Lookbackهای 5/10/20 است.


## به‌روزرسانی BOOT-001 و BOOT-002 — 2026-11-04

- C2-T030-SB050 به‌عنوان Baseline candidate شناسایی شده است. از Journal اجرای 2026-11-03 هر 67 ورودی استخراج و SET بازسازی‌شده ساخته شده؛ 67/67 مقدار با سورس v1.082 و Journal منطبق است. [گزارش بازسازی SET](../reports/20261104_W0_C2_SET_RECONSTRUCTION_FA.md) و [manifest اجرای تاریخی](../experiments/W0_C2_BASELINE_RUN_20261103.json).
- فایل اصلی SET تاریخی و hash باینری EX5 آن اجرا در دسترس نیستند؛ Freeze نهایی Baseline هنوز CONDITIONAL است.
- Preflight پیشرفته GitHub Actions با 24 کنترل، 24 PASS و صفر FAIL روی Commit eb43035187a2f4e2ab2dfbd8aebea838c555949a اجرا شد: [Run 41858327181](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41858327181). این فقط Static Repository Validation است.
- BOOT-002 اکنون چهار Run دارد: H1STRUCT v1.083/LB5، MultiAudit v1.084/LB5 (جفت کنترل)، و MultiAudit/LB10 و LB20 (حساسیت قانون SOS/SOW).
- Lookback10/20 صرفاً diagnostics نیستند؛ مقدار Lookback سطح priorHigh/priorLow فعال در ProcessWaitStrength را تغییر می‌دهد.

**وضعیت اجرا:** دو Compile واقعی و چهار Strategy Tester Run هنوز انجام نشده‌اند. W1/W2/W3 همچنان BLOCKED هستند.


## نتیجه نهایی Preflight و طراحی چهار Run — 2026-11-04

دو اجرای متوالی Preflight پس از ارتقای Validator و Run Card هر دو 27 PASS و 0 FAIL داشتند:
- [Run 41858805308](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41858805308)
- [Run 41858859791](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41858859791)

[Manifest ماشینی](../experiments/BOOT_002_STATIC_PREFLIGHT_RUN_003.json).

BOOT-002 به چهار Run A/B/C/D تغییر کرده است: v1.083/LB5، v1.084/LB5، v1.084/LB10 و v1.084/LB20. Lookback10/20 شرط فعال SOS/SOW را تغییر می‌دهند و sensitivity آزمایشی‌اند. Preflight فقط کنترل ایستای مخزن است؛ دو Compile و چهار MT5 Tester Run هنوز NOT RUN هستند.


## BOOT-003 — مهاجرت اولیه Legacy Event Ledger

اسکریپت محافظه‌کارانه [migrate_legacy_event_csv.py](../scripts/migrate_legacy_event_csv.py) و تست‌های واحد آن در مخزن ثبت شده‌اند. هدف تبدیل Event CSV اجرای C2 به Event Ledger استاندارد است؛ هیچ candidate_id، cycle_id، attempt_id، UTC یا Label حدس زده نمی‌شود. GitHub Actions آن را به‌صورت تست واحد + مهاجرت واقعی اجرا و خروجی CSV/manifest را به‌صورت Artifact ذخیره خواهد کرد.

این فقط گام آغازین BOOT-003 است؛ instrumentation جدید MQL5 و Candidate Ledger کامل هنوز انجام نشده‌اند. W1/W2/W3 همچنان BLOCKED هستند.


## نتیجه BOOT-003 — Legacy Event Ledger اولیه

Run [41859743204](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41859743204) با موفقیت:
- Preflight: 27 PASS / 0 FAIL
- Unit tests: 5/5 موفق
- ورودی و خروجی normalized: 346 / 346 ردیف
- Range groups مبتنی بر شناسه legacy: 65
- Candidate/Cycle/Attempt ID و Label ساخته‌شده: صفر
- SHA-256 خروجی CSV: `5e1d95e2e1174e7af81771a7e506675d4a0221576011de530fc748ddc9860f7e`

[گزارش مهاجرت](../reports/20261104_LEGACY_EVENT_LEDGER_MIGRATION_RUN_FA.md) و [manifest ماشینی](../experiments/BOOT_003_LEGACY_EVENT_MIGRATION_RUN_001.json).

Artifact با نام `legacy-event-ledger-1efbb979e031898521aab9ccab799f1fc143fa71` در صفحه Run بالا برای 30 روز قابل دریافت است. این فقط Event Ledger قدیمی است؛ Event/Candidate instrumentation جدید MQL5 همچنان باز است و Dataset آموزشی W1/W2/W3 هنوز آماده نیست.


## وضعیت BOOT-003 پس از طراحی Event Ledger v2

Legacy Event Migration با 346 ردیف و 65 Range group موفق شده است؛ گزارش در [20261104_LEGACY_EVENT_LEDGER_MIGRATION_RUN_FA.md](../reports/20261104_LEGACY_EVENT_LEDGER_MIGRATION_RUN_FA.md).

قراردادهای Event/Candidate و Feature/Label به schema 1.2-draft ارتقا یافته‌اند. [مشخصات instrumentation v2](BOOT_003_MQL5_EVENT_LEDGER_V2_SPEC_FA.md) تعیین می‌کند Candidate در M5 Recovery و پیش از PlaceTrade ساخته شود؛ بنابراین ردهای اجرایی نیز ثبت می‌شوند. هیچ کد MQL5 برای این تغییر هنوز پیاده‌سازی یا Compile نشده است.


## شروع موازی ۹ نقش — 2026-11-04

نه مسیر کاری مستقل در GitHub ثبت شده‌اند: Issueهای #2 تا #10 و branchهای `agent/00...`، `agent/01...`، `agent/02...`، `agent/03...`، `agent/04...`، `agent/w0...`، `agent/w1...`، `agent/w2...` و `agent/w3...`.

- [برنامه موازی و وابستگی‌ها](PARALLEL_AGENT_LEARNING_SPRINT_FA.md)
- [Manifest ماشینی Sprint](../experiments/PARALLEL_AGENT_SPRINT_20261104.json)
- [W1 HMM research starter](W1_HMM_REGIME_RESEARCH_STARTER_FA.md)
- [W2 ML scoring starter](W2_ML_CANDIDATE_SCORING_STARTER_FA.md)
- [W3 Hybrid starter](W3_HYBRID_INTEGRATION_STARTER_FA.md)

**شفافیت اجرا:** Issue و branchها مسیرهای role-based tracking هستند؛ ۹ پردازه مستقل Agent به‌صورت سرویس خودکار مستقر نشده‌اند. یادگیری پژوهشی و prototypeهای synthetic مجازند؛ fit روی XAUUSD واقعی تا تکمیل Candidate/Feature/Label dataset، داده خام معتبر و Gateهای MT5 مسدود است.
