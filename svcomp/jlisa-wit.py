#!/usr/bin/env python3
# jlisa-wit: SV-COMP wrapper for the jLISA Witness Validator.
#
# Bridges the BenchExec calling convention to the Java validator:
#
#   jlisa-wit --witness <witness.graphml|.yml> --property <file.prp> INPUT...
#
# where INPUT... are the task's input files as BenchExec passes them (for Java tasks,
# the shared common/ directory and the benchmark directory).
#
# The last line printed on stdout is always one of
#
#   Witness Correct        -> witness confirmed  (BenchExec: false)
#   Witness Spurious       -> witness rejected   (BenchExec: true)
#   Could not validate     -> no verdict         (BenchExec: unknown)
#
# A missing witness or an unsupported property is an error: message on stderr, exit code 1.
# Only the Python 3 standard library is used.
# Only valid-assert is supported: the validator does not yet distinguish
# no-runtime-exception violations from assertion failures.

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

VERSION = "1.0"
MAIN_CLASS = "it.unive.jlisa.witness.validator.Main"
VERDICTS = ("Witness Correct", "Witness Spurious", "Could not validate")
BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.realpath(__file__)))
LIB_DIR = os.path.join(BASE_DIR, "lib")


def parse_arguments():
    parser = argparse.ArgumentParser(prog="jlisa-wit", description="jLISA Witness Validator")
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument("--witness", required=True)
    parser.add_argument("--property", required=True)
    parser.add_argument("inputs", nargs="+")
    return parser.parse_args()

def main():
    args = parse_arguments()

    if not os.path.isfile(args.witness):
        print("witness file not found: " + args.witness, file=sys.stderr)
        sys.exit(1)
    
    with open(args.property) as f:
        if "G assert" not in f.read():
            print("unsupported property: " + args.property, file=sys.stderr)
            sys.exit(1)
    
    java = os.path.join(os.environ["JAVA_HOME"], "bin", "java") if "JAVA_HOME" in os.environ else "java"

    with tempfile.TemporaryDirectory(prefix="jlisa-wit-") as workdir:
        copies = []
        for i, path in enumerate(args.inputs):
            dest = os.path.join(workdir, str(i), os.path.basename(os.path.normpath(path)))
            shutil.copytree(path, dest)
            copies.append(os.path.relpath(dest, workdir))
        task_file = os.path.join(workdir, os.path.basename(copies[-1]) + ".yml")
        with open(task_file, "w") as f:
            f.write("input_files:\n" + "".join("  - '%s/'\n" % c for c in copies))

        cmd = [java, "--add-modules", "jdk.jdi", "-cp", os.path.join(LIB_DIR, "*"), MAIN_CLASS,
               "--witness", os.path.abspath(args.witness), "--benchmark", task_file]
        out = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True).stdout

    verdicts = [line.strip() for line in out.splitlines() if line.strip() in VERDICTS]
    print(verdicts[-1] if verdicts else "Could not validate")


if __name__ == "__main__":
    main()
