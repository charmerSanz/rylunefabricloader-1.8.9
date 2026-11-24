@echo off
where gradle >nul 2>nul || (echo Install Gradle 8.12.1 and JDK 17 first, or use GitHub Actions. & exit /b 1)
python tools\prepare_game.py
if errorlevel 1 exit /b 1
call gradle --no-daemon clean build
if errorlevel 1 exit /b 1
echo JAR: build\libs\RyluneFabric-1.8.9-0.3.0-alpha.jar
