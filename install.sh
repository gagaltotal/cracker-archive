#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════════
# Archive Password Cracker - Dependency Installer
# Features: Multi-distro support + Python venv
# ══════════════════════════════════════════════════════════════════════════════

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

VENV_DIR=".venv"
REQUIREMENTS="tqdm rarfile py7zr pyzipper"

echo -e "${CYAN}"
cat << 'EOF'
╔═══════════════════════════════════════════════════════════╗
║        ARCHIVE PASSWORD CRACKER - INSTALLER               ║
║        Multi-Distro + Python Venv Support                 ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# ══════════════════════════════════════════════════════════════════════════════
# DISTRO DETECTION
# ══════════════════════════════════════════════════════════════════════════════
detect_distro() {
    local distro="" version=""
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        distro="${ID}"
        version="${VERSION_ID}"
    elif [ -f /etc/redhat-release ]; then
        distro="rhel"
        version=$(grep -oE '[0-9]+' /etc/redhat-release | head -1)
    elif [ -f /etc/debian_version ]; then
        distro="debian"
        version=$(cat /etc/debian_version)
    elif [ -f /etc/arch-release ]; then
        distro="arch"
    elif [ -f /etc/alpine-release ]; then
        distro="alpine"
        version=$(cat /etc/alpine-release)
    else
        distro="unknown"
    fi
    
    echo "${distro}:${version}"
}

get_distro_family() {
    local distro=$1
    
    case "$distro" in
        ubuntu|debian|linuxmint|pop|elementary|zorin|mx|kali|parrot|deepin|devuan)
            echo "debian" ;;
        fedora|rhel|centos|rocky|alma|ol|oraclelinux|amzn|scientific|noble)
            echo "rhel" ;;
        opensuse*|sles|suse)
            echo "suse" ;;
        arch|manjaro|endeavouros|garuda|cachyos)
            echo "arch" ;;
        alpine)
            echo "alpine" ;;
        void)
            echo "void" ;;
        gentoo)
            echo "gentoo" ;;
        solus)
            echo "solus" ;;
        clearlinux|clear-linux-os)
            echo "clearlinux" ;;
        *)
            echo "unknown" ;;
    esac
}

# ══════════════════════════════════════════════════════════════════════════════
# PACKAGE CHECKERS
# ══════════════════════════════════════════════════════════════════════════════
cmd_exists() {
    command -v "$1" &> /dev/null
}

is_installed_debian() { dpkg -l "$1" 2>/dev/null | grep -q "^ii"; }
is_installed_rhel()   { rpm -q "$1" &> /dev/null; }
is_installed_arch()   { pacman -Qi "$1" &> /dev/null; }
is_installed_alpine() { apk -e info "$1" &> /dev/null; }
is_installed_suse()   { rpm -q "$1" &> /dev/null; }
is_installed_void()   { xbps-query "$1" &> /dev/null; }

# ══════════════════════════════════════════════════════════════════════════════
# PACKAGE INSTALLERS
# ══════════════════════════════════════════════════════════════════════════════
install_debian() {
    local pkg=$1
    is_installed_debian "$pkg" && echo -e "  ${GREEN}✓${NC} $pkg" && return 0
    echo -e "  ${YELLOW}↓${NC} $pkg"
    sudo apt-get update -qq 2>/dev/null
    sudo apt-get install -y -qq "$pkg" 2>/dev/null
    echo -e "  ${GREEN}✓${NC} $pkg"
}

install_rhel() {
    local pkg=$1
    is_installed_rhel "$pkg" && echo -e "  ${GREEN}✓${NC} $pkg" && return 0
    echo -e "  ${YELLOW}↓${NC} $pkg"
    if cmd_exists dnf; then sudo dnf install -y -q "$pkg"
    else sudo yum install -y -q "$pkg"; fi
    echo -e "  ${GREEN}✓${NC} $pkg"
}

install_arch() {
    local pkg=$1
    is_installed_arch "$pkg" && echo -e "  ${GREEN}✓${NC} $pkg" && return 0
    echo -e "  ${YELLOW}↓${NC} $pkg"
    sudo pacman -S --noconfirm --quiet "$pkg" 2>/dev/null
    echo -e "  ${GREEN}✓${NC} $pkg"
}

