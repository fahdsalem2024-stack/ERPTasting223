@echo off
REM ERP Test Automation - Scheduled Runs
REM Generated: 2026-10-04T14:05:15.775321

cd /d "D:\50505050505050505050050505050\erp-automation"
call venv\Scripts\activate.bat

REM === يومي صباحا اسلاعه 9  (09:00 يومياً) ===
python -m pytest tests/functional/test_03_sales_invoice.py::test_full_sales_invoice_flow -v

pause
