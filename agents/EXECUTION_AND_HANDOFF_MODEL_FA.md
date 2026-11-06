# مدل ساده استقرار و تحویل نقش‌های Wyckoff

**نسخه:** 2.0 — 2026-11-06  
**وضعیت:** طرح استقرار؛ هیچ runner مستقل و سرویس خودمختار دائمی هنوز مستقر نشده است.  
**نقشه اجرایی:** [STREAMLINED_AGENT_ROADMAP_FA.md](../docs/STREAMLINED_AGENT_ROADMAP_FA.md)

> این سند جایگزین طرح ۹ نقش/AGENT_04 جداگانه است. نسخه قبلی فقط در تاریخچه Git حفظ می‌شود.

## 1. ساختار فعال

شش نقش Agent تعریف شده‌اند: AGENT_00، AGENT_01، AGENT_02، AGENT_03، W1 و W2. W0 ربات پایه ثابت است و Agent هوش مصنوعی محسوب نمی‌شود. W3 تا عبور W1/W2 از ارزیابی مستقل خارج از نمونه معلق است. وظایف AGENT_04 در AGENT_03 ادغام شده‌اند.

این نقش‌ها به معنی شش مدل یا شش پردازه مستقل نیستند؛ می‌توانند با یک مدل پایه و prompt/tool permissions تفکیک‌شده اجرا شوند. جداسازی مجوز و artifact مهم‌تر از تعداد مدل‌هاست.

## 2. مسیر کار

1. AGENT_00 یک Issue با هدف، ورودی، مالک، معیار پذیرش و stop condition تعیین می‌کند.
2. Agent مسئول روی Branch محدود کار می‌کند و فقط artifactهای لازم را تولید می‌کند.
3. AGENT_02 در موارد مربوط به اجرا، Source/EX5/SET/Journal و هزینه‌ها را تطبیق می‌دهد.
4. AGENT_03 خروجی و Gate داده/Label/Fold را مستقلاً ممیزی می‌کند.
5. تصمیم Gate و merge حساس با کنترل انسانی انجام می‌شود.

**قاعده اصلی:** در هر زمان فقط یک اولویت اجرایی اصلی فعال است. W1/W2 می‌توانند پس از آماده‌شدن Dataset در مرحله مدل‌سازی موازی شوند.

## 3. حدود دسترسی

| نقش | مجوز اصلی | ممنوع |
|---|---|---|
| AGENT_00 | هماهنگی Issue/manifest | تغییر W0 یا تأیید ممیزی |
| AGENT_01 | داده خام read-only، processed data و Ledger | بازنویسی raw یا جعل Candidate/Label |
| AGENT_02 | فایل‌های اجرا و هزینه‌ها؛ گزارش/Replay | تغییر قواعد سیگنال |
| AGENT_03 | read-only شواهد و صدور Audit/Gate | تأیید کدی که خودش نوشته بدون ممیزی مستقل |
| W1 | Train folds و artifact HMM | fit روی Validation/Test/OOS |
| W2 | Candidate/Feature/Label مجاز و artifact ML | حذف Candidate یا fit روی Test/OOS |
| W0 | فقط Baseline ثابت و branch مجاز | تغییر main، ریسک یا سفارش زنده |

هیچ نقش به اعتبارنامه حساب، کلید خصوصی یا دسترسی ارسال سفارش واقعی نیاز ندارد.

## 4. تحویل و بازتولید

هر تحویل باید شامل این موارد باشد:
- issue_id / task_id و agent_id
- status: COMPLETE / BLOCKED / FAILED / WAITING
- branch و commit SHA
- ورودی‌ها، SET/config/data hashes
- artifact links و checksum
- تست‌های واقعی اجراشده و نتیجه
- limitations، UNKNOWNها و next action

اگر MT5 یا داده خام در دسترس نیست، Agent باید BLOCKED ثبت کند؛ نه اینکه اجرای انجام‌نشده را PASS اعلام کند.

## 5. امنیت و کنترل انسانی

- secrets در GitHub، log یا prompt ذخیره نشوند.
- raw data immutable بماند؛ هر تبدیل در لایه processed با manifest انجام شود.
- بدون manifest معتبر، Tester یا model result رسمی محسوب نشود.
- هیچ Agent مجاز به معامله زنده، تغییر بی‌اجازه ریسک یا override کردن کنترل‌های W0 نیست.
