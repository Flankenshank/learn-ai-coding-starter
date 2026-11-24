import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INTERPRETER = ROOT / "sloperator.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(INTERPRETER), *args], capture_output=True, encoding="utf-8"
    )


def test_runs_a_file():
    completed = run_cli(str(ROOT / "examples/hello.slop"))
    assert completed.returncode == 0
    assert completed.stdout == "hello, slop\n"
    assert completed.stderr == ""


def test_error_goes_to_stderr_after_earlier_output(tmp_path: Path):
    program = tmp_path / "boom.slop"
    program.write_text("hallucinate(“before”)✨\nhallucinate(missing)✨\n", encoding="utf-8")
    completed = run_cli(str(program))
    assert completed.returncode == 1
    assert completed.stdout == "before\n"
    assert completed.stderr == "SlopLang runtime error at line 2: undefined variable 'missing'\n"
    assert "Traceback" not in completed.stderr


def test_check_flag_validates_without_executing(tmp_path: Path):
    program = tmp_path / "ok.slop"
    program.write_text("hallucinate(“should not run”)✨\n", encoding="utf-8")
    completed = run_cli("--check", str(program))
    assert completed.returncode == 0
    assert completed.stdout == ""
    assert completed.stderr == ""


def test_check_flag_reports_syntax_errors(tmp_path: Path):
    program = tmp_path / "bad.slop"
    program.write_text("slop x = 1", encoding="utf-8")
    completed = run_cli("--check", str(program))
    assert completed.returncode == 1
    assert completed.stdout == ""
    assert completed.stderr == (
        "SlopLang syntax error at line 1: expected ✨ after variable declaration, "
        "but reached end of file\n"
    )


def test_check_flag_ignores_runtime_errors(tmp_path: Path):
    program = tmp_path / "runtime.slop"
    program.write_text("hallucinate(missing)✨\n", encoding="utf-8")
    completed = run_cli("--check", str(program))
    assert completed.returncode == 0
    assert completed.stdout == ""
    assert completed.stderr == ""


def test_check_flag_accepts_the_path_before_the_flag():
    completed = run_cli(str(ROOT / "examples/hello.slop"), "--check")
    assert completed.returncode == 0
    assert completed.stdout == ""
    assert completed.stderr == ""


def test_missing_file_and_usage():
    usage = run_cli()
    assert usage.returncode == 2
    assert "--check" in usage.stderr
    assert run_cli("--check").returncode == 2
    missing = run_cli(str(ROOT / "nope.slop"))
    assert missing.returncode == 2
    assert "could not read" in missing.stderr
