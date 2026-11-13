#!/usr/bin/env bash
echo "================================================================"
echo " ShieldGuard AI — Entorno de Demostracion en Vivo (Bash)"
echo " Golang Backend (:8080) + Angular Risk Console (:4200)"
echo "================================================================"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "[1/2] Iniciando Backend en Go (:8080)..."
cmd.exe /c start cmd /k "cd /d $DIR\\backend && shieldguard-backend.exe"

sleep 2

echo "[2/2] Iniciando Frontend en Angular (:4200)..."
cmd.exe /c start cmd /k "cd /d $DIR\\frontend && pnpm start"

echo ""
echo "================================================================"
echo " Todo listo! Abre tu navegador en: http://localhost:4200"
echo "================================================================"
