# BOOT-003 — بازبینی ایستای مسیرهای ثبت رویداد Ledger v2 (A002)

**شاخه:** `feature/w0-event-ledger-v2`  
**سورس بررسی‌شده:** `src/Wyckoff_XAUUSD_W0_v1_08_C2_T030_SB050_LEDGER_V2.mq5`  
**Git blob SHA-1:** `0366568d082af3e4fa5854e8ddf9790c94be25c8`  
**دامنه:** بررسی مسیرهای ثبت Candidate، ارزیابی M5، Order، Reset، Trade Transaction و رد LPSY؛ بدون تغییر سورس یا منطق معاملاتی.

## 1. نتیجه

**وضعیت: SOURCE REVIEW PASS WITH 1 ACTIONABLE LOGGING DEFECT + 2 TRACE-ORDER NOTES**

سورس بررسی‌شده با SHA ثبت‌شده در GitHub یکسان است. مسیر ایجاد Candidate پس از تأیید Recovery در M5 و پیش از فراخوانی `PlaceTrade` قرار دارد. اتصال سفارش و Deal به Candidate از طریق map شناسه‌های سفارش/Position انجام می‌شود و برای معاملهٔ A002 در CSV نیز به‌درستی قابل ردیابی است.

هیچ تغییری در قوانین ورود، خروج، اندازه موقعیت یا مدیریت ریسک در این مرحله اعمال نشده است.

## 2. بررسی Candidate و Order

- خطوط 1534–1548: ابتدا `M5_BUY_RECOVERY_CONFIRMED` ثبت می‌شود، سپس `LedgerBeginCandidate(...)` و بلافاصله `PlaceTrade(...)` فراخوانی می‌شوند.
- خطوط 306–328: `LedgerBeginCandidate` شناسهٔ Candidate می‌سازد و `CANDIDATE_CREATED` را ثبت می‌کند.
- خطوط 1311–1345: پس از بررسی retcode پذیرفته‌شده، Order link ثبت و `ORDER_OPENED` نوشته می‌شود.

**نتیجه:** ترتیب Candidate → ارسال/پذیرش Order در سورس صحیح است. زنجیرهٔ نمونه A002 نیز با EV52 و EV53 سازگار است.

## 3. یافته W1 — ثبت دیرهنگام M5_ENTRY_EVALUATION

در مسیر خرید، بعد از Recovery، Candidate و `PlaceTrade` اجرا می‌شوند (خطوط 1541–1548). رویداد `M5_ENTRY_EVALUATION` در انتهای `ProcessEntryBar` و در خطوط 1654–1675 ثبت می‌شود.

در CSV، EV54 پس از EV53 آمده، اما `Details` آن می‌گوید `bar=2026.04.24 18:50` و timestamp خود رویداد 18:55 است. بنابراین این رویداد snapshot تشخیصیِ ارزیابی کندل بسته‌شده است که در انتهای handler نوشته شده؛ ترتیب نوشتن CSV به‌تنهایی نشان نمی‌دهد که منطق تصمیم‌گیری پس از ارسال سفارش انجام شده باشد.

**اقدام:** در قرارداد Ledger مستند شود که `EventSequence` ترتیب emission/flush رویدادها را نشان می‌دهد، نه الزاماً ترتیب محاسبات داخلی یا causal order. برای نسخهٔ آینده می‌توان ارزیابی را پیش از side effect ثبت کرد، مشروط بر اینکه خروجی تشخیصی و جریان معاملاتی حفظ شوند. فعلاً این مورد فقط TRACE NOTE است؛ منطق معاملاتی تغییر نکند.

## 4. یافته W2 — SETUP_RESET پیش از TRADE_CLOSED

- خطوط 1702–1705: وقتی `g_setup.stage==ST_IN_POSITION` و موقعیت دیگر باز نیست، `ProcessSignalBar`، `ResetSetup("POSITION_CLOSED")` را اجرا می‌کند.
- خطوط 1911 به بعد: callback جداگانهٔ `OnTradeTransaction` رویداد Deal را پردازش می‌کند.
- خطوط 2041–2060: `TRADE_CLOSED` در این callback نوشته می‌شود.

در اجرای A002، EV56 با جزئیات `POSITION_CLOSED` قبل از EV57 (`TRADE_CLOSED`) درج شده و timestamp هر دو یکسان است. این با دو مسیر رویدادی مجزا در سورس سازگار است؛ اما قرارداد ترتیب lifecycle را مبهم می‌کند.

