# W2 — یادگیری و طرح اولیه ML Candidate Scoring

نسخه: 0.1 research starter  
وضعیت: **تعریف مسئله و synthetic pipeline مجاز؛ آموزش روی Candidateهای واقعی هنوز مسدود است.**

## 1. مسئله دقیق یادگیری

W2 نسخه اول در نقطه `M5_ENTRY` تصمیم می‌گیرد: بعد از بسته‌شدن Recovery معتبر و قبل از اجرای `PlaceTrade()`. در نتیجه، Candidate باید قبل از فیلتر Spread، tick، Stop، Volume، Filling و OrderSend ساخته شود تا فرصت‌های واجد سیگنال که اجرا نمی‌شوند هم باقی بمانند.

- یک candidate_id برای هر Recovery trigger مستقل.
- چند M5_ENTRY_EVALUATION در یک مسیر، Candidateهای مستقل نیستند.
- breakout/retest قبل از Recovery eventهای مسیرند؛ هنوز Entry Candidate نیستند.
- Candidate ردشده به‌علت Spread/Stop/Volume/OrderSend حذف نمی‌شود.

## 2. Targetها را مخلوط نکن

دو task مجزا تعریف شوند:

### Task A — رسیدن به Entry
برای نقطه تصمیم زودتر (مثلاً بعد از LPS/LPSY) برآورد می‌کند آیا مسیر به Recovery/M5_ENTRY خواهد رسید. این یک event/sequence target جداست و برای W2 Entry scoring نسخه اول الزامی نیست.

### Task B — کیفیت اقتصادی Entry
برای هر M5_ENTRY candidate، outcome در اجرای فرضی استاندارد محاسبه شود:
- regression target: `net_return_r` after costs.
- classification view: `net_return_r > 0` یا hurdle ازپیش‌تعریف‌شده.
- MFE/MAE و censoring جدا ثبت شوند.
- actual execution outcome و hypothetical standardized execution outcome از هم جدا بمانند.

برای Candidateی که order اجرا نشده، نباید actual R جعل شود. در عوض، counterfactual/hypothetical outcome فقط با execution assumption versioned و داده Bid/Ask/tick کافی محاسبه شود؛ reason عدم‌اجرا جدا نگهداری شود.

## 3. Feature snapshot

همه featureها باید قبل از PlaceTrade و در لحظه تصمیم قابل دسترس باشند. گروه‌های اولیه:
- Wyckoff: Spring/UTAD depth، Test quality، SOS/SOW strength، LPS/LPSY quality.
- Range: width/ATR، duration، touch count و فاصله تا range edge.
- Structure: internal swing break، range-edge distance، pivot-zone width و pivot confirmation age.
- Market: ATR/volatility، normalized returns، relative volume در صورت اعتبار.
- Execution: spread، session، quote age، distance-to-stop، volume constraints؛ فقط اگر در لحظه تصمیم معلوم باشند.
- W3-only: filtered HMM probability vector و fold/model identifiers.

هر feature باید source_event_ids، available_at، unit، missing_reason و feature_code_version داشته باشد.

## 4. مدل‌های baseline

به ترتیب complexity:
1. Logistic Regression — baseline شفاف و قابل audit.
2. Random Forest یا HistGradientBoosting — nonlinear challenger.
3. Calibration مثل sigmoid/isotonic فقط بعد از بررسی sample size و فقط روی validation.

فعلاً neural networks / LSTM / Transformer اضافه نشوند؛ dataset کوچک و candidate identity هنوز کامل نشده است.

## 5. Pipeline و validation

- feature preprocessor، missing-value imputation، scaler، feature selection و model fit داخل Train هر fold.
- chronology حفظ شود؛ train باید قبل از validation/test باشد.
- label start/end interval برای هر candidate لازم است؛ train labelهای هم‌پوشان با test purged شوند.
- embargo متناسب با label horizon و وابستگی زمانی تعریف شود.
- group_id حداقل در Range-level نگهداری شود تا نمونه‌های یک ساختار بین Train/Test نشت نکنند.
- thresholds فقط با validation انتخاب شوند؛ test فقط برای ارزیابی نهایی frozen.
- out-of-fold predictions و calibration diagnostics ذخیره شوند.

Scikit-learn `TimeSeriesSplit` ترتیب زمانی و gap را پشتیبانی می‌کند، ولی gap نمونه‌ای به‌تنهایی جایگزین purge بر اساس label interval و grouping در Range/Cycle نیست:
https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html

در مالی، labelهای دارای interval هم‌پوشان می‌توانند leakage ایجاد کنند؛ Purging/Embargo برای حذف overlap و جلوگیری از leakage طراحی شده‌اند. مرجع روش‌شناختی:
https://www.quantresearch.org/Innovations.htm
کتاب: Marcos López de Prado, *Advances in Financial Machine Learning*, Chapter 7.

## 6. معیارهای ارزیابی

### Predictive
- ROC-AUC و PR-AUC (در صورت عدم توازن).
- log loss و Brier score.
- calibration curve و reliability.
- precision/recall در operating threshold.
- coverage و rejected/accepted candidate rates.

### Economic
- net profit after costs.
- PF، max drawdown، expectancy/trade، netR distribution.
- trade count، exposure و turnover.
- performance dispersion across folds/periods.
- حساسیت به costs، spread، slippage و fill assumptions.

Accuracy به‌تنهایی معیار انتخاب مدل نیست؛ threshold با Validation و metrics اقتصادی after-cost سنجیده شود.

## 7. وضعیت داده واقعی فعلی

Event CSV مهاجرت‌شده 346 event دارد، 65 گروه Range مبتنی بر SetupID legacy و هیچ candidate_id/label ندارد. یک معامله واقعی در Run مورد استناد ثبت شده است؛ این برای fit/selection معتبر ML کافی نیست.

بنابراین:
- کد pipeline و unit tests با synthetic data مجازند.
- آموزش، threshold tuning و اعلام performance واقعی XAUUSD ممنوع است.
- پس از Event Ledger v2، candidate table و label table باید جدا و versioned ساخته شوند.

## منابع مطالعه
- Scikit-learn TimeSeriesSplit: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html
- López de Prado, *Advances in Financial Machine Learning*, Ch.7; overview: https://www.quantresearch.org/Innovations.htm
- Arian et al. (2024), *Backtest overfitting in the machine learning era...*, Knowledge-Based Systems, DOI 10.1016/j.knosys.2024.112477: https://www.sciencedirect.com/science/article/abs/pii/S0950705124011110
  - نتایج مقاله در محیط synthetic-controlled گزارش شده‌اند؛ آن‌ها تضمین برتری CPCV برای این سیستم یا XAUUSD نیستند.
