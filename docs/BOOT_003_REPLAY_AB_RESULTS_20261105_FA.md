# BOOT-003 — گزارش نتیجهٔ Replay A/B (۵ نوامبر ۲۰۲۶)

شاخه: feature/w0-event-ledger-v2  
Run A: Baseline C2 از main  
Run B: Ledger v2، شناسهٔ اجرا WM20261104A002  
وضعیت Comparator: PASS_SHARED_EA_INPUTS_AND_EVENT_STREAM_ONLY

## 1. خلاصهٔ اجرایی

Replay واقعی A/B اجرا شد. Comparator رسمی، جریان Legacy یازده‌ستونی دو اجرا را با کنارگذاشتن فقط EA_Version مقایسه کرد و هیچ اختلافی نیافت. ۶۷ ورودی مشترک دو فایل SET نیز برابر بودند.

این نتیجه نشان می‌دهد در همین بازه و همین Replay، Instrumentation مربوط به Event Ledger v2 جریان رویدادهای مشترک C2 را تغییر نداده است. این نتیجه سودآوری یا برابری در همهٔ شرایط بازار را اثبات نمی‌کند.

## 2. مشخصات و هم‌ترازی اجرا

| مشخصه | Run A — Baseline | Run B — Ledger v2 |
|---|---|---|
| حساب/سرور | WMMarkets-Demo | WMMarkets-Demo |
| نماد / تایم‌فریم | XAUUSD / M5 | XAUUSD / M5 |
| مدل | Every tick based on real ticks | Every tick based on real ticks |
| بازه | 2026.01.02 00:00 تا 2026.11.04 00:00 | 2026.01.02 00:00 تا 2026.11.04 00:00 |
| سرمایه | 10,000 USD | 10,000 USD |
| اهرم | 1:200 | 1:200 |
| تیک تولیدشده | 64,536,522 | 64,536,522 |
| کندل تولیدشده | 59,676 | 59,676 |
| تاریخچهٔ تیک | 2024.04.19 تا 2026.11.03 | 2024.04.19 تا 2026.11.03 |
| موجودی نهایی | 9,937.56 USD | 9,937.56 USD |

یادداشت: در عبارت History synchronization، انتهای تاریخچه در A برابر 2026.11.04 و در B برابر 2026.11.03 گزارش شده است. بازهٔ تاریخچهٔ تیک و تعداد تیک و کندل تولیدشده برابرند؛ اختلاف نشانگر انتهای Bar History برای ممیزی تکمیلی باز می‌ماند.

## 3. نتیجهٔ Comparator

فایل گزارش محلی: BOOT003_AB_compare.json

| معیار | نتیجه |
|---|---:|
| تعداد ردیف A | 126 |
| تعداد ردیف B | 126 |
| اختلاف ردیف‌ها | 0 |
| ستون‌های مقایسه‌شده | 10 از 11 |
| ستون مستثنا | EA_Version |
| ورودی مشترک SET | 67 |
| ورودی متفاوت | 0 |
| کلید مختص یک طرف | 0 |

ترتیب ردیف‌ها و تمام ستون‌های مقایسه‌شده برابرند.

## 4. شمارش Eventها در هر دو اجرا