**اقدام:** در runbook ذکر شود که `SETUP_RESET` و `TRADE_CLOSED` از مسیرهای متفاوت تولید می‌شوند و sequence فعلی ترتیب emission است. برای تغییر ترتیب یا defer کردن Reset، ابتدا باید یک design/test مستقل نوشته شود تا پاک‌شدن state یا پردازش مجدد سیگنال تحت تأثیر قرار نگیرد. فعلاً کد تغییر نکند.

## 5. یافته W3 — رویداد REJECT_LPSY_INVALIDATED فاقد جزئیات

در خطوط 1160–1163، شرط invalidation به‌صورت قابل مشاهده بررسی می‌شود، اما فراخوانی فعلی فقط این است:

`LogReject("REJECT_LPSY_INVALIDATED");`

پس EV126 در CSV فاقد `ReasonCode` و `Details` است. بلافاصله پس از آن `ResetSetup("LPSY invalidated")` اجرا می‌شود.

**اقدام پیشنهادی، فقط برای telemetry:** فراخوانی `LogReject` باید یک payload تشخیصی کوتاه اضافه کند؛ حداقل close، `strengthBreakLevel`، ATR، `InpLPSInvalidationATR` و مقدار آستانهٔ invalidation. منطق شرط و مسیر Reset نباید تغییر کند. پس از تغییر، MetaEditor compile و تست A/B با خروجی legacy برابر لازم است.

## 6. تطبیق مستقل CSV

فایل `A002_event_ledger_v2.csv`:

- 127 ردیف، 28 ستون، SchemaVersion=2؛
- EventID یکتا و EventSequence پیوسته از 1 تا 127؛
- زمان Event و ObservedAt غیرکاهشی و برابر در این run؛
- 22 Range که همگی با RANGE_FOUND معرفی شده‌اند؛ bounds در هر Range ثابت و High بزرگ‌تر از Low است؛
- یک Candidate ایجادشده؛ یک Decision پذیرفته‌شده در رخداد ORDER_OPENED؛ یک Order، یک Entry Deal، یک Position و یک Trade Closed؛
- شناسه‌های والد/فرزند Range → Cycle → Attempt → Candidate → Decision با الگوی تعریف‌شده سازگارند.

در این فایل 26 کنترل ساختاری/هویتی مستقل PASS شدند. این نتیجه فقط روی دادهٔ مشاهده‌شده است و اثبات نمی‌کند که تمام Candidateهای ردشده یا سیگنال‌های بالقوه در تمام مسیرها ثبت می‌شوند.

## 7. کنترل معامله و ریسک

برای معاملهٔ نمونه: Entry=4729.47، SL=4712.14، TP=4764.13، حجم=0.02، ریسک برنامه‌ریزی‌شده=34.66 USD، Net P/L=-62.44 USD، realized R=-1.802. خروج Deal در 4698.78 و 1336 point بدتر از قیمت مرجع SL ثبت شده است.

این مقادیر از نظر حسابی با هم سازگارند، اما علت واقعی فاصلهٔ Fill از SL فقط با تیک خام و گزارش/History اجرای سفارش قابل تعیین است. زیان برنامه‌ریزی‌شده سقف تضمین‌شده زیان نیست.

## 8. تصمیم و Gate بعدی

1. CSV و audit report در مخزن آرشیو شوند.
2. W1 و W2 در runbook به‌عنوان ترتیب emission مستند شوند، بدون تغییر رفتار معاملاتی.
3. W3 به‌عنوان اصلاح telemetry-only در یک commit مستقل پیاده‌سازی شود.
4. نسخهٔ اصلاح‌شده باید در MetaEditor کامپایل شود؛ سپس validator، تست واقعی MT5، و comparator A/B روی همان بازه اجرا شوند.
5. EX5 hash زمان اجرای قدیمی، تفاوت یک‌روزهٔ انتهای Bar History، HTML reports و compile logs همچنان Gateهای جداگانه‌اند.

**تصمیم فعلی:** Candidate/Decision/Order/Deal linkage برای A002 قابل‌ردیابی است؛ ممیزی Ledger `PASS WITH WARNINGS` باقی می‌ماند. تا تکمیل Gateهای بالا، داده برای آموزش نهایی W1/W2/W3 تأیید نشده است.