# Archive Password Cracker

Skrip CLI Python ini dirancang untuk mencoba memecahkan password pada arsip yang diproteksi, terutama format ZIP, RAR, dan 7z dengan menggunakan wordlist.

Proyek ini dibuat untuk kebutuhan pengujian, edukasi, dan audit keamanan pada arsip yang Anda miliki atau izinkan untuk diuji.

## Fitur

- Mendukung format ZIP, RAR, dan 7z
- Mendeteksi jenis arsip secara otomatis
- Mendukung ZIP dengan enkripsi ZipCrypto maupun AES-256 melalui library yang sesuai
- Menggunakan wordlist untuk mencoba password secara berurutan
- Menyediakan installer otomatis untuk dependensi Python dan paket sistem yang diperlukan
- Dapat memanfaatkan binary CLI sistem seperti unrar dan 7z jika tersedia untuk performa yang lebih cepat

## Struktur Project

- cracker_archive_tot.py: file utama program CLI
- install.sh: installer untuk menyiapkan environment dan dependensi
- requirements.txt: daftar dependency Python
- wordlist.txt: contoh wordlist sederhana
- secret.zip, secret.rar, secret.7z: contoh arsip uji yang tersedia di workspace

## Persyaratan

- Python 3.8 atau yang lebih baru
- pip
- Optional: unrar dan 7z untuk performa lebih cepat pada arsip RAR dan 7z

## Instalasi

### Opsi 1: Menggunakan installer

Jalankan perintah berikut di root proyek:

```bash
bash install.sh
```

Installer ini akan:

- membuat virtual environment di folder .venv
- menginstal dependency Python dari requirements.txt
- mencoba menyiapkan paket sistem yang dibutuhkan sesuai distro Linux

### Opsi 2: Instalasi manual

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Penggunaan

![Screen Capture](https://raw.githubusercontent.com/gagaltotal/cracker-archive/refs/heads/main/images/Screenshot%20from%202026-07-14%2012-08-37.png)

![Screen Capture](https://raw.githubusercontent.com/gagaltotal/cracker-archive/refs/heads/main/images/Screenshot%20from%202026-07-14%2012-08-51.png)

```bash
python3 cracker_archive_tot.py ARCHIVE WORDLIST
```

![Screen Capture](https://raw.githubusercontent.com/gagaltotal/cracker-archive/refs/heads/main/images/Screenshot%20from%202026-07-14%2012-09-15.png)

Contoh:

```bash
python3 cracker_archive_tot.py secret.zip wordlist.txt
python3 cracker_archive_tot.py protected.rar rockyou.txt
python3 cracker_archive_tot.py archive.7z passwords.txt
```

![Screen Capture](https://raw.githubusercontent.com/gagaltotal/cracker-archive/refs/heads/main/images/Screenshot%20from%202026-07-14%2012-10-17.png)

## Contoh Argumen

- ARCHIVE: path ke file arsip yang diproteksi password
- WORDLIST: path ke file daftar password

## Catatan Penting

- Gunakan tool ini hanya pada file arsip yang Anda miliki atau memiliki izin resmi untuk menguji.
- Kecepatan pencarian sangat bergantung pada kualitas wordlist dan ukuran arsip.
- Untuk arsip RAR dan 7z, tool ini akan mencoba memakai binary CLI sistem terlebih dahulu jika tersedia, lalu fallback ke library Python.

## Troubleshooting

Jika terjadi error terkait modul Python, pastikan environment sudah aktif:

```bash
source .venv/bin/activate
```

Jika modul tidak tersedia, jalankan ulang:

```bash
bash install.sh
```

## Lisensi

Proyek ini disediakan untuk tujuan edukasi dan pengujian yang sah. Pengguna bertanggung jawab penuh atas penggunaan tool ini.
