"""
Quick build script to compile xiaozhi_final.py to dist folder
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    print("=" * 60)
    print("🚀 miniZ MCP - Quick Build to dist/")
    print("=" * 60)
    print()
    
    # Get current directory
    current_dir = Path(__file__).parent
    os.chdir(current_dir)
    
    # Check if xiaozhi_final.py exists
    if not Path("xiaozhi_final.py").exists():
        print("❌ xiaozhi_final.py not found!")
        sys.exit(1)
    
    print("✅ Found xiaozhi_final.py")
    
    # Clean old build
    print("\n📦 Cleaning old build...")
    if Path("dist").exists():
        import shutil
        try:
            shutil.rmtree("dist")
            print("   Deleted old dist/")
        except:
            pass
    
    if Path("build").exists():
        import shutil
        try:
            shutil.rmtree("build")
            print("   Deleted old build/")
        except:
            pass
    
    # Build command
    print("\n🔨 Building with PyInstaller...")
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name=miniZ_MCP",
        "--noconfirm",
        "--clean",
        "--hidden-import=google.generativeai",
        "--hidden-import=openai",
        "--hidden-import=pystray",
        "--hidden-import=PIL",
        "xiaozhi_final.py"
    ]
    
    print(f"   Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True)
        
        # Check output
        exe_path = Path("dist/miniZ_MCP.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print("\n" + "=" * 60)
            print("🎉 BUILD THÀNH CÔNG!")
            print("=" * 60)
            print(f"\n📦 File: {exe_path.absolute()}")
            print(f"💾 Size: {size_mb:.2f} MB")
            print(f"\n✨ Bạn có thể chạy: dist\\miniZ_MCP.exe")
            return 0
        else:
            print("\n❌ Build failed - EXE not found!")
            return 1
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
