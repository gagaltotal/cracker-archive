#!/usr/bin/env python3
"""
Archive Password Cracker - Multi-format Support
Supports: ZIP, RAR, 7z, and password-protected archives
Author : GhostGTR666- Gagaltotal666
Github : github.com/gagaltotal 
"""

import sys
import os
import zipfile
import zlib
import argparse
import subprocess
import shutil
from tqdm import tqdm

try:
    import rarfile
    HAS_RAR = True
except ImportError:
    HAS_RAR = False

try:
    import py7zr
    HAS_7Z = True
except ImportError:
    HAS_7Z = False

try:
    import pyzipper
    HAS_PYZIPPER = True
except ImportError:
    HAS_PYZIPPER = False


# ══════════════════════════════════════════════════════════════════════════════
#                              ASCII BANNER
# ══════════════════════════════════════════════════════════════════════════════
BANNER = r"""
 ██████╗ ██████╗     █████╗ ██████╗  ██████╗██╗  ██╗    ████████╗ ██████╗ ████████╗
██╔════╝██╔════╝    ██╔══██╗██╔══██╗██╔════╝██║  ██║    ╚══██╔══╝██╔═══██╗╚══██╔══╝
██║     ██║         ███████║██████╔╝██║     ███████║       ██║   ██║   ██║   ██║   
██║     ██║         ██╔══██║██╔══██╗██║     ██╔══██║       ██║   ██║   ██║   ██║   
╚██████╗╚██████╗    ██║  ██║██║  ██║╚██████╗██║  ██║       ██║   ╚██████╔╝   ██║   
 ╚═════╝ ╚═════╝    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝       ╚═╝    ╚═════╝    ╚═╝   

Archive Password Cracker - Multi-format Support
Supports: ZIP, RAR, 7z, and password-protected archives
Author : GhostGTR666- Gagaltotal666
Github : github.com/gagaltotal
Version : 1.0.0 
"""


# ══════════════════════════════════════════════════════════════════════════════
#                            HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def detect_archive_type(filepath: str) -> str:
    filepath_lower = filepath.lower()
    ext_map = {'.zip': 'zip', '.rar': 'rar', '.7z': '7z'}
    for ext, archive_type in ext_map.items():
        if filepath_lower.endswith(ext):
            return archive_type
    try:
        with open(filepath, 'rb') as f:
            header = f.read(10)
        if header[:4] == b'PK\x03\x04': return 'zip'
        elif header[:7] == b'Rar!\x1a\x07': return 'rar'
        elif header[:6] == b'7z\xbc\xaf\x27\x1c': return '7z'
    except Exception: pass
    return 'unknown'

def check_dependencies(archive_type: str) -> list:
    missing = []
    if archive_type == 'rar' and not HAS_RAR:
        missing.append("rarfile (pip install rarfile) + unrar binary")
    elif archive_type == '7z' and not HAS_7Z:
        missing.append("py7zr (pip install py7zr)")
    return missing

def is_password_supported(archive_type: str) -> bool:
    return archive_type in ['zip', 'rar', '7z']

def count_words(wordlist_path: str) -> int:
    count = 0
    try:
        with open(wordlist_path, 'rb') as f:
            for _ in f: count += 1
    except Exception as e: print(f"[!] Error reading wordlist: {e}")
    return count

def validate_files(archive_path: str, wordlist_path: str) -> bool:
    for path, desc in [(archive_path, "Archive"), (wordlist_path, "Wordlist")]:
        if not os.path.isfile(path):
            print(f"[!] {desc} not found: {path}"); return False
        if not os.access(path, os.R_OK):
            print(f"[!] Cannot read {desc}: {path}"); return False
    return True


