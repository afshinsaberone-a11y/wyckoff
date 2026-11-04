# پروتکل رسمی Financial ML Core+

نسخه: 1.0-draft  
تاریخ ثبت: 2026-11-04  
وضعیت: طراحی پژوهش؛ هنوز آزمایش W1/W2/W3 اجرا یا تأیید نشده است.

## 1. هدف

هدف این پروتکل سنجش ارزش افزوده تشخیص رژیم HMM و امتیازدهی ML روی هسته Wyckoff است. این پروژه پژوهش و اعتبارسنجی است، نه وعده سودآوری یا مجوز معامله زنده.

اصل مرکزی: چهار نسخه باید یک موتور Wyckoff، یک فضای Candidate، یک داده و یک موتور اجرای مشترک داشته باشند. تفاوت اصلی فقط در عامل آزمایشی HMM و ML باشد.

## 2. وضعیت مرجع در شروع پروتکل

طبق مستندات مخزن در 2026-11-04:
- H1STRUCT Audit یک معامله ثبت کرده و خالص نتیجه آن منفی بوده است.
- 67 Range، 16 Test و 9 رویداد SOS/SOW در قیف ممیزی ثبت شده‌اند؛ هر 9 Strength از نوع شکست Swing داخلی بوده‌اند.
- MultiAudit v1.084 و SETهای Lookback در مخزن هستند؛ بررسی ایستا و تطابق SET ثبت شده، اما MetaEditor Compile و Strategy Tester run تأیید نشده‌اند.
- پوشش تیک تاریخی، spreadهای صفر/مفقود، gap و اجرای SL محدودیت‌های باز هستند.
- هیچ OOS/Walk-Forward یا Forward Demo معتبر تأیید نشده است.

پس شروع آموزش ML/HMM قبل از تکمیل Event Ledger و اعتبارسنجی W0 مجاز نیست. تعداد نمونه فعلی برای نتیجه‌گیری درباره عملکرد ML کافی اثبات نشده است.

## 3. چهار بازوی آزمایش

| نسخه | Wyckoff | HMM | ML | سؤال |
|---|---|---|---|---|
| W0 | ثابت | خاموش | خاموش | Baseline چیست؟ |
| W1 | ثابت | روشن | خاموش | آیا رژیم بازار ارزش افزوده دارد؟ |
| W2 | ثابت | خاموش | روشن | آیا امتیاز ستاپ ارزش افزوده دارد؟ |
| W3 | ثابت | روشن | روشن | آیا ترکیب هر دو بهتر است؟ |

نسخه اصلی W3 از خروجی دو مسیر مستقل W1/W2 استفاده می‌کند. آموزش end-to-end یا واردکردن HMM probabilities به featureهای ML، آزمایش فرعی `W3_INTERACTION` است و نباید با W3 اصلی مخلوط شود.

## 4. معماری ۹ نقش

یک هماهنگ‌کننده، چهار توسعه‌دهنده نسخه‌ای و چهار نقش پشتیبان تعریف شده‌اند. مشخصات هر نقش در پوشه [agents](../agents/README_FA.md) قرار دارد. قراردادهای داده در پوشه [contracts](../contracts/EVENT_AND_CANDIDATE_SCHEMA_FA.md) ثبت شده‌اند.

این‌ها نقش‌های منطقی‌اند و هنوز به‌صورت Agentهای مستقل مستقر نشده‌اند. برای استقرار واقعی باید ابزار، مجوز، محیط اجرا، دسترسی فایل، log و کنترل انسانی هر نقش تعریف شود. هیچ نقشی دسترسی ارسال سفارش واقعی ندارد.

## 5. Gateهای اجرا

### Gate 0 — Freeze پروتکل
مالک: AGENT_04.  
خروجی: فرضیه‌ها، معیارها، Candidate universe، label horizon، split و stopping rules.  
شرط عبور: manifest آزمایش و نسخه پروتکل ثبت شده باشد.

### Gate 1 — اعتبار W0
مالک: W0، با همکاری AGENT_02 و ممیزی AGENT_03.  
کارها: Compile واقعی، هویت Expert/EA_Version، اجرای تستر، مسیرهای state machine و ثبت تمام Candidateها.  
شرط عبور: Baseline قابل بازتولید باشد و محدودیت‌های tick/اجرای سفارش مستند شود. MultiAudit تا زمان Compile و Tester run فقط diagnostic source بررسی‌شده است.

