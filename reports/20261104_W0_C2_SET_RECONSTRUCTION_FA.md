# گزارش بازسازی SET مرجع C2 از Tester Journal

تاریخ: 2026-11-04  
Task: تکمیل BOOT-001 / Baseline Identity  
وضعیت: **PASS برای تطبیق تنظیمات؛ Baseline کلی هنوز CONDITIONAL به علت نبود EX5 تاریخی و hash باینری.**

## 1. منبع بازسازی

Journal آرشیوشده:
- فایل: `events/20261103.log`
- Git blob SHA: `3d15f5e801691d63b6041ad6aba6aac68bfe7ffb`
- Expert اجراشده: `Wyckoff_XAUUSD_W0_v1_08_C2_T030_SB050.ex5`
- بازه: 2024-01-02 00:00 تا 2026-10-17 00:00
- نماد/تایم‌فریم: XAUUSD / M5
- سرور: WMMarkets-Demo
- Tester build: 6230
- Deposit: 10,000 USD
- Leverage: 1:200
- مدل: generating based on real ticks
- نسخه ثبت‌شده در Event CSV: `1.08-C2-TIMING-SB050-T030`

سورس:
- `src/Wyckoff_XAUUSD_W0_v1_08_C2_T030_SB050.mq5`
- Git blob SHA: `7e6e7ddaf6dd8ef976e53f611018815a4874dd60`
- `#property version=1.082`
- `EA_VERSION=1.08-C2-TIMING-SB050-T030`

## 2. فایل بازسازی‌شده

فایل جدید:
`sets/Wyckoff_C2_T030_SB050_RECONSTRUCTED_FROM_20261103_JOURNAL.set`

Git blob SHA:
`9b5db0bec781de2fbbcb732822a7766d24f5384d`

این فایل از خطوط ورودی Tester در Journal استخراج شده است. **فایل SET اصلی ذخیره‌شده در زمان اجرای تاریخی نیست**؛ نسخه‌ای بازسازی‌شده از همان 67 مقدار ثبت‌شده در Journal است. نام‌گذاری عمداً این محدودیت را آشکار می‌کند.

## 3. نتیجه تطبیق

| مقایسه | تعداد |
|---|---:|
| ورودی‌های استخراج‌شده از Journal | 67 |
| ورودی‌های سورس C2 v1.082 | 67 |
| کلیدهای SET بازسازی‌شده | 67 |
| کلید مفقود در SET | 0 |
| کلید اضافه در SET | 0 |
| مقدار متفاوت Journal در برابر SET | 0 |
| ورودی سورس بدون معادل در SET | 0 |

بنابراین:
- کلیدهای SET با ورودی‌های سورس C2 برابرند.
- همه 67 مقدار SET با مقادیر ثبت‌شده در Journal دقیقاً برابرند.
- این SET برای بازتولید تنظیمات اجرای آرشیوشده قابل استفاده است؛ اما به‌تنهایی باینری EX5 تاریخی را بازسازی یا اثبات نمی‌کند.

## 4. پارامترهای مهم ثبت‌شده

| پارامتر | مقدار |
|---|---:|
| RiskPercent | 0.50 |
| RewardRisk | 2.00 |
| StopATRBuffer | 0.50 |
| RangeLookbackBars | 80 |
| RangeWidth ATR | 2.5 تا 10.0 |
| StrengthSwingLookback | 5 |
| EntryRetestToleranceATR | 0.30 |
| Breakout/Retest/Recovery Expiry | 12 / 12 / 12 |
| H4 Context Filter | false |
| MaxSpreadPoints | 80 |
| LogRejectedSetups | true |
| ExportCSV | true |

مقادیر کامل و 67 کلید در فایل SET قرار دارند؛ جدول بالا فقط تنظیمات شاخص را نمایش می‌دهد.

## 5. نتیجه اجرای تاریخی مرتبط

Journal پایان همان اجرا را با `final balance 9937.56 USD` نشان می‌دهد. موجودی اولیه 10,000 USD بوده؛ خالص اختلاف -62.44 USD است. Event CSV مرتبط:
- `events/Wyckoff_W0_events_v1_08_C2_SB050_T030_TIMING_B12_R12_RC12.csv`
- Git blob SHA: `49eeb12ec611bc0ac5df04a8d7c0aa4f3454b01a`
- 346 ردیف داده شامل EA_INIT.
- 65 RANGE_FOUND، 15 TEST_CONFIRMED، 6 SOS_CONFIRMED، 2 SOW_CONFIRMED، 3 M5_BREAKOUT_CONFIRMED و 1 ORDER_OPENED/TRADE_CLOSED.

این خلاصه مختص اجرای 2026-11-03 تا 2026-10-17 است و نباید با اجرای جداگانه‌ای که گزارش 2026-11-04 تا 2026-11-04 توصیف می‌کند ادغام شود.

## 6. چه چیزی هنوز برای Freeze نهایی کم است؟

- فایل EX5 تاریخی در مخزن موجود نیست.
- SHA-256 باینری EX5 تاریخی از Journal قابل استخراج نیست.
- فایل اصلی SET هنگام اجرای تاریخی موجود نیست؛ فقط مقدارها از Journal بازسازی شده‌اند.
- برای بازتولید معتبر، باید همین سورس v1.082 در MetaEditor با Build مشخص Compile و با SET بازسازی‌شده روی بازه/شرایط ثبت‌شده تست شود؛ سپس HTML، Journal، CSV و hash EX5 جدید نگهداری شوند.

## 7. تصمیم BOOT-001

- هویت سورس C2 v1.082 و EA_VERSION: **PASS بر اساس تطبیق سورس/Journal/CSV**.
- تطبیق 67 ورودی بازسازی‌شده با Journal و سورس: **PASS**.
- دسترسی به فایل اصلی SET تاریخی: **NOT AVAILABLE**؛ SET بازسازی‌شده موجود است.
- زنجیره EX5 تاریخی به سورس و hash باینری: **NOT AVAILABLE**.
- Freeze نهایی Baseline: **CONDITIONAL** تا Compile/Tester بازتولیدی با artifactهای قابل‌ردیابی انجام شود.

این گزارش هیچ Compile، Tester یا معامله جدیدی را ادعا نمی‌کند.
