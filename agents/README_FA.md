# رجیستری ایجنت‌های Financial ML Core+

آخرین بازبینی: 2026-11-06  
وضعیت: نقشه نقش‌ها ساده شده؛ ایجنت‌های مستقل هنوز به‌صورت سرویس مستقر نشده‌اند.

> **نقشه اجرایی جاری:** [نقشه راه ساده‌شده](../docs/STREAMLINED_AGENT_ROADMAP_FA.md). معماری ۹ نقش پایین‌تر، سابقه طراحی است. در مسیر فعال، وظایف AGENT_04 در AGENT_03 ادغام شده، W3 تعلیق است و W0 ربات پایه است نه یک Agent هوش مصنوعی.

## آرایش فعال

- هماهنگی: AGENT_00
- ربات مرجع: W0
- داده و Candidate Ledger: AGENT_01
- MT5 و اجرای بک‌تست: AGENT_02
- HMM: W1 و ML: W2 به‌صورت موازی پس از عبور از Gate داده
- ممیزی و حاکمیت داده: AGENT_03
- W3 فقط بعد از اثبات ارزش مستقل W1/W2 فعال می‌شود.

## شمارش صحیح

این معماری **۹ نقش** دارد:
- یک هماهنگ‌کننده: AGENT_00
- چهار ایجنت نسخه‌ای: W0، W1، W2، W3
- چهار ایجنت زیرساختی/کنترلی: AGENT_01 تا AGENT_04

این‌ها نقش‌های منطقی مستقل‌اند؛ لزوماً به معنی ۹ مدل هوش مصنوعی یا ۹ پردازش مستقل نیستند. ممکن است در پیاده‌سازی با یک مدل پایه و ابزارها/دسترسی‌های تفکیک‌شده اجرا شوند. استقلال ممیزی نیز با جداسازی دسترسی، خروجی خام و آزمون خودکار تقویت می‌شود، نه صرفاً با نام‌گذاری Agent.

## فهرست

| شناسه | نام | مالکیت | مجوز اصلی |
|---|---|---|---|
| AGENT_00 | Orchestrator | جریان کار | تخصیص کار و کنترل وابستگی‌ها |
| W0 | Wyckoff Baseline | نسخه مرجع | توسعه در شاخه آزمایشی و ثبت رویداد |
| W1 | HMM Regime | نسخه رژیم | آموزش HMM فقط در Train |
| W2 | ML Scoring | نسخه امتیازدهی | آموزش و امتیازدهی ستاپ‌ها |
| W3 | Hybrid (تعلیق تا عبور W1/W2) | مرحله مشروط | ادغام کنترل‌شده خروجی W1 و W2 |
| AGENT_01 | Data & Event Engineering | داده | کیفیت، ثبت رویداد و Dataset |
| AGENT_02 | Execution & Backtesting | اجرا | شبیه‌سازی هزینه/سفارش و تطبیق |
| AGENT_03 | Independent Auditor | ممیزی | بررسی مستقل و گزارش PASS/CONDITIONAL/REJECT |
| AGENT_04 | Research Governance (وظایف ادغام‌شده در AGENT_03) | سابقه طراحی | Freeze فرضیه، معیار، Fold و تغییرات |

## ترتیب وابستگی

`AGENT_04` پروتکل و فرضیه را Freeze می‌کند. `AGENT_01` داده و Event Ledger را آماده می‌کند. `W0` منبع فرصت‌های ساختاری است. `AGENT_02` رفتار اجرای مشترک را تثبیت می‌کند. `AGENT_03` Gateهای مربوط را ممیزی می‌کند. پس از تأیید دیتاست و قرارداد برچسب، `W1` و `W2` می‌توانند موازی کار کنند؛ `W3` بعد از تثبیت خروجی‌های آن دو آغاز می‌شود.

## قاعده اختیار

هیچ Agent مجاز به:
- ارسال سفارش واقعی یا دسترسی به اعتبارنامه حساب معاملاتی نیست.
- تغییر خاموش W0، قواعد ریسک یا موتور اجرا نیست.
- آموزش یا تنظیم روی Test/OOS نیست.
- تأیید مستقل کار خودش نیست.
- حذف فرصت نامطلوب از Event Ledger نیست.

