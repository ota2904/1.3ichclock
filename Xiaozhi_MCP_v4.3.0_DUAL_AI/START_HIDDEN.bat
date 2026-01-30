@echo off
chcp 65001 >nul
title 🚀 miniZ MCP - System Tray Mode

:: Run in hidden mode with system tray
start /min pythonw tray_app.py --hidden

:: Or use python if pythonw not available
:: python tray_app.py --hidden
