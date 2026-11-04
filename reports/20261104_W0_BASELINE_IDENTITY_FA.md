# گزارش تطبیق هویت Baseline W0 و نسخه‌های تشخیصی

تاریخ بررسی: 2026-11-04  
Task: BOOT-001  
وضعیت: **CONDITIONAL / تطبیق اولیه انجام شد؛ Freeze نهایی Baseline هنوز کامل نیست.**

## 1. نتیجه مدیریتی

نسخه‌ای که شواهد بک‌تست موجود آن را به‌عنوان C2 پایه معرفی می‌کنند، فایل زیر است:

- Expert گزارش‌شده: `Wyckoff_XAUUSD_W0_v1_08_C2_T030_SB050`
- CSV EA_Version: `1.08-C2-TIMING-SB050-T030`
- سورس متناظر موجود در مخزن: `src/Wyckoff_XAUUSD_W0_v1_08_C2_T030_SB050.mq5`
- Git blob SHA سورس: `7e6e7ddaf6dd8ef976e53f611018815a4874dd60`
- تعداد خطوط فایل: 1,706
- `#property version=1.082`

این تطبیق بر مبنای سورس و هویت ثبت‌شده در گزارش Tester/CSV است. **زنجیره رمزنگاری‌شده EX5 → سورس هنوز اثبات نشده است**؛ فایل EX5 همان اجرای تاریخی و شناسه Build متصل به آن در بسته شواهد موجود نیست. همچنین SET اصلی همان اجرای C2 در فهرست SETهای مخزن پیدا نشد. بنابراین این نسخه «Baseline candidate» است، نه Baseline نهایی Freezeشده.

## 2. تفکیک سه نسخه

| نقش | فایل سورس | property version | EA_VERSION داخلی | وضعیت شواهد |
|---|---|---:|---|---|
| C2 پایه / Baseline candidate | `...C2_T030_SB050.mq5` | 1.082 | `1.08-C2-TIMING-SB050-T030` | گزارش Tester و CSV با این شناسه منطبق‌اند |
| H1STRUCT Audit | `...C2_H1STRUCT_AUDIT.mq5` | 1.083 | `1.08-C2-H1STRUCT-AUDIT-SB050-T030` | گزارش Tester، CSV و رویدادهای Audit منطبق‌اند |
| H1STRUCT MultiAudit | `...C2_H1STRUCT_MULTI_AUDIT.mq5` | 1.084 | `1.08-C2-H1STRUCT-ML-AUDIT-SB050-T030` | سورس و بررسی ایستا موجود؛ Compile/Tester تأیید نشده |

### 2.1 C2 پایه

منبع گزارش: `reports/20261104_C2_T030_SB050_BACKTEST_REVIEW_FA.md`.

- Expert در Tester: `Wyckoff_XAUUSD_W0_v1_08_C2_T030_SB050`
- CSV EA_Version: `1.08-C2-TIMING-SB050-T030`
- سورس: `src/Wyckoff_XAUUSD_W0_v1_08_C2_T030_SB050.mq5`
- Git blob SHA: `7e6e7ddaf6dd8ef976e53f611018815a4874dd60`
- `#define EA_VERSION` در خط 205 سورس با شناسه CSV برابر است.
- گزارش: XAUUSD / WMMarkets-Demo، M5، بازه 2024-01-02 تا 2026-11-04، Deposit=10,000 USD، Leverage=1:200، 201,630 bars و 177,991,586 ticks، کیفیت اعلامی 89% real ticks.
- Net Profit: `-62.44 USD`؛ معاملات: 1؛ نتیجه: 0 برد / 1 باخت.
- تنظیمات کلیدی گزارش‌شده: RiskPercent=0.50، RR=2.0، Stop ATR Buffer=0.50، M5 Retest Tolerance=0.30 ATR.

این خروجی، C2 پایه است؛ نه H1STRUCT Audit. نام CSV شامل واژه H1StructureAudit بوده، اما خود CSV فاقد فیلدهای `H1_RANGE_CONTEXT_AUDIT` و `structureClass` مورد انتظار نسخه H1STRUCT است.

