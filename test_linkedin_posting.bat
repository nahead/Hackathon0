@echo off
echo ======================================
echo LinkedIn Posting Test
echo ======================================

REM Set your LinkedIn credentials here
set LINKEDIN_EMAIL=your_email@example.com
set LINKEDIN_PASSWORD=your_password_here

REM Set headless mode (false = visible browser)
set HEADLESS=false

echo.
echo [CONFIG] Email: %LINKEDIN_EMAIL%
echo [CONFIG] Headless: %HEADLESS%
echo.
echo [INFO] Browser will open and login to LinkedIn
echo [INFO] Then it will post the approved content
echo.
pause

python linkedin_playwright_poster.py

pause
