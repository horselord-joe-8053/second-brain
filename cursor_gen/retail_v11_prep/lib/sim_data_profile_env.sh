# shellcheck shell=bash
# Resolve RETAIL_SIM_DATA_PROFILE paths into env vars (single source: sim_data_profile.py).
retail_sim_data_profile_exports() {
  local root="$1"
  export PYTHONPATH="${root}/scripts/retail${PYTHONPATH:+:$PYTHONPATH}"
  # shellcheck disable=SC2046
  eval "$("${root}/scripts/py" "${root}/scripts/retail/retail_brain/sim_data_profile.py" --shell)"
}

retail_sim_data_profile_banner() {
  local phase="$1"
  echo ""
  echo "=== RETAIL sim_data_profile=${RETAIL_SIM_DATA_PROFILE} — ${phase} ==="
  echo "  Label:   ${RETAIL_SIM_PROFILE_LABEL}"
  echo "  CSV:     ${RETAIL_SIM_CSV}"
  echo "  Eval:    ${RETAIL_SIM_EVAL}"
  echo "  Reports: ${RETAIL_SIM_REPORTS_DIR}"
  echo ""
}
