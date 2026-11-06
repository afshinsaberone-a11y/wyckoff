# W1 H1 Market-Series Preflight v1.2 — 2026-11-06

## وضعیت
**PRECHECK PASS / TRAINING GATE NOT APPROVED.** این خروجی برای بررسی مستقل داده و پروتکل ساخته شده است؛ هیچ HMM، scaler یا مدل دیگری Fit نشده، Label ساخته نشده و هیچ تغییری در W0 یا EA اعمال نشده است.

## منبع و کیفیت
- منبع: `XAUUSD_H1.csv`، SHA-256: `2843cf278818fb271f232ca8473570e0cdae7770968d2f45774048fb19e5039f`.
- 16,539 کندل؛ از 2024.01.02 01:00 تا 2026.10.16 23:00 با زمان خام Broker Server.
- timestamp صعودی و یکتا؛ OHLC نامعتبر=0؛ مقدار عددی مفقود/غیرمتناهی=0.
- Spread صفر: 1,150 ردیف (6.953%); real_volume در تمام ردیف‌ها صفر؛ این فیلدها Feature مدل نیستند.
- tick_volume فقط diagnostic است و به‌عنوان volume واقعی بازار تفسیر نمی‌شود.

## اصلاح معنای زمان و Featureها در v1.2
- 16,371 ردیف Feature پس از Warm-up 168 کندل مشاهده‌شده.
- تمام پنجره‌ها صریحاً برحسب **observed H1 bars** هستند، نه wall-clock hours: 14obs، 24obs، 100obs، 168obs.
- بازده هر مشاهده از Close کندل مشاهده‌شدهٔ قبلی محاسبه می‌شود؛ اگر بین دو مشاهده بازار بسته بوده، elapsed hours جدا ثبت می‌شود.
- زمان nominal close برابر open+1h فقط یک قرارداد اسمی است. چون OHLC CSV زمان اولین Tick بعد از بسته‌شدن را ندارد، `available_at_server`، `actual_tick_observed_at_server` و `decision_time_server` خالی‌اند؛ زمان واقعی مشاهده/تصمیم حدس زده نشده است.
- آزمون future-invariance روی تغییر داده‌های پس از cutoff انجام شد.

## ممیزی فاصله‌های زمانی
در کل منبع 721 فاصلهٔ غیر یک‌ساعته مشاهده شد:
- 555 فاصلهٔ 2h: recurring daily break candidate.
- 17 فاصلهٔ 4h: early-close/holiday candidate.
- 142 فاصلهٔ 49–54h: weekend-closure candidate.
- 4 فاصلهٔ 27–36h: year-end/special-closure candidate.
- 3 فاصلهٔ 74–75h: long-holiday-closure candidate.

پس از Warm-up، 714 فاصله در Feature rows باقی می‌ماند و تک‌تک در gap audit فهرست شده‌اند. این طبقه‌بندی فقط از الگوی timestamp استخراج شده و **تقویم رسمی سرور WMMarkets نیست**؛ همهٔ برچسب‌ها unverified هستند. هیچ کندل مصنوعی اضافه نشده است.

## فرض baseline پیشنهادی برای HMM
واحد انتقال، کندل معاملاتی مشاهده‌شده است: یک transition برای هر H1 bar موجود. بازار بسته بوده، کندل مصنوعی تولید نمی‌کنیم؛ elapsed hours و gap class صرفاً diagnostics باقی می‌مانند. حساسیت جداگانه با reset کردن posterior پس از weekend/long-holiday gaps پیشنهاد می‌شود. این فرض باید توسط AGENT_03 تأیید شود.

## Fold plan پیشنهادی (تأییدنشده)
- Train: 11,672 ردیف؛ 2024.01.11 تا قبل از 2026.01.01.
- Validation: 2,910 ردیف؛ 2026.01.01 تا قبل از 2026.07.01.
- Test: 1,789 ردیف؛ 2026.07.01 تا پایان دادهٔ موجود.
- Scaler و پارامترهای HMM فقط روی Train fit شوند؛ Validation فقط برای diagnostics/selection؛ Test یک بار پس از Freeze. در replay فقط filtered probabilities مجاز است.

## آزمون‌های محلی
`python -m pytest -q test_w1_h1_preflight_v12.py` → **5 passed**.
آزمون‌ها: future invariance، عدم جعل زمان واقعی availability، شمارش/طبقه‌بندی gapها، کران Featureها و fold counts.

## Artifact fingerprints
- Feature CSV: `W1_H1_market_features_precheck_v12.csv`
  SHA-256: `63724ffc5e2df934dcfdab19ceb78a30a597de93df785405fad5b9eb3b2f96d6`
- Gap audit CSV:
  SHA-256: `e8d803745a740ed4488a89e51c11a197518a9ae72f8042bff30cd344a64ef92a`
- ZIP package:
  SHA-256: `848d1b735f63c10cd3df45df5a92418b233965fad429f07939d0d7d8c61c1ff3`

Feature CSV به این گزارش ضمیمه/در مخزن عمومی قرار نگرفته؛ بسته در محیط گفتگو ارائه شده است تا داده مشتق‌شدهٔ بروکر بدون ضرورت در مخزن عمومی کپی نشود.

## درخواست از AGENT_03
یک Gate مستقل دربارهٔ این پنج مورد صادر شود:
1. semantics زمان nominal close در برابر actual observation؛
2. استفاده از observed-bar time و رفتار HMM در daily/weekend/holiday gaps؛
3. مناسب بودن Foldهای train/validation/test و مرزهای زمانی؛
4. point-in-time بودن Featureها و منع smoothed probabilities؛
5. exclusions مربوط به spread صفر و real_volume/tick_volume.

تا صدور PASS، HMM روی داده واقعی fit یا انتخاب نشود و هیچ posterior به W0 وصل نشود. W2 Candidate/Outcome Gate نیز جداگانه BLOCKED می‌ماند.