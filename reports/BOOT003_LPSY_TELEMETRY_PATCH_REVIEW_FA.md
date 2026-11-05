# BOOT-003 — بازبینی ایستای اصلاح Telemetry برای LPSY Invalidation

**شاخه:** `fix/boot003-lpsy-ledger-diagnostics`  
**شاخهٔ مبنا:** `feature/w0-event-ledger-v2`  
**PR:** [#12 — Draft](https://github.com/afshinsaberone-a11y/wyckoff/pull/12)  
**Commit:** `cdd0319fdbe4bf8f8208ede9ca25462ae35b7dfc`  
**MQ5 Git Blob SHA پس از اصلاح:** `553eea104b81cf31cce5a858e3d5743bb4499669`

## هدف

رفع نقص telemetry در EV126 از RunID برابر `WM20261104A002`: رویداد `REJECT_LPSY_INVALIDATED` فاقد مقدار `Details` بود.

نکتهٔ معنایی مهم: این invalidation قبل از ایجاد Candidate رخ می‌دهد. بنابراین خالی‌بودن CandidateID و DecisionID و به تبع آن DecisionStatus/ReasonCode مطابق سیاست فعلی Ledger است. نباید شناسه یا تصمیم مصنوعی ساخته شود. فقط Details تشخیصی نیاز به تکمیل دارد.

## تغییر انجام‌شده

یک helper محدود به نام `LogRejectWithLedgerDetails` اضافه شده است که دو payload جداگانه می‌پذیرد:
- `legacyDetails`: مقدار خالی برای حفظ خروجی 11 ستونی فعلی؛
- `ledgerDetails`: شامل close، strengthBreakLevel، ATR، InpLPSInvalidationATR و invalidationThreshold.

فراخوانی جدید فقط در شاخهٔ فروش/شرط `REJECT_LPSY_INVALIDATED` اعمال شده است.

## کنترل‌های ایستای انجام‌شده

- Helper جدید در سورس شاخهٔ fix وجود دارد.
- فراخوانی قبلی بدون Details برای `REJECT_LPSY_INVALIDATED` حذف شده است.
- `legacyDetails` به‌صورت صریح رشتهٔ خالی است.
- شرط معاملاتی اصلی عیناً حفظ شده است:
  `bar.close>g_setup.strengthBreakLevel+InpLPSInvalidationATR*atr`
- فراخوانی `ResetSetup("LPSY invalidated")` حفظ شده است.
- هیچ شرط ورود/خروج، sizing، SL/TP، ریسک یا state transition دیگری تغییر نکرده است.
- مقایسهٔ Commit با شاخهٔ مبنا نشان می‌دهد فقط یک MQ5 تغییر کرده: 35 افزودن و 1 حذف.
- سورس پس از ثبت مجدداً از GitHub fetch و محل helper/branch بررسی شد.

## وضعیت اعتبارسنجی

**STATIC REVIEW: PASS** برای محدودبودن diff و حفظ شرط و Reset.

موارد زیر هنوز انجام نشده‌اند و نباید PASS فرض شوند:
1. Compile در MetaEditor؛
2. اجرای مجدد Strategy Tester روی همان بازه/SET؛
3. کنترل خروجی جدید Ledger با Validator؛
4. مقایسهٔ A/B روی CSV قدیمی 11 ستونی و 67 ورودی مشترک؛
5. تأیید Hash فایل EX5 تولیدشده از همین سورس.

GitHub Actions برای Commit این patch در زمان بررسی، run مرتبطی گزارش نکرده است. CI پایتون جایگزین کامپایل MQL5 نیست.

## دستور اجرای بعدی

1. شاخهٔ fix را در محیط MT5 دریافت کنید.
2. فایل MQ5 را در MetaEditor باز و Compile کنید.
3. در صورت صفر خطا، Compile log و EX5 جدید را آرشیو کنید.
4. با SETهای ثابت، یک Replay جدید با RunID یکتا اجرا کنید.
5. هر دو CSV قدیمی A و B را با Comparator رسمی مقایسه کنید.
6. Validator روی Ledger 28 ستونی جدید اجرا شود و بررسی کنید EV مربوط به LPSY Details تشخیصی دارد، درحالی‌که CandidateID/DecisionID/DecisionStatus/ReasonCode خالی مانده‌اند.
7. فقط پس از PASS تمام موارد، PR از Draft خارج شود.

**هیچ ادعای سودآوری یا آمادگی حساب واقعی از این تغییر نتیجه نمی‌شود.**
