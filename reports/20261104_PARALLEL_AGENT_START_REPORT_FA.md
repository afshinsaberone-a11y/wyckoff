# گزارش شروع موازی ۹ نقش — Financial ML Core+

تاریخ: 2026-11-04  
وضعیت: **۹ Issue و ۹ Branch ایجاد شده‌اند؛ W1/W2/W3 دارای prototype کد و CI اختصاصی هستند.**

## 1. ثبت مسیرهای کاری

| نقش | Issue | Branch | شروع قابل مشاهده |
|---|---:|---|---|
| AGENT_00 | [#2](https://github.com/afshinsaberone-a11y/wyckoff/issues/2) | `agent/00-orchestrator-parallel-sprint` | هماهنگی/گیت‌ها |
| AGENT_01 | [#3](https://github.com/afshinsaberone-a11y/wyckoff/issues/3) | `agent/01-data-engineering` | Event Ledger migration و Data inventory |
| AGENT_02 | [#4](https://github.com/afshinsaberone-a11y/wyckoff/issues/4) | `agent/02-execution-backtest` | Run Card چهارگانه و execution audit |
| AGENT_03 | [#5](https://github.com/afshinsaberone-a11y/wyckoff/issues/5) | `agent/03-independent-audit` | audit شواهد و Gateها |
| AGENT_04 | [#6](https://github.com/afshinsaberone-a11y/wyckoff/issues/6) | `agent/04-governance` | schema 1.2 و Label/Fold governance |
| W0 | [#7](https://github.com/afshinsaberone-a11y/wyckoff/issues/7) | `agent/w0-wyckoff-ledger` | state machine و Event Ledger v2 |
| W1 | [#8](https://github.com/afshinsaberone-a11y/wyckoff/issues/8) | `agent/w1-hmm-regime-learning` | HMM forward-filter prototype |
| W2 | [#9](https://github.com/afshinsaberone-a11y/wyckoff/issues/9) | `agent/w2-ml-scoring-learning` | Candidate validator و purge prototype |
| W3 | [#10](https://github.com/afshinsaberone-a11y/wyckoff/issues/10) | `agent/w3-hybrid-integration` | HMM→ML interface validator |

## 2. خروجی‌های کدنویسی شروع‌شده

### W1 — HMM causal filter
- `research/w1_forward_filter.py`
- `research/test_w1_forward_filter.py`
- الگوریتم forward recursion فقط از posterior مرحله قبل و observation فعلی استفاده می‌کند.
- تست‌ها شامل نرمال‌بودن probability، تغییرناپذیری گذشته در مقابل تغییر observationهای آینده، ادامه state از Train به Test، state غیرقابل‌دسترس و observation ناممکن‌اند.
- آخرین Commit: `281cb9a77f6e080f726d8faa271d0f40b0db04d9`.

### W2 — Candidate point-in-time و Purge
- `research/w2_candidate_validator.py`
- `research/test_w2_candidate_validator.py`
- featureهایی که پس از decision sequence در دسترس می‌شوند رد می‌شوند.
- Candidate ID تکراری در Train/Test رد می‌شود.
- label interval overlap، گروه Range مشترک و embargo بعد از هر test interval قابل حذف و گزارش هستند.
- این تابع یک primitive آزمایشی است و به‌تنهایی CPCV کامل نیست.
- آخرین Commit: `062f1c582f73fdf7c775285b7bc3a7ddd7600d52`.

### W3 — HMM-to-ML interface
- `contracts/W3_HMM_ML_INTERFACE_V1.schema.json`
- `research/w3_interface_validator.py`
- `research/test_w3_interface_validator.py`
- payload ناقص، dimension اشتباه، probability غیرنرمال، timestamp آینده یا vector قدیمی را رد می‌کند.
- رفتار fail-closed است؛ هیچ risk control از W0 override نمی‌شود.
- آخرین Commit: `248bb7db5595633a68ad2c4ab1ddf3887d1efbb1`.

## 3. تست خودکار شاخه‌های پژوهشی

Workflow مستقل:
`.github/workflows/parallel-agent-learning-tests.yml`

سه Run ثبت شده‌اند:
| نقش | Run ID | وضعیت فعلی هنگام گزارش |
|---|---:|---|
| W1 | 41864331424 | QUEUED |
| W2 | 41864363747 | QUEUED |
| W3 | 41864218329 | QUEUED |

این Runها هنوز نتیجه PASS/FAIL ندارند؛ پس کدها «ثبت شده و آماده اجرای تست» هستند، نه «تأییدشده». اجرای واقعی test output باید از Job Log بررسی شود.

## 4. خلاصه یادگیری پژوهشی

### W1
Forward filtering برآورد `P(S_t | X_1:t)` است و برای تصمیم زنده مناسب‌تر از smoothed posterior مشروط به کل نمونه است. مستندات Statsmodels فیلترشده و smoothed probabilities را جدا تعریف می‌کند. در hmmlearn نیز MAP/forward-backward و Viterbi باید با دقت از inference forward-only تفکیک شوند.

### W2
TimeSeriesSplit ترتیب زمانی و gap را پشتیبانی می‌کند، اما interval-based purging، Group leakage و embargo مالی باید به‌صورت مشخص اضافه شوند. Candidate universe نسخه اول W2 فقط Recovery trigger در M5_ENTRY است؛ eventهای M5_ENTRY_EVALUATION نمونه مستقل محسوب نمی‌شوند.

### W3
W0/W1/W2/W3 به‌صورت طرح 2×2 باقی می‌مانند. HMM output فقط filtered probability vector و با fold/model identifiers وارد W3 می‌شود. W3 نباید risk controls یا execution assumptions را تغییر دهد.

## 5. منابع پژوهشی اولیه

1. Statsmodels — Markov switching filtered/smoothed probabilities:  
   https://github.com/statsmodels/statsmodels/blob/main/statsmodels/tsa/regime_switching/markov_switching.py
2. Statsmodels — Markov autoregression example:  
   https://github.com/statsmodels/statsmodels/blob/main/examples/python/markov_autoregression.py
3. hmmlearn — HMM fitting, Viterbi and MAP decoding:  
   https://github.com/hmmlearn/hmmlearn/blob/main/doc/source/tutorial.rst
4. Scikit-learn — TimeSeriesSplit و gap:  
   https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html
5. Murphy — HMM forward filtering:  
   https://probml.github.io/ssm-book/chapters/hmm/hmm_filter.html
6. López de Prado — purging/embargo overview:  
   https://www.quantresearch.org/Innovations.htm
7. Arian et al. (2024), *Backtest overfitting in the machine learning era*, Knowledge-Based Systems:  
   https://www.sciencedirect.com/science/article/abs/pii/S0950705124011110  
   یافته‌های آن مقاله به محیط synthetic-controlled آن مطالعه مربوط‌اند و به‌تنهایی برتری CPCV برای XAUUSD را اثبات نمی‌کنند.

## 6. مرز اجرا و محدودیت‌ها

- ۹ Issue و ۹ Branch، ۹ نقش کاری را در GitHub قابل رهگیری می‌کنند؛ **۹ پردازه Agent مستقل/همیشه‌فعال مستقر نشده‌اند**.
- W1/W2 synthetic research و unit tests را می‌توانند انجام دهند؛ HMM/ML fit روی XAUUSD واقعی هنوز مجاز نیست.
- Event CSV قدیمی 346 ردیف event دارد، نه candidate dataset.
- M1/Tick خام، Candidate/Feature/Label dataset و چهار Run واقعی BOOT-002 هنوز موانع اصلی‌اند.
- هیچ کدی به C2 baseline یا MultiAudit روی main تزریق نشده است؛ prototypeها روی branchهای جدا هستند.

## 7. تصمیم بعدی

1. نتایج CI سه prototype را از Job Logs دریافت و هر خطا را اصلاح کن.
2. هر Agent گزارش مستقل خود را به Issue مربوط پیوست کند.
3. AGENT_03 نتایج W1/W2/W3 synthetic tests را ممیزی کند.
4. Compile/Tester واقعی BOOT-002 و داده خام M1/Tick را جداگانه پیگیری کن.
5. تا تکمیل Gateها، W1/W2/W3 صرفاً در مرحله research/synthetic باقی بمانند.
