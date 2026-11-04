# قرارداد داده — Event و Candidate

نسخه schema: 1.0-draft  
مالک: AGENT_01؛ تأیید ساختاری: AGENT_04؛ ممیزی: AGENT_03.

## اصول
- رویداد ساختاری، فرصت معاملاتی، تصمیم، سفارش و معامله موجودیت‌های جدا هستند.
- هر رکورد شناسه پایدار دارد؛ ارتباط‌ها با ID انجام می‌شود، نه با اتکا به ترتیب ردیف CSV.
- زمان وقوع، زمان قابل‌دسترسی‌شدن و زمان تصمیم جدا ذخیره شوند.
- فرصت‌های اجرا‌نشده و ردشده نیز باید ثبت شوند.

## Event record
| فیلد | نوع پیشنهادی | توضیح |
|---|---|---|
| event_id | string | شناسه یکتا و پایدار |
| event_type | enum/string | RANGE_FOUND، SPRING، UTAD، TEST، SOS، SOW، LPS، LPSY و ... |
| setup_id | string/null | پیوند به Candidate یا چرخه ساختاری |
| symbol | string | XAUUSD |
| timeframe | string | H4/H1/M5 |
| direction | BUY/SELL/NEUTRAL | جهت در زمان ثبت |
| event_time_utc | timestamp | زمان نظری وقوع |
| available_at_utc | timestamp | نخستین زمان مجاز برای استفاده |
| source_bar_time | timestamp | کندل منبع |
| source_bar_close_time | timestamp | زمان بسته‌شدن کندل منبع |
| price_level | decimal/null | سطح مرتبط |
| range_id | string/null | شناسه Range |
| parent_event_id | string/null | رویداد والد |
| rule_version | string | نسخه قاعده |
| data_version | string | نسخه داده |
| evidence_ref | string | مسیر رکورد/لاگ/کندل پشتیبان |

## Candidate record
| فیلد | نوع پیشنهادی | توضیح |
|---|---|---|
| setup_id | string | شناسه یکتای Candidate |
| range_id | string/null | Range والد |
| direction | BUY/SELL | جهت |
| candidate_time_utc | timestamp | زمان ایجاد Candidate |
| decision_time_utc | timestamp | زمان تصمیم |
| available_at_utc | timestamp | زمان دسترس‌پذیری آخرین ورودی |
| entry_model | string | شناسه منطق M5 |
| hypothetical_entry | decimal/null | قیمت ورود فرضی |
| hypothetical_sl | decimal/null | حد ضرر فرضی |
| hypothetical_tp | decimal/null | حد سود فرضی |
| risk_target_pct | decimal/null | ریسک هدف آزمایش |
| status | enum | PENDING/ACCEPTED/REJECTED/EXPIRED/INVALIDATED/NOT_TRADED/EXECUTED |
| rejection_reason | string/null | علت مشخص رد |
| expiry_time_utc | timestamp/null | پایان اعتبار |
| invalidation_time_utc | timestamp/null | زمان ابطال |
| feature_snapshot_id | string/null | پیوند به ویژگی‌ها |
| experiment_id | string | آزمایش سازنده |
| code_commit | string | Commit تولیدکننده |

## Decision record
هر تصمیم باید `decision_id`، `setup_id`، `decision_time_utc`، `decision_type`، `decision_reason`، `agent_or_engine`، `model_version`، `threshold_version` و `input_snapshot_id` داشته باشد.

## قواعد اعتبارسنجی
1. `available_at_utc <= decision_time_utc` برای همه ورودی‌های تصمیم الزامی است.
2. `EXECUTED` باید به سفارش و deal قابل ردیابی متصل باشد.
3. Candidate بدون معامله، Candidate نامعتبر نیست؛ وضعیت و علت آن باید حفظ شود.
4. اگر یک رکورد اصلاح شد، نسخه اصلی و audit trail آن حفظ شود.
5. timestampهای broker/server time همراه با timezone/offset منبع نیز نگهداری شوند.
