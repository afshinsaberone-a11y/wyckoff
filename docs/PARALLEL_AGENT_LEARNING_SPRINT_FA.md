# Sprint شروع موازی ۹ ایجنت — Financial ML Core+

تاریخ آغاز: 2026-11-04  
مبنای مخزن هنگام ایجاد شاخه‌ها: `9e0002dfaeae04e8a9bb2ad70fbd9b769316cf7e`  
وضعیت: **۹ مسیر کاری و یادگیری در GitHub باز شده‌اند؛ اجراهای مستقلِ سرویس‌محور هنوز فعال نیستند.**

## 1. هدف

شروع هم‌زمان تحلیل، یادگیری پژوهشی، طراحی، ممیزی و آماده‌سازی آزمایش‌ها برای ۹ نقش. مسیرهای مستقل باید خروجی‌های خود را بدون تغییر C2 baseline و بدون ادعای اجرای ابزارهای در دسترس‌نبوده تولید کنند.

## 2. نقشه کار موازی

| نقش | Issue | Branch | شروع اکنون | وابستگی/محدودیت |
|---|---:|---|---|---|
| AGENT_00 Orchestrator | [#2](https://github.com/afshinsaberone-a11y/wyckoff/issues/2) | `agent/00-orchestrator-parallel-sprint` | هماهنگی و کنترل وابستگی‌ها | ادغام پس از خروجی مسیرها |
| AGENT_01 Data | [#3](https://github.com/afshinsaberone-a11y/wyckoff/issues/3) | `agent/01-data-engineering` | Ledger، inventory و کیفیت داده | M1/Tick خام در مخزن موجود نیست |
| AGENT_02 Execution | [#4](https://github.com/afshinsaberone-a11y/wyckoff/issues/4) | `agent/02-execution-backtest` | آمادگی چهار Run و parser نتایج | Compile/Tester نیازمند MT5 کاربر |
| AGENT_03 Auditor | [#5](https://github.com/afshinsaberone-a11y/wyckoff/issues/5) | `agent/03-independent-audit` | ممیزی مستقل شواهد و Gateها | ادعاها فقط با artifact |
| AGENT_04 Governance | [#6](https://github.com/afshinsaberone-a11y/wyckoff/issues/6) | `agent/04-governance` | Label/Fold و leakage rules | Outcome dataset هنوز موجود نیست |
| W0 Wyckoff | [#7](https://github.com/afshinsaberone-a11y/wyckoff/issues/7) | `agent/w0-wyckoff-ledger` | ممیزی state machine و instrumentation | C2/MultiAudit پایه Freeze |
| W1 HMM | [#8](https://github.com/afshinsaberone-a11y/wyckoff/issues/8) | `agent/w1-hmm-regime-learning` | یادگیری HMM و forward filter روی synthetic | fit روی XAUUSD واقعی فعلاً ممنوع |
| W2 ML | [#9](https://github.com/afshinsaberone-a11y/wyckoff/issues/9) | `agent/w2-ml-scoring-learning` | یادگیری scorer و pipeline مصنوعی | Candidate/Label واقعی وجود ندارد |
| W3 Hybrid | [#10](https://github.com/afshinsaberone-a11y/wyckoff/issues/10) | `agent/w3-hybrid-integration` | معماری و قرارداد HMM+ML | integration عملیاتی تا Freeze W1/W2 متوقف |

**توضیح اجرایی:** این شاخه‌ها و Issueها فضای کاری مستقل و قابل پیگیری هستند؛ ایجاد آن‌ها به‌تنهایی ۹ پردازه/ربات مستقل را اجرا نمی‌کند. نقش‌ها هنوز سرویس‌های خودکار GitHub یا عامل‌های همیشه‌فعال نیستند. اجرای این Sprint از طریق همین گردش‌کار، خروجی‌های مستند و تحویل‌های جدا انجام می‌شود.

## 3. کارهای قابل انجام موازی در فاز اول

### مسیرهای یادگیری
- W1: HMM، Forward filtering در برابر smoothing، fit boundaries، state mapping و diagnostics.
- W2: Candidate scoring، Logistic baseline، tree challenger، calibration و economic evaluation.
- W3: 2×2 factorial design، interface و failure behavior.
- AGENT_04: قرارداد point-in-time و Purged/Embargo fold.
- AGENT_03: ممیزی مستقل ادعاهای علمی/فنی و شواهد موجود.

### مسیرهای داده/اجرا/استراتژی
- AGENT_01: مهاجرت Event CSV موجود، Data inventory و آماده‌سازی validator.
- W0: state lifecycle و MQL5 Event Ledger v2 در branch مجزا.
- AGENT_02: آماده‌سازی Compile/Tester و parser چهار Run؛ اجرای MT5 تا دسترسی به محیط کاربر مسدود است.
- AGENT_00: مدیریت وابستگی‌ها، تصمیم‌ها و ادغام کنترل‌شده.

## 4. قواعد مشترک همه مسیرها

1. C2 baseline، H1STRUCT v1.083 و MultiAudit v1.084 دست‌نخورده بمانند.
2. هیچ مسیر پژوهشی، مدل یا feature را روی داده آینده‌نگر/label leakage آموزش ندهد.
3. HMM live feature باید filtered probability باشد؛ smoothed posterior که از داده آینده استفاده می‌کند ممنوع است.
4. تمام preprocessors، scalerها، feature selection و model fitting فقط داخل Train هر Fold انجام شوند.
5. Synthetic prototype فقط صحت کد/منطق را می‌سنجد و نتیجه مالی XAUUSD محسوب نمی‌شود.
6. Event CSV قدیمی 346 ردیف دارد اما Candidate dataset نیست؛ فقط یک معامله واقعی در اجرای C2 مورد استناد ثبت شده است.
7. هیچ‌یک از Issueها تا تحویل artifact، تست و گزارش محدودیت‌ها Complete نشوند.

## 5. Gateهای هماهنگ‌کننده

| Gate | شرط | وضعیت آغاز |
|---|---|---|
| G0 — Baseline Identity | سورس/SET/EX5/Journal قابل ردیابی | CONDITIONAL |
| G1 — BOOT-002 | دو Compile و چهار Run A/B/C/D + audit | OPEN؛ MT5 evidence لازم |
| G2 — Event Ledger v2 | instrumentation، compile و replay | SPECIFIED؛ NOT IMPLEMENTED |
| G3 — Data/Execution | M1/Tick coverage و costs قابل ممیزی | BLOCKED تا داده خام |
| G4 — Label/Fold | Candidateها، label windows، purge/embargo | طراحی موازی؛ داده واقعی ناقص |
| G5 — Learning Readiness | G0 تا G4 با تصمیم ممیزی | BLOCKED |
| G6 — W1/W2 evaluation | out-of-fold/OOS، ثبات و after-cost | پس از G5 |
| G7 — W3 integration | W1 و W2 مستقل و Freeze | پس از G6 |

## 6. سیاست شروع یادگیری

- **شروع الآن:** مطالعه، طراحی، پیاده‌سازی toy/synthetic، unit test، API/interface و research note.
- **شروع بعد از داده/گیت:** fit HMM واقعی، supervised ML واقعی، selection و threshold tuning.
- **شروع بعد از MT5:** مقایسه عملکرد معاملاتی، execution sensitivity و risk conclusions.

## 7. تحویل اجباری هر Agent

هر Issue باید در پایان یک گزارش با قالب زیر داشته باشد:
- Objective و branch/commit.
- منابع و versionهای بررسی‌شده.
- یافته‌ها و تصمیم‌ها.
- artifactها و hashes.
- test evidence و نتیجه.
- محدودیت‌ها و UNKNOWNها.
- وابستگی بعدی و پیشنهاد Gate.
- تفاوت research/synthetic با نتیجه production.

این Sprint به معنی شروع موازی کارهای مستقل است؛ نه تأیید استراتژی، نه آموزش موفق مدل و نه اجازه معامله زنده.