### 2.2 H1STRUCT Audit

منبع گزارش: `reports/20261104_H1STRUCT_AUDIT_RUN_ANALYSIS_FA.md`.

- Expert در HTML: `Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_AUDIT`
- CSV EA_Version: `1.08-C2-H1STRUCT-AUDIT-SB050-T030`
- سورس: `src/Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_AUDIT.mq5`
- Git blob SHA: `782236125264e6915090650e60737fee0c31beb6`
- تعداد خطوط: 1,771؛ `#property version=1.083`
- گزارش شامل 67 رویداد H1 Range Context Audit و داده‌های structureClass است.
- نتیجه ثبت‌شده: Net Profit=-62.44 USD؛ یک معامله.

این نسخه یک اجرای تشخیصی ساختار H1 است و با اجرای C2 پایه یکی نیست؛ یکسان بودن P/L به معنای یکسان بودن نسخه یا اجرای تست نیست.

### 2.3 H1STRUCT MultiAudit

- سورس: `src/Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT.mq5`
- Git blob SHA: `b7849fdad9df0cd3e4f0dbc694cd3db92c3040b0`
- تعداد خطوط: 1,884؛ `#property version=1.084`
- شناسه داخلی فعلی: `1.08-C2-H1STRUCT-ML-AUDIT-SB050-T030`
- رویدادهای تشخیصی: `SOS_STRENGTH_BAR_AUDIT` و `SOW_STRENGTH_BAR_AUDIT`.
- گزارش بررسی ایستا می‌گوید predicateهای معاملاتی SOS/SOW، Spring/UTAD، Test، LPS/LPSY، M5 trigger، SL/TP، ریسک، order-send و expiry تغییر نکرده‌اند.
- بررسی delimiter و تطابق SET انجام شده؛ **MetaEditor Compile و Strategy Tester run انجام/تأیید نشده‌اند.**

نکته نام‌گذاری: عبارت `ML-AUDIT` در EA_VERSION این فایل به خانواده MultiLookback Audit مربوط است؛ نباید آن را به معنی فعال بودن Machine Learning تعبیر کرد. بهتر است در نسخه بعدی شناسه‌های MultiAudit و ML Research صریحاً از هم متمایز باشند، اما تغییر شناسه باید با نسخه جدید و ثبت‌شده انجام شود.

## 3. کنترل SETهای MultiAudit

سه SET موجود بررسی و 67 کلید هرکدام parse شد:

| SET | Git blob SHA | InpStrengthSwingLookback |
|---|---|---:|
| `Wyckoff_C2_H1StructureMultiAudit_2024_2026.set` | `4879efccac2e3051096327e47a3fb4e32d7719b8` | 5 |
| `Wyckoff_C2_H1STRUCT_SL10_2024_2026.set` | `620f0887dc9e927ca16721b02101b113d4904a68` | 10 |
| `Wyckoff_C2_H1STRUCT_SL20_2024_2026.set` | `f418566630435d2d7c5efdeba709ffceb05ee7af` | 20 |

مقایسه کلیدبه‌کلید نشان داد فقط دو مقدار متفاوت‌اند:
1. `InpStrengthSwingLookback`: به‌ترتیب 5، 10 و 20.
2. `InpCSVFileName`: نام فایل خروجی جداگانه برای جلوگیری از overwrite.

پس در سطح فایل SET، آزمایش Lookback کنترل‌شده است. هنوز باید پس از Compile موفق، در Strategy Tester نیز هویت Expert، نسخه و تمام ورودی‌های بارگذاری‌شده ثبت شوند.

SET چهارم `Wyckoff_C2_H1StructureAudit_2024_2026.set` نیز در مخزن وجود دارد؛ 67 کلید دارد و مربوط به نسخه H1STRUCT Audit است. این فایل جایگزین SET مربوط به C2 پایه نیست.

## 3.4 دو اجرای C2 با بازه‌های متفاوت؛ شمارش‌ها را ادغام نکن

