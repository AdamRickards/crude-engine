#!/usr/bin/env bash
# Offline / PR proofs. No switch required. Same script humans and Actions run.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
PY="${PYTHON:-python3}"

pass=0
fail=0
skip=0

run() {
  local name="$1"
  shift
  echo
  echo "════════════════════════════════════════"
  echo "PROOF  $name"
  echo "CMD    $*"
  echo "════════════════════════════════════════"
  if "$@"; then
    echo "RESULT PASS  $name"
    pass=$((pass + 1))
    return 0
  else
    echo "RESULT FAIL  $name"
    fail=$((fail + 1))
    return 1
  fi
}

echo "crude-engine offline CI  (root=$ROOT)"

run "import-smoke" "$PY" -c "from crude_engine import FeatureEngine; print(FeatureEngine)"

if [[ -f local/generator/validate_schemas.py ]]; then
  run "validate-schemas" "$PY" local/generator/validate_schemas.py --errors
else
  echo "SKIP  validate-schemas (local/generator/validate_schemas.py missing)"
  skip=$((skip + 1))
fi

run "program-files" "$PY" scripts/generate_status.py --check
run "snmp-loop-drain" "$PY" tests/test_snmp_loop_drain.py
run "principles" "$PY" scripts/check_principles.py

# Catalogue proofs are the 2.10 exit. They are expected red in cycle 0
# until the generator/schema work lands. Tracked separately so a red
# catalogue does not hide a broken import.
echo
echo "── release proofs (may be red until 2.10) ──"
cat_rc=0
"$PY" scripts/check_catalogue.py || cat_rc=$?
if [[ $cat_rc -eq 0 ]]; then
  echo "RESULT PASS  catalogue"
  pass=$((pass + 1))
else
  echo "RESULT FAIL  catalogue  (cycle 0 expected until Docs-* tasks close)"
  fail=$((fail + 1))
fi

echo
echo "════════════════════════════════════════"
echo "offline: $pass passed, $fail failed, $skip skipped"
echo "════════════════════════════════════════"

# Required-to-merge today: import, program files, validator (if present).
# Principles + catalogue stay visible but do not fail the script until
# we flip REQUIRE_RELEASE_PROOFS=1 (2.10 exit).
if [[ "${REQUIRE_RELEASE_PROOFS:-0}" == "1" ]]; then
  [[ $fail -eq 0 ]]
  exit $?
fi

# Soft lane (cycle 0): fail only on import + program files.
# Validator / principles / catalogue are scored above and stay red
# until their cycle tasks close. Flip REQUIRE_RELEASE_PROOFS=1 for 2.10.
soft=0
"$PY" -c "from crude_engine import FeatureEngine" || soft=1
"$PY" scripts/generate_status.py --check || soft=1
"$PY" tests/test_snmp_loop_drain.py || soft=1
exit $soft
