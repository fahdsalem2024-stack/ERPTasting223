# ERP Test Automation — ملخص نهائي

## رابط GitHub
https://github.com/fahdsalim19977-sys/erp-automation

## الحالة
- ✅ اختبار فاتورة بيع يعمل
- ✅ موقع ويب كامل
- ✅ CI/CD يعمل

## التشغيل السريع
cd D:\50505050505050505050050505050\erp-automation
venv\Scripts\activate
python web\app.py
ثم افتح: http://localhost:5000
- Username: admin
- Password: password

## اختبار فاتورة البيع
python -m pytest tests/functional/test_03_sales_invoice.py -v -s
## Docker
docker-compose up -d
## رفع تحديثات
git add .
git commit -m "update"
git push
## معلومات مهمة
- Framework: Python + Selenium + Flask
- الموقع: 8 صفحات
- 5 تابات إعدادات
- عربي/إنجليزي
- Docker + CI/CD
