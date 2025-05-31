@echo off
echo ========= הפעלת מערכת CashFlowIQ =========
echo.
cd /d "%~dp0"
echo מעבר לתיקיית הפרויקט: %CD%
echo.
echo מפעיל את השרת...
start "" http://localhost:8501
streamlit run app.py
echo.
echo האפליקציה הופעלה! 