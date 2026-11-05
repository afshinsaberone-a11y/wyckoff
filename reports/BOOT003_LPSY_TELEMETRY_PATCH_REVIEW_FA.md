# BOOT-003 — بازبینی ایستای اصلاح Telemetry برای LPSY Invalidation

**شاخه:** `fix/boot003-lpsy-ledger-diagnostics-rebased`  
**شاخهٔ مبنا:** `feature/w0-event-ledger-v2`  
**Commit:** `fae0a30210c171e1817e0cf5a6d6c7cd57e35de9`  
**MQ5 Git Blob SHA پس از اصلاح:** `553eea104b81cf31cce5a858e3d5743bb4499669`

## هدف و تفسیر صحیح EV126

RunID برابر `WM20261104A002` در EV126 رویداد `REJECT_LPSY_INVALIDATED` را بدون Details ثبت کرده است. این invalidation قبل از Candidate creation رخ می‌دهد؛ بنابراین CandidateID و DecisionID خالی‌اند و طبق سیاست Ledger، DecisionStatus و ReasonCode نیز باید خالی بمانند. ساخت شناسه/تصمیم مصنوعی ممنوع است.

## اصلاح telemetry-only

Helper جدید `LogRejectWithLedgerDetails` سه ورودی مستقل می‌گیرد:
- reason؛
- `legacyDetails` که برای این رخداد صریحاً خالی نگه داشته می‌شود؛
- `ledgerDetails` که close، strengthBreakLevel، ATR، InpLPSInvalidationATR و invalidationThreshold را ثبت می‌کند.

در نتیجه فقط Details در Ledger 28 ستونی تکمیل می‌شود و خروجی Legacy یازده‌ستونی از نظر Details بدون تغییر می‌ماند.

## کنترل‌های ایستا

- Helper و فراخوانی جدید در سورس fetch‌شده از GitHub موجودند.
- فراخوانی قدیمی بدون Details برای REJECT_LPSY_INVALIDATED دیگر وجود ندارد.
- legacyDetails به‌صورت صریح رشتهٔ خالی است.
- شرط invalidation عیناً حفظ شده است:
  `bar.close>g_setup.strengthBreakLevel+InpLPSInvalidationATR*atr`
- `ResetSetup("LPSY invalidated")` حفظ شده است.
- هیچ شرط معاملاتی، مدیریت ریسک، حجم، SL/TP یا state transition تغییر نکرده است.
- شاخه از آخرین head شاخهٔ feature ساخته شد؛ diff این PR فقط یک commit و یک فایل MQ5 با 35 افزودن و 1 حذف است.

## وضعیت

**STATIC REVIEW: PASS (محدود به diff و کنترل متنی).**

هنوز موارد زیر تأیید نشده‌اند:
1. Compile واقعی MQL5 در MetaEditor؛
2. اجرای مجدد MT5 Strategy Tester؛
3. برابری Legacy CSV با Comparator و 67 ورودی مشترک؛
4. اجرای Ledger validator روی Run جدید؛
5. Hash فایل EX5 حاصل از همین compile.

در زمان بررسی، برای commit patch اجرای GitHub Actions مرتبطی مشاهده نشد. CI پایتون نیز جایگزین کامپایل MQL5 نیست.

## دستور پذیرش

پس از Compile موفق، Run جدید با SET ثابت و RunID یکتا اجرا شود. سپس:
- Legacy A/B comparator باید همچنان ده ستون مشترک و ترتیب ردیف‌ها را برابر نشان دهد؛
- Ledger جدید باید Details تشخیصی EV مربوط به LPSY invalidation را پر کند؛
- CandidateID/DecisionID/DecisionStatus/ReasonCode برای ردشدن پیش از Candidate خالی باقی بمانند؛
- هیچ تغییر معاملاتی در گزارش Diff دیده نشود.

**هیچ ادعای سودآوری یا آمادگی حساب واقعی از این اصلاح نتیجه نمی‌شود.**
