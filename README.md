# Wyckoff W0 — XAUUSD / MetaTrader 5

پروژه پژوهشی ساخت و ارزیابی اکسپرت مبتنی بر توالی وایکوف برای XAUUSD در MT5.

> وضعیت: توسعه و اعتبارسنجی؛ نتایج ثبت‌شده تا این مرحله زیان‌ده‌اند. استفاده روی حساب واقعی تأیید نشده است.

## آرشیو گفتگو و پیشرفت
- [آرشیو یکپارچهٔ گفتگو، تصمیم‌ها، نسخه‌ها، تست‌ها و وضعیت پروژه تا 2026-11-04](docs/CHAT_AND_PROJECT_ARCHIVE_FA.md) — خلاصهٔ فنی مستند؛ نه رونوشت کلمه‌به‌کلمهٔ چت.

## مستندات
- [وضعیت پروژه](docs/PROJECT_STATUS_FA.md)
- [تاریخچه بک‌تست](docs/BACKTEST_HISTORY_FA.md)
- [فهرست فایل‌ها و انتقال](docs/FILE_REGISTER_FA.md)
- [قواعد توسعه و ممیزی](docs/DEVELOPMENT_RULES_FA.md)

## ساختار راهبرد
- زمینه H4 (اختیاری)، ساختار H1، ورود M5
- خرید: Accumulation/Range → Spring → Test → SOS → LPS → تأیید M5
- فروش: Distribution/Range → UTAD → Test → SOW → LPSY → تأیید M5

## آخرین ممیزی ساختار H1 — 2026-11-04

- [سورس تشخیصی چندسطحی H1STRUCT MultiAudit v1.084](src/Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT.mq5)
- [SET همراه MultiAudit با Lookback مبنا=5](sets/Wyckoff_C2_H1StructureMultiAudit_2024_2026.set)
- [راهنمای اجرای MultiAudit](docs/C2_H1STRUCT_MULTI_AUDIT_README_FA.md)
- [اعتبارسنجی ایستای سورس](docs/C2_H1STRUCT_MULTI_AUDIT_VALIDATION.txt)
- [تحلیل عمیق شکست‌های H1، Lookback و Pivotها](reports/20261104_H1STRUCT_MULTI_LOOKBACK_DEEP_REVIEW_FA.md)
- [گزارش اجرای H1STRUCT پایه](reports/20261104_H1STRUCT_AUDIT_RUN_ANALYSIS_FA.md)

برای مقایسهٔ کامل Lookback نیز SETهای [10 کندل](sets/Wyckoff_C2_H1STRUCT_SL10_2024_2026.set) و [20 کندل](sets/Wyckoff_C2_H1STRUCT_SL20_2024_2026.set) آماده‌اند. این SETها باید با Expert تشخیصی H1STRUCT اجرا شوند.

وضعیت MultiAudit: افزوده‌های تشخیصی و تطابق SET به‌صورت ایستا بررسی شده‌اند؛ هنوز در MetaEditor کامپایل و در Strategy Tester اجرا نشده‌اند. هیچ شرط معاملاتی C2 بر اساس Pivotها یا Creek/Ice تغییر نکرده است.

## ایمنی
هیچ نسخه‌ای در این مخزن به‌عنوان آماده معامله زنده معرفی نمی‌شود. سورس‌ها و نتایج باید به نسخه دقیق، تنظیمات و گزارش تست متناظر متصل باشند.
