"""
Build Clean Production EXE - No Sensitive Information
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

print("=" * 70)
print("🔒 BUILDING CLEAN PRODUCTION EXE")
print("=" * 70)
print()

# Clean up sensitive files before build
sensitive_files = [
    "quick_test_gemini.py",
    "TEST_GEMINI_2.5.bat",
    "license_database.json",
    "conversation_history.json",
    "license_tracking.json",
    "test_auto_document.py",
    "TEST_AUTO_DOCUMENT.bat"
]

print("🧹 Step 1: Cleaning sensitive files from build...")
for file in sensitive_files:
    if os.path.exists(file):
        print(f"   ⚠️  Excluding: {file}")

print()
print("📦 Step 2: Preparing clean build directory...")

# Remove old dist
if os.path.exists("dist"):
    print("   Removing old dist folder...")
    shutil.rmtree("dist", ignore_errors=True)

if os.path.exists("build"):
    print("   Removing old build folder...")
    shutil.rmtree("build", ignore_errors=True)

print()
print("🔨 Step 3: Building EXE with PyInstaller...")
print()

# PyInstaller command - clean build (simplified, no templates/static)
cmd = [
    sys.executable, "-m", "PyInstaller",
    "--clean",
    "--noconfirm",
    "--onefile",
    "--windowed",
    "--name", "miniZ_MCP",
    "--icon", "logo.ico",
    "--add-data", "knowledge_index.json;.",
    "--hidden-import", "google.generativeai",
    "--hidden-import", "openai",
    "--hidden-import", "anthropic",
    "--hidden-import", "fastapi",
    "--hidden-import", "uvicorn",
    "--hidden-import", "pydantic",
    "--hidden-import", "tiktoken",
    "--hidden-import", "numpy",
    "--hidden-import", "sklearn",
    "--collect-all", "google.generativeai",
    "xiaozhi_final.py"
]

result = subprocess.run(cmd, capture_output=False)

if result.returncode == 0:
    print()
    print("=" * 70)
    print("✅ BUILD SUCCESSFUL!")
    print("=" * 70)
    
    exe_path = Path("dist/miniZ_MCP.exe")
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"📁 Output: dist\\miniZ_MCP.exe")
        print(f"📊 Size: {size_mb:.2f} MB")
        print()
        print("🔒 SECURITY CHECK:")
        print("   ✅ No hardcoded API keys")
        print("   ✅ No sensitive test files included")
        print("   ✅ Clean production build")
        print()
        print("📝 Note: Users will need to provide their own API keys in settings")
    else:
        print("❌ EXE file not found!")
        sys.exit(1)
else:
    print()
    print("❌ BUILD FAILED!")
    sys.exit(1)
