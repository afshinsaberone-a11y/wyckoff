# ممیزی مستقل Prototypeهای W1/W2/W3 — 2026-11-04

Task: AGENT_03 / Independent Audit  
Scope: سورس، تست‌ها، قرارداد JSON و خروجی واقعی GitHub Actions در سه Branch پژوهشی  
Verdict: **CONDITIONAL PASS برای Prototypeهای synthetic؛ NOT READY برای fit روی XAUUSD یا اتصال عملیاتی**

## 1. شواهد اجرای واقعی CI

پنج Run اختصاصی بررسی و Job/Step و خروجی log آن‌ها خوانده شد:

| مسیر | Run ID | نتیجه | تعداد تست‌کیس |
|---|---:|---|---:|
| W1 / HMM | 41864325081 | SUCCESS | 8 |
| W1 / HMM | 41864331424 | SUCCESS | 8 |
| W2 / ML | 41864355912 | SUCCESS | 7 |
| W2 / ML | 41864363747 | SUCCESS | 7 |
| W3 / Hybrid | 41864218329 | SUCCESS | 6 |

- 5/5 Job موفق‌اند.
- 21 تست‌کیس متمایز وجود دارد.
- به‌دلیل اجرای دوباره W1 و W2، در مجموع 36 اجرای تست‌کیس از logها قابل مشاهده است.
- هر Job مرحلهٔ Checkout، Python setup و تست نقش‌محور را با نتیجه success گذرانده است.

لینک اجراها:
- https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41864325081
- https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41864331424
- https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41864355912
- https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41864363747
- https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41864218329

هشدار محیطی Actions دربارهٔ deprecation مربوط به Node.js 20 نیز در logها دیده شده است؛ این هشدار باعث شکست Jobهای بررسی‌شده نشده است.

## 2. W1 — Causal HMM Forward Filter

Branch: `agent/w1-hmm-regime-learning`  
Source commit: `281cb9a77f6e080f726d8faa271d0f40b0db04d9`  
Files:
- `research/w1_forward_filter.py`
- `research/test_w1_forward_filter.py`

### نقاط قوت تأییدشده
- recursion به‌صورت log-domain و با log-sum-exp پیاده‌سازی شده است.
- در هر گام فقط posterior قبلی، transition matrix و emission همان observation وارد می‌شوند.
- استفاده از filtered probability به‌جای smoothed posterior در docstring و منطق تابع صریح است.
- continuation از انتهای Train با انتقال posterior قبلی به prior ابتدای segment بعدی مستند و تست شده است.
- تست future-invariance، نرمال بودن احتمال‌ها، continuation، transition نامعتبر، observation ناممکن و ابعاد نامعتبر موفق‌اند.

### محدودیت‌ها/ریسک‌های باقیمانده
1. تابع، emission log-likelihood را از بیرون دریافت می‌کند؛ خودش تضمین نمی‌کند که emissionها یا پارامترهای مدل فقط با Train fit شده باشند. این باید در fit harness و قرارداد Fold تضمین شود.
2. `_probability_vector` مجموع را finite بودن کنترل نمی‌کند. ورودی‌های finite ولی بسیار بزرگ می‌توانند sum را به infinity برسانند و normalization نامعتبر تولید کنند. پیشنهاد: کنترل finite بودن total و ترجیحاً محدودیت probability ورودی یا normalization مقاوم.
3. تست future-invariance یک تغییر مشخص در آینده را بررسی می‌کند؛ برای مرحله بعد بهتر است آزمون property-style روی چند مرز زمانی و چند دنبالهٔ آینده اضافه شود.

نتیجه W1: **PASS برای forward-filter primitive و تست‌های فعلی؛ CONDITIONAL برای fit/selection و fold-local preprocessing.**

## 3. W2 — Candidate Point-in-Time و Purging

Branch: `agent/w2-ml-scoring-learning`  
Source commit: `062f1c582f73fdf7c775285b7bc3a7ddd7600d52`  
Files:
- `research/w2_candidate_validator.py`
- `research/test_w2_candidate_validator.py`

### نقاط قوت تأییدشده
- feature با available sequence پس از decision رد می‌شود.
- candidate_id تکراری و شناسهٔ مشترک در Train/Test رد می‌شود.
- overlap بازهٔ label، اشتراک group و embargo بعد از هر Test interval بررسی می‌شوند.
- دلیل حذف هر Candidate در `removed_reasons` ثبت می‌شود.
- هفت تست point-in-time، duplicate، interval purge، group purge و embargo موفق‌اند.

### یافته‌های ممیزی
1. نوع فیلدهای sequence به‌صورت سخت‌گیرانه کنترل نشده است. `bool` در Python زیرکلاس `int` است؛ بنابراین مقدارهایی مانند `decision_seq=True` ممکن است از کنترل عددی عبور کنند. float یا string نیز می‌تواند رفتار مبهم یا TypeError ایجاد کند.
2. اعضای `feature_available_seq` از نظر integer بودن و non-negative بودن کنترل نمی‌شوند.
3. primitive، chronology کلی Foldها و overlap پنجرهٔ Feature را کنترل نمی‌کند؛ docstring نیز این مسئولیت را به caller واگذار کرده است. بنابراین نباید آن را CPCV یا purged walk-forward کامل معرفی کرد.
4. label interval فقط با محور sequence عددی مدل شده است؛ در تبدیل به دیتاست واقعی باید time basis، bar index، label horizon و timezone/server sequence ثابت و versioned شوند.