| Event | تعداد در هر دو اجرا |
|---|---:|
| BREAKOUT_PHASE_EXPIRED | 1 |
| EA_INIT | 1 |
| LPS_CONFIRMED | 2 |
| M5_BREAKOUT_CONFIRMED | 1 |
| M5_BUY_RECOVERY_CONFIRMED | 1 |
| M5_ENTRY_EVALUATION | 23 |
| M5_ENTRY_SKIPPED_PRE_READY | 2 |
| M5_RETEST_CONFIRMED | 1 |
| ORDER_OPENED | 1 |
| RANGE_FOUND | 22 |
| REJECT_LPSY_INVALIDATED | 1 |
| REJECT_NO_REENTRY | 2 |
| REJECT_SOS_WRONG_SIDE_OF_RANGE | 2 |
| REJECT_SPRING_TOO_DEEP | 11 |
| REJECT_UTAD_TOO_DEEP | 5 |
| SETUP_RESET | 22 |
| SOS_CONFIRMED | 2 |
| SOW_CONFIRMED | 1 |
| SPRING_CANDIDATE | 8 |
| SPRING_CONFIRMED | 4 |
| TEST_CONFIRMED | 5 |
| TRADE_CLOSED | 1 |
| TRADE_ENTRY_DEAL | 1 |
| UTAD_CANDIDATE | 4 |
| UTAD_CONFIRMED | 2 |
| **مجموع** | **126** |

رویدادهای معاملاتی در هر دو اجرا: یک ORDER_OPENED، یک TRADE_ENTRY_DEAL، یک TRADE_CLOSED و صفر TRADE_PARTIAL_EXIT.

## 5. نتیجهٔ مالی و Validator

موجودی نهایی هر دو اجرا 9,937.56 USD بوده است؛ نسبت به سرمایهٔ اولیه، تغییر خالص موجودی در این Replay برابر 62.44- USD است. لاگ A یک معاملهٔ BUY با حجم 0.02 را نشان می‌دهد که در 2026.04.27 با SL بسته شد؛ زیان خالص ثبت‌شده 62.44- USD و realizedR برابر 1.802- بود. به دلیل برابری ردیف‌های Legacy، رویداد TRADE_CLOSED در B نیز عیناً برابر است.

اعتبارسنجی قبلی Ledger v2 برای RunID برابر WM20261104A002 نیز PASS بود: 127 ردیف، 28 ستون، 127 EventID یکتا، یک Candidate، یک Candidate creation، یک Decision، یک Order opened، یک Entry deal، یک Trade closed، دو Deal event، صفر خطا و صفر هشدار.

Validator ساختاری قبلی برای A002 بدون خطا و هشدار بود. ممیزی مستقل معنایی انجام شد و وضعیت آن PASS WITH WARNINGS است؛ 26 کنترل ساختاری/هویتی PASS شدند و سه هشدار در گزارش مستقل ثبت شده‌اند. پیوند Candidate → Decision → Order → Deal → Position برای یک Candidate مشاهده‌شده قابل ردیابی است، اما کامل‌بودن ثبت همهٔ Candidateهای ممکن اثبات نشده است. گزارش: [ممیزی Ledger A002](../reports/BOOT003_A002_LEDGER_AUDIT_FA.md) و [بازبینی مسیرهای سورس](../reports/BOOT003_A002_LEDGER_SOURCE_REVIEW_FA.md).

## 6. هویت سورس‌ها

| سورس | Git Blob SHA-1 |
|---|---|
| Baseline C2 در main | 7e6e7ddaf6dd8ef976e53f611018815a4874dd60 |
| Ledger v2 در feature/w0-event-ledger-v2 | 0366568d082af3e4fa5854e8ddf9790c94be25c8 |

Git Blob SHA محاسبه‌شده از هر دو فایل محلی دقیقاً با شناسهٔ GitHub برابر بود.

## 7. SHA-256 فایل‌های اصلی آرشیوشده

