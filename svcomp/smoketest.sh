#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

./jlisa-wit --version

check() {
  local witness="$1"
  shift
  local actual
  actual="$(./jlisa-wit --witness "test/$witness" --property test/valid-assert.prp test/common/ test/nondet-assert/ | tail -n 1)"
  echo "$witness: $actual"
  for expected in "$@"; do
    [ "$actual" = "$expected" ] && return 0
  done
  return 1
}

check witness-correct.graphml "Witness Correct"
check witness-spurious.graphml "Witness Spurious" "Could not validate"