install_alpine() {
    local pkg=$1
    is_installed_alpine "$pkg" && echo -e "  ${GREEN}✓${NC} $pkg" && return 0
    echo -e "  ${YELLOW}↓${NC} $pkg"
    sudo apk add --quiet "$pkg" 2>/dev/null
    echo -e "  ${GREEN}✓${NC} $pkg"
}

install_suse() {
    local pkg=$1
    is_installed_suse "$pkg" && echo -e "  ${GREEN}✓${NC} $pkg" && return 0
    echo -e "  ${YELLOW}↓${NC} $pkg"
    sudo zypper install -y -q "$pkg" 2>/dev/null
    echo -e "  ${GREEN}✓${NC} $pkg"
}

install_void() {
    local pkg=$1
    is_installed_void "$pkg" && echo -e "  ${GREEN}✓${NC} $pkg" && return 0
    echo -e "  ${YELLOW}↓${NC} $pkg"
    sudo xbps-install -y "$pkg" 2>/dev/null
    echo -e "  ${GREEN}✓${NC} $pkg"
}

install_pkg() {
    local pkg=$1 family=$2
    case "$family" in
        debian)    install_debian "$pkg" ;;
        rhel)      install_rhel "$pkg" ;;
        arch)      install_arch "$pkg" ;;
        alpine)    install_alpine "$pkg" ;;
        suse)      install_suse "$pkg" ;;
        void)      install_void "$pkg" ;;
        *)         echo -e "  ${RED}?${NC} $pkg (unknown distro, skipping)" ;;
    esac
}

# ══════════════════════════════════════════════════════════════════════════════
# VENV MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
setup_venv() {
    local python_cmd=""

    if cmd_exists python3; then
        python_cmd="python3"
    elif cmd_exists python; then
        python_cmd="python"
    else
        echo -e "  ${RED}✗${NC} Python3 not found!"
        return 1
    fi
    
    if ! $python_cmd -m venv --help &> /dev/null; then
        echo -e "  ${RED}✗${NC} venv module not available"
        echo -e "  ${YELLOW}!${NC} Install python3-venv package first"
        return 1
    fi
    
    if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/activate" ]; then
        echo -e "  ${GREEN}✓${NC} Virtual environment exists ($VENV_DIR)"
    else
        echo -e "  ${YELLOW}↓${NC} Creating virtual environment ($VENV_DIR)..."
        $python_cmd -m venv "$VENV_DIR"
        echo -e "  ${GREEN}✓${NC} Virtual environment created"
    fi
    
    source "$VENV_DIR/bin/activate"
    
    echo -e "  ${YELLOW}↓${NC} Upgrading pip..."
    pip install --quiet --upgrade pip 2>/dev/null || true
    echo -e "  ${GREEN}✓${NC} pip upgraded"
}

