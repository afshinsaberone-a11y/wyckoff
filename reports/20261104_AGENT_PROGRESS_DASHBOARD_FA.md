# داشبورد پیشرفت واقعی ۹ مسیر کاری — Financial ML Core+

**تاریخ snapshot: 2026-11-04**  
**Commit مبنای مقایسه Branchها:** `fb1afdf45d62dc8a155792a4954922aa710a4411`  
**مخزن:** https://github.com/afshinsaberone-a11y/wyckoff  
**مبنای درصدها:** شواهد ثبت‌شده در Issue، Branch، Commit، فایل‌های خروجی و GitHub Actions؛ نه زمان سپری‌شده یا ادعای فعال‌بودن عامل خودمختار.

## خلاصه مدیریتی

- **میانگین ساده ۹ مسیر: 33.3٪**. این میانگین فقط شاخص مقایسه‌ای است؛ به‌دلیل تفاوت اندازه و وابستگی کارها، معادل درصد تکمیل کل پروژه نیست.
- **۳ مسیر W1/W2/W3** کد و تست مستقل ثبت کرده‌اند.
- **۵ مسیر AGENT_00 تا AGENT_02 و AGENT_04 و W0** هنوز Commit اختصاصی جلوتر از main ندارند. AGENT_03 اکنون گزارش مستقل خود را در Branch اختصاصی Commit کرده است.
- **۵ از ۵ اجرای CI مخصوص prototypeها با موفقیت پایان یافته‌اند**؛ ۲۱ تست‌کیس متمایز (۳۶ اجرای تست‌کیس با احتساب تکرارها) در logها PASS هستند.
- مدل‌های HMM/ML روی داده واقعی XAUUSD هنوز آموزش داده نشده‌اند؛ W3 عملیاتی نیز شروع نشده است.

## جدول درصد پیشرفت

| نقش | پیشرفت | وضعیت قابل مشاهده | مانع یا گام بعدی |
|---|---:|---|---|
| AGENT_00 Orchestrator | **30٪** | Issue/Branchها، برنامه Sprint، گزارش شروع و Manifest هماهنگی ثبت شده‌اند | گزارش تحویل‌های واقعی نقش‌ها، ثبت تصمیم‌ها و پیگیری مداوم؛ Branch اختصاصی هنوز Commit جلوتر از main ندارد |
| AGENT_01 Data Engineering | **10٪** | Issue و Branch ایجاد شده‌اند | Commit و artifact اختصاصی، inventory داده، pipeline و validator؛ M1/Tick خام در مخزن موجود نیست |
| AGENT_02 Execution/Backtest | **10٪** | Issue و Branch ایجاد شده‌اند | Commit اختصاصی، parser، دو Compile و چهار Run واقعی MT5؛ اجرای Tester در محیط کاربر لازم است |
| AGENT_03 Independent Audit | **25٪** | گزارش ممیزی مستقل W1/W2/W3 در Branch اختصاصی ثبت شده؛ CI و محدودیت‌های هر prototype با log تأیید شده‌اند | پیگیری اصلاح یافته‌های W2/W3، همگام‌سازی Branch و ممیزی نسخه اصلاحی |
| AGENT_04 Governance | **10٪** | Issue و Branch ایجاد شده‌اند | Freeze قراردادها و آزمون‌های مستقل leakage/fold؛ artifact اختصاصی این مسیر هنوز Commit نشده |
| W0 Wyckoff/Ledger | **10٪** | Issue و Branch ایجاد شده‌اند | پیاده‌سازی MQL5 برای Event/Candidate Ledger v2، سپس Compile/Replay؛ مشخصات موجود به‌تنهایی پیاده‌سازی نیست |
| W1 HMM | **70٪** | forward-filter prototype؛ دو CI موفق، هرکدام ۸ تست (۱۶ اجرا) | fold-local fit harness، آزمون‌های property-based و ممیزی مستقل؛ fit واقعی همچنان BLOCKED |
| W2 ML Scoring | **70٪** | Candidate validator؛ دو CI موفق، هرکدام ۷ تست (۱۴ اجرا) | strict type validation، Fold/feature-window controls، candidate dataset و scorer؛ آموزش واقعی BLOCKED |
| W3 Hybrid | **65٪** | JSON contract و fail-closed validator؛ یک CI موفق با ۶ تست | رفع mismatch بین schema و Python validator؛ integration عملیاتی تا Freeze W1/W2 و Ledger متوقف است |

## روش محاسبه درصد

درصد، **برآورد تکمیل تحویل‌های هر Issue** است و با وزن‌دهی به این مراحل محاسبه می‌شود:

| مرحله | وزن |
|---|---:|
| تعریف محدوده، Issue و Branch | 10٪ |
| مطالعه و طراحی/Research note | 15٪ |
| artifact اجرایی یا پیاده‌سازی | 30٪ |
| نوشتن تست‌ها | 10٪ |
| اجرای موفق و قابل‌تکرار تست‌ها | 15٪ |
| ممیزی مستقل و تحویل | 10٪ |
| ادغام، Freeze و پذیرش نهایی | 10٪ |

برای شش مسیر بدون Commit اختصاصی، صرفاً ثبت Issue/Branch به‌عنوان شروع کار منظور شده است. اسناد و کارهای قبلی موجود در main—مانند مهاجرت 346 Event، Run Card و گزارش‌های Baseline—به‌اشتباه به‌عنوان خروجی تازه Agentها حساب نشده‌اند؛ آن‌ها شواهد و پیش‌نیازهای پروژه‌اند. برای AGENT_00، مستندات هماهنگی Sprint و Manifest نیز به‌عنوان خروجی شروع هماهنگی لحاظ شده‌اند.