در مخزن یک اجرای C2 کامل‌تر از Journal مورخ 2026-11-03 قابل بازیابی است:
- Expert: `Wyckoff_XAUUSD_W0_v1_08_C2_T030_SB050.ex5`
- بازه: 2024-01-02 تا 2026-10-17 00:00
- ورودی `InpCSVFileName=Wyckoff_W0_events_v1_08.csv`
- خروجی متناظر در مخزن: `events/Wyckoff_W0_events_v1_08_C2_SB050_T030_TIMING_B12_R12_RC12.csv`
- همان EA_Version پایه C2 و final balance برابر 9,937.56 USD.

Event CSV این اجرای مشخص 346 ردیف داده (شامل EA_INIT) و 65 RANGE_FOUND، 15 TEST_CONFIRMED، 6 SOS و 2 SOW دارد. این شمارش با گزارش C2 مورخ 2026-11-04 که بازه را تا 2026-11-04 ذکر می‌کند یکی نیست.

گزارش C2 مورخ 2026-11-04 به CSV دیگری با نام `Wyckoff_C2_H1StructureAudit_2024_2026_C2_SB050_T030_TIMING_B12_R12_RC12.csv` ارجاع می‌دهد. این فایل با همان نام در مخزن فعلی یافت نشد. محتمل است دو بازه/اجرای متفاوت باشند؛ بدون CSV و Journal اجرای 2026-11-04 نباید شمارش‌های دو run را به‌عنوان اختلاف داخل یک اجرا یا یک Baseline واحد تفسیر کرد.

گزارش جزئی: [ممیزی آمادگی داده Financial ML](20261104_FINANCIAL_ML_DATA_READINESS_AUDIT_FA.md).

## 4. محدودیت‌های باقی‌مانده برای Freeze نهایی

| مورد | وضعیت |
|---|---|
| تطبیق نام Expert و EA_VERSION برای C2 پایه | PASS در گزارش‌های موجود |
| تطبیق نام Expert و EA_VERSION برای H1STRUCT Audit | PASS در گزارش‌های موجود |
| سورس و blob SHA هر سه نسخه | موجود |
| MultiAudit source static review | PASS طبق گزارش ایستای مخزن |
| تطبیق 67 کلید SETهای 5/10/20 | PASS؛ دو کلید متفاوت طبق انتظار |
| EX5 binary hash و زنجیره Compile-to-source برای اجرای C2 تاریخی | موجود/تأییدنشده |
| SET دقیق اجرای تاریخی C2 پایه | در پوشه sets پیدا نشد |
| Compile واقعی MultiAudit v1.084 | انجام/تأیید نشده |
| Tester run واقعی MultiAudit v1.084 | انجام/تأیید نشده |

## 5. تصمیم BOOT-001

**نتیجه: CONDITIONAL.**

1. C2-T030-SB050 به‌عنوان Baseline candidate شناسایی می‌شود.
2. H1STRUCT Audit فقط نسخه تشخیصی ساختار است.
3. MultiAudit v1.084 فقط سورس تشخیصی با بررسی ایستا و SETهای کنترل‌شده است؛ هنوز نسخه قابل استناد Tester نیست.
4. Baseline نهایی فقط پس از ثبت SET دقیق، هویت باینری/Build یا بازتولید Compile از همان سورس و بسته کامل گزارش/CSV/Journal Freeze خواهد شد.
5. تا آن زمان W1/W2 آموزش رسمی را آغاز نمی‌کنند.

## 6. گام بعدی

BOOT-002: ابتدا MultiAudit v1.084 در MetaEditor کامپایل شود. اگر کامپایل موفق بود، اجرای SET=5، سپس 10 و 20 با محدوده و شرایط کاملاً ثابت انجام شود. فایل‌های HTML، Journal و CSV هر اجرا باید با Expert name و EA_VERSION همان نسخه تطبیق داده شوند.

این گزارش فقط از سورس‌ها و مستندات ثبت‌شده در GitHub استخراج شده است؛ هیچ Compile، بک‌تست یا اجرای MT5 جدیدی در این مرحله انجام نشده است.