# ══════════════════════════════════════════════════════════════════════════════
# PIP INSTALLER (venv)
# ══════════════════════════════════════════════════════════════════════════════
pip_install_venv() {
    local pkg=$1
    
    if pip show "$pkg" &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} $pkg (venv)"
        return 0
    fi
    
    echo -e "  ${YELLOW}↓${NC} $pkg (installing to venv)..."
    pip install --quiet "$pkg"
    
    if pip show "$pkg" &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} $pkg (venv)"
        return 0
    else
        echo -e "  ${RED}✗${NC} $pkg (failed)"
        return 1
    fi
}

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
main() {
    local distro_info=$(detect_distro)
    local distro=$(echo "$distro_info" | cut -d: -f1)
    local version=$(echo "$distro_info" | cut -d: -f2)
    local family=$(get_distro_family "$distro")
    
    echo -e "${BOLD}[1/5] Detecting System...${NC}"
    echo -e "  Distribution : ${CYAN}${distro}${NC}"
    echo -e "  Version      : ${CYAN}${version}${NC}"
    echo -e "  Family       : ${CYAN}${family}${NC}"
    echo ""
    
    echo -e "${BOLD}[2/5] Installing System Packages...${NC}"
    
    declare -A SYSTEM_PKGS
    SYSTEM_PKGS[debian]="python3 python3-venv python3-pip unrar p7zip-full"
    SYSTEM_PKGS[rhel]="python3 python3-pip unrar p7zip"
    SYSTEM_PKGS[arch]="python python-virtualenv python-pip unrar p7zip"
    SYSTEM_PKGS[alpine]="python3 py3-venv py3-pip unrar p7zip"
    SYSTEM_PKGS[suse]="python3 python3-venv python3-pip unrar p7zip"
    SYSTEM_PKGS[void]="python3 python3-pip unrar p7zip"
    
    if [ "$family" = "unknown" ]; then
        echo -e "  ${YELLOW}!${NC} Unknown distro, skipping system packages"
        echo -e "  ${YELLOW}!${NC} Manually install: python3, python3-venv, unrar"
    else
        local pkgs="${SYSTEM_PKGS[$family]:-""}"
        for pkg in $pkgs; do
            install_pkg "$pkg" "$family" || true
        done
    fi
    echo ""
    
    echo -e "${BOLD}[3/5] Setting Up Virtual Environment...${NC}"
    if ! setup_venv; then
        echo -e "${RED}Failed to setup venv${NC}"
        exit 1
    fi
    echo ""
    
    echo -e "${BOLD}[4/5] Installing Python Packages (venv)...${NC}"
    for pkg in $REQUIREMENTS; do
        pip_install_venv "$pkg" || true
    done
    echo ""
    
    echo -e "${BOLD}[5/5] Verifying Installation...${NC}"
    
    local errors=0
    
    if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/activate" ]; then
        echo -e "  ${GREEN}✓${NC} Virtual environment ($VENV_DIR)"
    else
        echo -e "  ${RED}✗${NC} Virtual environment"
        errors=$((errors + 1))
    fi
    
    if [ -f "$VENV_DIR/bin/python" ]; then
        local py_ver=$($VENV_DIR/bin/python --version 2>&1)
        echo -e "  ${GREEN}✓${NC} Python ($py_ver)"
    else
        echo -e "  ${RED}✗${NC} Python in venv"
        errors=$((errors + 1))
    fi
    
    if [ -f "$VENV_DIR/bin/pip" ]; then
        echo -e "  ${GREEN}✓${NC} pip (venv)"
    else
        echo -e "  ${RED}✗${NC} pip in venv"
        errors=$((errors + 1))
    fi
    
    for pkg in tqdm rarfile py7zr; do
        if $VENV_DIR/bin/python -c "import $pkg" 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} $pkg"
        else
            echo -e "  ${YELLOW}!${NC} $pkg (not installed - ${pkg/rarfile/RAR}/$[7z] support disabled)"
        fi
    done
    
    if cmd_exists unrar; then
        echo -e "  ${GREEN}✓${NC} unrar binary"
    else
        echo -e "  ${YELLOW}!${NC} unrar binary (RAR support limited)"
    fi
    
    echo ""
    echo -e "═══════════════════════════════════════════════════════════════"
    
    if [ $errors -eq 0 ]; then
        echo -e "${GREEN}${BOLD}  ✓ Installation complete!${NC}"
    else
        echo -e "${YELLOW}${BOLD}  ! Installation completed with $errors error(s)${NC}"
    fi
    
    echo -e "═══════════════════════════════════════════════════════════════"
    echo ""
    echo -e "${CYAN}To activate venv in future sessions:${NC}"
    echo -e "    source $VENV_DIR/bin/activate"
    echo ""
    echo -e "${CYAN}To run the cracker:${NC}"
    echo -e "    source $VENV_DIR/bin/activate"
    echo -e "    python cracker_archive_tot.py <archive> <wordlist>"
    echo ""
    echo -e "${CYAN}Example:${NC}"
    echo -e "    source $VENV_DIR/bin/activate && python cracker_archive_tot.py test.zip wordlist.txt"
    echo ""
}

main