# قرارداد داده — Experiment و Walk-Forward Fold

نسخه schema: 1.0-draft.

## Experiment manifest
هر آزمایش باید حداقل این فیلدها را داشته باشد:

| فیلد | توضیح |
|---|---|
| experiment_id | شناسه یکتا و immutable |
| hypothesis | فرضیه مشخص و قابل ابطال |
| variant | W0/W1/W2/W3 یا آزمایش فرعی |
| parent_experiment_id | آزمایش والد |
| protocol_version | نسخه پروتکل |
| code_commit | Commit کد |
| data_hash | هش داده و manifest |
| config_hash | هش تنظیمات |
| feature_schema_version | نسخه ویژگی |
| label_schema_version | نسخه برچسب |
| cost_model_version | نسخه هزینه اجرا |
| symbol/broker | XAUUSD / WMMarkets-Demo یا مقدار واقعی ثبت‌شده |
| account_spec | ارز، سرمایه، اهرم و قرارداد |
| date_range | بازه آزمون |
| tick_model | مدل تیک و محدودیت پوشش |
| risk/SL/TP | قواعد اجرای مشترک |
| random_seed | در صورت وجود تصادف |
| created_at | زمان ثبت |
| status | DRAFT/FROZEN/RUNNING/COMPLETE/INVALIDATED |

## تعریف چهار نسخه
| Variant | HMM | ML | هدف |
|---|---:|---:|---|
| W0 | No | No | Baseline frozen |
| W1 | Yes | No | اثر HMM |
| W2 | No | Yes | اثر ML |
| W3 | Yes | Yes | اثر ترکیبی |

هر نسخه باید از همان Candidate universe W0 استفاده کند. فیلتر ممکن است تعداد معاملات را تغییر دهد؛ برابرکردن مصنوعی تعداد معاملات ممنوع است.

## Fold manifest
هر Fold باید:
- train_start/end
- validation_start/end
- test_start/end
- purge_rule
- embargo_rule
- label_horizon
- grouped_setup/range policy
- scaler/model fit scope
- threshold selection scope
- fit artifact hashes
داشته باشد.

## Purge و Embargo
Purge بر اساس هم‌پوشانی واقعی label window هر نمونه با بازه ارزیابی انجام می‌شود؛ صرف حذف تعداد ثابت ردیف‌ها کافی نیست. Embargo باید با افق برچسب، زمان نگهداری و وابستگی زمانی متناسب باشد و در هر Fold به‌صورت دقیق مستند شود.

تمام تنظیمات، انتخاب ویژگی، scaling، HMM، calibration و threshold در هر Fold فقط با Train/Validation همان Fold انجام شود. Test و OOS فقط یک‌بار برای ارزیابی نهایی استفاده شوند.

## ماتریس تحلیل
- W1 − W0: اثر HMM.
- W2 − W0: اثر ML.
- W3 − W1: اثر ML در حضور HMM.
- W3 − W2: اثر HMM در حضور ML.
- (W3 − W1) − (W2 − W0): تعامل تقریبی دو عامل، با تفسیر متناسب با طراحی آزمایش.

## توقف
اگر داده یا هزینه یا کد مشترک بین نسخه‌ها متفاوت باشد، آزمایش invalidated شود. هر تغییر پس از مشاهده OOS، یک experiment جدید است و OOS مشاهده‌شده دیگر untouched محسوب نمی‌شود.