# ══════════════════════════════════════════════════════════════════════════════
#                              CRACKER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def crack_zip(archive_path: str, wordlist_path: str) -> str | None:
    """
    Crack ZIP - Fixed: Auto-detect AES encryption, uses Memory Read + CRC check.
    """
    zf = None
    try:
        is_aes = False
        with zipfile.ZipFile(archive_path, 'r') as temp_zf:
            for info in temp_zf.infolist():
                if info.flag_bits & 0x1 and info.compress_type == 99:
                    is_aes = True
                    break

        if is_aes:
            if not HAS_PYZIPPER:
                print("[!] Archive uses AES-256 encryption.")
                print("[!] Python's built-in zipfile cannot crack AES.")
                print("[!] Install pyzipper: pip install pyzipper")
                return None
            zf = pyzipper.AESZipFile(archive_path, 'r')
            enc_type = "AES-256"
        else:
            zf = zipfile.ZipFile(archive_path, 'r')
            enc_type = "ZipCrypto"

        test_info = None
        for info in zf.infolist():
            if (info.flag_bits & 0x1) and not info.is_dir() and info.file_size > 0:
                test_info = info
                break
        
        if not test_info:
            for info in zf.infolist():
                if info.flag_bits & 0x1:
                    test_info = info
                    break

        if not test_info:
            print("[*] Archive is not password protected!")
            return None

        n_words = count_words(wordlist_path)
        print(f"[*] Encryption type: {enc_type}")
        print(f"[*] Total passwords to test: {n_words:,}")
        print(f"[*] Test file: {test_info.filename}")

        with open(wordlist_path, 'rb') as wordlist:
            for word in tqdm(wordlist, total=n_words, unit="word", desc="Cracking"):
                pwd_bytes = word.strip()
                
                try:
                    data = zf.read(test_info.filename, pwd=pwd_bytes)
                    
                    if test_info.file_size == 0 or (zlib.crc32(data) & 0xffffffff) == test_info.CRC:
                        return pwd_bytes.decode('utf-8', errors='ignore')
                        
                except RuntimeError:
                    continue
                except Exception:
                    continue
                    
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        if zf: zf.close()
    
    return None


def crack_rar(archive_path: str, wordlist_path: str) -> str | None:
    """
    Crack RAR - Prioritas pakai CLI unrar, fallback ke rarfile.
    """
    if shutil.which('unrar'):
        return crack_rar_cli(archive_path, wordlist_path)
        
    if HAS_RAR:
        return crack_rar_py(archive_path, wordlist_path)
        
    print("[!] 'unrar' binary tidak ditemukan di sistem.")
    print("[!] Install dengan: bash install.sh")
    return None

