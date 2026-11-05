# BOOT-003 — زمینهٔ زمانی اجرای سفارش و بررسی لغزش SL (۵ نوامبر ۲۰۲۶)

**وضعیت:** `TIMESTAMP_REVIEW_REQUIRED`  
**منبع تکمیلی:** مخزن `afshinsaberone-a11y/grok-ai-trader`  
**نماد:** XAUUSD  
**نمونه:** 199 سفارش بازار تطبیق‌یافته

## 1. خروجی Timing Audit

گزارش aggregate ارائه‌شده از PowerShell:

| شاخص | مقدار |
|---|---:|
| سفارش بازار مشاهده‌شده | 199 |
| سفارش تطبیق‌یافته | 199 |
| زمان Setup گمشده | 0 |
| مرجع Quote گمشده | 0 |
| Deal سازگار گمشده | 0 |
| زمان اجرای Deal گمشده | 0 |
| Deal قبل از Setup | 0 |
| Deal در همان میلی‌ثانیه Setup | 2 |
| Deal بعد از Setup | 197 |
| Deal قبل از Order Done | 0 |
| Deal در/بعد از Order Done | 199 |
| VWAP برابر Quote مرجع | 199 |
| VWAP متفاوت از Quote مرجع | 0 |

## 2. تفکیک عمر Quote از Setup-to-Fill

| سنجه | میانه | P95 | بیشینه |
|---|---:|---:|---:|
| عمر Quote در زمان Setup | 165 ms | 443.9 ms | 777 ms |
| Setup تا اولین Fill | 1 ms | 2 ms | 3 ms |
| Quote مرجع تا اولین Fill | 166 ms | 444.8 ms | 779 ms |

بنابراین در این نمونه، فاصلهٔ Quote-to-Fill عمدتاً با عمر Quote پیش از Setup توضیح داده می‌شود؛ زمان ثبت‌شده از Setup تا اولین Fill کوتاه است. این تفکیک، latency خالص شبکه یا broker را اندازه نمی‌گیرد.

از 199 سفارش، 197 مورد (98.995%) بعد از زمان Setup و 2 مورد (1.005%) در همان میلی‌ثانیه ثبت شده‌اند. هیچ Deal پیش از زمان Setup یا پیش از Order Done مشاهده نشده است.

## 3. قیمت مرجع

گزارش ارائه‌شده می‌گوید هر 199 VWAP دقیقاً با قیمت مرجع برابر بوده و deviation برابر صفر پوینت است.

Helper موجود در مخزن منبع، آخرین Quote معتبر دوطرفه در یا پیش از زمان Setup را انتخاب می‌کند؛ برای BUY از ASK و برای SELL از BID استفاده می‌کند. منبع و روش:
- [Quote capture helper](https://github.com/afshinsaberone-a11y/grok-ai-trader/blob/main/tools/mt5_xauusd_slippage_history_probe.py)
- Git blob SHA-1: `ed8dc303fe7d1d6c2e242c46b08989c8bd595df7`

با این حال، صفر بودن deviation در تمام 199 سفارش یک نتیجهٔ بسیار تمیز است و باید با نمونهٔ مستقل کوچک، تعداد جداگانه BUY/SELL، precision قیمت و حد سنی Quote دوباره کنترل شود. خروجی حاضر aggregate است و قیمت‌های خام یا ticketها را در اختیار این ممیزی قرار نمی‌دهد.

## 4. ارتباط با رخداد A002

در ممیزی Ledger مربوط به RunID=`WM20261104A002`، معاملهٔ نمونه با:
- SL مرجع: 4712.14
- قیمت خروج: 4698.78
- اختلاف adverse: 13.36 واحد قیمت یا 1,336 پوینت

ثبت شده بود.

Timing Audit جدید علت این اختلاف را اثبات نمی‌کند، زیرا:
1. خروجی 199 سفارش، سفارش/Deal مربوط به Position و Exit Deal در A002 را مشخص نمی‌کند.
2. هیچ ticket یا قیمت خام per-order در خروجی aggregate موجود نیست.
3. این گزارش مسیر `DEAL_REASON_SL` را جداگانه شناسایی نکرده و قیمت trigger تا اولین Quote اجرایی بعد از trigger را بازسازی نمی‌کند.

## 5. آزمون بعدی لازم

یک بررسی جداگانه و فقط خواندنی برای خروج‌های `DEAL_REASON_SL` لازم است که این نقاط را به هم متصل کند:
1. SL ذخیره‌شده روی Position؛
2. اولین Tick اجرایی پس از عبور قیمت از Stop؛
3. timestamp فعال‌شدن/ثبت سفارش خروج؛
4. timestamp و قیمت Deal خروج؛
5. هرگونه فاصلهٔ زمانی، شکاف بازار یا کمبود Tick history.

اتصال داخلی باید بر مبنای Position/Order/Deal واقعی در MT5 انجام شود؛ اما گزارش نهایی می‌تواند فقط شناسهٔ ماسک‌شده و آمار aggregate صادر کند. هیچ سفارش جدیدی ارسال یا Positionی تغییر داده نشود.

## 6. فایل‌های شواهد

- [گزارش کامل Timing Audit در Grok AI Trader](https://github.com/afshinsaberone-a11y/grok-ai-trader/blob/main/docs/research/xauusd-order-deal-timestamp-audit-20261105.md)
- [JSON ماشینی Timing Audit](https://github.com/afshinsaberone-a11y/grok-ai-trader/blob/main/artifacts/xauusd-quote-fill-timing-audit.json)
- [Issue پیگیری بررسی قیمت صفر و مسیر SL](https://github.com/afshinsaberone-a11y/grok-ai-trader/issues/360)

## 7. تصمیم

این نتیجه فقط یک بررسی زمانی مکمل است. آن را به‌عنوان توضیح قطعی لغزش 1,336 پوینتی، معیار ثابت هزینهٔ اجرای WMMarkets، یا اثبات نبود slippage در Stop Loss استفاده نکنید.

**وضعیت BOOT-003:** Replay A/B همچنان PASS محدود دارد؛ ممیزی Ledger A002 همچنان PASS WITH WARNINGS است؛ علت SL adverse deviation باز می‌ماند.
