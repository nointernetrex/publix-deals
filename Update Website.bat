@echo off
title Publix Deals Website Updater
cd /d "%~dp0"

echo ============================================
echo    Publix Deals Website Updater
echo ============================================
echo.

REM Generate the website from the Word document
echo Step 1: Generating website from Publix_Final.docx...
python generate_website.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to generate website!
    pause
    exit /b 1
)

echo.
echo Step 2: Pushing to GitHub...
git add index.html
git commit -m "Update deals for this week"
git push

echo.
echo ============================================
echo    Done! Website updated successfully.
echo ============================================
echo.
echo Your website will be live in a few minutes at:
echo https://nointernetrex.github.io/publix-deals/
echo.
pause
