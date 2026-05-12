@echo off
title Aurum Grid Bot — MGC / NinjaTrader

if not exist logs mkdir logs
if not exist data mkdir data

:loop
echo ======================================
echo [%date% %time%] Starting Aurum Grid Bot...
echo ======================================

venv\Scripts\python.exe src\main.py >> logs\bot.log 2>&1

echo ======================================
echo [%date% %time%] Bot stopped. Restarting in 5s...
echo ======================================

ping 127.0.0.1 -n 6 > nul
goto loop
