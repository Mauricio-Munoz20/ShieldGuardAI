@echo off
chcp 65001 >nul
title ShieldGuard AI - Live Demo

echo.
echo  ================================================================
echo   ShieldGuard AI - Demostracion en Vivo
echo   Servidor Unificado (Backend + Frontend) en :8080
echo  ================================================================
echo.
echo  Abriendo navegador en http://localhost:8080 ...
echo.

start "" "http://localhost:8080"

cd /d "%~dp0backend"
shieldguard-backend.exe
