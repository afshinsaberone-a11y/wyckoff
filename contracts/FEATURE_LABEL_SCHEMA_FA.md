# قرارداد داده — Feature و Label

نسخه schema: 1.0-draft.

## جداسازی بنیادی
Feature snapshot در لحظه تصمیم ساخته می‌شود. Label outcome بعد از پنجره آینده ساخته می‌شود. این دو باید در فایل/جدول و مسیر کد جدا باشند.

## Feature record
| فیلد | نوع | توضیح |
|---|---|---|
| feature_snapshot_id | string | شناسه یکتا |
| setup_id | string | Candidate مرتبط |
| decision_time_utc | timestamp | لحظه تصمیم |
| feature_name | string | نام ویژگی |
| feature_value | numeric/string/null | مقدار |
| unit | string/null | واحد |
| source_event_ids | array | رویدادهای منبع |
| available_at_utc | timestamp | زمان دسترس‌پذیری |
| feature_code_version | string | نسخه محاسبه |
| missing_reason | string/null | علت داده مفقود |

قانون: برای هر feature باید `available_at_utc <= decision_time_utc` برقرار باشد. ویژگی‌هایی مانند Pivot یا Swing فقط پس از بسته‌شدن کندل تأییدکننده قابل دسترس‌اند.

## گروه‌های اولیه Feature
- Range: width/ATR، duration، touch count و پراکندگی برخوردها.
- Wyckoff: عمق Spring/UTAD، Test quality، SOS/SOW type و strength، LPS/LPSY quality.
- Structure: فاصله تا Range Edge، internal swing break، candidate zone width.
- Market: ATR، realized volatility، relative volume و returns.
- Regime: فقط در W1/W3، احتمال فیلترشده HMM؛ state ID و مدل/Fold نیز ثبت شود.

## Label record
| فیلد | نوع | توضیح |
|---|---|---|
| label_id | string | شناسه یکتا |
| setup_id | string | Candidate مرتبط |
| label_definition_version | string | نسخه تعریف برچسب |
| label_start_utc | timestamp | شروع مشاهده outcome |
| label_end_utc | timestamp/null | پایان افق |
| horizon_spec | string | افق ثابت یا قانون barrier |
| outcome_class | enum/string | کلاس هدف |
| net_return_r | numeric/null | outcome برحسب R پس از هزینه |
| mfe_r | numeric/null | بیشینه حرکت مساعد |
| mae_r | numeric/null | بیشینه حرکت نامساعد |
| censoring_status | enum | COMPLETE/RIGHT_CENSORED/INVALID |
| execution_assumption_id | string | فرض اجرا |
| cost_model_version | string | نسخه هزینه‌ها |

## تعریف outcome
قبل از دیدن Validation/Test باید تعیین شود:
- افق ثابت زمانی است یا barrier مبتنی بر SL/TP/حد زمانی.
- قیمت ورود فرضی و زمان مجاز ورود چیست.
- اگر SL و TP در یک کندل یا بازه غیرقابل تفکیک برخورد کنند، قاعده محافظه‌کارانه چیست.
- spread، commission، swap، slippage و gap چگونه لحاظ می‌شوند.
- پایان تاریخچه یا نبود تیک چگونه censoring ایجاد می‌کند.

## قواعد آماری
- Labelهای هم‌پوشان باید برای Purge شناسایی شوند.
- Candidateهای متعدد از یک Range ممکن است وابستگی داشته باشند؛ group_id حفظ شود.
- وزن‌دهی/oversampling فقط داخل Train انجام شود.
- معیارهای classification به تنهایی اثبات سود معاملاتی نیستند.
- آستانه score فقط با Validation انتخاب شود.
