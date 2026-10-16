#!/usr/bin/env bash
# Load repo-root .env into the shell without overriding variables already set (mirrors utils.retail_fru.env).
load_repo_env() {
  local root="${1:?repo root}"
  local env_file="$root/.env"
  [[ -f "$env_file" ]] || return 0
  local raw line key val
  while IFS= read -r raw || [[ -n "$raw" ]]; do
    line="${raw%%#*}"
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    [[ -z "$line" || "$line" != *=* ]] && continue
    key="${line%%=*}"
    key="${key%"${key##*[![:space:]]}"}"
    val="${line#*=}"
    val="${val#"${val%%[![:space:]]*}"}"
    val="${val%"${val##*[![:space:]]}"}"
    val="${val#\"}"; val="${val%\"}"
    val="${val#\'}"; val="${val%\'}"
    if [[ -n "$key" && -z "${!key+x}" ]]; then
      export "$key=$val"
    fi
  done < "$env_file"
}
