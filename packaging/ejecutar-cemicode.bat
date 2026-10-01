@echo off
title CEMICODE Portable - Coding Agent + DGX GDX Spark
set "CEMICODE_HOME=%~dp0"
cd /d "%CEMICODE_HOME%"
if not exist ".env" (
  echo [CEMICODE] Creando .env desde .env.example...
  copy /y ".env.example" ".env" >nul
  echo Edita .env con tu DGX_CLAVE antes de continuar.
)
"%CEMICODE_HOME%bin\cemicode.exe" -m gdx-spark/Qwen3.6-35B-A3B %*
pause
