#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

./jlisa-wit --version

check() {
  local witness="$1" expected="$2"
  local actual
  actual="$(./jlisa-wit --witness "test/$witness" --property test/valid-assert.prp test/common/ test/nondet-assert/ | tail -n 1)"
  echo "$witness: $actual"
  [ "$actual" = "$expected" ]
}

check witness-correct.graphml "Witness Correct"
check witness-spurious.graphml "Witness Spurious"
