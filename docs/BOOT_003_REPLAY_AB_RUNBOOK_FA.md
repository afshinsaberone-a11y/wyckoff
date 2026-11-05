# BOOT-003 — دستور اجرای Replay A/B بین C2 و Ledger v2

**شاخه:** \`feature/w0-event-ledger-v2\`  
**هدف:** اثبات اینکه Instrumentation و Event Ledger v2 رفتار معاملاتی C2 را تغییر نداده است.  
**وضعیت فعلی (2026-11-05):** Replay واقعی A/B اجرا شد؛ جریان Legacy و 67 ورودی مشترک PASS شدند. جزئیات و Gateهای باز در بخش 8 و گزارش docs/BOOT_003_REPLAY_AB_RESULTS_20261105_FA.md ثبت شده‌اند.

## 1. اصل مقایسه

دو EA باید با یک داده و یک تنظیمات اجرا شوند:

- **A — Baseline:** \`src/Wyckoff_XAUUSD_W0_v1_08_C2_T030_SB050.mq5\` از شاخهٔ \`main\`.
- **B — Instrumented:** \`src/Wyckoff_XAUUSD_W0_v1_08_C2_T030_SB050_LEDGER_V2.mq5\` از شاخهٔ \`feature/w0-event-ledger-v2\`.

هر دو نسخه یک CSV قدیمی/مشترک با Schema یازده‌ستونی می‌نویسند:

\`ServerTime, EA_Version, Symbol, InitialBalance, SetupID, Direction, Event, Details, RangeHigh, RangeLow, PositionID\`

فقط ستون \`EA_Version\` در مقایسه نادیده گرفته می‌شود، چون شناسهٔ Build دو فایل عمداً متفاوت است. ده ستون دیگر، ترتیب سطرها و تعداد سطرها باید دقیقاً برابر باشند. فایل ۲۸ ستونی Event Ledger v2 در این مقایسه با CSV یازده‌ستونی C2 مقایسه نمی‌شود؛ آن فایل برای اعتبارسنجی هویت Candidate/Decision/Order/Deal است.

## 2. قفل کردن محیط آزمایش

قبل از Run A این مقادیر را ثبت و ثابت کنید:

- حساب/سرور: همان حساب WMMarkets-Demo؛
- Symbol: XAUUSD؛
- Period: M5؛
- Model: Every tick based on real ticks؛
- تاریخ و ساعت شروع/پایان: دقیقاً یکسان و با ساعت سرور؛
- Initial deposit، ارز حساب و Leverage: یکسان؛
- Spread mode/value، commission، swap و execution delay: یکسان؛
- همان تاریخچهٔ تیک و بارهای همگام‌شده؛
- Optimization و Forward: خاموش؛ فقط Single Run؛
- همهٔ ورودی‌های مشترک EA: یکسان.

از بازهٔ دقیق Run A002 استفاده کنید؛ تاریخ را از لاگ یا Screenshot اجرای A002 استخراج کنید، حدس نزنید. هر دو فایل \`.set\` را از تب Inputs ذخیره کنید. ورودی‌های اختصاصی Ledger با پیشوند \`InpLedger\` فقط در B وجود دارند و Comparator آن‌ها را از مقایسهٔ ورودی‌های مشترک کنار می‌گذارد.

## 3. ساخت دو EA و اجرای جداگانه

1. فایل Baseline را از شاخهٔ \`main\` دانلود و در MetaEditor با نام اصلی خودش Compile کنید.
2. فایل Ledger v2 را از شاخهٔ \`feature/w0-event-ledger-v2\` دانلود و جداگانه Compile کنید.
3. برای هر دو، \`InpExportCSV=true\` باشد و مقدار \`InpCSVFileName\` مشترک بماند.
4. Run A را با Baseline اجرا کنید و CSV یازده‌ستونی و گزارش HTML و Journal را با نام A ذخیره کنید.
5. Run B را با Ledger v2 اجرا کنید. \`InpLedgerRunID\` باید یکتا باشد؛ برای نمونه \`WM20261104AB001\`. CSV یازده‌ستونی نسخهٔ B، CSV بیست‌وهشت‌ستونی Ledger و گزارش HTML و Journal را جداگانه ذخیره کنید.
6. فایل‌های A و B را پس از هر Run از مسیر Common Files کپی و بلافاصله نام‌گذاری کنید؛ اجازه ندهید اجرای بعدی فایل قبلی را جایگزین کند.

**مهم:** برای A/B، CSV قدیمی یازده‌ستونی هر دو EA را به Comparator بدهید. فایل \`Wyckoff_W0_event_ledger_v2_<RunID>.csv\` را به‌عنوان ورودی دوم Comparator استفاده نکنید.

## 4. نام فایل‌های CSV

نام دقیق در Journal چاپ می‌شود. الگوی ساخت نام در سورس:

- Baseline: \`<InpCSVFileName بدون پسوند>_C2_SB050_T030_TIMING_B<BreakoutExpiry>_R<RetestExpiry>_RC<RecoveryExpiry>.csv\`
- Ledger v2 legacy: \`<InpCSVFileName بدون پسوند>_LEDGER_V2_C2_SB050_T030_TIMING_B<BreakoutExpiry>_R<RetestExpiry>_RC<RecoveryExpiry>.csv\`
- Event Ledger v2: \`<InpLedgerFileName بدون پسوند>_<InpLedgerRunID>.csv\`

به خروجی Journal اتکا کنید، نه به نام فرضی فایل.

## 5. اجرای Comparator در PowerShell

فایل Comparator را در پوشهٔ کاری BOOT-003 دریافت کنید:

\`\`\`powershell
$u = "https://raw.githubusercontent.com/afshinsaberone-a11y/wyckoff/feature/w0-event-ledger-v2/research/replay_ab_compare.py"
Invoke-WebRequest -Uri $u -OutFile .\\replay_ab_compare.py
\`\`\`

فایل‌ها را با نام‌های زیر در همان پوشه قرار دهید:

- \`A_C2_legacy.csv\`
- \`B_LEDGER_V2_legacy.csv\`
- \`A_C2.set\`
- \`B_LEDGER_V2.set\`

سپس اجرا کنید:

\`\`\`powershell
python .\\replay_ab_compare.py .\\A_C2_legacy.csv .\\B_LEDGER_V2_legacy.csv --baseline-set .\\A_C2.set --ledger-set .\\B_LEDGER_V2.set --output-json .\\BOOT003_AB_compare.json
\`\`\`

کد خروجی:

- \`0\`: ورودی‌های مشترک SET و جریان رویداد مشترک CSV برابرند؛ این فقط Gate مقایسهٔ EA است، نه تأیید کامل محیط Tester.
- \`2\`: اختلاف در جریان رویداد یا ورودی‌های مشترک پیدا شده است.
- \`3\`: ورودی نامعتبر، فایل ناقص یا خطای I/O.
- \`4\`: CSVها برابرند، اما فایل‌های SET برای کنترل ورودی‌ها ارائه نشده‌اند؛ A/B هنوز Pass نیست.

گزارش JSON تعداد سطرها، تعداد هر Event، Eventهای معاملاتی، اولین محل اختلاف، ستون‌های متفاوت و مقادیر دو طرف را نگه می‌دارد.

## 6. معیار پذیرش نهایی A/B

برای قبول Replay A/B باید همهٔ شرایط زیر مستند باشند:

1. Comparator جریان ۱۱ ستونی را بدون اختلاف تأیید کند.
2. ورودی‌های مشترک دو فایل SET برابر باشند.
3. Symbol، Period، تاریخ‌ها، مدل تیک، Spread، Deposit، Leverage، Commission/Swap و تاریخچهٔ بازار از شواهد Tester برابر باشند.
4. گزارش‌های HTML و Journal هر دو Run ذخیره و بررسی شده باشند.
5. Order/Deal/Position و معاملات نهایی با History حساب/Tester تطبیق داده شوند.
6. Hash فایل MQ5، EX5، SET، CSV و HTML هر دو Run ثبت شده باشد.
7. هیچ هشدار تاریخچه، missing ticks، یا تفاوت محیطی حل‌نشده باقی نمانده باشد.

اگر اولین اختلاف در Event stream ظاهر شد، اولین ردیف و مقادیر دو طرف باید بررسی شوند. اختلاف را با حذف سطر، تغییر دستی CSV یا نادیده گرفتن ستون‌های استراتژی پنهان نکنید. \`Details\`، \`SetupID\`، RangeHigh/Low، Direction، PositionID و زمان Event بخشی از مقایسه‌اند.

## 7. محدودیت

برابری CSV و ورودی‌ها نشان می‌دهد رویدادهای ثبت‌شدهٔ مشترک در دو Run یکسان‌اند؛ اما به‌تنهایی صحت دادهٔ بازار، یکسانی محیط Tester، اجرای صحیح partial fill در همهٔ حالت‌ها یا سودآوری را ثابت نمی‌کند. نتیجهٔ مالی، تطبیق تاریخچه و ممیزی مستقل باید جدا ثبت شود. تا تکمیل همهٔ Gateها، دادهٔ BOOT-003 برای آموزش W1/W2/W3 تأیید نهایی نیست.

## 8. نتیجهٔ اجرای واقعی Replay A/B — 2026-11-05

Run A با Baseline C2 از main و Run B با Ledger v2 (RunID برابر WM20261104A002) اجرا شدند. هر دو روی WMMarkets-Demo، XAUUSD M5، مدل Every tick based on real ticks، بازهٔ 2026.01.02 00:00 تا 2026.11.04 00:00، سرمایهٔ 10,000 USD و اهرم 1:200 بودند.

نتیجهٔ Comparator رسمی:
- Status: PASS_SHARED_EA_INPUTS_AND_EVENT_STREAM_ONLY
- هر دو CSV تعداد 126 ردیف داشتند؛ 10 ستون غیر از EA_Version و ترتیب ردیف‌ها برابر بود؛ صفر اختلاف.
- 67 ورودی مشترک SET برابر بود؛ کلید مختص یک طرف یا مقدار متفاوت وجود نداشت.
- تعداد تیک تولیدشده در هر دو اجرا 64,536,522 و تعداد کندل‌ها 59,676 بود.
- موجودی نهایی هر دو اجرا 9,937.56 USD بود.

این PASS به جریان رویداد مشترک و ورودی‌های مشترک محدود است و اثبات کامل یکسانی تمام تنظیمات محیط Tester، هویت EX5 زمان اجرا یا سودآوری نیست.

### 8.1 Gateهای باز

- Hash دقیق EX5 در لحظهٔ اجرا ثبت نشده است؛ لاگ A اندازهٔ بارگذاری 127,938 و لاگ B/A002 اندازهٔ بارگذاری 146,391 بایت را نشان می‌دهد، درحالی‌که فایل‌های فعلی به‌ترتیب 127,900 و 146,328 بایت‌اند.
- انتهای History synchronization در A برابر 2026.11.04 و در B برابر 2026.11.03 گزارش شده؛ Tick History span و تعداد تیک/کندل تولیدشده برابر است.
- Spread mode/value، commission، swap و execution delay هنوز مستقل مستند نشده‌اند.
- HTML report و Compile logها آرشیو نشده‌اند.
- ممیزی معنایی CSV بیست‌وهشت‌ستونی A002 انجام شده و PASS WITH WARNINGS است؛ جزئیات در گزارش A002 آمده است.

گزارش جزئی و Hashهای آرشیوشده در docs/BOOT_003_REPLAY_AB_RESULTS_20261105_FA.md ثبت شده‌اند. تا بستن موارد بالا، BOOT-003 را برای آموزش W1/W2/W3 تأیید نهایی نکنید.


## 9. ممیزی Event Ledger v2 — A002 (2026-11-05)

فایل 28 ستونی RunID=`WM20261104A002` در مسیر `experiments/BOOT_003_A002_event_ledger_v2.csv` آرشیو شده است. ممیزی مستقل شامل 127 ردیف، 28 ستون و 26 کنترل ساختاری/هویتی موفق بود. زنجیرهٔ یک Candidate ثبت‌شده تا Decision پذیرفته‌شده، Order، Deal ورودی، Position و Trade Closed قابل ردیابی است. وضعیت: **PASS WITH WARNINGS**.

### 9.1 قرارداد ترتیب رویدادها

- `EventSequence` ترتیب ثبت/ارسال رویدادها به Ledger را نشان می‌دهد؛ نباید بدون بررسی مسیر کد آن را ترتیب دقیق همهٔ محاسبات داخلی یا causal order فرض کرد.
- `M5_ENTRY_EVALUATION` در انتهای `ProcessEntryBar` نوشته می‌شود و ممکن است پس از Candidate/Order باشد، در حالی که فیلد Details زمان کندل ارزیابی‌شده را نگه می‌دارد.
- `SETUP_RESET(POSITION_CLOSED)` و `TRADE_CLOSED` از مسیرهای جداگانهٔ OnTick/ProcessSignalBar و OnTradeTransaction می‌آیند؛ ترتیب آنها در نسخهٔ فعلی ثبت emission را منعکس می‌کند.
- رویداد `REJECT_LPSY_INVALIDATED` در A002 فاقد Details است. خالی‌بودن CandidateID/DecisionID و به تبع آن DecisionStatus/ReasonCode، چون رخداد قبل از ایجاد Candidate رخ می‌دهد، طبق سیاست Ledger مورد انتظار است. فقط Details باید در Ledger پر شود و Legacy Details خالی بماند.

### 9.2 فایل‌های آرشیوشده

- `experiments/BOOT_003_A002_event_ledger_v2.csv`
- `reports/BOOT003_A002_LEDGER_AUDIT_FA.md`
- `experiments/BOOT003_A002_LEDGER_AUDIT.json`
- `reports/BOOT003_A002_LEDGER_SOURCE_REVIEW_FA.md`
- `experiments/BOOT003_SHA256_MANIFEST_20261105.json`

### 9.3 Gateهای باقی‌مانده

1. افزودن Details تشخیصی فقط به Ledger برای REJECT_LPSY_INVALIDATED در commit مستقل؛ DecisionStatus/ReasonCode پیش از Candidate خالی می‌مانند و خروجی Legacy باید برابر حفظ شود.
2. MetaEditor compile و آرشیو compile log برای هر دو نسخه.
3. حل اختلاف انتهای Bar History (A=2026.11.04، B=2026.11.03) یا مستندسازی کافی آن.
4. ثبت/تطبیق Spread mode/value، Commission، Swap و Execution delay.
5. آرشیو HTML reports و بررسی دقیق SL fill با تیک خام/History؛ زیان A002 برابر 1.802R بوده است.
6. Hash فایل EX5 زمان اجرا در Replay تاریخی موجود نیست؛ Hash فایل فعلی جایگزین آن مدرک نمی‌شود.

تا بسته‌شدن Gateهای بالا، داده برای آموزش نهایی W1/W2/W3 تأیید نشده است.


پیگیری telemetry-only برای EV126 در [Issue شمارهٔ 11](https://github.com/afshinsaberone-a11y/wyckoff/issues/11) ثبت شده است. پیش از پذیرش این تغییر، برابری کامل CSV قدیمی A/B و عدم تغییر منطق معاملاتی باید دوباره ثابت شود.


اصلاح telemetry-only در [Draft PR شمارهٔ 13](https://github.com/afshinsaberone-a11y/wyckoff/pull/13) روی شاخهٔ `fix/boot003-lpsy-ledger-diagnostics-rebased` آمادهٔ کامپایل و تست است؛ PR شمارهٔ 12 superseded و بسته شد.


## 10. Timing Audit تکمیلی برای SL

نتیجهٔ aggregate از 199 سفارش بازار در [گزارش زمینهٔ اجرای SL](../reports/BOOT003_SL_EXECUTION_TIMING_CONTEXT_20261105_FA.md) ثبت شده است. این sample برای زمان‌بندی عمومی سفارش مفید است، اما Position/Exit Deal A002 را شناسایی نمی‌کند و جایگزین بررسی `DEAL_REASON_SL` نیست. پیش از نتیجه‌گیری دربارهٔ لغزش 1,336 پوینتی، یک مسیر مستقل trigger-to-fill فقط خواندنی لازم است.
