"""What all the runners share, whatever the language."""

import os
import resource
import signal
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class CompileResult:
	"""The result of a compilation.

	ok tells whether it worked, output is what the compiler printed (errors
	and warnings), and binary is the program built, or None if it failed.
	objects are the compiled student files (.o), without any test main.
	"""
	ok: bool
	output: str
	binary: Path | None
	objects: tuple[Path, ...] = ()

@dataclass(frozen=True)
class RunResult:
	"""What happened when the student's program ran on one test.

	stdout is what it printed (bytes, as a program prints them), exit_code
	its exit code if it ended by itself, signal the name of the signal that
	killed it ("SIGSEGV"...), and timed_out tells whether it took too long.
	"""
	stdout: bytes
	exit_code: int | None
	signal: str | None
	timed_out: bool

# Seconds a program may run on one test before it is stopped.
DEFAULT_TIMEOUT = 5.0
# Bytes a program may print on one test: past this, the system stops it
# (signal SIGXFSZ), so that printing forever cannot fill the memory.
MAX_OUTPUT = 1_000_000

def run_command(argv, stdin="", timeout=DEFAULT_TIMEOUT, max_output=MAX_OUTPUT):
	"""Run `argv` with `stdin` as its standard input; return a RunResult.

	The input and output go through temporary files, not pipes: we wait for
	the program itself, so a child that keeps a pipe open cannot block us.
	The program runs in its own process group (start_new_session), and the
	whole group is stopped at the end: no child started with fork() is left
	running, whether the program ended by itself or timed out.
	"""
	with tempfile.TemporaryFile() as stdin_file, tempfile.TemporaryFile() as stdout_file:
		stdin_file.write(stdin.encode())
		stdin_file.seek(0)
		process = subprocess.Popen(
			argv, stdin=stdin_file, stdout=stdout_file, stderr=subprocess.DEVNULL,
			start_new_session=True,
			# Runs in the child just before the program starts.
			preexec_fn=lambda: resource.setrlimit(
				resource.RLIMIT_FSIZE, (max_output, max_output)
			),
		)
		try:
			process.wait(timeout=timeout)
			timed_out = False
		except subprocess.TimeoutExpired:
			timed_out = True
		_stop_group(process.pid)
		process.wait()
		stdout_file.seek(0)
		stdout = stdout_file.read()
	if timed_out:
		return RunResult(stdout, None, None, True)
	# A negative return code means "killed by a signal": -11 is SIGSEGV.
	if process.returncode < 0:
		return RunResult(stdout, None, signal.Signals(-process.returncode).name, False)
	return RunResult(stdout, process.returncode, None, False)

def _stop_group(group):
	"""Kill every process left in the process group `group`, if any."""
	try:
		# The group has the same number as the program that leads it.
		os.killpg(group, signal.SIGKILL)
	except ProcessLookupError:
		pass
