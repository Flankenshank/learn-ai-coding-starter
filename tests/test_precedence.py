from sloperator.runner import run_source


def run(source: str) -> str:
    result = run_source(source)
    assert result.stderr == "", result.stderr
    return result.stdout


def test_multiplication_binds_tighter_than_addition():
    # (2 + 3) * 4 would be 20; 2 + (3 * 4) is 14.
    assert run("hallucinate(2 + 3 * 4)✨") == "14\n"


def test_multiplication_binds_tighter_on_either_side_of_addition():
    assert run("hallucinate(3 * 4 + 2)✨") == "14\n"


def test_multiplication_binds_tighter_than_subtraction():
    assert run("hallucinate(10 - 2 * 3)✨") == "4\n"
