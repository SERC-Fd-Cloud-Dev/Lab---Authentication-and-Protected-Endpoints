#!/usr/bin/env bash
# Check if common dev container features/tools are installed and print versions
# Tools covered: Docker, .NET SDK, Python3, SQL Server Tools (sqlcmd), Git
# Optionally tries a lightweight SQL Server query if a db is reachable.

# Usage: ./scripts/check-features.sh
# Env overrides: DB_HOST (default: db), SA_PASSWORD (default: P@ssw0rd)

# Do not exit on first error; we want a full report.
set -u

DB_HOST="${DB_HOST:-db}"
SA_PASSWORD="${SA_PASSWORD:-P@ssw0rd}"

# Colors
if [[ -t 1 ]] && command -v tput >/dev/null 2>&1; then
  ncolors=$(tput colors 2>/dev/null || echo 0)
else
  ncolors=0
fi
if [[ "$ncolors" -ge 8 ]]; then
  GREEN='\033[0;32m'
  RED='\033[0;31m'
  YELLOW='\033[0;33m'
  BLUE='\033[0;34m'
  BOLD='\033[1m'
  RESET='\033[0m'
else
  GREEN=''
  RED=''
  YELLOW=''
  BLUE=''
  BOLD=''
  RESET=''
fi

have() {
  command -v "$1" >/dev/null 2>&1
}

print_section() {
  printf "\n${BOLD}${BLUE}==> %s${RESET}\n" "$1"
}

print_ok() {
  printf "${GREEN}✔${RESET} %s\n" "$1"
}

print_warn() {
  printf "${YELLOW}⚠${RESET} %s\n" "$1"
}

print_err() {
  printf "${RED}✖${RESET} %s\n" "$1"
}

# Individual checks
check_docker() {
  print_section "Docker"
  if have docker; then
    local v
    v=$(docker --version 2>/dev/null || true)
    [[ -n "$v" ]] && print_ok "$v" || print_warn "docker installed but version not detected"
  else
    print_err "docker not found on PATH"
  fi
}

check_dotnet() {
  print_section ".NET SDK"
  if have dotnet; then
    local v
    v=$(dotnet --version 2>/dev/null || true)
    if [[ -n "$v" ]]; then
      print_ok ".NET SDK $v"
    else
      print_warn "dotnet installed but version not detected"
    fi
  else
    print_err "dotnet not found on PATH"
  fi
}

check_python() {
  print_section "Python3"
  if have python3; then
    local v
    v=$(python3 --version 2>/dev/null || true)
    [[ -n "$v" ]] && print_ok "$v" || print_warn "python3 installed but version not detected"
  else
    print_err "python3 not found on PATH"
  fi
}

check_sqlite() {
  print_section "SQLite"
  if have sqlite3; then
    local v
    v=$(sqlite3 --version 2>/dev/null || true)
    if [[ -n "$v" ]]; then
      print_ok "$v"
    else
      print_warn "sqlite3 installed but version not detected"
    fi
  else
    print_err "sqlite3 not found on PATH"
  fi
}

check_sqlcmd() {
  print_section "SQL Server Tools (sqlcmd)"
  if have sqlcmd; then
    # sqlcmd doesn't have --version; the second line of -? contains version info on most builds
    local v
    v=$(sqlcmd -? 2>/dev/null | awk 'NR==2' || true)
    if [[ -n "$v" ]]; then
      print_ok "$v"
    else
      print_warn "sqlcmd installed but version not detected"
    fi

    # Try a lightweight server query if possible; do not fail the script on error
    local server_info
    server_info=$(sqlcmd -S "$DB_HOST" -U SA -P "$SA_PASSWORD" -C -Q "SET NOCOUNT ON; SELECT @@VERSION;" -W -h-1 2>/dev/null || true)
    if [[ -n "$server_info" ]]; then
      print_ok "Connected to '$DB_HOST' and retrieved server version:"
      echo "$server_info" | sed 's/^/   /'
    else
      print_warn "Could not query SQL Server at '$DB_HOST' (skipping)."
    fi
  else
    print_err "sqlcmd not found on PATH"
  fi
}

check_git() {
  print_section "Git"
  if have git; then
    local v
    v=$(git --version 2>/dev/null || true)
    [[ -n "$v" ]] && print_ok "$v" || print_warn "git installed but version not detected"
  else
    print_err "git not found on PATH"
  fi
}

main() {
  print_section "Environment"
  print_ok "DB_HOST=${DB_HOST}"
  # Avoid printing password contents; indicate if it's set
  if [[ -n "${SA_PASSWORD:-}" ]]; then
    print_ok "SA_PASSWORD is set (hidden)"
  else
    print_warn "SA_PASSWORD is not set; using default if needed"
  fi

  check_docker
  check_dotnet
  check_python
  check_sqlite
  check_sqlcmd
  check_git

  echo
}

main "$@"