def crack_rar_cli(archive_path: str, wordlist_path: str) -> str | None:
    """Crack RAR menggunakan unrar CLI (Native C, sangat cepat)."""
    n_words = count_words(wordlist_path)
    print(f"[*] Total passwords to test: {n_words:,}")
    print(f"[*] Engine: unrar CLI (Fast Mode)")

    with open(wordlist_path, 'rb') as wordlist:
        for word in tqdm(wordlist, total=n_words, unit="word", desc="Cracking"):
            pwd_str = word.strip().decode('utf-8', errors='ignore')
            
            try:
                result = subprocess.run(
                    ['unrar', 't', f'-p{pwd_str}', '-inul', archive_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                if result.returncode == 0:
                    return pwd_str
            except Exception:
                continue
                
    return None

def crack_rar_py(archive_path: str, wordlist_path: str) -> str | None:
    """Crack RAR menggunakan library rarfile (Fallback mode)."""
    rf = None
    try:
        rf = rarfile.RarFile(archive_path, 'r')
        file_list = [f for f in rf.namelist() if not f.endswith('/')]
        if not file_list: return None
            
        test_file = file_list[0]
        test_info = rf.getinfo(test_file)
        expected_size = test_info.file_size

        n_words = count_words(wordlist_path)
        print(f"[*] Total passwords to test: {n_words:,}")
        print(f"[*] Engine: rarfile Python (Slow Mode)")

        with open(wordlist_path, 'rb') as wordlist:
            for word in tqdm(wordlist, total=n_words, unit="word", desc="Cracking"):
                pwd_str = word.strip().decode('utf-8', errors='ignore')
                try:
                    data = rf.read(test_file, pwd=pwd_str)
                    if data and len(data) == expected_size:
                        return pwd_str
                except Exception:
                    continue
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        if rf:
            try: rf.close()
            except: pass
    return None


def crack_7z(archive_path: str, wordlist_path: str) -> str | None:
    """
    Crack 7z - Prioritas pakai CLI 7z, fallback ke py7zr.
    """
    if shutil.which('7z'):
        return crack_7z_cli(archive_path, wordlist_path)
        
    if HAS_7Z:
        return crack_7z_py(archive_path, wordlist_path)
        
    print("[!] '7z' binary tidak ditemukan di sistem.")
    print("[!] Install dengan: bash install.sh")
    return None

def crack_7z_cli(archive_path: str, wordlist_path: str) -> str | None:
    """Crack 7z menggunakan 7z CLI (Native C)."""
    n_words = count_words(wordlist_path)
    print(f"[*] Total passwords to test: {n_words:,}")
    print(f"[*] Engine: 7z CLI (Fast Mode)")

    with open(wordlist_path, 'rb') as wordlist:
        for word in tqdm(wordlist, total=n_words, unit="word", desc="Cracking"):
            pwd_str = word.strip().decode('utf-8', errors='ignore')
            
            try:
                result = subprocess.run(
                    ['7z', 't', f'-p{pwd_str}', archive_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                if result.returncode == 0:
                    return pwd_str
            except Exception:
                continue
                
    return None

def crack_7z_py(archive_path: str, wordlist_path: str) -> str | None:
    """Crack 7z menggunakan library py7zr (Fallback mode)."""
    try:
        n_words = count_words(wordlist_path)
        print(f"[*] Total passwords to test: {n_words:,}")
        print(f"[*] Engine: py7zr Python (Slow Mode)")

        with open(wordlist_path, 'rb') as wordlist:
            for word in tqdm(wordlist, total=n_words, unit="word", desc="Cracking"):
                pwd_str = word.strip().decode('utf-8', errors='ignore')
                
                try:
                    with py7zr.SevenZipFile(archive_path, mode='r', password=pwd_str) as sz:
                        names = sz.getnames()
                        if not names: continue
                        
                        data = sz.read([names[0]])
                        if names[0] in data:
                            file_bytes = data[names[0]].read()
                            if len(file_bytes) > 0:
                                return pwd_str
                                
                except Exception:
                    continue

    except py7zr.Bad7zFile:
        print("[!] Invalid or corrupted 7z file")
    except Exception as e:
        print(f"[!] Error: {e}")
        
    return None


# ══════════════════════════════════════════════════════════════════════════════
#                              MAIN FUNCTION
# ══════════════════════════════════════════════════════════════════════════════
def main():
    print(BANNER)
    
    parser = argparse.ArgumentParser(
        description=(
            "═══════════════════════════════════════════════════════════\n"
            "  Multi-Format Archive Password Cracker (CLI + Python)\n"
            "  Mendukung: ZIP (ZipCrypto/AES-256), RAR, 7Z\n"
            "═══════════════════════════════════════════════════════════"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Contoh Penggunaan:\n"
            "  python %(prog)s secret.zip    wordlist.txt\n"
            "  python %(prog)s protected.rar rockyou.txt\n"
            "  python %(prog)s archive.7z    passwords.txt\n"
            "\n"
            "Catatan:\n"
            "  - Untuk RAR dan 7z, tool ini otomatis memprioritaskan binary CLI\n"
            "    sistem (unrar, 7z) untuk kecepatan maksimal, dan fallback ke\n"
            "    library Python jika binary tidak tersedia.\n"
            "  - Pastikan jalankan 'bash install.sh' terlebih dahulu untuk\n"
            "    menginstall dependensi Python (venv) dan binary sistem."
        )
    )
    
    parser.add_argument(
        'archive', 
        metavar='ARCHIVE',
        help='Path ke file arsip yang dilindungi password (ZIP, RAR, 7Z)'
    )
    parser.add_argument(
        'wordlist', 
        metavar='WORDLIST',
        help='Path ke file wordlist daftar password'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 1.0 Final'
    )
    
    args = parser.parse_args()
    
    if not validate_files(args.archive, args.wordlist):
        sys.exit(1)
    
    archive_type = detect_archive_type(args.archive)
    print(f"[*] Detected archive type: {archive_type.upper()}")
    print(f"[*] Archive: {args.archive}")
    print(f"[*] Wordlist: {args.wordlist}")
    print("-" * 60)
    
    if not is_password_supported(archive_type):
        print(f"[!] Format '{archive_type}' does not support password encryption.")
        sys.exit(1)
    
    missing_deps = check_dependencies(archive_type)
    if missing_deps:
        print(f"[!] Missing dependencies: {', '.join(missing_deps)}")
        print("[*] Run: bash install.sh")
        sys.exit(1)
    
    crackers = {'zip': crack_zip, 'rar': crack_rar, '7z': crack_7z}
    cracker_func = crackers.get(archive_type)
    
    if not cracker_func:
        print(f"[!] No cracker available for format: {archive_type}")
        sys.exit(1)
    
    print("[*] Starting password cracking...")
    result = cracker_func(args.archive, args.wordlist)
    
    print("-" * 60)
    if result:
        print(f"[+] ══════════════════════════════════════════════════")
        print(f"[+]  PASSWORD FOUND: {result}")
        print(f"[+] ══════════════════════════════════════════════════")
        sys.exit(0)
    else:
        print("[!] Password not found. Try a different wordlist.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Exit Good Byee!")
        sys.exit(1)