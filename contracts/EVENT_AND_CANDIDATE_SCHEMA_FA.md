# قرارداد داده — Event، Range، Cycle، Attempt و Candidate

نسخه schema: 1.2-draft  
مالک: AGENT_01؛ تأیید ساختاری: AGENT_04؛ ممیزی: AGENT_03.  
این نسخه بخش v1.1 را با قرارداد عملیاتی BOOT-003 Event Ledger v2 هماهنگ می‌کند.

## 1. موجودیت‌ها و سلسله‌مراتب

| شناسه | معنی | زمان ایجاد |
|---|---|---|
| run_id | یک اجرای مشخص Tester/Replay | قبل از شروع Run؛ یکتا در manifest |
| range_id | یک Trading Range | هنگام RANGE_FOUND |
| cycle_id | یک مسیر ساختاری زیر Range | اولین Spring/UTAD attempt که چرخه را آغاز می‌کند |
| attempt_id | یک تلاش مستقل Spring/UTAD | برای هر تلاش جدید |
| candidate_id | فرصت ورود مستقل در M5_ENTRY | بعد از Recovery معتبر و پیش از PlaceTrade |
| decision_id | ارزیابی یک Gate/تصمیم | برای هر تصمیم اجرایی/مدلی |
| order_id | Ticket واقعی Order | پس از پذیرش سفارش |
| deal_id | Ticket واقعی Deal | از OnTradeTransaction |
| position_id | شناسه Position | از DEAL_POSITION_ID |
| trade_id | شناسه معامله اقتصادی تجمیع‌شده | فقط پس از تعریف و تأیید Join ورود/partial fills/خروج |
| legacy_setup_id | SetupID فایل‌های قدیمی | همان مقدار تاریخی؛ بدون تغییر |

هر شناسه باید یکتا و پایدار باشد. شناسه‌های جدید به run_id متصل شوند تا دو اجرای هم‌پارامتر نیز با هم تداخل نکنند.

## 2. قواعد identity

### Range
در سورس C2 فعلی، g_setupCounter هنگام تشخیص Range افزایش می‌یابد و همان مقدار با نام SetupID در Event CSV نوشته می‌شود. بنابراین:
- SetupID قدیمی فقط به legacy_setup_id نگاشت می‌شود.
- در migration می‌توان با شواهد سورس یک range_id مصنوعی deterministic ساخت: LEGACY_RANGE:{EA_Version}:{Symbol}:{SetupID}.
- این شناسه migration است؛ آن را با شناسه‌ای که سورس v2 در زمان اجرا ساخته اشتباه نکن.

### Cycle و Attempt
- cycle_id مسیر ساختاری Spring/UTAD → Test → Strength → LPS/LPSY را گروه می‌کند.
- attempt_id هر تلاش مستقل Spring یا UTAD را مشخص می‌کند.
- اگر مرز یک چرخه در state machine قابل اثبات نیست، cycle_id خالی بماند.
- تلاش مجدد نباید با attempt قبلی ادغام شود.

### Candidate
نقطه تصمیم W2 نسخه اول M5_ENTRY است. در سورس W0، candidate_id درست پس از تأیید M5 Recovery و پیش از PlaceTrade ساخته می‌شود. این نقطه پیش از فیلتر Spread، tick، stop، volume، filling و OrderSend است؛ بنابراین Candidateهایی که اجرا نمی‌شوند نیز ثبت می‌شوند.

- هر Recovery trigger مستقل candidate_id جدید می‌گیرد.
- چند رویداد M5_ENTRY_EVALUATION در یک مسیر Candidate مستقل محسوب نمی‌شوند.
- M5 breakout/retest پیش از Recovery، eventهای مسیرند و candidate_id ندارند.
- Spread rejection یا OrderSend failure نباید Candidate را حذف کند.

## 3. Event record — schema v2

| فیلد | نوع | الزام | توضیح |
|---|---|---|---|
| schema_version | string | بله | نسخه ردیف، مثلاً EVENT_LEDGER_V2 |
| run_id | string | بله | اجرای مشخص |
| event_id | string | بله | شناسه یکتای هر event row |
| event_sequence | integer | بله | ترتیب افزایشی ردیف در Run |
| event_type | string/enum | بله | RANGE_FOUND، SPRING، TEST، SOS، M5... |
| event_time_server | datetime string | بله | زمان خام ثبت event در سرور |
| observed_at_server | datetime string | بله | زمان مشاهده/پردازش توسط EA |
| time_basis | enum | بله | BROKER_SERVER_RAW تا زمان اثبات timezone |
| source_timeframe | string/null | در صورت وجود | H4/H1/M5 |
| source_bar_open_server | datetime/null | در صورت وجود | زمان بازشدن کندل منبع |
| symbol | string | بله | XAUUSD |
| direction | BUY/SELL/NEUTRAL | بله | جهت در زمان event |
| range_id | string/null | در صورت وجود | Range والد |
| cycle_id | string/null | در صورت وجود | چرخه والد |
| attempt_id | string/null | در صورت وجود | تلاش والد |
| candidate_id | string/null | در صورت وجود | Candidate والد |
| decision_id | string/null | در صورت وجود | تصمیم والد |
| order_id | string/null | در صورت وجود | Order واقعی |
| deal_id | string/null | در صورت وجود | Deal واقعی |
| position_id | string/null | در صورت وجود | Position واقعی |
| legacy_setup_id | string/null | برای migration | SetupID فایل قدیمی |
| ea_version | string | بله | شناسه دقیق EA |
| rule_version | string | بله | نسخه قواعد |
| code_commit | string | بله | Commit سورس |
| data_version | string | در صورت وجود | داده/manifest |
| decision_status | string/null | در صورت وجود | ACCEPTED/REJECTED/EXPIRED/INVALIDATED |
| reason_code | string/null | در صورت وجود | کد استاندارد علت |
| details | string | اختیاری | متن تکمیلی |
| range_high/range_low | decimal/null | در صورت وجود | سطوح Range |

