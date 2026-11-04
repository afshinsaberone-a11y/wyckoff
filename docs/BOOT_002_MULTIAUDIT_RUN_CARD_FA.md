# کارت اجرای BOOT-002 — کنترل H1STRUCT در برابر MultiAudit و حساسیت Lookback

نسخه کارت: 2.0-draft  
هدف: چهار اجرای کنترل‌شده برای سنجش عدم‌تداخل افزوده‌های تشخیصی v1.084 و اثر تغییر فعال Lookback بر SOS/SOW.  
وضعیت: **آماده اجرای کاربر در MT5؛ هیچ‌یک از چهار اجرای جدید هنوز انجام نشده است.**

## 1. یافته‌ای که طراحی آزمایش را تغییر می‌دهد

پارامتر InpStrengthSwingLookback صرفاً تشخیصی نیست. در تابع ProcessWaitStrength تعداد کندل‌های قبلی H1 برای محاسبه priorHigh و priorLow را تعیین می‌کند؛ سپس SOS/SOW فقط در صورت بسته‌شدن کندل بیرون این سطح محلی تأیید می‌شود.

بنابراین:
- Lookback=5 مسیر مرجع و کنترل است.
- Lookback=10 و 20، شرط فعال شکست Swing را تغییر می‌دهند و آزمایش حساسیت قانون معاملاتی SOS/SOW هستند؛ نه صرفاً گزارش تشخیصی.
- در هر سه اجرای v1.084، تابع Audit سطوح 5/10/20/40 را گزارش می‌کند؛ اما مقدار InpStrengthSwingLookback همچنان بر مسیر واقعی state machine اثر می‌گذارد.

## 2. طراحی چهار Run

| Run | Expert | SET | Lookback فعال | نقش آزمایش |
|---|---|---|---:|---|
| A | H1STRUCT Audit v1.083 | Wyckoff_C2_H1StructureAudit_2024_2026.set | 5 | کنترل مرجع |
| B | MultiAudit v1.084 | Wyckoff_C2_H1StructureMultiAudit_2024_2026.set | 5 | کنترل عدم‌تداخل افزوده‌های تشخیصی |
| C | MultiAudit v1.084 | Wyckoff_C2_H1STRUCT_SL10_2024_2026.set | 10 | حساسیت فعال قانون SOS/SOW |
| D | MultiAudit v1.084 | Wyckoff_C2_H1STRUCT_SL20_2024_2026.set | 20 | حساسیت فعال قانون SOS/SOW |

Run A و B جفت کنترل‌اند. SETهایشان از نظر 67 ورودی فقط در InpCSVFileName تفاوت دارند. سورس v1.084 نیز خطوط اجرایی v1.083 را در همان ترتیب حفظ کرده و افزوده‌های Audit تشخیصی دارد. پس با داده و شرایط یکسان، تصمیم‌های معاملاتی A و B باید تطبیق کنند؛ تفاوت مورد انتظار، رویدادهای Diagnostic و شناسه نسخه است.

Run C و D آزمایش‌های جدا برای حساسیت Lookback هستند. تغییر Lookback می‌تواند تعداد/زمان SOS/SOW و کل مسیرهای بعدی را تغییر دهد.

## 3. هویت دقیق دو Expert

### Expert A — کنترل v1.083
سورس:
src/Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_AUDIT.mq5

- Tester Expert: Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_AUDIT
- property version: 1.083
- CSV EA_VERSION: 1.08-C2-H1STRUCT-AUDIT-SB050-T030
- SET: sets/Wyckoff_C2_H1StructureAudit_2024_2026.set

### Expert B/C/D — کنترل و حساسیت v1.084
سورس:
src/Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT.mq5

- Tester Expert: Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT
- property version: 1.084
- CSV EA_VERSION: 1.08-C2-H1STRUCT-ML-AUDIT-SB050-T030

عبارت ML-AUDIT در این شناسه نام تاریخی MultiLookback Audit است و به معنی اجرای Machine Learning نیست.

از C2 پایه (...C2_T030_SB050) برای این چهار Run استفاده نکنید؛ این آزمایش مشخصاً H1STRUCT v1.083 را با MultiAudit v1.084 مقایسه می‌کند.

## 4. Compile و هویت Binary

