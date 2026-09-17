import os
import subprocess
import shutil
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# --- KONFIGURASI ABSOLUT ---
PROJECT_DIR = Path(r"D:\GUI Duren\GUI Duren")
INNO_SETUP_COMPILER = Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe")
ISS_FILE = PROJECT_DIR / "build_installer.iss"
MAIN_SCRIPT = PROJECT_DIR / "main.py"
ICON_PATH = PROJECT_DIR / "ui" / "styles" / "icon.ico"

def check_dependencies():
    """Ensure bandit and flake8 are installed."""
    try:
        import bandit
        import flake8
    except ImportError:
        print("[!] Menginstal dependensi statik analisis (bandit & flake8)...")
        subprocess.run([sys.executable, "-m", "pip", "install", "bandit", "flake8"], check=True)

def step1_static_scan():
    print("\n[1/5] PRE-BUILD STATIC SCAN (Bandit & Flake8)...")
    
    # Run Bandit
    print("      -> Menjalankan Bandit (Security Scanner)...")
    bandit_cmd = ["bandit", "-r", "core/", "ui/", "main.py", "-ll"] # -ll shows only HIGH severity
    bandit_proc = subprocess.run(bandit_cmd, cwd=PROJECT_DIR, capture_output=True, text=True)
    
    if bandit_proc.returncode != 0:
        if "Severity: High" in bandit_proc.stdout or "Severity: High" in bandit_proc.stderr:
            print("\n🚨 [FATAL] Bandit menemukan isu keamanan HIGH Severity!")
            print(bandit_proc.stdout)
            sys.exit(1)
            
    # Run Flake8 (Syntax/Logic errors)
    print("      -> Menjalankan Flake8 (Logic Scanner)...")
    # We only care about fatal errors (F) and syntax errors (E9)
    flake8_cmd = ["flake8", "core/", "ui/", "main.py", "--select=E9,F63,F7,F82"]
    flake8_proc = subprocess.run(flake8_cmd, cwd=PROJECT_DIR, capture_output=True, text=True)
    
    if flake8_proc.returncode != 0:
        print("\n🚨 [FATAL] Flake8 menemukan kode yang berpotensi crash!")
        print(flake8_proc.stdout)
        sys.exit(1)
        
    print("      ✅ Static scan lolos (Tidak ada isu HIGH severity/fatal).")

def step2_clean_build():
    print("\n[2/5] Membersihkan cache dan sisa build sebelumnya...")
    dirs_to_clean = ["build", "dist", "Output"]
    for d in dirs_to_clean:
        dir_path = PROJECT_DIR / d
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"      - Folder '{d}' berhasil dihapus.")

def step3_run_pyinstaller():
    print("\n[3/5] Memulai PyInstaller (Membekukan Kode Python)...")
    print("      Proses ini memakan waktu beberapa menit. Harap tunggu...")
    
    cmd = [
        "pyinstaller", 
        "--noconfirm", 
        "--onedir", 
        "--windowed",
        "--name=DurianVision", 
        "--collect-data=ultralytics",
        "--hidden-import=torchvision",
        "--hidden-import=ultralytics",
        "--hidden-import=cv2",
        "--hidden-import=scipy",
        "--hidden-import=pynput.keyboard._win32",
        "--hidden-import=openpyxl",
        "--add-data=config;config/",
        "--add-data=ui;ui/",
        "--add-data=core;core/"
    ]
    
    if (PROJECT_DIR / "best.pt").exists():
        cmd.append("--add-data=best.pt;.")
    if (PROJECT_DIR / "classifier.pt").exists():
        cmd.append("--add-data=classifier.pt;.")
        
    if ICON_PATH.exists():
        cmd.append(f"--icon={ICON_PATH}")
        
    cmd.append(str(MAIN_SCRIPT))
    
    subprocess.run(cmd, cwd=PROJECT_DIR, check=True)
    print("      ✅ Build file executables (.exe) selesai!")

def step4_post_build_scan():
    print("\n[4/5] POST-BUILD ARTIFACT SCANNER (Menganalisis warn-DurianVision.txt)...")
    warn_file = PROJECT_DIR / "build" / "DurianVision" / "warn-DurianVision.txt"
    
    if not warn_file.exists():
        print("      ⚠️ File peringatan tidak ditemukan, melewati scan artifact.")
        return
        
    with open(warn_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Extract "missing module named X"
    missing_modules = re.findall(r"missing module named '([^']+)'", content)
    critical_libs = ['ultralytics', 'torch', 'PyQt6', 'cv2']
    
    found_critical = []
    for lib in critical_libs:
        for missing in missing_modules:
            if missing.startswith(lib):
                # Pengecualian (False Positives) untuk modul internal C PyTorch dan komponen opsional
                if (missing.startswith('torch._C') or missing.startswith('torch._inductor') 
                    or missing.startswith('torch_xla') or missing.startswith('torchcomms') 
                    or missing.startswith('torch.distributed') or missing.startswith('torch.utils')):
                    continue
                found_critical.append(missing)
                
    if found_critical:
        print("\n🚨 [FATAL] PyInstaller gagal memasukkan dependensi kritis berikut:")
        for mod in set(found_critical):
            print(f"      - {mod}")
        print("\n❌ BUILD DIGAGALKAN. Exe berpotensi crash (ModuleNotFoundError).")
        print("Solusi: Tambahkan modul tersebut ke --hidden-import.")
        sys.exit(1)
        
    print("      ✅ Artifact scan lolos (Semua dependensi kritis ter-bundle).")

def step5_compile_inno_setup():
    print("\n[5/5] Mengkompilasi Installer dengan Inno Setup...")
    
    if not INNO_SETUP_COMPILER.exists():
        print(f"      ❌ ERROR: Compiler Inno Setup tidak ditemukan di: {INNO_SETUP_COMPILER}")
        sys.exit(1)
        
    if not ISS_FILE.exists():
        print(f"      ❌ ERROR: File script {ISS_FILE} tidak ditemukan!")
        sys.exit(1)

    result = subprocess.run([str(INNO_SETUP_COMPILER), str(ISS_FILE)], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("\n      ❌ ERROR: Gagal mengkompilasi installer Inno Setup!")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)
        
    print("      ✅ Kompresi selesai!")

def main():
    print("=== 🚀 DURIANVISION ENTERPRISE CI/CD PIPELINE ===")
    check_dependencies()
    step1_static_scan()
    step2_clean_build()
    step3_run_pyinstaller()
    step4_post_build_scan()
    step5_compile_inno_setup()
    
    print("\n[🎉] PROTOKOL SELESAI!")
    print(r"      File siap edar berada di: D:\GUI Duren\GUI Duren\Output\DurianVision_Setup_v1.exe")

if __name__ == "__main__":
    main()
