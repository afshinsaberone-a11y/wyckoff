# قرارداد داده — Feature و Label

نسخه schema: 1.2-draft.

## 1. جداسازی بنیادی
Feature snapshot در لحظه تصمیم ساخته می‌شود. Label outcome پس از پنجره آینده ساخته می‌شود. این دو در جدول و مسیر پردازش جدا بمانند.

## 2. نقطه تصمیم W2
نسخه اول W2 فقط برای M5_ENTRY تعریف می‌شود: کندل Recovery معتبر که موتور W0 پس از آن آماده فراخوانی PlaceTrade است. candidate_id قبل از فیلترهای اجرایی ساخته می‌شود.

- هر Recovery trigger مستقل یک candidate_id دارد.
- M5_ENTRY_EVALUATIONهای تکراری یک مسیر Candidate جدید نیستند.
- Candidateهای قبل از Recovery در Event Ledger می‌مانند؛ با Entry candidates مخلوط نمی‌شوند.
- Candidate واجد شرایطی که به‌علت Spread، Stop، Volume، Filling یا OrderSend اجرا نمی‌شود، به‌عنوان Candidate ردشده حفظ می‌شود.
- هدف «رسیدن به M5_ENTRY» یک مسئله جدا از «بازده پس از ورود» است؛ آن‌ها دو label مختلف‌اند.

## 3. Feature record

| فیلد | نوع | توضیح |
|---|---|---|
| feature_snapshot_id | string | شناسه یکتا |
| run_id | string | Run سازنده |
| candidate_id | string | Candidate مرتبط |
| group_id | string | گروه Range/Cycle برای Split |
| decision_time_server | datetime | زمان خام سرور در نقطه تصمیم |
| time_basis | enum | BROKER_SERVER_RAW تا زمان اثبات offset |
| decision_time_utc | timestamp/null | فقط پس از نگاشت timezone معتبر |
| feature_name | string | نام ویژگی |
| feature_value | numeric/string/null | مقدار |
| unit | string/null | واحد |
| source_event_ids | array | رویدادهای منبع |
| available_at_server | datetime | زمان در دسترس شدن |
| available_at_utc | timestamp/null | فقط پس از نگاشت timezone معتبر |
| feature_code_version | string | نسخه محاسبه |
| data_version | string | نسخه داده |
| missing_reason | string/null | علت داده مفقود |

قانون point-in-time: زمان available هر Feature نباید از decision time دیرتر باشد. در یک time basis یکسان، این مقایسه باید با timestamp server یا bar sequence قابل بازتولید انجام شود. داده‌های چندمنبعی فقط پس از تطبیق timezone/offset ادغام شوند.

## 4. گروه‌های اولیه Feature
- Range: width/ATR، duration، touch count و پراکندگی برخوردها.
- Wyckoff: عمق Spring/UTAD، Test quality، SOS/SOW type و strength، LPS/LPSY quality.
- Structure: فاصله تا Range Edge، internal swing break، candidate zone width.
- Market: ATR، realized volatility، relative volume و returns.
- Execution context: spread، session، tick coverage، distance to stop و volume constraints؛ فقط اگر در لحظه تصمیم معلوم باشند.
- Regime: در W1/W3، filtered probability HMM؛ state ID، مدل و Fold نیز ثبت شود.

## 5. Label record

| فیلد | نوع | توضیح |
|---|---|---|
| label_id | string | شناسه یکتا |
| run_id | string | Run برچسب‌گذاری |
| candidate_id | string | Candidate مرتبط |
| label_definition_version | string | نسخه تعریف برچسب |
| label_start_server | datetime | شروع outcome در time basis خام |
| label_end_server | datetime/null | پایان پنجره |
| time_basis | enum | basis timestamp |
| label_start_utc/label_end_utc | timestamp/null | فقط پس از offset معتبر |
| horizon_spec | string | افق ثابت یا قانون barrier |
| entry_assumption_id | string | فرض اجرای ورود |
| outcome_class | enum/string | کلاس هدف |
| net_return_r | numeric/null | outcome برحسب R پس از هزینه |
| mfe_r | numeric/null | بیشینه حرکت مساعد |
| mae_r | numeric/null | بیشینه حرکت نامساعد |
| censoring_status | enum | COMPLETE/RIGHT_CENSORED/INVALID |
| non_entry_reason | string/null | علت عدم ورود/اجرا |
| execution_assumption_id | string | فرض اجرا |
| cost_model_version | string | نسخه هزینه‌ها |

## 6. تعریف outcome پیش از مشاهده Test
قبل از آموزش باید مشخص شود:
- افق ثابت زمانی است یا barrier مبتنی بر SL/TP/حد زمانی.
- قیمت ورود فرضی و زمان مجاز ورود چیست.
- برخورد هم‌زمان SL و TP در داده غیرقابل تفکیک چگونه مدیریت می‌شود.
- spread، commission، swap، slippage و gap چگونه لحاظ می‌شوند.
- Candidate واجد شرایطی که سفارش رد شده با چه فرض fill فرضی برچسب می‌گیرد.
- Candidateی که به دلیل نبود M5 trigger به نقطه تصمیم نرسیده، label مربوط به Entry scoring نمی‌گیرد؛ برای «رسیدن به Entry» مسئله جدا تعریف شود.
- پایان تاریخچه یا نبود تیک چگونه censoring ایجاد می‌کند.
- برای تبدیل به UTC، timezone/offset سرور و DST باید مستند باشد؛ تا آن زمان زمان خام سرور و bar sequence حفظ شوند.

## 7. قواعد آماری
- Labelهای هم‌پوشان برای Purge شناسایی شوند.
- Candidateهای متعدد از یک Range/Cycle در Split گروهی باقی بمانند.
- Oversampling و class weighting فقط داخل Train انجام شود.
- معیارهای classification به‌تنهایی اثبات سود معاملاتی نیستند.
- threshold و calibration فقط با Validation انتخاب شوند.
- عملکرد «رسیدن به Entry» و «بازده پس از Entry» جدا گزارش شود.
