# کارت اجرای BOOT-002 — MultiAudit v1.084

نسخه کارت: 1.0-draft  
هدف: اجرای قابل تکرار MultiAudit v1.084 با سه SET برای Lookbackهای 5/10/20.  
وضعیت فعلی: **آماده اجرای کاربر در MT5؛ هنوز هیچ اجرای جدیدی انجام نشده است.**

## 1. هویت دقیق Expert

فقط همین فایل را انتخاب کنید:

`src/Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT.mq5`

پس از Compile، نام Expert مورد انتظار در Tester:

`Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT`

شناسه داخلی مورد انتظار در CSV:

`1.08-C2-H1STRUCT-ML-AUDIT-SB050-T030`

این عبارت `ML-AUDIT` نام تاریخی شناسه MultiLookback Audit است و به معنی اجرای مدل Machine Learning نیست.

از اجرای فایل‌های زیر برای این Task استفاده نکنید:
- C2 پایه: `...C2_T030_SB050`
- H1STRUCT Audit v1.083: `...C2_H1STRUCT_AUDIT`

## 2. فایل‌های SET

| ترتیب | فایل | مقدار مورد انتظار |
|---:|---|---:|
| 1 | `sets/Wyckoff_C2_H1StructureMultiAudit_2024_2026.set` | 5 |
| 2 | `sets/Wyckoff_C2_H1STRUCT_SL10_2024_2026.set` | 10 |
| 3 | `sets/Wyckoff_C2_H1STRUCT_SL20_2024_2026.set` | 20 |

در هر سه فایل 67 ورودی وجود دارد. مقایسه کلیدبه‌کلید فقط دو تفاوت را نشان داده:
- `InpStrengthSwingLookback` = 5، 10 یا 20.
- `InpCSVFileName` = نام مجزای خروجی.

در Strategy Tester بعد از بارگذاری هر SET، مقدار Lookback و سایر ورودی‌های مشترک را در تب Inputs بررسی کنید. اگر ورودی دیگری غیر از این دو تفاوت دارد، run را شروع نکنید.

## 3. پیش‌نیاز Compile

1. فایل MQ5 را از مخزن دریافت کنید و با MetaEditor باز کنید.
2. پیش از Compile، مطمئن شوید فایل همان MultiAudit v1.084 است.
3. Compile کنید.
4. پنجره Errors باید صفر خطای Compile داشته باشد. Warningها را حذف یا توجیه کنید؛ متن Warningها را نگه دارید.
5. فایل EX5 تولیدشده، زمان، MetaEditor build و SHA-256 آن را ثبت کنید.
6. اگر Compile شکست خورد، هر سه تست متوقف می‌شوند؛ تغییر سورس برای رفع خطا باید با Commit/نسخه جدید ثبت شود و نتیجه این دور به v1.084 نسبت داده نشود.

PowerShell برای محاسبه SHA-256 فایل EX5:

```powershell
Get-FileHash "PATH_TO_EX5" -Algorithm SHA256
```

## 4. تنظیمات مشترک Strategy Tester

برای بازتولید اجرای C2 آرشیوشده، نقطه شروع شناخته‌شده این است:
- Symbol: XAUUSD
- Period: M5
- Broker/server: WMMarkets-Demo
- Model: Every tick based on real ticks
- Deposit: 10,000 USD
- Leverage: 1:200
- Start: 2024.01.02 00:00
- End: 2026.10.17 00:00

این بازه از Journal اجرای C2 مورخ 2026-11-03 گرفته شده است. **قبل از شروع هر سه Run، تاریخچه مشترک را در ترمینال بررسی کنید.** اگر داده کامل‌تری وجود دارد و تصمیم به استفاده از آن گرفته می‌شود، تاریخ جدید باید پیش از اولین Run ثبت و برای هر سه Run عیناً ثابت شود؛ وسط آزمایش تاریخ پایان را تغییر ندهید.

قواعد مشترک:
- یکسان بودن Account/Deposit/Leverage، Symbol، Period، model، تاریخ، Expert binary و همه ورودی‌های غیر از Lookback و نام CSV.
- Optimization خاموش.
- همان نسخه EX5 برای هر سه Run.
- در صورت استفاده از Forward testing یا سایر گزینه‌ها، غیرفعال و یکسان نگه داشته شوند.
- هیچ پارامتر دیگری را برای جبران تعداد معاملات تغییر ندهید.

## 5. ترتیب اجرا

