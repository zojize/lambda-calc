from inline_snapshot import snapshot

from lambda_calc.core import alpha_equiv, get_env, all_beta_reductions, is_valid_reduction, is_simple
from lambda_calc.parser import parse
from lambda_calc.ast import Var, Fun, App
from lambda_calc.wrapper import check_candidate_str



def test_reducer_success():
    #Test1
    candidate_str1 = """
    (λx.x)(λz.yz)(z)\n
    b-> ((λz.yz)z)\n
    a-> ((λx.yx)z)\n
    b-> (y z)\n
    """
    errors1= check_candidate_str(candidate_str1)
    assert(len(errors1) == 0)

    #Test2 (Wrong alpha reduction)
    candidate_str2 = """
    (λx.x)(λz.yz)(z)\n
    b-> ((λz.yz)z)\n
    a-> ((λx.yx)f)\n
    b-> (y z)\n
    """
    errors2 = check_candidate_str(candidate_str2)
    assert('Line 2 is not a valid alpha reduction' in errors2)

    #Test3 (Wrong beta reduction)
    candidate_str3 = """
    (λx.x)(λz.yz)(z)\n
    b-> ((λz.cz)z)\n
    a-> ((λx.yx)z)\n
    b-> (y z)\n
    """
    errors3 = check_candidate_str(candidate_str3)
    assert('Line 1 is not a valid beta reduction' in errors3)


    #Test4 (Invalid parsing: Missing brackets in alpha reduction for line2)
    parse_str = '(λx.x)(λz.yz)(z)'
    candidate_str4= """
    (λx.x)(λz.yz)(z)\n
    b-> ((λz.cz)z)\n
    a-> (λx.yx)z)\n
    b-> (y z)\n
    """
    errors4= check_candidate_str(candidate_str4)
    assert('Line 2 could not be parsed' in errors4)

if __name__ == "__main__":
    test_reducer_success()
