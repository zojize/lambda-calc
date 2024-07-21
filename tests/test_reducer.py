from inline_snapshot import snapshot

from lambda_calc.core import alpha_equiv, get_env, all_beta_reductions, is_valid_reduction, is_simple
from lambda_calc.parser import parse
from lambda_calc.ast import Var, Fun, App
from lambda_calc.wrapper import Reducer



def test_reducer_success():
    #Test1
    parse_str = '(λx.x)(λz.yz)(z)'
    candidate_str = """
    (λx.x)(λz.yz)(z)\n
    b-> ((λz.yz)z)\n
    a-> ((λx.yx)z)\n
    b-> (y z)\n
    """
    reducer = Reducer(lambdastring = parse_str, candidatestring = candidate_str)
    assert(len(reducer.all_beta_reducs) == len(reducer.candidate_beta_reducs))
    assert(len(reducer.alpha_error_list) == 0)
    assert(len(reducer.beta_error_list) == 0)
    assert(len(reducer.general_error_list) == 0)

    #Test2 (Wrong alpha reduction)
    parse_str = '(λx.x)(λz.yz)(z)'
    candidate_str = """
    (λx.x)(λz.yz)(z)\n
    b-> ((λz.yz)z)\n
    a-> ((λx.yx)f)\n
    b-> (y z)\n
    """
    reducer2 = Reducer(lambdastring = parse_str, candidatestring = candidate_str)
    assert(len(reducer2.all_beta_reducs) == len(reducer2.candidate_beta_reducs))
    assert(len(reducer2.alpha_error_list) == 1)
    assert('Line 2 is not a valid alpha reduction' in reducer2.alpha_error_list)

    #Test2 (Wrong beta reduction)
    parse_str = '(λx.x)(λz.yz)(z)'
    candidate_str = """
    (λx.x)(λz.yz)(z)\n
    b-> ((λz.cz)z)\n
    a-> ((λx.yx)z)\n
    b-> (y z)\n
    """
    reducer3 = Reducer(lambdastring = parse_str, candidatestring = candidate_str)
    assert('Line 1 is not a valid beta reduction' in reducer3.beta_error_list)

if __name__ == "__main__":
    test_reducer_success()