### Gate 2 — Data & Event Ledger
مالک: AGENT_01.  
کارها: manifest داده، کیفیت M1/tick، ساخت/تطبیق M5/H1/H4، Event Ledger، Candidate Ledger و Decision Ledger.  
شرط عبور: Candidateهای اجراشده، ردشده، منقضی و ابطال‌شده ثبت و schema validation پاس شده باشد.

### Gate 3 — Label و Validation Freeze
مالک: AGENT_04؛ ممیزی AGENT_03.  
کارها: تعریف outcome، افق، SL/TP barrier، هزینه، right-censoring، Purge، Embargo و Foldها.  
شرط عبور: هیچ تعریف برچسب یا split پس از مشاهده Test تغییر نکرده باشد.

### Gate 4 — W1 و W2
مالک: W1 و W2 به‌صورت موازی.  
کارها: آموزش در هر Train fold، انتخاب در Validation، پیش‌بینی point-in-time و ثبت artifact hashes.  
شرط عبور: آزمون leakage و reproducibility پاس شود.

### Gate 5 — W3
مالک: W3.  
کارها: ترکیب خروجی‌های Freeze شده W1/W2 و تحلیل اثر تعاملی.  
شرط عبور: زمان‌بندی و provenance دو ورودی هم‌تراز باشد.

### Gate 6 — مقایسه نهایی
مالک: AGENT_02؛ ممیزی AGENT_03؛ تصمیم پروتکل با AGENT_04.  
کارها: ارزیابی after-cost در تمام Foldها، uncertainty، پایداری، گزارش نتایج منفی و محدودیت‌ها.  
شرط عبور: Audit PASS یا شروط CONDITIONAL برآورده شده باشد.

### Gate 7 — Forward Demo
فقط نسخه‌های واجد شرایط وارد مرحله مشاهده/دموی آتی می‌شوند. تأیید این مرحله نیز مجوز Live نیست. تصمیم Live نیازمند بررسی انسانی جدا، آزمون ریسک اجرایی و مجوز مستقل است.

## 6. اصول Dataset

Dataset از معاملات اجراشده تنها ساخته نمی‌شود. تمام فرصت‌های ساختاری و Candidateهای W0، حتی اگر هیچ معامله‌ای ایجاد نکرده باشند، وارد Ledger می‌شوند.

جداکن:
1. raw market data
2. structural events
3. setup candidates
4. decision history
5. point-in-time feature snapshots
6. future outcome labels
7. actual execution/trade records

هر feature باید زمان قابل‌دسترس‌شدن داشته باشد و از decision_time دیرتر نباشد. Labelها باید در جدول جدا باشند و هر outcome window برای Purge قابل شناسایی باشد. Candidate بدون outcome کامل باید right-censored علامت بخورد.

## 7. اصول HMM

- HMM در هر Fold فقط با Train fit شود.
- تصمیم زمان t فقط از filtered probability استفاده کند: `P(S_t | X_1,...,X_t)`.
- smoothed probabilities که داده آینده را در بر می‌گیرند برای تصمیم گذشته ممنوع‌اند.
- scaler و feature transforms فقط روی Train fit شوند.
- State label switching بین Foldها بررسی شود.
- معنا و نام رژیم‌ها با شواهد Train تعیین شود و لزوماً برچسب اقتصادی قطعی نیست.

## 8. اصول ML

- baseline مدل: Logistic Regression.
- مدل‌های بعدی: Random Forest و Gradient Boosting، هر یک با Experiment ID مستقل.
- تمام preprocessing و feature selection فقط داخل Train fit شود.
- آستانه و calibration فقط از Validation انتخاب شوند.
- class imbalance و dependency بین setupها کنترل شود.
- معیارهای classification مثل PR-AUC و Brier مکمل‌اند، نه جایگزین عملکرد معاملاتی.

## 9. Purged Walk-Forward و Embargo

