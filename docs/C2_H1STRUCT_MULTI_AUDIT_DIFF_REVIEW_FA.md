# تغییرات v1.083 → v1.084

- نسخه و EA_Version تغییر یافته‌اند.
- یک تابع تشخیصی افزوده شده که روی کندل‌های H1 واجد معیار قدرت اجرا می‌شود.
- این تابع سطوح High/Low قبلی برای Lookbackهای 5، 10، 20 و 40 را ثبت می‌کند.
- سه Pivot اخیر 2-left/2-right، دامنهٔ ATR آن‌ها و عبور/عدم عبور کندل از کل ناحیهٔ سه Pivot ثبت می‌شود.
- فقط هنگام قرارداشتن state machine در ST_WAIT_STRENGTH، تعداد کندل‌های دریافت‌شده به اندازهٔ لازم برای محاسبات تشخیصی افزایش می‌یابد.
- هیچ شرط پذیرش SOS/SOW، Spring/UTAD، Test، LPS/LPSY، M5 breakout/retest/recovery، SL/TP، Risk، OrderSend یا Expiry تغییر نکرده است.
- Pivotها صرفاً candidate هستند؛ در کد به‌عنوان Creek/Ice قطعی یا فیلتر معامله استفاده نمی‌شوند.

این مقایسهٔ ایستای سورس است. Compile در MetaEditor و اجرای MT5 تأیید نشده‌اند.


## بازبینی مستقل تکمیلی — 2026-11-04

گزارش کامل LCS line diff و تحلیل نقطه‌ای تابع تشخیصی در [20261104_MULTIAUDIT_STATIC_CODE_REVIEW_FA.md](../reports/20261104_MULTIAUDIT_STATIC_CODE_REVIEW_FA.md) ثبت شد. جمع‌بندی: 117 خط افزوده و 4 خط metadata حذف؛ هیچ خط اجرایی پایه در مقایسه حذف نشده است. این بررسی ایستا است و جایگزین Compile/Strategy Tester نیست.