اقدام پیشنهادی: اعتبارسنجی دقیق integerها با رد bool، تست مقادیر منفی/float/string و افزودن Fold-level validator جدا؛ بدون ادعای CPCV کامل.

نتیجه W2: **PASS برای primitiveهای فعلی؛ CONDITIONAL برای استفادهٔ واقعی تا رفع type validation و تکمیل Fold/Feature-window controls.**

## 4. W3 — HMM-to-ML Interface

Branch: `agent/w3-hybrid-integration`  
Source commit: `248bb7db5595633a68ad2c4ab1ddf3887d1efbb1`  
Files:
- `research/w3_interface_validator.py`
- `research/test_w3_interface_validator.py`
- `contracts/W3_HMM_ML_INTERFACE_V1.schema.json`

### نقاط قوت تأییدشده
- فیلدهای هویت مدل، Fold، Candidate، sequence و data version لازم‌اند.
- احتمال‌ها از نظر dimension، finite بودن، دامنهٔ [0,1] و مجموع 1 کنترل می‌شوند.
- HMM output که بعد از decision در دسترس قرار گرفته یا از حد staleness قدیمی‌تر باشد رد می‌شود.
- رفتار fail-closed در توضیح تابع صریح است.
- شش تست موفق‌اند.

### یافته‌های قرارداد/کد
1. **عدم تطابق schema و Python validator:** JSON Schema دارای `additionalProperties: false` است، اما تابع Python کلیدهای ناشناخته را رد نمی‌کند. در نتیجه ممکن است payload در Python پذیرفته شود ولی طبق schema معتبر نباشد.
2. Schema حداقل دو state را الزام می‌کند (`minItems=2`)، ولی تابع اگر caller مقدار `expected_states=1` بدهد، بردار یک‌عضوی را می‌پذیرد. خود پارامتر `expected_states` باید integer و حداقل 2 باشد.
3. schema دو فیلد اختیاری `source_bar_open_server` و `observed_at_server` را تعریف می‌کند؛ تابع Python نوع/مقدار آن‌ها را کنترل نمی‌کند.
4. پارامترهای کنترلی `max_staleness_bars` و `probability_tolerance` اعتبارسنجی نمی‌شوند؛ مقادیر منفی یا غیر finite باید رد شوند.
5. دامنه و واحد `posterior_entropy` در قرارداد مشخص نشده است. پیش از اعمال سقف باید معلوم شود entropy در nats است یا normalized entropy؛ فعلاً فقط finite و non-negative کنترل می‌شود.

اقدام پیشنهادی: parity کامل Python/schema، reject کلید ناشناخته، کنترل optional fields و اعتبارسنجی پارامترهای validator؛ برای entropy ابتدا تعریف واحد را در schema مستند کنید.

نتیجه W3: **CONDITIONAL PASS برای interface prototype؛ قرارداد نسخه 1 هنوز نیازمند همسان‌سازی است.**

## 5. ماتریس Gate

| Gate | نتیجه | دلیل |
|---|---|---|
| Branch-specific CI | PASS | پنج Run موفق |
| W1 filter primitive | PASS با محدودیت | fit harness و fold-local emissions وجود ندارد |
| W2 point-in-time/purge primitive | PASS با محدودیت | sequence type و Fold/feature-window coverage ناقص |
| W3 interface validator | CONDITIONAL | schema/Python parity gap |
| Real XAUUSD HMM/ML fit | BLOCKED | Candidate/Feature/Label dataset و Fold manifest کامل نیست |
| W3 operational integration | BLOCKED | W1/W2 و Ledger مستقل Freeze نشده‌اند |
| Production EA / Live | NOT APPROVED | هیچ شواهد OOS/Forward Demo کافی وجود ندارد |

## 6. اقدام‌های اصلاحی پیشنهادی برای Branchها

### W1
- کنترل finite بودن مجموع initial weights.
- افزودن تست extreme finite values و future-invariance در چند cutoff.
- طراحی fit harness که preprocessing و emission parameters را فقط از Train بگیرد؛ هنوز روی دادهٔ واقعی اجرا نشود.

### W2
- رد bool، float، string و sequence منفی در تمام فیلدهای index.
- تست feature availability sequence با ورودی‌های malformed.
- افزودن Fold contract و feature-window purge به‌صورت ماژول جدا؛ primitive فعلی به‌عنوان primitive باقی بماند.

### W3
- همسان‌سازی کلیدهای مجاز Python با schema.
- رد expected_states کمتر از 2 و پارامترهای کنترلی نامعتبر.
- اعتبارسنجی اختیاری بودن دو timestamp field.
- افزودن تست schema/Python parity و ثبت معنای entropy.

این موارد در این گزارش به‌عنوان پیشنهاد/یافته ثبت شده‌اند؛ هیچ‌یک از سورس W1/W2/W3 در این ممیزی تغییر داده نشده است.

## 7. مرز نتیجه‌گیری

CI موفق یعنی تست‌های مصنوعی و قراردادهای محدود موجود عبور کرده‌اند. این نتیجه به معنی fit موفق HMM، یادگیری ML، پیش‌بینی سودآوری، مدل معتبر برای XAUUSD یا آماده بودن W3 برای اتصال به EA نیست.

تا زمان وجود M1/Tick خام قابل ردیابی، Event/Candidate Ledger v2، Feature snapshot، Label outcome، Fold manifest و ارزیابی out-of-fold/after-cost، آموزش روی دادهٔ واقعی و ادعای performance باید BLOCKED بماند.
