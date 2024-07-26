from inline_snapshot import snapshot

from lambda_calc.core import alpha_equiv, get_env, all_beta_reductions, is_valid_reduction, is_simple
from lambda_calc.parser import parse
from lambda_calc.ast import Var, Fun, App
from lambda_calc.wrapper import check_candidate_str


def test_reducer_success():
    # Test1
    candidate_str = """
    (λx.x)(λz.yz)(z)
    b-> ((λz.yz)z)
    b-> (y z)
    """
    errors = check_candidate_str(candidate_str, '(λx.x)(λz.yz)(z)')
    assert not errors

    # Test2 (Wrong alpha reduction)
    candidate_str = """
    (λx.x)(λz.yz)(z)
    b-> ((λz.yz)z)
    a-> ((λx.yx)f)
    b-> (y z)
    """
    errors = check_candidate_str(candidate_str, '(λx.x)(λz.yz)(z)')
    assert errors == snapshot(["Line 3: Alpha reduction is not valid"])

    # Test3 (Wrong beta reduction)
    candidate_str = """
    (λx.x)(λz.yz)(z)
    b-> ((λz.cz)z)
    b-> (y z)
    """
    errors = check_candidate_str(candidate_str, '(λx.x)(λz.yz)(z)')
    assert errors == snapshot(["Line 2: Invalid beta reduction"])

    # Test4 (Invalid parsing: Missing brackets in alpha reduction for line2)
    candidate_str = """
    (λx.x)(λy.y)(λz.yz)(z)
    b-> (λy.y)(λz.yz)(z)
    b-> ((λz.cz)z
    b-> (y z)
    """
    errors = check_candidate_str(candidate_str, '(λx.x)(λy.y)(λz.yz)(z)')
    assert errors == snapshot(["Line 3: Could not parse lambda expression"])

    # Test5
    candidate_str = """
    (λx.x)(λz.yz)(z)
    b-> ((λz.yz)z)
    a-> ((λx.yx)z)
    b-> (y z)
    """
    errors = check_candidate_str(candidate_str, '(λx.x)(λz.yz)(z)')
    assert errors == snapshot(["Line 3: Alpha reduction not necessary"])

    # Test6 (Adding unnecessary lines to a simple expression)
    candidate_str = """
    (λx.x)(λz.yz)(z)
    b-> ((λz.yz)z)
    a-> ((λx.yx)z)
    b-> (y z)
    b-> (y z)
    """
    errors = check_candidate_str(candidate_str, '(λx.x)(λz.yz)(z)')
    assert errors == snapshot(["Line 3: Alpha reduction not necessary", "Line 5: Invalid beta reduction"])
