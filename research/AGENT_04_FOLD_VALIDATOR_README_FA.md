# AGENT_04 Fold Manifest Validator — راهنمای اجرا

این prototype قرارداد زمانی Fold را قبل از ساخت Dataset یا Fit کنترل می‌کند.

## اجرا

```bash
python -m unittest discover -s research -p "test_fold_manifest_validator.py" -v
```

## ورودی ضروری

یک manifest باید شناسه Fold، بازه‌های sequence برای Train/Validation/Test، افق label، قاعده purge، embargo، سیاست گروه‌بندی و scope عملیات fit/tuning را داشته باشد.

## قواعد Fail-Closed

- sequenceها باید integer غیرمنفی باشند؛ bool پذیرفته نیست.
- هر window باید start <= end داشته باشد.
- Train باید کامل پیش از Validation و Validation کامل پیش از Test باشد.
- label horizon حداقل یک bar است.
- purge بر اساس overlap واقعی label interval انجام می‌شود، نه صرفاً gap ثابت.
- scaler و model فقط در Train fit می‌شوند.
- threshold فقط در Validation انتخاب می‌شود.
- group policy باید صریح و غیرخالی باشد.

## محدودیت

این کد **Fold را تولید نمی‌کند**، Candidateها را نمی‌خواند، overlap واقعی labelها را حذف نمی‌کند و CPCV کامل نیست. این‌ها باید در مرحلهٔ dataset split و با ابزار candidate-level مثل W2 اعمال و ممیزی شوند. این تست‌ها روی manifest مصنوعی‌اند و هیچ مدل یا نتیجهٔ معاملاتی XAUUSD را آموزش/تأیید نمی‌کنند.