| فایل | بایت | SHA-256 |
|---|---:|---|
| A_C2_baseline_complete.mq5 | 69231 | 64F0C690195405876D2B81BF14C39EF885EC69D8D86295D0B6ACC8BC10EAE15D |
| A_C2_baseline_complete.ex5 | 127900 | 7ADEDED61B14D97B5222B27264F5E075F4D9DB90E585AE2F1D61261527CB98F0 |
| Ledger v2 MQ5 | 86942 | 870BFC7C61DC566C075385CF28EA7D3C5D8C812A17B23CFDD7C17DF79156EA9E |
| Ledger v2 EX5 | 146328 | A88EE1D9C57577FD4D382CF9BEA8B91D0BB58B697409C6028112C654B73C7BE1 |
| A_C2.set | 6864 | FF8CFB53D19E58287B998B426E9A753A7C94CBA9F04F4399105CAAFD7F876839 |
| B_LEDGER_V2.set | 7006 | C71D4347745D183938FBA301AB3C601B05DD9F27E677CC1DAF90DE429B1E9D4E |
| A legacy CSV | 24900 | 599FE903F9552FE107C2957D2B3F62703F8F014049321CF9C332BB54F898B829 |
| B legacy CSV | 26286 | 78E466121BCC355423924C84B2D27065FFD1971FB45E935E5A3D485B1608C427 |
| A Tester log | 70196 | 39A384DD1F21537E5E8B6CC711126F973B0FA22FD0DD37C5B94575F18F5EA791 |
| B A002 evidence | 37346 | EBF310409105A17636840C78DF4760407371432487E5B9DE13B742EE5F4E3BEF |
| Comparator script | 13044 | 1FD072A8F408AE9EE7E1439194B57DA9D82DC5CAFF8969DD562BFF0F44897A03 |
| Comparator JSON | 3145 | 1454E22934DBF989940C9043E364F8AF9928E2416BF5D0F36CB40B8EC35A2A45 |

فایل BOOT003_SHA256_manifest.json نیز در پوشهٔ محلی پروژه ساخته شد (4728 بایت).

## 8. محدودیت‌ها و Gateهای باز

1. Hash باینری EX5 در لحظهٔ اجرای تاریخی ثبت نشده است. لاگ Tester اندازهٔ بارگذاری‌شدهٔ A را 127938 بایت و B/A002 را 146391 بایت نشان می‌دهد؛ اندازهٔ فایل‌های فعلی به‌ترتیب 127900 و 146328 بایت است. Hash فعلی، هویت دقیق EX5 بارگذاری‌شده در آن لحظه را اثبات نمی‌کند.
2. انتهای نشانگر History synchronization در دو لاگ یک روز تفاوت دارد؛ هرچند Tick History span و تعداد تیک/کندل تولیدشده برابرند.
3. Spread mode/value، Commission، Swap و Execution delay از شواهد موجود به‌طور مستقل تطبیق داده نشده‌اند.
4. فایل HTML هر دو اجرا آرشیو نشده است.
5. خروجی Compile نسخهٔ A به‌صورت متنی گزارش شده (0 errors و 0 warnings)، اما Compile log آرشیو نشده؛ Compile log متناظر B نیز در دسترس نیست.
6. ممیزی معنایی A002 انجام شده است؛ سه هشدار آن شامل emission دیرهنگام snapshot ارزیابی M5 نسبت به ORDER_OPENED، ترتیب SETUP_RESET/TRADE_CLOSED در دو مسیر callback، و خالی بودن جزئیات REJECT_LPSY_INVALIDATED است. دو مورد اول در بازبینی سورس به‌عنوان تفاوت ترتیب emission/callback مستند شدند؛ مورد سوم نقص telemetry قابل اصلاح است.

## 9. تصمیم

Gate مقایسهٔ رفتاری BOOT-003 برای همین Replay با وضعیت محدود PASS ثبت می‌شود: جریان Legacy برابر، ورودی‌های مشترک برابر و شرایط اصلی Tester هم‌تراز هستند. کل ممیزی BOOT-003 هنوز بسته نیست. پیش از تأیید داده برای آموزش W1/W2/W3، موارد باز بالا باید بررسی و مستند شوند.


## 10. ممیزی مستقل Event Ledger v2 و بازبینی سورس — 2026-11-05

فایل خام 28 ستونی A002 با نام `experiments/BOOT_003_A002_event_ledger_v2.csv` به مخزن اضافه شد. SHA-256 آن:

`77097b3adae7099f0b8199cb58b509f956ade2149ee2d721bf20832c3fd20ba9`

