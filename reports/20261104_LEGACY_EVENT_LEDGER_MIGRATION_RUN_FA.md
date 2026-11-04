# گزارش اجرای مهاجرت Legacy Event Ledger — BOOT-003

تاریخ: 2026-11-04  
وضعیت: **PASS برای مهاجرت اولیه Event Log؛ BOOT-003 کامل نیست.**

## 1. اجرای تأییدشده

- GitHub Actions Run: [41859743204](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41859743204)
- Commit: `1efbb979e031898521aab9ccab799f1fc143fa71`
- Job: `static-preflight`
- نتیجه: success
- Preflight: 27 PASS / 0 FAIL
- Unit tests: 5 passed / 0 failed

## 2. ورودی و خروجی

فایل منبع:
`events/Wyckoff_W0_events_v1_08_C2_SB050_T030_TIMING_B12_R12_RC12.csv`

- Git blob SHA: `49eeb12ec611bc0ac5df04a8d7c0aa4f3454b01a`
- EA_Version: `1.08-C2-TIMING-SB050-T030`
- ردیف منبع: 346
- ردیف normalized: 346
- گروه‌های Range مبتنی بر شمارنده legacy: 65

خروجی CSV:
- نام: `events_normalized.csv`
- SHA-256: `5e1d95e2e1174e7af81771a7e506675d4a0221576011de530fc748ddc9860f7e`

## 3. کنترل ضدجعل Candidate و Label

مهاجر به‌صورت عمدی این موارد را ایجاد نکرد:
- candidate_id: صفر
- cycle_id: صفر
- attempt_id: صفر
- decision_id: صفر
- trade_id: صفر
- Feature Snapshot: صفر
- Label Outcome: صفر
- timestamp UTC ساخته‌شده: صفر

دلیل: CSV قدیمی فقط SetupID/Range context و زمان خام ServerTime را ثبت می‌کند. سورس C2، شمارنده g_setupCounter را هنگام ساخت Range افزایش می‌دهد؛ پس SetupID به legacy_setup_id نگاشت شده و یک range_id مهاجرتی deterministic از آن ساخته شده است. این Range ID جای candidate_id را نمی‌گیرد.

زمان خام ServerTime نگهداری شده است. timezone/offset و زمان کندل منبع در CSV وجود ندارند؛ بنابراین تبدیل UTC، available_at یا decision_time انجام نشده است.

## 4. Artifact قابل دریافت

GitHub Actions Artifact:
- ID: `13337654909`
- نام: `legacy-event-ledger-1efbb979e031898521aab9ccab799f1fc143fa71`
- حجم ZIP: 26,858 bytes
- SHA-256: `00482187a859e1284e9fc0dbacd2d676d017538129a708082d1846fe9a50e7c0`
- تاریخ انقضا: 2026-12-04 15:37:58 UTC

برای دریافت، صفحه [Run 41859743204](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41859743204) را باز کنید و در بخش Artifacts فایل بالا را دریافت کنید.

## 5. تصمیم BOOT-003

- مهاجرت اولیه Legacy Event CSV: **PASS**.
- تعداد ردیف‌ها و گروه‌های Range: **تأیید شد**.
- Candidate/Cycle/Attempt identity: **هنوز ساخته نشده**.
- Feature Snapshot/Label Outcome: **هنوز موجود نیست**.
- instrumentation جدید MQL5: **انجام نشده**.

پس فقط گام نخست BOOT-003 انجام شده است. برای کامل‌شدن آن، W0 و AGENT_01 باید در یک نسخه instrumentation جداگانه، range_id/cycle_id/attempt_id/candidate_id و زمان‌های source_bar/available_at/decision_time را ثبت کنند؛ سپس Replay و Auditor باید نگاشت‌ها را بررسی کنند. تا آن زمان W1/W2/W3 مجاز به آموزش رسمی نیستند.