برای W1/W2/W3، تست‌های نوشته‌شده و اجراهای موفق CI در درصد لحاظ شده‌اند؛ اما هیچ امتیازی بابت fit روی دادهٔ واقعی XAUUSD، OOS یا integration عملیاتی منظور نشده است. درصد AGENT_03 نیز صرفاً تحویل گزارش ممیزی اولیه را منعکس می‌کند، نه بسته‌شدن همهٔ یافته‌ها.

## شواهد زنده Branchها

| Branch | Ahead نسبت به merge-base | Behind نسبت به main | تفسیر |
|---|---:|---:|---|
| AGENT_00 | 0 | 10 | بدون Commit اختصاصی؛ هماهنگی در main مستند است |
| AGENT_01 | 0 | 10 | بدون Commit اختصاصی؛ داده خام و pipeline باقی است |
| AGENT_02 | 0 | 10 | بدون Commit اختصاصی؛ نیازمند Compile/Tester واقعی |
| AGENT_03 | 1 | 10 | گزارش ممیزی prototypeها Commit شده؛ یافته‌ها نیازمند پیگیری |
| AGENT_04 | 0 | 10 | بدون Commit اختصاصی؛ contract/fold governance باقی است |
| W0 | 0 | 10 | بدون Commit اختصاصی؛ Ledger v2 MQL5 هنوز پیاده‌سازی نشده |
| W1 | 6 | 17 | کد و تست مستقل؛ دو CI موفق؛ Branch با main واگراست |
| W2 | 8 | 17 | validator و تست مستقل؛ دو CI موفق؛ Branch با main واگراست |
| W3 | 5 | 17 | contract و validator مستقل؛ CI موفق؛ Branch با main واگراست |

**نکته:** Ahead/behind در Branchهای W1/W2/W3 به معنی آماده‌بودن برای Merge نیست؛ Branchها باید با تغییرات جدید main همگام شوند و تست‌ها/ممیزی تکمیل شوند.

## وضعیت CI مخصوص W1/W2/W3

<badge>۵/۵ SUCCESS</badge> — ۲۱ تست‌کیس متمایز، ۳۶ اجرای تست‌کیس شامل تکرار اجرای W1 و W2.

| مسیر | Run ID | Job status | نتیجه |
|---|---:|---|---|
| W1 | 41864325081 | completed | SUCCESS — ۸ تست |
| W1 | 41864331424 | completed | SUCCESS — ۸ تست |
| W2 | 41864355912 | completed | SUCCESS — ۷ تست |
| W2 | 41864363747 | completed | SUCCESS — ۷ تست |
| W3 | 41864218329 | completed | SUCCESS — ۶ تست |

لینک‌ها:
- [W1 Run 41864325081](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41864325081)
- [W1 Run 41864331424](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41864331424)
- [W2 Run 41864355912](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41864355912)
- [W2 Run 41864363747](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41864363747)
- [W3 Run 41864218329](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41864218329)

## گزارش ممیزی مستقل

[گزارش AGENT_03 روی Branch ممیزی](https://github.com/afshinsaberone-a11y/wyckoff/blob/agent/03-independent-audit/reports/20261104_W1_W2_W3_PROTOTYPE_AUDIT_FA.md) — نتیجه CONDITIONAL PASS برای prototypeهای synthetic؛ mismatch قرارداد W3 و نبود type validation سخت‌گیرانه در W2 از یافته‌های اصلی‌اند.

## Gateهای پروژه که هنوز بسته نشده‌اند

1. **BOOT-001 Baseline:** تطبیق 67 ورودی SET بازسازی‌شده با Journal/SOURCE موفق است، اما EX5 تاریخی و hash آن موجود نیست؛ Freeze نهایی همچنان CONDITIONAL است.
2. **BOOT-002 MT5:** Run Card آماده است، ولی دو Compile و چهار Tester Run جدید A/B/C/D انجام نشده‌اند.
3. **BOOT-003 Ledger:** مهاجرت اولیه 346 Event در CI موفق بوده؛ اما Event/Candidate Ledger v2 در MQL5 هنوز پیاده‌سازی، Compile و Replay نشده است.
4. **Data readiness:** M1/Tick خام، Candidate ID مستقل، Feature snapshot و Outcome label واقعی کافی نیست.
5. **W1/W2:** فقط research و synthetic prototype مجاز است؛ fit روی XAUUSD واقعی BLOCKED است.
6. **W3:** integration عملیاتی BLOCKED تا Freeze مستقل W1/W2 و آماده‌شدن Ledger.

## اولویت اجرایی بعدی

1. پیگیری یافته‌های ممیزی W1/W2/W3 و رفع type validation در W2 و schema parity در W3؛ سپس CI مجدد.
2. AGENT_01، AGENT_02، AGENT_04 و W0 باید اولین Commit و artifact اختصاصی خود را در Branch مربوط ثبت کنند؛ AGENT_03 گزارش اولیه را تحویل داده است.
3. پس از اصلاح W2/W3، AGENT_03 ممیزی مجدد انجام دهد و سپس Branchها را برای همگام‌سازی/PR آماده کند.
4. BOOT-002 و Event Ledger v2 از مسیر MT5 کاربر پیش بروند؛ نتیجه اجرا تا زمان دریافت HTML/Journal/CSV و Compile logs ثبت نمی‌شود.

## محدودیت معنای «Agent»

این ۹ مورد، **۹ مسیر کاری نقش‌محور در GitHub** هستند که با Issue و Branch ردیابی می‌شوند؛ ۹ پردازه Agent خودمختار و همیشه‌فعال deploy نشده‌اند. درصد بالا نیز درصد تکمیل artifact و تحویل است، نه ساعت کار یا وضعیت یک ربات در حال اجرا.
