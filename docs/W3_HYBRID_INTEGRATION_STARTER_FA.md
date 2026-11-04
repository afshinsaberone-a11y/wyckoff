# W3 — یادگیری و معماری Hybrid HMM + ML

نسخه: 0.1 research starter  
وضعیت: **معماری و طراحی آزمون آغاز شده؛ integration اجرایی مسدود تا Freeze مستقل W1/W2.**

## 1. تعریف factorial experiment

W0/W1/W2/W3 یک طرح 2×2 است:

| نسخه | HMM Regime | ML Score |
|---|---|---|
| W0 | خاموش | خاموش |
| W1 | روشن | خاموش |
| W2 | خاموش | روشن |
| W3 | روشن | روشن |

اثرهای اصلی:
- HMM در نبود ML: W1 − W0.
- ML در نبود HMM: W2 − W0.
- اثر ML وقتی HMM حاضر است: W3 − W1.
- اثر HMM وقتی ML حاضر است: W3 − W2.
- interaction باید با اختلافِ اختلاف گزارش شود، نه فقط مقایسه W3 با W0.

## 2. Interface

W1 خروجی point-in-time می‌دهد:
- `run_id`
- `hmm_model_version`
- `fold_id`
- `decision_time`
- `filtered_prob_state_0...K-1`
- `posterior_entropy`
- `state_mapping_version`
- `input_data_version`

W2 ورودی می‌گیرد:
- Frozen W0 candidate snapshot.
- W0 features.
- در W3 فقط filtered HMM probability vector + model/fold version از W1.

W2 باید علاوه بر score، نسخه مدل، feature list، preprocessing hash، threshold version و calibration artifact را گزارش کند.

## 3. قواعد causality و execution

- HMM probability در timestamp Candidate با اطلاعات تا همان timestamp محاسبه شود.
- Smoothed posterior یا Viterbi path که از observations آینده استفاده می‌کند ممنوع است.
- W1 و W2 در هر fold فقط با Train fit شوند.
- Feature selection و calibration روی Test ممنوع است.
- W3 نباید risk limit، position size cap، spread filter، SL/TP یا safety gateهای W0 را override کند.
- وقتی ورودی HMM/ML unavailable، stale یا خارج از schema است، رفتار fail-closed یا fallback صریح و versioned باشد؛ هرگز silent bypass رخ ندهد.

## 4. Fair comparison

همه چهار arm باید یکسان داشته باشند:
- Candidate universe، symbol، timeframe، data version و test dates.
- execution simulator، Bid/Ask، spread، commission، swap، slippage، gap policy.
- risk sizing، stop/target و W0 execution assumptions.
- threshold selection protocol و validation budget.

تعداد معاملات نباید مصنوعی برابر شود؛ اختلاف آن بخشی از اثر فیلترهاست. اما تمام فرصت‌های بالقوه باید در candidate ledger حفظ شوند تا sample selection bias کنترل شود.

## 5. Uncertainty و robustness

گزارش شود:
- per-fold / per-period metrics و dispersion.
- economic performance after-cost.
- calibration و coverage.
- turnover و trades avoided/added.
- confidence intervals با روش سازگار با وابستگی زمانی و clustering در Range/Cycle، نه IID bootstrap ساده.
- حساسیت به تعداد stateها، model initialization، threshold و هزینه اجرا.

مقاله Arian et al. (2024) در یک محیط synthetic-controlled چند روش OOS را مقایسه می‌کند و نشان می‌دهد CV design می‌تواند روی PBO/DSR اثر جدی بگذارد؛ این نتیجه را نباید به‌عنوان برتری تضمین‌شده یک روش برای XAUUSD تعمیم داد:
https://www.sciencedirect.com/science/article/abs/pii/S0950705124011110

## 6. برنامه موازی W3

1. ساخت JSON interface contract و validator.
2. synthetic tests برای missing/stale probability vector.
3. طراحی factorial analysis notebook بدون داده معاملاتی واقعی.
4. تست invariantهای W0 risk controls.
5. طراحی گزارش interaction و per-fold uncertainty.
6. آماده‌سازی adapter فقط پس از آنکه W1 output و W2 model artifact جداگانه Freeze شدند.

## 7. Gate

اکنون مجاز: research, architecture, interface tests و synthetic simulations.  
فعلاً مسدود: اتصال به EA، اجرای W3 روی XAUUSD واقعی و ادعای performance تا تکمیل W0 baseline، Event/Candidate Ledger، labels، data quality، W1/W2 validation و independent audit.
