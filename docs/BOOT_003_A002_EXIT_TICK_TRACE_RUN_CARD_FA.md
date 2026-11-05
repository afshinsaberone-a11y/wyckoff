# BOOT-003 — کارت اجرای A002 Exit Tick Trace

**هدف:** بازسازی زنجیرهٔ Quote → Stop Trigger → Deal برای معاملهٔ A002 با استفاده از همان دادهٔ Strategy Tester و ساعت سرور بروکر. این اجرا فقط برای ممیزی تاریخی است؛ هیچ قانون ورود/خروج، SL/TP، حجم یا ریسک تغییر نمی‌کند.

## 1. هویت و وضعیت ابزار

- شاخهٔ تشخیصی: `forensics/a002-exit-tick-trace-20261105`
- سورس پایه: `src/Wyckoff_XAUUSD_W0_v1_08_C2_T030_SB050_LEDGER_V2.mq5`
- تغییر: افزودن ردیاب اختیاری و فقط‌خواندنی Quote در `OnTick` و ثبت متادیتای Deal در `OnTradeTransaction`.
- پیش‌فرض `InpEnableExitTickTrace=false` است؛ فقط در اجرای تشخیصی تاریخی فعال شود.
- ردیاب فقط `SymbolInfoTick` را می‌خواند و فایل CSV می‌نویسد؛ هیچ تابع ارسال/اصلاح/بستن سفارش را فراخوانی نمی‌کند.
- وضعیت فعلی: تغییر سورس در Git ثبت شده و کنترل‌های ایستای اولیه انجام شده‌اند؛ **MetaEditor Compile و Strategy Tester هنوز اجرا نشده‌اند**. تا دریافت شواهد کامپایل و تست، این شاخه Draft باقی بماند.

## 2. تنظیمات اجرای Tester

برای حفظ قابلیت مقایسه، تنظیمات A002 زیر عیناً حفظ شوند:

| پارامتر | مقدار A002 |
|---|---|
| Server | WMMarkets-Demo |
| Symbol | XAUUSD |
| Period | M5 |
| Model | Every tick based on real ticks |
| From (server time) | 2026.01.02 00:00 |
| To (server time) | 2026.11.04 00:00 |
| Initial deposit | 10,000 USD |
| Leverage | 1:200 |
| Optimization | Off |
| Forward | Off |
| Run mode | Single test |

مرجع کنترل اجرای A002 تعداد 64,536,522 تیک و 59,676 کندل تولیدشده را ثبت کرده است. این تعدادها را در اجرای تشخیصی تازه با Journal مقایسه کنید؛ برابری آن‌ها به‌تنهایی اثبات همسانی کامل تاریخچه نیست، اما اختلاف باید گزارش شود.

**مهم:** تاریخ شروع/پایان را کوتاه نکنید؛ Warm-up و تاریخچهٔ قبل از ورود باید همانند A002 باقی بمانند. از همان دادهٔ همگام‌شدهٔ WMMarkets و همان سرور/نماد/مدل استفاده کنید. Spread mode/value، commission، swap و execution delay را نیز از Tester ثبت و با شواهد A002 مقایسه کنید. هر تفاوت محیطی را صریحاً ثبت کنید.

## 3. ورودی‌های جدید و نام فایل‌های یکتا

در Inputs فقط این موارد را برای تشخیص تغییر دهید:

```text
InpEnableExitTickTrace = true
InpExitTickTraceStart  = 2026.04.24 18:50:00
InpExitTickTraceEnd    = 2026.04.27 01:05:00
InpLedgerRunID         = WM20261105A003TRACE
InpCSVFileName         = Wyckoff_W0_A002_EXITTRACE_20261105.csv
InpLedgerFileName      = BOOT003_A002_EXIT_TRACE_LEDGER.csv
```

Start/End به **ساعت سرور WMMarkets** هستند، نه ساعت محلی ویندوز. RunID باید یکتا بماند. نام CSV قدیمی و Ledger نیز عمداً یکتا انتخاب شده تا فایل‌های A002 یا اجرای قبلی حذف/جایگزین نشوند.

همهٔ ورودی‌های استراتژی، به‌ویژه RiskPercent، RewardRisk، StopATRBuffer، Lookbackها، expiryها، تایم‌فریم‌ها، Magic و فیلترها باید با A002 برابر بمانند. از Optimizer استفاده نکنید.

## 4. خروجی مورد انتظار

ردیاب، در هر OnTick داخل بازه، Bid، Ask، Spread، Last، حجم/پرچم تیک و timestamp میلی‌ثانیه‌ای را ثبت می‌کند. در رخداد Deal نیز ticket، زمان میلی‌ثانیه‌ای Deal، قیمت Deal و کد علت خروج ضمیمه می‌شود.

نام فایل Trace:

`BOOT003_A002_EXIT_TICK_TRACE_WM20261105A003TRACE.csv`

مسیر در Journal چاپ می‌شود و در Common Files ترمینال قرار دارد. فایل‌های Legacy CSV و Event Ledger نیز با نام‌های یکتای تعیین‌شده در همان Common Files ذخیره می‌شوند.

در پایان، این موارد را از همان Run جمع‌آوری و آرشیو کنید:
1. فایل Trace بالا؛
2. Event Ledger 28 ستونی Run جدید؛
3. Legacy Event CSV؛
4. Strategy Tester HTML Report؛
5. Journal کامل `.log`؛
6. فایل `.set` استفاده‌شده؛
7. Compile log و hash سورس/EX5 تولیدشده.

## 5. روش تحلیل نقطهٔ فعال‌شدن SL

معاملهٔ هدف A002 یک BUY بوده است؛ سمت قابل‌اجرای خروج آن **BID** است. سطح SL مرجع 4712.14 است.

