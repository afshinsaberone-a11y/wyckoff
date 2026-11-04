# گزارش تأیید GitHub Actions — Financial ML Core+ Preflight

تاریخ: 2026-11-04  
Workflow: `.github/workflows/financial-ml-preflight.yml`  
Job: `static-preflight`  
نتیجه: **دو اجرای متوالی SUCCESS**

## 1. اجراهای تأییدشده

| Run ID | Commit بررسی‌شده | نتیجه | لینک |
|---:|---|---|---|
| 41856290720 | `ec3f92cb94737f63f73c9276827b5f5dac934aaf` | SUCCESS | [Run 1](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41856290720) |
| 41856507674 | `3e2a6138131ef08531ea743378906a31ef35232c` | SUCCESS | [Run 2](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41856507674) |

برای هر دو اجرا:
- workflow status: completed
- job conclusion: success
- checkout: success
- Python setup: success
- static preflight command: success

## 2. کنترل‌هایی که Validator انجام می‌دهد

- وجود سورس H1STRUCT v1.083 و MultiAudit v1.084.
- تطبیق `#property version=1.084`.
- تطبیق `EA_VERSION=1.08-C2-H1STRUCT-ML-AUDIT-SB050-T030`.
- حفظ همه خطوط غیرmetadata سورس مبنا در MultiAudit و ترتیب آن‌ها.
- نبود فراخوانی ارسال/بازکردن پوزیشن داخل تابع تشخیصی.
- وجود هر دو رویداد `SOS_STRENGTH_BAR_AUDIT` و `SOW_STRENGTH_BAR_AUDIT`.
- یک فراخوانی تابع Audit برای شاخه BUY و یک فراخوانی برای SELL.
- وجود 67 ورودی و تطابق با 67 کلید هر SET.
- Lookbackهای 5/10/20.
- اختلاف مجاز فقط `InpStrengthSwingLookback` و `InpCSVFileName`.
- معتبر بودن JSON manifest و عدم پیش‌ادعای Run موفق.
- تطابق نام Expert و EA_VERSION در Run Card.

## 3. محدوده اعتبار نتیجه

این دو SUCCESS فقط به معنی عبور کنترل‌های ایستای repository است. این Workflow:
- MQL5 را در MetaEditor کامپایل نمی‌کند.
- EX5 را نمی‌سازد یا امضای binary را تأیید نمی‌کند.
- MT5 Strategy Tester را اجرا نمی‌کند.
- کیفیت real ticks، spread، slippage یا fill را تأیید نمی‌کند.
- سودآوری یا وجود edge معاملاتی را اثبات نمی‌کند.

## 4. اثر روی Gate پروژه

- Static Preflight: **PASS**
- BOOT-002 Compile: **OPEN / NOT RUN**
- BOOT-002 MT5 Runs (5/10/20): **OPEN / NOT RUN**
- W1/W2/W3 training: **BLOCKED**
- Forward Demo / Live: **NOT APPROVED**

Run Manifestها و گزارش‌ها باید با Commit و فایل‌های خام همان اجرا تطبیق داده شوند. هیچ عدد یا هش مفقودی نباید از روی نام فایل حدس زده شود.


## تکمیل Preflight پس از ارتقای BOOT-002 به چهار Run

نسخه Validator و Run Card گسترش یافت تا طراحی چهار Run، بازه مشترک پیش از Run A و اثر فعال Lookback روی SOS/SOW بررسی شود. دو اجرای متوالی موفق:
- Run 41858805308، Commit `021089b2378170da7cfc2bf1e841dd2eb613cc9c`: 27 PASS / 0 FAIL.
- Run 41858859791، Commit `29ca36b3ed1b0e8d8efb7d94d53e504a31d9fecf`: 27 PASS / 0 FAIL.

[Manifest دو اجرا](../experiments/BOOT_002_STATIC_PREFLIGHT_RUN_003.json).

این نتایج صرفاً Static Repository Validation هستند. BOOT-002 هنوز به دو MetaEditor Compile و چهار MT5 Strategy Tester Run نیاز دارد.
