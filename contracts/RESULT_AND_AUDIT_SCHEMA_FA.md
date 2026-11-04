# قرارداد داده — Result و Audit

نسخه schema: 1.0-draft.

## Result manifest
برای هر آزمایش و Fold این شاخص‌ها را ثبت کن:
- net_profit_after_costs
- gross_profit، gross_loss و profit_factor
- max_balance_drawdown و max_equity_drawdown به مقدار و درصد
- expectancy_per_trade و realized_R
- trade_count، win_count، loss_count
- exposure و average_holding_time
- spread، commission، swap، slippage و gap attribution
- confidence intervals و روش محاسبه آن‌ها
- PR-AUC، Brier و calibration برای مدل‌های classification، در صورت کاربرد

مقادیر نامعتبر، تعریف‌نشده یا دارای نمونه ناکافی باید صریحاً `NA/INSUFFICIENT_SAMPLE` ثبت شوند؛ صفر جایگزین مقدار نامعلوم نشود.

## Trade record
حداقل: trade_id، setup_id، order_id، deal_id، side، volume، intended_entry، fill_entry، SL، TP، exit_time، exit_price، gross_PnL، commission، swap، slippage_estimate، net_PnL، realized_R، execution_reason، data_quality_flags.

## Audit finding
| فیلد | توضیح |
|---|---|
| finding_id | شناسه |
| severity | CRITICAL/HIGH/MEDIUM/LOW |
| category | Leakage/Data/Execution/Code/Stats/Governance |
| experiment_id | آزمایش متاثر |
| evidence_ref | فایل/خط/رویداد |
| reproduction_steps | روش بازتولید |
| impact | اثر بر نتیجه |
| remediation | اصلاح پیشنهادی |
| status | OPEN/RESOLVED/ACCEPTED_RISK |

## Audit verdict
- PASS: شواهد و کنترل‌های ضروری قابل قبول‌اند.
- CONDITIONAL: نقص و اقدام لازم مشخص است؛ Gate مشروط است.
- REJECT: نتیجه فعلی قابل اتکا نیست.

## قواعد تفسیر
- یک معامله برای نتیجه‌گیری درباره edge، PF یا ثبات کافی نیست.
- Confidence interval با روش وابسته به زمان/خوشه setup گزارش شود؛ bootstrap تصادفی ساده روی معاملات وابسته می‌تواند گمراه‌کننده باشد.
- Net profit باید بعد از همه هزینه‌های قابل اندازه‌گیری باشد.
- نتیجه بهتر در یک دوره واحد، اثبات برتری پایدار نیست.
- هر جدول مقایسه باید تعداد نمونه، Foldها، محدودیت داده و وضعیت Audit را نشان دهد.