برای هر Run:
1. Expert MultiAudit v1.084 را انتخاب کنید.
2. SET مربوط را Load کنید.
3. مقدار `InpStrengthSwingLookback` را روی 5، 10 یا 20 بررسی کنید.
4. از تب Inputs و تنظیمات Tester تصویر/گزارش نگه دارید.
5. Run را اجرا کنید.
6. پس از پایان، HTML Report، Journal کامل و CSV تولیدشده را ذخیره کنید.
7. CSV باید EA_Version دقیق `1.08-C2-H1STRUCT-ML-AUDIT-SB050-T030` داشته باشد.
8. رخدادهای `SOS_STRENGTH_BAR_AUDIT` و `SOW_STRENGTH_BAR_AUDIT` باید در CSV ظاهر شوند، اگر کندل قوی در بازه وجود داشته باشد.
9. نام فایل، timestamp، حجم و SHA-256 هر artifact را ثبت کنید.
10. قبل از Run بعدی، خروجی قبلی را به پوشه جداگانه منتقل کنید؛ از overwrite شدن CSV جلوگیری کنید.

CSV در `MQL5/Files` ذخیره می‌شود. سورس تابع `EffectiveCSVFileName()` به نام `InpCSVFileName` یک suffix شامل تنظیمات Breakout/Retest/Recovery اضافه می‌کند؛ نام واقعی فایل را از خود ترمینال بردارید و حدس نزنید.

## 6. کنترل پذیرش هر Run

Run فقط در صورت تحقق تمام موارد زیر `COMPLETE` است:
- Compile log و EX5 hash ثبت شده.
- Expert name در Tester همان MultiAudit است.
- EA_Version در CSV برابر شناسه مورد انتظار است.
- مقدار Lookback در تب Inputs و Journal درست است.
- تاریخ، مدل تیک، Deposit و Leverage با دو Run دیگر یکسان است.
- HTML، Journal و CSV موجود و غیرخالی‌اند.
- هشدارهای history/tick ثبت و محدودیت‌های پوشش گزارش شده‌اند.
- CSV مربوط به همان Run است و overwrite نشده است.

اگر Expert یا EA_Version اشتباه بود، Run `INVALIDATED` است؛ حتی اگر Tester عبارت Test passed چاپ کند.

## 7. چه چیزهایی را مقایسه کنیم؟

در این آزمایش هدف اصلی تغییرات ساختاری است، نه انتخاب سودده‌ترین SET:
- تعداد و زمان SOS/SOWهای confirmed.
- تعداد رویدادهای Diagnostic برای 5/10/20/40.
- نسبت عبور از هر سطح محلی در کندل‌های Strength.
- تعداد و پهنای Pivot bands و تعداد Pivotهای تأییدشده.
- فاصله تا Range edge برحسب ATR.
- اتصال هر Strength به Test، LPS/LPSY، M5 breakout/retest/recovery.
- تعداد معاملات و Net P/L صرفاً به‌عنوان پیامد ثانویه و با توجه به تعداد نمونه.

رخداد `SOS_STRENGTH_BAR_AUDIT` یا `SOW_STRENGTH_BAR_AUDIT` می‌تواند پیش از رد مکانی SOS/SOW ثبت شود؛ آن را با `SOS_CONFIRMED` یا `SOW_CONFIRMED` یکی نگیرید. شمارش رویدادهای Diagnostic برابر تعداد Candidateهای مستقل هم نیست.

## 8. محدودیت تفسیر

- این تست برای حساسیت ساختاری Lookback است؛ به‌تنهایی بهینه‌سازی یا اثبات Edge نیست.
- پوشش Real Tick در Journal قدیمی کامل و یکنواخت نبوده است؛ هشدارهای هر Run جدا ثبت شوند.
- یکسان بودن نام نسخه و یکسان بودن SET به‌تنهایی صحت EX5 را اثبات نمی‌کند؛ SHA-256 باینری و log Compile نگهداری شود.
- Compile و Tester Run باید واقعی و مستند باشند؛ گزارش ایستا جایگزین آن‌ها نیست.

قالب JSON برای ثبت ماشینی هر Run: [BOOT_002_RUN_MANIFEST_TEMPLATE.json](../experiments/BOOT_002_RUN_MANIFEST_TEMPLATE.json). برای سه Lookback یک کپی مستقل بسازید و هیچ مقدار ناشناخته را حدس نزنید.

## 9. تحویل نهایی BOOT-002

پوشه پیشنهادی تحویل:

```text
runs/BOOT-002/
  compile/
    metaeditor_build.txt
    compile_log.txt
    expert.ex5.sha256
  lookback_05/
    tester.html
    journal.log
    events.csv
    run_manifest.json
  lookback_10/
    tester.html
    journal.log
    events.csv
    run_manifest.json
  lookback_20/
    tester.html
    journal.log
    events.csv
    run_manifest.json
  comparison/
    BOOT_002_LOOKBACK_COMPARISON_FA.md
```

پس از هر سه Run، AGENT_02 manifestها را تطبیق می‌دهد؛ AGENT_01 رویدادهای ساختاری را استخراج می‌کند؛ AGENT_03 هویت نسخه، تنظیمات، کیفیت تاریخچه و مقایسه را ممیزی می‌کند. BOOT-002 تنها پس از عبور این کنترل‌ها COMPLETE می‌شود.
