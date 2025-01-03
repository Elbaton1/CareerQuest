@echo off
REM Navigate to the directory containing the Python script
cd /d "C:\Users\mobri\Documents\School\mun-job-listings"

REM Run the Python script using Python interpreter
python scraper.py

REM Check if the Python script executed successfully
IF %ERRORLEVEL% NEQ 0 (
    echo Python script encountered an error. Exiting batch script.
    pause
    exit /b %ERRORLEVEL%
)

REM Add all changes to Git staging area
git add .

REM Check if git add was successful
IF %ERRORLEVEL% NEQ 0 (
    echo Git add failed. Exiting batch script.
    pause
    exit /b %ERRORLEVEL%
)

REM Commit changes with a timestamped message
FOR /F "tokens=1-4 delims=/ " %%i in ('date /t') do (
    SET month=%%i
    SET day=%%j
    SET year=%%k
)
FOR /F "tokens=1-2 delims=: " %%i in ('time /t') do (
    SET hour=%%i
    SET minute=%%j
)
SET commitMessage=Update on %month%-%day%-%year% at %hour%:%minute%

git commit -m "%commitMessage%"

REM Check if git commit was successful
IF %ERRORLEVEL% NEQ 0 (
    echo Git commit failed. Maybe there are no changes to commit.
    pause
    exit /b %ERRORLEVEL%
)

REM Push changes to the master branch on origin
git push origin master

REM Check if git push was successful
IF %ERRORLEVEL% NEQ 0 (
    echo Git push failed.
    pause
    exit /b %ERRORLEVEL%
)

REM Pause to keep the command window open after execution
echo All operations completed successfully.
pause
