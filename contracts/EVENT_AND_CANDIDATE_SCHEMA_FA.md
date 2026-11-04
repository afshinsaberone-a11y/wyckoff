# قرارداد داده — Event، Range، Cycle و Candidate

نسخه schema: 1.1-draft  
مالک: AGENT_01؛ تأیید ساختاری: AGENT_04؛ ممیزی: AGENT_03.

## اصول
- رویداد ساختاری، محدوده Range، چرخه Wyckoff، تلاش یک رویداد، فرصت ورود، تصمیم، سفارش و معامله موجودیت‌های جدا هستند.
- شناسه legacy به‌صورت خودکار معادل Candidate ID فرض نشود.
- زمان وقوع، زمان بسته‌شدن bar منبع، زمان available شدن، و زمان تصمیم جدا ذخیره شوند.
- فرصت‌های اجرا‌نشده و ردشده نیز باید ثبت شوند.
- یک Candidate نباید با Candidate دیگر فقط به علت داشتن Range والد یکسان ادغام شود.

## سلسله‌مراتب شناسه

| ID | معنی |
|---|---|
| range_id | یک Trading Range تشخیص‌داده‌شده |
| cycle_id | یک چرخه ساختاری زیر یک Range (Spring/UTAD → Test → Strength → LPS/LPSY) |
| attempt_id | یک تلاش مستقل Spring/UTAD یا تلاش مجدد |
| candidate_id | یک فرصت در نقطه تصمیم ثابت و قابل امتیازدهی |
| decision_id | یک تصمیم فیلتر/رد/قبول |
| trade_id | معامله شبیه‌سازی‌شده یا واقعی |
| legacy_setup_id | مقدار فعلی SetupID در لاگ‌های قدیمی |

**هشدار سازگاری:** در سورس C2 فعلی، شمارنده `g_setupCounter` هنگام شناسایی Range افزایش می‌یابد و همان مقدار با نام `SetupID` در Event CSV نوشته می‌شود. پس این فیلد به `legacy_setup_id` نگاشت شود؛ نه اینکه بدون بررسی به `candidate_id` تبدیل شود.

هر Candidate باید range_id و cycle_id والد خود را در صورت وجود داشته باشد. چند Candidate از یک cycle باید candidate_id مجزا و group_id مشترک داشته باشند.

## Event record

| فیلد | نوع پیشنهادی | توضیح |
|---|---|---|
| event_id | string | شناسه یکتا و پایدار |
| event_type | enum/string | RANGE_FOUND، SPRING، UTAD، TEST، SOS، SOW، LPS، LPSY و ... |
| range_id | string/null | Range والد |
| cycle_id | string/null | چرخه ساختاری والد |
| attempt_id | string/null | تلاش ساختاری والد |
| legacy_setup_id | string/null | SetupID در لاگ قدیمی |
| symbol | string | XAUUSD |
| timeframe | string | H4/H1/M5 |
| direction | BUY/SELL/NEUTRAL | جهت هنگام ثبت |
| event_time_utc | timestamp | زمان bar/event منبع |
| source_bar_open_utc | timestamp | زمان بازشدن bar منبع |
| source_bar_close_utc | timestamp | زمان بسته‌شدن bar منبع |
| available_at_utc | timestamp | نخستین زمانی که رویداد برای تصمیم قابل استفاده است |
| decision_time_utc | timestamp/null | زمان تصمیم مرتبط |
| server_time | timestamp | زمان خام بروکر/سرور |
| server_timezone | string | timezone یا offset سرور |
| price_level | decimal/null | سطح مرتبط |
| parent_event_id | string/null | رویداد والد |
| rule_version | string | نسخه قاعده |
| code_commit | string | Commit تولیدکننده |
| data_version | string | نسخه داده |
| evidence_ref | string | مسیر رکورد/لاگ/کندل پشتیبان |

## Candidate record

| فیلد | نوع پیشنهادی | توضیح |
|---|---|---|
| candidate_id | string | شناسه یکتا برای هر فرصت |
| candidate_type | enum | STRUCTURE_STAGE / M5_ENTRY |
| decision_stage | string | نقطه تصمیم ازپیش‌تعریف‌شده |
| range_id | string | Range والد |
| cycle_id | string/null | چرخه ساختاری والد |
| attempt_id | string/null | تلاش رویداد والد |
| legacy_setup_id | string/null | شناسه نگاشت‌شده از نسخه قدیمی |
| group_id | string | کلید گروه برای Split/Uncertainty |
| direction | BUY/SELL | جهت |
| candidate_time_utc | timestamp | زمان ایجاد |
| decision_time_utc | timestamp | زمان snapshot و تصمیم |
| available_at_utc | timestamp | آخرین زمان availability ورودی‌ها |
| entry_model | string | شناسه منطق ورود |
| hypothetical_entry | decimal/null | قیمت ورود فرضی |
| hypothetical_sl | decimal/null | حد ضرر فرضی |
| hypothetical_tp | decimal/null | حد سود فرضی |
| risk_target_pct | decimal/null | ریسک هدف آزمایش |
| status | enum | PENDING/ACCEPTED/REJECTED/EXPIRED/INVALIDATED/NOT_TRADED/EXECUTED |
| rejection_reason | string/null | علت مشخص رد |
| expiry_time_utc | timestamp/null | پایان اعتبار |
| invalidation_time_utc | timestamp/null | زمان ابطال |
| feature_snapshot_id | string/null | snapshot ویژگی |
| experiment_id | string | آزمایش سازنده |
| code_commit | string | Commit تولیدکننده |

## Decision record
هر تصمیم باید `decision_id`، `candidate_id`، `decision_time_utc`، `decision_type`، `decision_reason`، `agent_or_engine`، `model_version`، `threshold_version` و `input_snapshot_id` داشته باشد.

## نگاشت نسخه‌های قدیمی
- ستون `SetupID` به `legacy_setup_id` نگاشت شود.
- `range_id` فقط وقتی ساخته شود که هر RANGE_FOUND و lifecycle بعدی با شواهد قابل اتصال باشد.
- تلاش‌های چندباره Spring/UTAD از جزئیات و توالی رویداد بازسازی شوند؛ اگر مبهم است، `attempt_id=UNKNOWN` بماند.
- `candidate_id` قدیمی جعل نشود؛ فقط با الگوریتم migration deterministic و ثبت‌شده ایجاد شود.
- رکوردهایی که اتصال آن‌ها قطعی نیست تا بازبینی از supervised training کنار گذاشته شوند.

## قواعد اعتبارسنجی
1. `available_at_utc <= decision_time_utc` برای همه ورودی‌های تصمیم الزامی است.
2. `EXECUTED` باید به سفارش، deal و trade_id قابل ردیابی متصل باشد.
3. Candidate بدون معامله نامعتبر نیست؛ وضعیت و علت آن حفظ شود.
4. اگر رکوردی اصلاح شد، نسخه اصلی و audit trail آن حفظ شود.
5. زمان server همراه timezone/offset منبع نگهداری شود.
6. Splitها باید بر اساس group_id/range_id/cycle_id از قرارگرفتن وابستگی‌های یک ساختار در Train و Test جلوگیری کنند.