## 4. Candidate record

هر Candidate در جدول مستقل نگهداری شود:

| فیلد | نوع | توضیح |
|---|---|---|
| candidate_id | string | شناسه یکتا |
| run_id | string | Run سازنده |
| candidate_type | enum | M5_ENTRY در نسخه اول |
| decision_stage | string | M5_ENTRY |
| range_id/cycle_id/attempt_id | string/null | والدهای ساختاری |
| group_id | string | حداقل Range-level برای group split |
| direction | BUY/SELL | جهت |
| source_bar_open_server | datetime | کندل Recovery منبع |
| candidate_time_server | datetime | زمان ثبت Recovery |
| decision_time_server | datetime | زمان تصمیم |
| time_basis | enum | BROKER_SERVER_RAW |
| entry_model | string | نسخه منطق ورود |
| entry_price_request | decimal/null | قیمت Quote درخواست |
| hypothetical_sl/tp | decimal/null | فقط اگر محاسبه شده |
| risk_target_pct | decimal/null | ریسک هدف |
| status | enum | CREATED/REJECTED/ORDER_ACCEPTED/EXPIRED/INVALIDATED |
| rejection_reason | string/null | دلیل رد اجرای سفارش |
| order_id/deal_id/position_id | string/null | شناسه‌های واقعی پس از ایجاد |
| feature_snapshot_id | string/null | Snapshot point-in-time |
| experiment_id | string | آزمایش |
| code_commit | string | نسخه سورس |

## 5. Decision record

هر تصمیم باید این فیلدها را داشته باشد:
- decision_id، candidate_id و run_id
- decision_time_server و time_basis
- decision_stage، decision_type، decision_status
- reason_code، agent_or_engine
- model_version و threshold_version در W1/W2/W3
- input_snapshot_id و feature_snapshot_id

یک Candidate می‌تواند چند decision_id داشته باشد؛ Candidate ID ثابت می‌ماند.

## 6. زمان و timezone

CSV قدیمی فقط ServerTime دارد؛ timezone/offset، source bar time و availability را ندارد.
- زمان خام سرور را نگهداری کن.
- time_basis را BROKER_SERVER_RAW قرار بده.
- event_time_utc، source_bar_close_utc و available_at_utc تا زمان اثبات offset خالی بمانند.
- TimeCurrent را با زمان کندل منبع یکی فرض نکن.
- source_bar_open_server و observed_at_server را جدا ثبت کن.
- تبدیل UTC فقط با timezone/offset معتبر و قابل ممیزی انجام شود؛ DST تاریخی باید پوشش داده شود.

## 7. نگاشت نسخه‌های قدیمی

- SetupID به legacy_setup_id نگاشت شود.
- range_id قدیمی فقط با شواهد افزایش g_setupCounter هنگام RANGE_FOUND بازسازی شود.
- candidate_id، cycle_id، attempt_id، trade_id، decision_id یا UTC از CSV قدیمی جعل نشود.
- PositionID قدیمی فقط legacy_position_id بماند تا Order/Deal join تأیید شود.
- Migration باید source hash، row number و algorithm version ثبت کند.
- event_id در migration باید deterministic باشد؛ برای duplicate rows، source row number بخشی از seed باشد.

## 8. قواعد Split و ممیزی

- حداقل group_id برابر Range است تا Candidateهای یک Range بین Train/Test نشت نکنند.
- اگر cycleهای مستقل در یک Range وجود دارند، تحلیل حساسیت group split در Range-level و Cycle-level جدا گزارش شود؛ split در سطح Candidate خام ممنوع است.
- هر Candidate اجرا‌نشده حفظ شود.
- Feature و Label در جدول‌های مستقل باشند.
- UTC خالی را به‌عنوان زمان واقعی گزارش نکن.
- Order/Deal/Position باید از شناسه‌های واقعی MT5 استخراج شوند؛ text details به‌تنهایی برای Join کافی نیست.