تقسیم داده زمانی است؛ shuffle تصادفی مجاز نیست. برای هر نمونه، label_start و label_end ثبت می‌شود. نمونه‌های Train که label window آن‌ها با دوره Validation/Test هم‌پوشانی دارد purge شوند. Embargo بر اساس حداکثر افق برچسب و وابستگی زمانی انتخاب و در Fold manifest ثبت شود؛ تعداد ثابتی ردیف بدون توجیه انتخاب نشود.

تمام مدل‌ها، state mappingها، scalerها، feature selection و thresholdها در هر Fold فقط با Train/Validation همان Fold fit شوند. Test/OOS برای تنظیم مدل استفاده نشود.

## 10. کنترل اجرای معامله

فرض‌های زیر بین نسخه‌ها ثابت‌اند:
- نماد، بروکر، بازه و منبع داده.
- سرمایه، ارز حساب، اهرم و مشخصات قرارداد.
- Bid/Ask، spread، commission، swap، slippage و gap model.
- سیگنال پایه، Entry/SL/TP و قواعد حجم.
- محدودیت پوزیشن و قواعد fill.
- مدل تیک و نحوه مدیریت بخش‌های فاقد tick.

ریسک هدف 0.5% پارامتر مرجع گزارش‌شده است، نه تضمین سقف زیان واقعی؛ gap، slippage و fill ممکن است زیان را از مقدار محاسبه‌شده بیشتر کنند. ریسک واقعی پس از rounding حجم باید ثبت شود.

## 11. معیارهای گزارش

معیارهای اصلی:
- Net Profit after costs
- Profit Factor
- Max Balance/Equity Drawdown
- Expectancy per Trade و realized R
- Number of Trades
- Exposure و Holding Time
- Stability بین Foldها/دوره‌ها
- Confidence Intervals و uncertainty

هر عدد باید همراه تعداد نمونه و کیفیت داده نمایش داده شود. با یک معامله، PF یا expectancy نباید به‌عنوان برآورد معتبر استراتژی تفسیر شود. برای بازنمونه‌گیری، وابستگی زمانی و خوشه Candidateهای یک Range لحاظ شود.

## 12. قواعد تغییر و ابطال

- W0 با Commit/Tag و config hash Freeze شود.
- هر تغییر در قواعد یا execution یک Experiment مستقل است.
- اگر پس از مشاهده OOS تنظیم شد، OOS قبلی دیگر untouched نیست.
- اگر data hash، cost model یا code version با نسخه‌های دیگر متفاوت باشد، مقایسه مستقیم invalidated است.
- تعداد معامله‌ها برابر تحمیل نشود.
- گزارش ناموفق، زیان‌ده و نتیجه بدون edge نیز باید ثبت شود.

## 13. وضعیت فعلی و اقدام بعدی

اولویت اجرایی:
1. کامپایل و اجرای واقعی MultiAudit؛
2. مقایسه Lookbackهای 5/10/20 با شرایط کاملاً ثابت، پس از تأیید هویت Expert؛
3. تکمیل Event/Candidate Ledger؛
4. تثبیت برچسب‌ها و Foldها؛
5. آغاز W1/W2؛
6. سپس W3.

این سند مشخصات و پروتکل طراحی‌شده را ثبت می‌کند؛ به‌تنهایی به معنی اجرای ایجنت‌ها، کامپایل کد یا انجام بک‌تست جدید نیست.


## 14. مدل استقرار و برنامه شروع

مشخصات اجرا و مجوزهای Agentها در [مدل استقرار و تحویل](../agents/EXECUTION_AND_HANDOFF_MODEL_FA.md) آمده است. قالب استاندارد تحویل در [Agent Handoff Schema](../contracts/AGENT_HANDOFF_SCHEMA_FA.md) قرار دارد. بسته‌های کاری و معیار پذیرش هر مرحله در [برنامه راه‌اندازی](FINANCIAL_ML_CORE_PLUS_BOOTSTRAP_PLAN_FA.md) ثبت شده‌اند.

اولین بسته کاری BOOT-001 باید هویت دقیق Baseline را با Expert name، EA_Version، سورس، Commit، SET و گزارش تست تطبیق دهد. تا پیش از آن نباید C2 پایه، H1STRUCT Audit و MultiAudit یک نسخه واحد تلقی شوند.
