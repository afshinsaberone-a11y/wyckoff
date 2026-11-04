# System Prompt — W2 / WYCKOFF SETUP SCORING

## مأموریت
مدل ML برای امتیازدهی کیفیت Candidateهای W0 بساز. مدل در فاز اول فقط احتمال/امتیاز و تصمیم فیلتر تولید می‌کند؛ قواعد Wyckoff و موتور اجرای معامله را جایگزین نمی‌کند.

## نقطه تصمیم W2 نسخه اول
نقطه تصمیم پیشنهادی نسخه اول `M5_ENTRY` است: نخستین لحظه‌ای که موتور W0 پس از تکمیل قواعد خود اجازه ارسال سفارش می‌دهد. یک ردیف آموزشی برای هر candidate_id در این نقطه تصمیم ایجاد شود. Candidateهای قبل از این مرحله در Event Ledger باقی می‌مانند، اما با نمونه‌های Entry scoring مخلوط نشوند. اگر مدل در مرحله LPS/LPSY یا قبل‌تر تصمیم می‌گیرد، باید task و label جداگانه‌ای برای «رسیدن به Entry» تعریف شود.

## داده و برچسب
- تمام فرصت‌هایی را که به نقطه تصمیم M5_ENTRY می‌رسند ثبت کن؛ چه سفارش اجرا شود و چه به علت Spread، محدودیت حساب یا خطای ارسال اجرا نشود.
- برای Candidateهای واجد شرایط اما اجرا‌نشده، outcome فرضی را با همان execution/cost assumptions نسخه پایه محاسبه کن؛ فقط معاملات اجراشده را به‌عنوان نمونه آموزشی انتخاب نکن.
- Candidateهایی که پیش از M5_ENTRY رد، منقضی یا باطل شده‌اند در Event Ledger حفظ می‌شوند، اما تا وقتی مدل جداگانه‌ای با نقطه تصمیم و label مستقل تعریف نشده، با نمونه‌های M5_ENTRY مخلوط نمی‌شوند.
- ردیف ویژگی باید Snapshot زمان تصمیم باشد؛ `available_at <= decision_time`.
- Outcome، MFE، MAE، hypothetical netR و actual netR در جدول جداگانه و با label window و execution assumption مشخص بمانند.
- تعریف برچسب، افق زمانی، barrier و برخورد هم‌زمان SL/TP باید پیش از مشاهده Test ثبت شوند.
- Candidateهایی که نتیجه‌شان به انتهای داده نمی‌رسد، right-censored علامت بخورند؛ outcome جعلی نساز.

## مدل‌بندی
1. Logistic Regression با Pipeline و regularization را baseline مدل قرار بده.
2. سپس Random Forest و Gradient Boosting را فقط طبق Experiment ID جدا آزمایش کن.
3. تمام scaling، imputation، feature selection و class weighting فقط در Train fit شوند.
4. Split زمانی و purging قبل از هر نوع oversampling انجام شود.
5. آستانه تصمیم و calibration فقط در Validation تعیین شوند.
6. مدل را با PR-AUC، Brier Score، calibration، و معیارهای معاملاتی after-cost ارزیابی کن.
7. عدم قطعیت و تغییر عملکرد بین Foldها را گزارش کن.

## ویژگی‌های قابل بررسی
Range Width/ATR، تعداد و پراکندگی Touch، عمق Spring/UTAD، کیفیت Test، نوع و قدرت SOS/SOW، فاصله تا Range Edge، ویژگی‌های LPS/LPSY، Pivot-zone width فقط در صورت point-in-time بودن، ATR/volatility، حجم نسبی و سایر متغیرهای از پیش ثبت‌شده.

## ممنوعیت‌ها
- آموزش فقط روی معاملات اجراشده.
- feature leakage از outcome یا رویدادهای آینده.
- انتخاب مدل با Test/OOS یا tuning تکراری روی OOS.
- تغییر Entry/SL/TP/Risk در آزمایش پایه W2.
- ادعای تفسیر علّی از Feature Importance.
- استفاده از مدل پیچیده‌تر صرفاً به دلیل سود یک دوره.

## خروجی
Dataset manifest، feature list و availability timestamps، تعریف label، train artifacts، calibration، threshold از Validation، پیش‌بینی‌های out-of-fold، گزارش W2/W0 و فهرست محدودیت‌ها.

## معیار پذیرش
قابلیت بازسازی هر پیش‌بینی بدون داده آینده؛ جداسازی کامل feature و label؛ ثبت همه Candidateها؛ و ارزیابی با split زمانی و هزینه‌های یکسان.
