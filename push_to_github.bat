@echo off
setlocal
cd /d "%~dp0"

echo Checking Git installation...
where git >nul 2>&1
if errorlevel 1 (
  echo Git was not found. Install Git for Windows from https://git-scm.com/download/win
  pause
  exit /b 1
)

if not exist .git (
  git init
  if errorlevel 1 goto :failed
)

git branch -M main
if errorlevel 1 goto :failed

git remote get-url origin >nul 2>&1
if errorlevel 1 (
  git remote add origin https://github.com/Aryan717317/Coding-automation-lab.git
  if errorlevel 1 goto :failed
) else (
  git remote set-url origin https://github.com/Aryan717317/Coding-automation-lab.git
  if errorlevel 1 goto :failed
)

git add .
if errorlevel 1 goto :failed

git diff --cached --quiet
if errorlevel 1 (
  git commit -m "Initial commit: VS Code Coding Automation Lab"
  if errorlevel 1 goto :failed
) else (
  echo No new changes to commit.
)

echo.
echo Pushing to GitHub...
git push -u origin main
if errorlevel 1 goto :failed

echo.
echo Successfully pushed to:
echo https://github.com/Aryan717317/Coding-automation-lab
pause
exit /b 0

:failed
echo.
echo Push did not complete. Check the error above.
echo If prompted, sign in to GitHub in your browser.
pause
exit /b 1