هر تغییر باید با شناسه آزمایش، Commit، نسخه داده و تنظیمات ثبت شود. تصمیم‌های Gate و تغییر پروتکل در اختیار AGENT_04 و تأیید انسانی است.

## فایل‌های اختصاصی

- [AGENT_00 — Orchestrator](AGENT_00_ORCHESTRATOR_FA.md)
- [W0 — Wyckoff Baseline](AGENT_W0_WYCKOFF_FA.md)
- [W1 — HMM Regime](AGENT_W1_HMM_FA.md)
- [W2 — ML Scoring](AGENT_W2_ML_FA.md)
- [W3 — Hybrid](AGENT_W3_HYBRID_FA.md)
- [AGENT_01 — Data & Event Engineering](AGENT_01_DATA_ENGINEERING_FA.md)
- [AGENT_02 — Execution & Backtesting](AGENT_02_EXECUTION_BACKTEST_FA.md)
- [AGENT_03 — Independent Auditor](AGENT_03_AUDITOR_FA.md)
- [AGENT_04 — Research Governance](AGENT_04_GOVERNANCE_FA.md)

## قراردادهای مشترک

- [Event و Candidate Schema](../contracts/EVENT_AND_CANDIDATE_SCHEMA_FA.md)
- [Feature و Label Schema](../contracts/FEATURE_LABEL_SCHEMA_FA.md)
- [Experiment و Fold Schema](../contracts/EXPERIMENT_AND_FOLD_SCHEMA_FA.md)
- [Result و Audit Schema](../contracts/RESULT_AND_AUDIT_SCHEMA_FA.md)
- [پروتکل کلان Financial ML Core+](../docs/FINANCIAL_ML_CORE_PLUS_PROTOCOL_FA.md)


## استقرار و گردش کار
- [مدل استقرار، مجوزها و چرخه Job](EXECUTION_AND_HANDOFF_MODEL_FA.md)
- [قرارداد تحویل بین ایجنت‌ها](../contracts/AGENT_HANDOFF_SCHEMA_FA.md)
- [برنامه راه‌اندازی BOOT-001 تا BOOT-007](../docs/FINANCIAL_ML_CORE_PLUS_BOOTSTRAP_PLAN_FA.md)


## وضعیت آمادگی داده
- [ممیزی آمادگی داده و Candidate Identity](../reports/20261104_FINANCIAL_ML_DATA_READINESS_AUDIT_FA.md)
- قرارداد schema 1.1-draft، SetupID قدیمی را به‌عنوان legacy_setup_id می‌شناسد؛ candidate_id مستقل باید در instrumentation جدید تولید شود.


## کنترل خودکار مخزن
- [Preflight Validator](../scripts/validate_financial_ml_preflight.py)
- [GitHub Actions workflow](../.github/workflows/financial-ml-preflight.yml)

این workflow فقط قراردادها، هویت سورس و تطابق SETها را به‌صورت ایستا بررسی می‌کند؛ Compile/Tester را انجام نمی‌دهد.


## BOOT-003 Event Ledger v2
- [مشخصات instrumentation MQL5](../docs/BOOT_003_MQL5_EVENT_LEDGER_V2_SPEC_FA.md)
- قراردادهای Event/Candidate و Feature/Label اکنون schema 1.2-draft هستند؛ Event Ledger legacy به‌تنهایی داده آموزشی محسوب نمی‌شود.


## شروع موازی Sprint — 2026-11-04

برای ۹ نقش، Issueهای GitHub #2 تا #10 و branchهای مستقل ایجاد شده‌اند. [برنامه موازی](../docs/PARALLEL_AGENT_LEARNING_SPRINT_FA.md) و [Manifest](../experiments/PARALLEL_AGENT_SPRINT_20261104.json).

W1/W2/W3 بسته‌های شروع پژوهشی مستقل دارند. این‌ها role-based workspaces و دستورکارهای قابل اجرا هستند؛ سرویس‌های Agent مستقل و دائماً فعال نیستند. همه کارها باید با artifact و evidence گزارش شوند.
