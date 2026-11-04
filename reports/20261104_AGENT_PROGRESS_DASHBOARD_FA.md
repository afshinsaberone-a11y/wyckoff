# داشبورد پیشرفت واقعی ۹ مسیر کاری — Financial ML Core+

**تاریخ snapshot: 2026-11-04**  
**مخزن:** https://github.com/afshinsaberone-a11y/wyckoff  
**مبنای درصدها:** شواهد ثبت‌شده در Issue، Branch، Commit، فایل‌های خروجی و GitHub Actions؛ نه زمان سپری‌شده یا ادعای فعال‌بودن عامل خودمختار.

## خلاصه مدیریتی

- **میانگین ساده ۹ مسیر: 26.7٪**. این میانگین فقط شاخص مقایسه‌ای است؛ به‌دلیل تفاوت اندازه و وابستگی کارها، معادل درصد تکمیل کل پروژه نیست.
- **۳ مسیر W1/W2/W3** کد و تست مستقل ثبت کرده‌اند.
- **۶ مسیر AGENT_00 تا AGENT_04 و W0** هنوز Commit اختصاصی جلوتر از main ندارند؛ Branchهایشان شش Commit از main عقب‌اند.
- **۰ از ۵ اجرای CI مخصوص prototypeها کامل شده‌اند**؛ هر پنج Job در آخرین بررسی queued بوده‌اند. بنابراین تست موفق برای W1/W2/W3 ثبت نشده است.
- مدل‌های HMM/ML روی داده واقعی XAUUSD هنوز آموزش داده نشده‌اند؛ W3 عملیاتی نیز شروع نشده است.

## جدول درصد پیشرفت

| نقش | پیشرفت | وضعیت قابل مشاهده | مانع یا گام بعدی |
|---|---:|---|---|
| AGENT_00 Orchestrator | **30٪** | Issue/Branchها، برنامه Sprint، گزارش شروع و Manifest هماهنگی ثبت شده‌اند | گزارش تحویل‌های واقعی نقش‌ها، ثبت تصمیم‌ها و پیگیری مداوم؛ Branch اختصاصی هنوز Commit جلوتر از main ندارد |
| AGENT_01 Data Engineering | **10٪** | Issue و Branch ایجاد شده‌اند | Commit و artifact اختصاصی، inventory داده، pipeline و validator؛ M1/Tick خام در مخزن موجود نیست |
| AGENT_02 Execution/Backtest | **10٪** | Issue و Branch ایجاد شده‌اند | Commit اختصاصی، parser، دو Compile و چهار Run واقعی MT5؛ اجرای Tester در محیط کاربر لازم است |
| AGENT_03 Independent Audit | **10٪** | Issue و Branch ایجاد شده‌اند | گزارش مستقل با severity، شواهد، اختلاف‌ها و اثر Gate؛ هنوز artifact اختصاصی این مسیر ثبت نشده |
| AGENT_04 Governance | **10٪** | Issue و Branch ایجاد شده‌اند | Freeze قراردادها و آزمون‌های مستقل leakage/fold؛ artifact اختصاصی این مسیر هنوز Commit نشده |
| W0 Wyckoff/Ledger | **10٪** | Issue و Branch ایجاد شده‌اند | پیاده‌سازی MQL5 برای Event/Candidate Ledger v2، سپس Compile/Replay؛ مشخصات موجود به‌تنهایی پیاده‌سازی نیست |
| W1 HMM | **55٪** | Research note، forward-filter prototype و test file ثبت شده‌اند؛ Branch شش Commit جلوتر از merge-base است | CI هنوز queued؛ پس از تست سبز، audit، fit فقط پس از تأمین داده/گیت‌ها |
| W2 ML Scoring | **55٪** | Candidate validator، تست‌های point-in-time/purge/embargo و workflow ثبت شده‌اند؛ Branch هشت Commit جلوتر از merge-base است | CI هنوز queued؛ scorer و ارزیابی مدل واقعی/after-cost ساخته یا اجرا نشده‌اند |
| W3 Hybrid | **50٪** | قرارداد JSON، interface validator، تست‌ها و workflow ثبت شده‌اند؛ Branch پنج Commit جلوتر از merge-base است | CI هنوز queued؛ integration واقعی تا Freeze مستقل W1/W2 و Ledger متوقف است |

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

