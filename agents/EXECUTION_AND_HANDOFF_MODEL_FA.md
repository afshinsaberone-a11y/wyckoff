# مدل استقرار، اجرا و تحویل بین ایجنت‌ها

نسخه: 1.0-draft  
وضعیت: طرح عملیاتی؛ هیچ Agent runner یا محیط مستقل هنوز مستقر نشده است.

## 1. نقش منطقی در برابر Agent فعال

فایل‌های System Prompt تعریف می‌کنند هر نقش چه مسئولیتی دارد؛ اما به‌تنهایی یک عامل خودکار را مستقر نمی‌کنند. برای استقرار واقعی هر نقش به runner، محیط فایل، ابزارهای مجاز، مجوز GitHub، ثبت اجرا، کنترل هزینه و مسیر تأیید انسانی نیاز است.

پیشنهاد می‌شود در شروع از orchestrator مرکزی و jobهای محدود و قابل بازتولید استفاده شود. لازم نیست ۹ مدل مستقل اجرا شوند؛ جداسازی مسئولیت و مجوز از تعداد مدل‌ها مهم‌تر است.

## 2. جداسازی محیط و شاخه

الگوی شاخه:
agent/<agent-id>/<task-id>

مثال:
- agent/W0/BOOT-003-event-ledger
- agent/W1/EXP-W1-FOLD-01
- agent/AGENT_03/AUDIT-EXP-001

قواعد:
1. Baseline با tag یا commit مشخص و read-only نگهداری شود.
2. هر Agent در شاخه کاری خودش تغییر دهد.
3. هیچ Agent مستقیماً روی main commit نکند.
4. تحویل کد از طریق Pull Request با لینک آزمایش و چک‌لیست باشد.
5. Auditor دسترسی read-only به artifactهای مورد ممیزی داشته باشد.
6. Governance مسئول پذیرش پروتکل و تصمیم Gate باشد؛ merge نهایی با کنترل انسانی انجام شود.
7. داده خام immutable باشد؛ هر پاک‌سازی باید در لایه processed و با log انجام شود.

## 3. سطوح دسترسی پیشنهادی

| نقش | خواندن | نوشتن | ممنوع |
|---|---|---|---|
| AGENT_00 | همه manifestها و وضعیت‌ها | task/registry | تغییر کد استراتژی و تأیید ممیزی |
| W0 | داده و قرارداد | فقط شاخه W0 | تغییر main و استفاده از HMM/ML |
| W1 | W0 ledger و Train folds | artifacts مدل W1 | Test/OOS fit و تغییر W0 |
| W2 | Candidate/Feature/Label مجاز | artifacts مدل W2 | حذف Candidate و تغییر execution |
| W3 | artifacts Freezeشده W1/W2 | artifacts ترکیبی | آموزش مجدد روی OOS |
| AGENT_01 | raw data | processed data و ledger | بازنویسی raw data |
| AGENT_02 | داده، کد و config | گزارش اجرا و replay tests | تغییر قواعد سیگنال |
| AGENT_03 | همه شواهد | فقط Audit Report | تغییر artifact تحت ممیزی |
| AGENT_04 | همه manifestها | protocol/gate/change log | دست‌کاری نتایج خام |

هیچ نقش پژوهشی به credentials، API token حساب معاملاتی، یا اجازه ارسال سفارش واقعی نیاز ندارد.

## 4. چرخه یک Job

1. AGENT_00 یک Task با ورودی، هدف، مجوز و معیار پذیرش مشخص صادر می‌کند.
2. AGENT_04 تأیید می‌کند Task با پروتکل Freezeشده سازگار است.
3. Agent مسئول در شاخه و محیط مجزا اجرا می‌کند.
4. خروجی‌ها با manifest و checksum ذخیره می‌شوند.
5. Agent تحویل‌دهنده نتیجه را به شکل COMPLETE، BLOCKED یا FAILED گزارش می‌کند.
6. AGENT_03 در موارد لازم خروجی را مستقل ممیزی می‌کند.
7. AGENT_04 وضعیت Gate را ثبت می‌کند؛ merge یا عبور حساس با تأیید انسانی است.

## 5. قرارداد تحویل

هر تحویل باید حداقل شامل این موارد باشد:
- task_id، agent_id، experiment_id
- status، objective، summary
- inputs و نسخه/هش هر ورودی
- outputs و مسیر artifactها
- code_commit، data_hash، config_hash، model_hash
- checks_run و نتیجه هر تست
- limitations، open_findings
- next_action، requested_gate

ساختار جزئی در [Agent Handoff Schema](../contracts/AGENT_HANDOFF_SCHEMA_FA.md) آمده است.

## 6. قابلیت بازتولید و امنیت

- seed، نسخه کتابخانه‌ها، محیط اجرا و timestamp ذخیره شوند.
- فایل خام، log و گزارش نهایی با checksum پیوند بخورند.
- secrets در GitHub، log یا Prompt قرار نگیرند.
- داده و خروجی‌ها با حداقل دسترسی و سیاست نگهداری مناسب ذخیره شوند.
- اجرای Tester یا آموزش مدل بدون manifest معتبر «نتیجه رسمی» محسوب نشود.
- اگر runner یا ابزار موردنیاز موجود نیست، Agent باید BLOCKED بدهد و دلیل را ثبت کند؛ نباید نتیجه را شبیه‌سازی یا جعل کند.
