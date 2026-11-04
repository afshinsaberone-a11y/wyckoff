# آزمایش کنترل‌شدهٔ Strength Swing Lookback — H1STRUCT

## هدف

مقایسهٔ اثر تنها یک ورودی، یعنی `InpStrengthSwingLookback`، روی مرحلهٔ SOS/SOW و قیف ورود. نسخهٔ مبنا با مقدار 5 قبلاً اجرا شده است. این دو SET جدید مقادیر 10 و 20 را آزمایش می‌کنند.

## فایل‌ها

- نسخهٔ مبنا: `InpStrengthSwingLookback=5`؛ خروجی H1STRUCT فعلی.
- آزمایش A: `sets/Wyckoff_C2_H1STRUCT_SL10_2024_2026.set`؛ مقدار 10.
- آزمایش B: `sets/Wyckoff_C2_H1STRUCT_SL20_2024_2026.set`؛ مقدار 20.

در هر دو SET فقط دو فیلد با SET مبنا متفاوت است:
1. `InpStrengthSwingLookback`: مقدار 10 یا 20.
2. `InpCSVFileName`: نام مستقل برای جلوگیری از بازنویسی CSV هر آزمایش.

تمام پارامترهای ریسک، Range، Spring/UTAD، Test، SOS/SOW، LPS/LPSY و M5 بدون تغییر باقی می‌مانند.

## روش اجرا

1. Expert را `Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_AUDIT` انتخاب کنید.
2. نماد XAUUSD، تایم‌فریم M5، مدل Every tick based on real ticks، تاریخ 2024.01.02 تا 2026.11.04، موجودی 10,000 USD و اهرم 1:200 را ثابت نگه دارید.
3. ابتدا SET شماره 10 و سپس SET شماره 20 را جداگانه بارگذاری و اجرا کنید.
4. در هر اجرا HTML Report، Journal کامل و CSV خروجی را نگه دارید.
5. نسخهٔ EA را در CSV بررسی کنید؛ باید `1.08-C2-H1STRUCT-AUDIT-SB050-T030` باشد.

## چه چیزی مقایسه شود؟

- تعداد و زمان `SOS_CONFIRMED` و `SOW_CONFIRMED`.
- تعداد `INTERNAL_SWING_BREAK` در برابر `RANGE_EDGE_BREAK`.
- `remainingToRangeHighATR` / `remainingToRangeLowATR`.
- `barsAfterTest` و `elapsedHoursAfterTest`.
- تعداد LPS/LPSY و invalidation آن‌ها.
- تعداد M5 breakout، retest، recovery و سفارش بازشده.
- تغییرات تعداد setupهای رسیده به مرحلهٔ بعد؛ نه فقط سود/زیان نهایی.

## پیش‌بینی مجاز از دادهٔ فعلی

بازمحاسبهٔ OHLC برای 8 سیگنال SOS/SOW دارای دادهٔ M1 نشان داد:
- lookback=5: هر 8 شکست محلی موجود تأیید می‌شود.
- lookback=10: 6 از 8.
- lookback=20: 3 از 8.
- lookback=40: 1 از 8.

این فقط sensitivity check روی همان کندل‌های سیگنال موجود است؛ نتیجهٔ کامل بک‌تست برای مقادیر 10/20 نیست، چون با تغییر lookback ممکن است کندل Strength دیگری در زمان دیگری انتخاب شود یا setup منقضی شود.

## قاعدهٔ کنترل آزمایش

هیچ ورودی دیگری را هم‌زمان تغییر ندهید. نتایج را به عنوان سه نسخهٔ تشخیصی 5/10/20 مقایسه کنید. با یک یا چند معامله نمی‌توان دربارهٔ برتری سودآوری نتیجه گرفت. این آزمایش برای سنجش کیفیت ساختار H1 و اثر lookback است، نه تأیید استفادهٔ دمو یا Live.