برای W1/W2/W3، تست‌فایل نوشته‌شده امتیاز دارد، اما تا زمانی که CI واقعاً اجرا و سبز نشود، امتیاز «تست موفق» صفر است. هیچ درصدی بابت HMM/ML training واقعی، OOS یا integration عملیاتی منظور نشده است.

## شواهد زنده Branchها

| Branch | Ahead نسبت به merge-base | Behind نسبت به main | تفسیر |
|---|---:|---:|---|
| AGENT_00 | 0 | 6 | Commit اختصاصی جدید ندارد |
| AGENT_01 | 0 | 6 | Commit اختصاصی جدید ندارد |
| AGENT_02 | 0 | 6 | Commit اختصاصی جدید ندارد |
| AGENT_03 | 0 | 6 | Commit اختصاصی جدید ندارد |
| AGENT_04 | 0 | 6 | Commit اختصاصی جدید ندارد |
| W0 | 0 | 6 | Commit اختصاصی جدید ندارد |
| W1 | 6 | 13 | کد و تست روی Branch مستقل؛ با main واگراست |
| W2 | 8 | 13 | کد و تست روی Branch مستقل؛ با main واگراست |
| W3 | 5 | 13 | قرارداد و validator روی Branch مستقل؛ با main واگراست |

**نکته:** Ahead/behind در Branchهای W1/W2/W3 به معنی آماده‌بودن برای Merge نیست؛ Branchها باید با تغییرات جدید main همگام شوند و تست‌ها/ممیزی تکمیل شوند.

## وضعیت CI مخصوص W1/W2/W3

| مسیر | Run ID | Job status | نتیجه |
|---|---:|---|---|
| W1 | 41864325081 | queued | هنوز اجرا نشده |
| W1 | 41864331424 | queued | هنوز اجرا نشده |
| W2 | 41864355912 | queued | هنوز اجرا نشده |
| W2 | 41864363747 | queued | هنوز اجرا نشده |
| W3 | 41864218329 | queued | هنوز اجرا نشده |

لینک‌ها:
- [W1 Run 41864325081](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41864325081)
- [W1 Run 41864331424](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41864331424)
- [W2 Run 41864355912](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41864355912)
- [W2 Run 41864363747](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41864363747)
- [W3 Run 41864218329](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41864218329)

## Gateهای پروژه که هنوز بسته نشده‌اند

1. **BOOT-001 Baseline:** تطبیق 67 ورودی SET بازسازی‌شده با Journal/SOURCE موفق است، اما EX5 تاریخی و hash آن موجود نیست؛ Freeze نهایی همچنان CONDITIONAL است.
2. **BOOT-002 MT5:** Run Card آماده است، ولی دو Compile و چهار Tester Run جدید A/B/C/D انجام نشده‌اند.
3. **BOOT-003 Ledger:** مهاجرت اولیه 346 Event در CI موفق بوده؛ اما Event/Candidate Ledger v2 در MQL5 هنوز پیاده‌سازی، Compile و Replay نشده است.
4. **Data readiness:** M1/Tick خام، Candidate ID مستقل، Feature snapshot و Outcome label واقعی کافی نیست.
5. **W1/W2:** فقط research و synthetic prototype مجاز است؛ fit روی XAUUSD واقعی BLOCKED است.
6. **W3:** integration عملیاتی BLOCKED تا Freeze مستقل W1/W2 و آماده‌شدن Ledger.

## اولویت اجرایی بعدی

1. رفع صف CI و گرفتن خروجی واقعی تست‌های W1/W2/W3؛ اصلاح خطاها پیش از هر ادعای PASS.
2. AGENT_01، AGENT_02، AGENT_03، AGENT_04 و W0 باید اولین Commit و artifact اختصاصی خود را در Branch مربوط ثبت کنند.
3. AGENT_03 پس از آماده‌شدن تست‌ها، ممیزی مستقل W1/W2/W3 را انجام دهد.
4. BOOT-002 و Event Ledger v2 از مسیر MT5 کاربر پیش بروند؛ نتیجه اجرا تا زمان دریافت HTML/Journal/CSV و Compile logs ثبت نمی‌شود.

## محدودیت معنای «Agent»

این ۹ مورد، **۹ مسیر کاری نقش‌محور در GitHub** هستند که با Issue و Branch ردیابی می‌شوند؛ ۹ پردازه Agent خودمختار و همیشه‌فعال deploy نشده‌اند. درصد بالا نیز درصد تکمیل artifact و تحویل است، نه ساعت کار یا وضعیت یک ربات در حال اجرا.
