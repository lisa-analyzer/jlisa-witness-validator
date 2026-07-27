#!/usr/bin/env python3
"""
BenchExec tool-info module for the jLISA Witness Validator.

This module describes how BenchExec should invoke the validator JAR so that
witness validation results can be included in SV-COMP score tables.

Usage (standalone, for manual testing):
    python3 validator.py --witness witness.graphml benchmark-directory/

BenchExec integration:
    Configure this file as the tool-info module in the benchmark XML:
        <tool name="jlisa-witness-validator" module="validator"/>

Output contract (stdout → BenchExec result mapping):
    "Witness Correct"    → confirmed
    "Witness Spurious"   → unknown
    "Could not validate" → unknown
"""

import os
import subprocess
import sys


# ---------------------------------------------------------------------------
# Standalone invocation (for manual testing without BenchExec)
# ---------------------------------------------------------------------------

def _run_standalone(args):
    """Thin wrapper for interactive / CI use outside BenchExec."""
    import argparse
    parser = argparse.ArgumentParser(description="jLISA Witness Validator")
    parser.add_argument("--witness", required=True, metavar="FILE",
                        help="Witness file (.graphml or .yaml)")
    parser.add_argument("--java", default=None, metavar="PATH",
                        help="Java executable (default: java on PATH)")
    parser.add_argument("--extra-sources", default=None, metavar="DIR",
                        help="Root directory of extra sources to compile (e.g. SV-COMP common/)")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable verbose logging")
    parser.add_argument("benchmark_dir", metavar="BENCHMARK_DIR",
                        help="Directory containing the Java benchmark")
    parsed = parser.parse_args(args)

    executable = _find_launcher_script() or _find_validator_jar()
    cmd = _build_command(executable, parsed.witness, parsed.benchmark_dir,
                         parsed.java, parsed.verbose, parsed.extra_sources)
    result = subprocess.run(cmd, capture_output=False)
    sys.exit(result.returncode)


def _find_validator_jar():
    """Locate the validator JAR relative to this script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Gradle application distribution layout
    lib_dir = os.path.join(script_dir, "build", "install",
                           "jlisa-witness-validator", "lib")
    if os.path.isdir(lib_dir):
        for f in os.listdir(lib_dir):
            if f.startswith("jlisa-witness-validator") and f.endswith(".jar"):
                return os.path.join(lib_dir, f)
    # Gradle build output fallback
    libs_dir = os.path.join(script_dir, "build", "libs")
    if os.path.isdir(libs_dir):
        for f in os.listdir(libs_dir):
            if f.endswith(".jar") and "sources" not in f and "javadoc" not in f:
                return os.path.join(libs_dir, f)
    raise FileNotFoundError(
        "Cannot find validator JAR. Run './gradlew installDist' first.")


def _find_launcher_script():
    """Return the path to the generated launcher script (Unix)."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    launcher = os.path.join(script_dir, "build", "install",
                            "jlisa-witness-validator", "bin",
                            "jlisa-witness-validator")
    if os.path.isfile(launcher):
        return launcher
    return None


def _build_command(jar_or_launcher, witness, benchmark_dir, java_exec, verbose,
                   extra_sources=None):
    """Build the command list to invoke the validator."""
    if jar_or_launcher.endswith(".sh") or not jar_or_launcher.endswith(".jar"):
        # Using the Gradle-generated launcher script (includes --add-modules jdk.jdi)
        cmd = [jar_or_launcher]
    else:
        # Direct JAR invocation — must include --add-modules jdk.jdi explicitly
        java_bin = java_exec or "java"
        cmd = [java_bin, "--add-modules", "jdk.jdi", "-jar", jar_or_launcher]

    cmd += ["--witness", witness, "--benchmark-dir", benchmark_dir]
    if java_exec:
        cmd += ["--java", java_exec]
    if extra_sources:
        cmd += ["--extra-sources", extra_sources]
    if verbose:
        cmd.append("--verbose")
    return cmd


# ---------------------------------------------------------------------------
# BenchExec tool-info module interface
# ---------------------------------------------------------------------------

class Tool:
    """BenchExec tool-info descriptor for jlisa-witness-validator."""

    TOOL_NAME = "jLISA Witness Validator"

    def name(self):
        return self.TOOL_NAME

    def version(self, executable):
        return "1.0"

    def executable(self, tool_locator=None):
        """Return the path to the launcher script (preferred) or the JAR."""
        launcher = _find_launcher_script()
        if launcher:
            return launcher
        return _find_validator_jar()

    def program_files(self, executable):
        return [executable]

    def cmdline(self, executable, options, task, rlimits):
        """
        Build the command line BenchExec will execute.

        :param executable:  path returned by :meth:`executable`
        :param options:     list of extra options from the benchmark XML
        :param task:        benchexec.tool_wrapper.Task object with the task info
        :param rlimits:     resource limits (unused)
        """
        # Extract witness file from task options (passed via benchmark XML)
        witness = None
        benchmark_dir = None

        # Try to read witness and input directory from task
        if hasattr(task, "options") and task.options:
            opts = task.options
            for i, opt in enumerate(opts):
                if opt == "--witness" and i + 1 < len(opts):
                    witness = opts[i + 1]
                if opt == "--benchmark-dir" and i + 1 < len(opts):
                    benchmark_dir = opts[i + 1]

        if witness is None and hasattr(task, "input_files") and task.input_files:
            # Heuristic: use first input file as witness
            witness = task.input_files[0]

        if benchmark_dir is None and hasattr(task, "input_files_base_dir"):
            benchmark_dir = task.input_files_base_dir

        cmd = [executable]
        if witness:
            cmd += ["--witness", witness]
        if benchmark_dir:
            cmd += ["--benchmark-dir", benchmark_dir]
        cmd += options
        return cmd

    def determine_result(self, run):
        """
        Map validator stdout to a BenchExec result category.

        :param run: benchexec run object with output attribute
        :return: BenchExec result string
        """
        output = getattr(run, "output", [])
        if isinstance(output, (list, tuple)):
            text = "\n".join(str(line) for line in output)
        else:
            text = str(output)

        if "Witness Correct" in text:
            return "confirmed"
        if "Witness Spurious" in text or "Could not validate" in text:
            return "unknown"
        return "unknown"


# ---------------------------------------------------------------------------
# Entry point for standalone use
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    _run_standalone(sys.argv[1:])
