# W1 — یادگیری و طرح اولیه HMM Regime Filter

نسخه: 0.1 research starter  
وضعیت: **مطالعه و طراحی آغاز شده؛ HMM روی داده XAUUSD fit نشده است.**

## 1. هدف W1

به W0 یک بردار احتمال رژیم بازار اضافه شود تا مشخص شود هر Candidate در چه محیطی شکل گرفته است. W1 نباید ترتیب Wyckoff یا محدودیت‌های ریسک W0 را حذف/جایگزین کند.

## 2. اصل علّی: Filtering، نه Smoothing

در زمان t، feature زنده باید از این توزیع استفاده کند:

`P(S_t | X_1, ..., X_t)`

نه:

`P(S_t | X_1, ..., X_T)` برای T>t.

در Statsmodels، filtered probabilities به داده تا زمان t مشروط‌اند؛ smoothed probabilities از کل نمونه استفاده می‌کنند و برای بازسازی live در زمان t مناسب نیستند. مستندات و کد رسمی این دو خروجی را از هم جدا می‌کند:
- https://github.com/statsmodels/statsmodels/blob/main/statsmodels/tsa/regime_switching/markov_switching.py
- https://github.com/statsmodels/statsmodels/blob/main/examples/python/markov_autoregression.py

کتابخانه hmmlearn مدل‌های HMM را با Baum–Welch/EM fit می‌کند و decoderهای Viterbi و MAP را جدا معرفی می‌کند؛ MAP/forward-backward روی کل sequence می‌تواند smoothing باشد، بنابراین `predict` یا `predict_proba` را بدون بررسی API برای feature زنده به‌کار نبرید:
- https://github.com/hmmlearn/hmmlearn/blob/main/doc/source/tutorial.rst

## 3. ورودی‌های پیشنهادی H1/H4

نسخه اول تا حد امکان با observables بازار و نه label/outcome معامله ساخته شود:
- H1 log return و return نرمال‌شده با ATR.
- realized volatility یا نسبت ATR کوتاه‌مدت به بلندمدت.
- range efficiency / absolute net move divided by total path.
- normalized candle range و body share.
- حجم نسبی فقط وقتی volume منبع و تعریف آن معتبر باشد.
- spread یا liquidity feature فقط در صورتی که history bid/ask قابل اعتماد باشد.

از ویژگی‌های مبتنی بر رویدادهای آینده، معامله‌های بعدی، یا outcome Candidate استفاده نشود. H1 data باید در زمان closed-bar قابل دسترس باشد؛ H4 context فقط پس از بسته‌شدن H4 مربوط.

## 4. معماری مدل پیشنهادی

- شروع با GaussianHMM.
- تعداد stateها: K=2 و K=3 به‌عنوان candidate؛ K=4 فقط sensitivity/diagnostic.
- Diagonal covariance به‌عنوان baseline ساده؛ full covariance فقط اگر sample کافی و پایداری عددی اثبات شد.
- چند initialization مستقل؛ بهترین fit فقط بر مبنای training likelihood/validation diagnostics انتخاب شود، نه test.
- همه scalerها/transformها و fit HMM فقط با Train هر fold.
- در boundary بین Train و Validation/Test، filtered state posterior آخر Train به‌عنوان initial condition برای forward recursion ادامه یابد؛ test observations به‌صورت ترتیبی وارد شوند و هیچ refit با test انجام نشود.
- state ID بین foldها ذاتاً معنا و ترتیب ثابت ندارد؛ state mapping هر fold فقط از آمار Train مانند volatility و mean return ساخته شود.

## 5. Forward-filter recursion

برای state j:

`log_alpha_t(j) = log_emission_j(x_t) + logsumexp_i(log_alpha_{t-1}(i) + log_A(i,j))`

سپس normalize:

`filtered_t = softmax(log_alpha_t)`

این recursion باید فقط از alpha قبلی و observation فعلی استفاده کند. unit test مهم: تغییر هر observation پس از t نباید احتمال filtered در زمان t را تغییر دهد.

مرجع آموزشی الگوریتم filtering و Bayesian update:
- https://probml.github.io/ssm-book/chapters/hmm/hmm_filter.html

## 6. تشخیص رژیم و کیفیت مدل

Stateها را قبل از آموزش «روندی/رنج/بحرانی» نام‌گذاری نکنید. پس از fit، هر state بر اساس Train summaries توصیف شود:
- conditional mean/variance returns.
- median volatility و ATR ratio.
- transition probability و expected duration.
- frequency و average dwell time.
- confidence/entropy probability vector.
- stability در seedهای مختلف و folds.
- warnings برای state collapse، نوسان زیاد transition، یا state بسیار کم‌تعداد.

اسم‌ها و mapping باید per-fold versioned باشند.

## 7. ارزیابی W1

W1 باید در کنار W0 مستقل ارزیابی شود:
- کیفیت تشخیص regime و پایداری stateها.
- turnover of regime assignment و زمان تغییر state.
- اثر فیلتر رژیم بر تعداد Wyckoff candidates و trades.
- بعد از هزینه: expectancy/R، PF، DD، net profit و تعداد معامله.
- robustness در بازه‌های مختلف؛ عملکرد یک دوره به‌تنهایی کافی نیست.

Threshold فیلتر HMM فقط در Validation تعیین شود. در Test/OOS فقط frozen threshold/model استفاده شود.

## 8. برنامه یادگیری/آزمایش فعلی

1. پیاده‌سازی الگوریتم forward filter مستقل از library decoder.
2. ساخت synthetic HMM با دو/سه رژیم و تست causality.
3. تست label switching با چند seed.
4. ساخت fold-local scaler و HMM fit harness.
5. تست continuation از آخرین alpha مربوط به Train به sequence آزمایشی.
6. مستندسازی API probability output برای W2/W3.

## 9. Gate

**مجاز اکنون:** research, synthetic prototype, unit tests و design review.  
**ممنوع اکنون:** fit/selection روی XAUUSD واقعی، گزارش performance واقعی یا ارسال regime output به EA زنده؛ چون داده خام M1/Tick، event/candidate dataset و Fold manifest کامل نیست.

## منابع برای مطالعه
- Statsmodels filtering vs smoothing definitions: https://github.com/statsmodels/statsmodels/blob/main/statsmodels/tsa/regime_switching/markov_switching.py
- Statsmodels Markov autoregression example: https://github.com/statsmodels/statsmodels/blob/main/examples/python/markov_autoregression.py
- hmmlearn HMM tutorial and algorithms: https://github.com/hmmlearn/hmmlearn/blob/main/doc/source/tutorial.rst
- Murphy, *Probabilistic Machine Learning: Advanced Topics*, HMM filtering: https://probml.github.io/ssm-book/chapters/hmm/hmm_filter.html
