# قرارداد داده — Feature و Label

نسخه schema: 1.1-draft.

## جداسازی بنیادی
Feature snapshot در لحظه تصمیم ساخته می‌شود. Label outcome بعد از پنجره آینده ساخته می‌شود. این دو در جدول و مسیر پردازش جدا نگهداری شوند.

## نقطه تصمیم و تعریف نمونه
W2 باید ابتدا یک نقطه تصمیم ازپیش‌تعریف‌شده داشته باشد. پیشنهاد نسخه اول: `M5_ENTRY` یعنی نخستین لحظه‌ای که موتور W0 بر اساس قواعد Freezeشده اجازه ارسال سفارش می‌دهد؛ snapshot باید پیش از ارسال سفارش و پیش از مشاهده حرکت بعدی ثبت شود.

- هر `candidate_id` یک نمونه مستقل در این نقطه تصمیم است.
- چند bar از یک Candidate را بدون تعریف مدل sequence به چند نمونه مستقل تبدیل نکن.
- Candidateهایی که به نقطه تصمیم M5_ENTRY نمی‌رسند، در Event Ledger باقی می‌مانند اما در دیتاست classification کیفیت Entry ادغام نمی‌شوند.
- فرصت‌هایی که در نقطه تصمیم واجد شرایط‌اند ولی سفارششان به علت spread، محدودیت حساب یا خطای اجرا باز نمی‌شود باید ثبت شوند؛ نتیجه فرضی آن‌ها با execution assumption مشخص و جدا محاسبه شود.
- اگر مدل در مرحله زودتر مانند پس از LPS/LPSY تصمیم بگیرد، target باید احتمال رسیدن به M5 entry و outcome بعد از ورود را جدا کند؛ این با Entry scoring یک مسئله واحد نیست.

## Feature record

| فیلد | نوع | توضیح |
|---|---|---|
| feature_snapshot_id | string | شناسه یکتا |
| candidate_id | string | Candidate مرتبط |
| group_id | string | گروه ساختاری برای split |
| decision_time_utc | timestamp | لحظه تصمیم |
| feature_name | string | نام ویژگی |
| feature_value | numeric/string/null | مقدار |
| unit | string/null | واحد |
| source_event_ids | array | رویدادهای منبع |
| available_at_utc | timestamp | زمان دسترس‌پذیری |
| feature_code_version | string | نسخه محاسبه |
| data_version | string | نسخه داده |
| missing_reason | string/null | علت داده مفقود |

قانون: برای هر feature باید `available_at_utc <= decision_time_utc` برقرار باشد. ویژگی‌هایی مانند Pivot یا Swing فقط پس از بسته‌شدن کندل تأییدکننده قابل دسترس‌اند.

## گروه‌های اولیه Feature
- Range: width/ATR، duration، touch count و پراکندگی برخوردها.
- Wyckoff: عمق Spring/UTAD، Test quality، SOS/SOW type و strength، LPS/LPSY quality.
- Structure: فاصله تا Range Edge، internal swing break، candidate zone width.
- Market: ATR، realized volatility، relative volume و returns.
- Execution context: spread، session، tick coverage، distance to stop و volume constraints؛ فقط اگر در لحظه تصمیم معلوم باشند.
- Regime: در W1/W3، احتمال فیلترشده HMM؛ state ID و مدل/Fold نیز ثبت شود.

## Label record

| فیلد | نوع | توضیح |
|---|---|---|
| label_id | string | شناسه یکتا |
| candidate_id | string | Candidate مرتبط |
| label_definition_version | string | نسخه تعریف برچسب |
| label_start_utc | timestamp | شروع مشاهده outcome |
| label_end_utc | timestamp/null | پایان افق |
| horizon_spec | string | افق ثابت یا قانون barrier |
| entry_assumption_id | string | فرض اجرای ورود |
| outcome_class | enum/string | کلاس هدف |
| net_return_r | numeric/null | outcome برحسب R پس از هزینه |
| mfe_r | numeric/null | بیشینه حرکت مساعد |
| mae_r | numeric/null | بیشینه حرکت نامساعد |
| censoring_status | enum | COMPLETE/RIGHT_CENSORED/INVALID |
| non_entry_reason | string/null | عدم تولید entry یا عدم اجرا |
| execution_assumption_id | string | فرض اجرا |
| cost_model_version | string | نسخه هزینه‌ها |

## تعریف outcome پیش از مشاهده Test
پیش از آموزش باید مشخص شود:
- افق ثابت زمانی است یا barrier مبتنی بر SL/TP/حد زمانی.
- قیمت ورود فرضی و زمان مجاز ورود چیست.
- اگر SL و TP در یک کندل یا بازه غیرقابل تفکیک برخورد کنند، قاعده محافظه‌کارانه چیست.
- spread، commission، swap، slippage و gap چگونه لحاظ می‌شوند.
- Candidate واجد شرایطی که سفارش واقعی آن رد شده، با چه فرض fill فرضی برچسب می‌گیرد.
- Candidateی که هیچ trigger در پنجره مجاز ندارد، non-entry است؛ نباید بازده معامله‌ای ساختگی به آن نسبت داد.
- پایان تاریخچه یا نبود تیک چگونه censoring ایجاد می‌کند.

## قواعد آماری
- Labelهای هم‌پوشان برای Purge شناسایی شوند.
- Candidateهای متعدد از یک Range/Cycle در Split به‌صورت گروهی نگهداری شوند.
- Oversampling و class weighting فقط داخل Train انجام شود.
- معیارهای classification به‌تنهایی اثبات سود معاملاتی نیستند.
- آستانه score فقط با Validation انتخاب شود.
- عملکرد دو هدف «رسیدن به Entry» و «بازده پس از Entry» جدا گزارش شود؛ این دو label را در یک ستون مبهم مخلوط نکن.