1. هر دو سورس v1.083 و v1.084 را در یک نسخه MetaEditor باز کنید.
2. هر دو را با همان MetaEditor build کامپایل کنید.
3. خطاهای Compile باید صفر باشد؛ Warningها را ذخیره و توضیح دهید.
4. هر دو EX5 را جداگانه نگه دارید؛ SHA-256، زمان ساخت، MetaEditor build و مسیر فایل را ثبت کنید.
5. برای Run A از EX5 v1.083 و برای B/C/D از همان EX5 v1.084 استفاده کنید.
6. هر تغییر سورس برای رفع خطا باید با Commit/نسخه جدید ثبت شود.

محاسبه SHA-256 در PowerShell:
    Get-FileHash "PATH_TO_EX5" -Algorithm SHA256

## 5. بازه زمانی مشترک و شرایط Tester

گزارش تاریخی H1STRUCT Audit اجرای XAUUSD,M5 از 2024.01.02 تا 2026.11.04 را توصیف می‌کند. اجرای C2 آرشیوشده در Journal دیگر تا 2026.10.17 است؛ این دو بازه را مخلوط نکنید.

**پیش از Run A، یک بازه مشترک را براساس تاریخچه واقعاً موجود در ترمینال انتخاب و Freeze کنید.** پیشنهاد اولیه برای بازتولید H1STRUCT:
- Start: 2024.01.02 00:00
- End: 2026.11.04 00:00

این بازه را فقط وقتی انتخاب کنید که داده و مدل تیک لازم برای هر چهار Run موجود باشد. اگر تاریخچه مشترک کوتاه‌تر است، همان بازه کوتاه‌تر را پیش از Run A انتخاب و هر چهار Run را دقیقاً با همان تاریخ اجرا کنید. بین اجراها تاریخ پایان را تغییر ندهید.

شرایط مشترک:
- Broker/server: WMMarkets-Demo
- Symbol: XAUUSD
- Period: M5
- Model: Every tick based on real ticks
- Deposit: 10,000 USD
- Leverage: 1:200
- Optimization و Forward testing: خاموش
- سرمایه، ارز، اهرم، اسپرد، کمیسیون، Swap، Deviation، مدل تیک و همه ورودی‌ها به‌جز شناسه CSV و Lookback فعال ثابت باشند.
- اگر پوشش Tick یا History بین اجراها متفاوت است، مقایسه معتبر نیست.

## 6. ترتیب اجرا

### Run A — H1STRUCT v1.083 / Lookback=5
1. Expert v1.083 و SET کنترل H1STRUCT را بارگذاری کنید.
2. Lookback=5 و تمام ورودی‌ها را بررسی کنید.
3. تاریخ و شرایط را Freeze و ثبت کنید.
4. Compile identity، Expert name، HTML، Journal و CSV را نگه دارید.

### Run B — MultiAudit v1.084 / Lookback=5
1. Expert v1.084 و SET اصلی MultiAudit را بارگذاری کنید.
2. Lookback=5 را تأیید کنید.
3. از همان EX5 v1.084 و همان شرایط Run A استفاده کنید.
4. HTML، Journal و CSV مستقل ذخیره کنید.

### Run C — MultiAudit v1.084 / Lookback=10
همان Expert و EX5 در Run B؛ فقط SET SL10 را بارگذاری کنید. Lookback=10 را در Inputs و Journal تأیید کنید.

### Run D — MultiAudit v1.084 / Lookback=20
همان Expert و EX5 در Run B؛ فقط SET SL20 را بارگذاری کنید. Lookback=20 را در Inputs و Journal تأیید کنید.

پس از هر Run، خروجی‌ها را به پوشه مختص همان Run انتقال دهید تا CSV قبلی overwrite نشود. تابع EffectiveCSVFileName به InpCSVFileName یک suffix شامل Breakout/Retest/Recovery expiry اضافه می‌کند؛ نام واقعی فایل را از Journal بردارید و حدس نزنید.

## 7. کنترل پذیرش هر Run

Run فقط وقتی COMPLETE است که:
- Compile log، MetaEditor build و EX5 SHA-256 ثبت شده باشند.
- Expert name و EA_VERSION با Run مورد انتظار تطبیق کنند.
- SET درست بارگذاری شده و مقدار Lookback در Inputs/Journal تأیید شده باشد.
- 67 ورودی با SET متناظر منطبق باشند.
- بازه، Symbol، timeframe، model، Deposit و Leverage در هر چهار Run یکسان باشد.
- HTML، Journal و CSV موجود و غیرخالی باشند.
- هشدارهای Tick/History و محدودیت پوشش ثبت شوند.
- فایل‌های خروجی مربوط به همان Run باشند و overwrite نشده باشند.

اگر Expert یا EA_VERSION اشتباه بود، Run INVALIDATED است؛ حتی اگر Tester پیام Test passed چاپ کند.