نتیجهٔ ممیزی: 127 ردیف، 28 ستون، 26 کنترل ساختاری/هویتی PASS، یک Candidate، یک Decision پذیرفته‌شده، یک Order، یک Entry Deal، یک Position و یک Trade Closed. ترتیب EventSequence پیوسته است و timestampها غیرکاهشی‌اند. وضعیت مستقل: **PASS WITH WARNINGS**.

سه یافته:
1. EV54 `M5_ENTRY_EVALUATION` بعد از EV53 `ORDER_OPENED` نوشته شده است. بازبینی سورس نشان داد snapshot ارزیابی در انتهای `ProcessEntryBar`، پس از اجرای `PlaceTrade`، ثبت می‌شود؛ جزئیات آن به کندل 18:50 اشاره دارد در حالی که timestamp ثبت 18:55 است. این تفاوت emission order است و به‌تنهایی خطای تصمیم معاملاتی را ثابت نمی‌کند.
2. EV56 `SETUP_RESET` پیش از EV57 `TRADE_CLOSED` در یک timestamp آمده است. سورس دو مسیر جدا را نشان می‌دهد: بررسی state در `OnTick/ProcessSignalBar` و ثبت Deal در `OnTradeTransaction`. ترتیب فعلی باید در قرارداد Ledger مستند شود؛ فعلاً منطق state تغییر نکند.
3. EV126 `REJECT_LPSY_INVALIDATED` بدون `ReasonCode` و `Details` است. در سورس، `LogReject` بدون payload تشخیصی فراخوانی می‌شود. اصلاح telemetry-only با افزودن close، threshold/level و ATR پیشنهاد می‌شود؛ شرط معاملاتی نباید تغییر کند.

گزارش‌ها و داده‌ها:
- [CSV خام A002](../experiments/BOOT_003_A002_event_ledger_v2.csv)
- [گزارش ممیزی فارسی](../reports/BOOT003_A002_LEDGER_AUDIT_FA.md)
- [گزارش ماشین‌خوان ممیزی](../experiments/BOOT003_A002_LEDGER_AUDIT.json)
- [بازبینی مسیرهای سورس](../reports/BOOT003_A002_LEDGER_SOURCE_REVIEW_FA.md)
- [Manifest هش‌های SHA-256](../experiments/BOOT003_SHA256_MANIFEST_20261105.json)

علت قیمت خروج 4698.78 در برابر SL مرجع 4712.14 (معادل 1336 پوینت adverse deviation) هنوز با تیک خام/History بروکر بررسی نشده است. هویت EX5 زمان اجرای تاریخی، HTML reports، compile logs و جزئیات Spread/Commission/Swap/Delay نیز Gateهای باز هستند. نتیجهٔ این Replay ادعای سودآوری نیست.


### 10.1 پیگیری اصلاح telemetry

برای افزودن جزئیات EV126 بدون تغییر منطق معاملاتی و بدون تغییر CSV مشترک Legacy، [Issue شمارهٔ 11 در GitHub](https://github.com/afshinsaberone-a11y/wyckoff/issues/11) ایجاد شد. این کار هنوز اجرا یا کامپایل نشده است؛ پذیرش آن منوط به حفظ برابری A/B و صفرشدن هشدار EV126 است.


### 10.2 اصلاح telemetry در Draft PR

اصلاح Details-only برای EV126 در [Draft PR شمارهٔ 13](https://github.com/afshinsaberone-a11y/wyckoff/pull/13) روی شاخهٔ `fix/boot003-lpsy-ledger-diagnostics-rebased` قرار دارد. PR قبلی شمارهٔ 12 به‌علت عقب‌ماندن شاخه بسته و با شاخه‌ای بر پایهٔ head فعلی جایگزین شد. این اصلاح هنوز در MetaEditor کامپایل یا در MT5 اجرا نشده است.