در Trace:
- `ExecutableSide=BID` برای BUY و `ExecutableSide=ASK` برای SELL است.
- `SignedStopDistancePoints` برای BUY برابر `(Bid - SL) / Point` است.
- مقدار مثبت یعنی Bid هنوز بالای SL است؛ صفر یا منفی یعنی Bid به SL رسیده یا از آن عبور کرده است.
- برای SELL علامت قرینه است و سمت قابل اجرا Ask خواهد بود.

برای BUY این توالی را استخراج کنید:
1. آخرین Tick قبل از اولین Bid برابر/کمتر از 4712.14؛
2. اولین Tick با Bid برابر/کمتر از 4712.14؛
3. اولین Quote پس از بازشدن مجدد بازار، در صورت وجود وقفهٔ آخر هفته؛
4. زمان Deal (با میلی‌ثانیه)، قیمت Deal و `DEAL_REASON_SL`؛
5. اختلاف زمانی بین اولین عبور از SL و Deal و اختلاف قیمت Deal با اولین Bid قابل اجرا.

در هر سطر، `TickTimeMsc` زمان خود Quote است و `DealTimeMsc` زمان Deal از History است. `ObservedTimeServer` زمان مشاهدهٔ callback را ثبت می‌کند؛ برای ترتیب، هر سه را کنار هم بررسی کنید. Quote خوانده‌شده در callback به‌تنهایی جایگزین دنبالهٔ OnTick نیست.

**هشدار کامل‌بودن Tick Trace:** در MQL5 اگر رویداد `NewTick` قبلی هنوز در صف باشد یا `OnTick` در حال پردازش باشد، رویداد جدید ممکن است به صف EA اضافه نشود. چون این Patch در هر `OnTick`، `SymbolInfoTick`، پیمایش Positionها و `FileWrite` اجرا می‌کند، CSV حاصل را باید «نمونه‌های Quote مشاهده‌شده در callbackها» دانست، نه تضمیناً تمام Tickهای منبع. بنابراین از آن به‌تنهایی برای تعیین قطعی اولین Tick عبور از SL استفاده نکنید. برای نسخهٔ دقیق‌تر، برداشت محدود و chunk‌شدهٔ `CopyTicksRange` با `COPY_TICKS_INFO` از همان تاریخچهٔ Strategy Tester پیشنهاد می‌شود؛ تعداد بازگشتی، `GetLastError`، خطای buffer و بازهٔ زمانی هر chunk باید ثبت شود. این برداشت تاریخچه هنوز در کد فعلی PR #15 پیاده‌سازی نشده است و باید جداگانه کامپایل و اعتبارسنجی شود. مرجع: https://www.mql5.com/en/docs/event_handlers/ontick و https://www.mql5.com/en/docs/series/copyticksrange

## 6. تفکیک نتیجه‌ها

- **Gap محتمل:** آخرین Bid قبل از وقفه بالای SL بوده و اولین Bid بعد از وقفه از قبل به‌طور معنادار پایین‌تر از SL باز شده است؛ Deal نیز با همان Quote/حرکت همخوانی دارد.
- **حرکت پیوسته اما Fill دور:** Trace چند Quote متوالی اطراف SL دارد، ولی Deal بسیار پایین‌تر و با تأخیر زمانی ثبت شده است؛ زمان‌بندی و مدل اجرای Tester باید بررسی شود.
- **شکاف/دادهٔ ناقص:** بین Quoteهای ثبت‌شده نزدیک SL فاصلهٔ زمانی غیرعادی یا هشدارهای history/tick وجود دارد؛ علت را تا تطبیق داده خام قطعی نکنید.
- **اشکال مرجع/گزارش:** Quoteهای قابل اجرا نزدیک SL یا بالاترند، اما Deal با قیمت 4698.78 ثبت شده؛ تطبیق Order/Deal/Position و زمان میلی‌ثانیه‌ای و نسخهٔ EX5 ضروری است.

هیچ‌یک از سناریوها را صرفاً با برچسب 89% real ticks نتیجه‌گیری نکنید. در گزارش قبلی Tester، کنار گذاشتن 80,385 دقیقه‌بار از تاریخچهٔ real ticks، 32 روز کاملِ متأثر و اختلاف قیمت/حجم گزارش شده بود؛ باید مشخص شود دقیقهٔ خروج 2026.04.27 01:00 در چه وضعیت داده‌ای قرار داشته است.

## 7. معیار پذیرش

- Compile در MetaEditor با 0 errors و 0 warnings؛ Compile log ذخیره شود.
- Run تاریخی با همان Tester configuration انجام شود؛ هیچ حساب زنده‌ای استفاده نشود.
- وجود فایل Trace و header کامل و ردیف Deal با timestamp/قیمت/علت تأیید شود.
- مقادیر ورودی معاملاتی با A002 تطبیق داده شوند؛ تفاوت فقط در ورودی‌های تشخیصی/نام فایل/RunID پذیرفته است.
- تعداد تیک/کندل تولیدشده، history warnings، spread و هزینه‌ها با A002 مقایسه شوند.
- Eventهای Legacy و نتیجهٔ معامله بررسی شوند تا اطمینان حاصل شود Instrumentation رفتار معاملاتی را عوض نکرده است.

**محدودیت مهم:** Trace این Patch در هر فراخوانی OnTick نمونه‌برداری از آخرین `SymbolInfoTick` را ذخیره می‌کند؛ برای بازسازی دقیق باید timestampهای Quote و callback و Deal با هم بررسی شوند. این تغییر به‌تنهایی تضمین نمی‌کند تاریخچهٔ تیک بروکر کامل یا همسان با اجرای تاریخی A002 بوده است.

**No live trading. No trading-rule change. No profitability claim.**