## 8. تحلیل و مقایسه

### کنترل عدم‌تداخل A در برابر B
مقایسه کنید:
- تعداد و زمان RANGE_FOUND، Spring/UTAD، Test، SOS/SOW و LPS/LPSY.
- قیمت/زمان SOS_CONFIRMED و SOW_CONFIRMED.
- M5 breakout/retest/recovery، order/deal و معاملات.
- SL/TP/volume و علت رد/انقضا.
- رویدادهای تشخیصی جدید v1.084 به‌صورت جدا.

با Lookback=5 و ورودی‌های همسان، تصمیم‌های معاملاتی A و B باید یکسان باشند. اگر تفاوتی دیده شد، ابتدا identity، build، inputs و data را بررسی کنید.

### حساسیت قانون SOS/SOW در C و D
برای Lookback=10 و 20 این موارد را با B مقایسه کنید:
- تعداد Testهایی که به SOS/SOW می‌رسند.
- تعداد SOS/SOW و طبقه‌بندی Internal Swing در برابر Range Edge.
- فاصله زمانی Test تا Strength.
- تعداد LPS/LPSY، M5 breakout/retest/recovery و معاملات.
- setupهای حذف‌شده یا ایجادشده بر اثر تغییر Lookback.
- Net P/L، PF و DD فقط به‌عنوان پیامد ثانویه و همراه با تعداد نمونه و کیفیت داده.

### تفسیر رویداد Audit
SOS_STRENGTH_BAR_AUDIT و SOW_STRENGTH_BAR_AUDIT روی کندل قوی ثبت می‌شوند و ممکن است قبل از رد مکانی SOS/SOW باشند:
- تعداد Diagnostic Audit را با SOS/SOW تأییدشده یکی نگیرید.
- تعداد این eventها را تعداد Candidateهای مستقل ننامید.
- چند تلاش از یک Range می‌توانند رخ دهند؛ برای ML به candidate_id مستقل نیاز است.

## 9. Manifest و خروجی‌ها

قالب JSON:
experiments/BOOT_002_RUN_MANIFEST_TEMPLATE.json

برای چهار Run یک کپی مستقل بسازید و variant را چنین ثبت کنید:
- H1STRUCT_1083_CONTROL_LB5
- MULTIAUDIT_1084_CONTROL_LB5
- MULTIAUDIT_1084_SENSITIVITY_LB10
- MULTIAUDIT_1084_SENSITIVITY_LB20

ساختار پیشنهادی:
    runs/BOOT-002/
      compile/
        metaeditor_build.txt
        v1083_compile_log.txt
        v1083.ex5.sha256
        v1084_compile_log.txt
        v1084.ex5.sha256
      run_A_h1struct_lb05/
        tester.html
        journal.log
        events.csv
        run_manifest.json
      run_B_multiaudit_lb05/
        tester.html
        journal.log
        events.csv
        run_manifest.json
      run_C_multiaudit_lb10/
        tester.html
        journal.log
        events.csv
        run_manifest.json
      run_D_multiaudit_lb20/
        tester.html
        journal.log
        events.csv
        run_manifest.json
      comparison/
        BOOT_002_LOOKBACK_COMPARISON_FA.md

پس از چهار Run، AGENT_02 ورودی‌ها و اجرای سفارش را تطبیق می‌دهد؛ AGENT_01 رویدادهای ساختاری را استخراج می‌کند؛ AGENT_03 هویت نسخه، یکسانی شرایط، پوشش تاریخچه و نتیجه مقایسه را مستقل ممیزی می‌کند.

## 10. محدودیت تفسیر و وضعیت Gate

- بازبینی ایستای v1.084 نشان داده خطوط اجرایی v1.083 حفظ شده‌اند؛ این شاهد، جایگزین Compile و Run نیست.
- GitHub Preflight فقط repository/static contracts را بررسی می‌کند.
- این آزمایش حساسیت ساختاری است، نه بهینه‌سازی یا اثبات Edge.
- پوشش Real Tick در Journal تاریخی کامل و یکنواخت نیست؛ هشدارهای هر Run جدا ثبت شوند.
- حتی پس از چهار Run موفق، OOS/WFO و Forward Demo همچنان لازم‌اند.

**BOOT-002 تنها پس از دو Compile، چهار Tester Run، تطبیق A/B، مقایسه C/D و Audit مستقل COMPLETE می‌شود.** تا آن زمان W1/W2/W3 آموزش رسمی را آغاز نمی‌کنند.
