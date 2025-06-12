@echo off
echo ========= הפעלת מערכת CashFlowIQ =========
echo.
cd /d "%~dp0"
echo מעבר לתיקיית הפרויקט: %CD%
echo.
echo מפעיל את השרת...
streamlit run app.py
echo.
echo האפליקציה הופעלה! 