from inline_snapshot import snapshot

from lambda_calc.core import alpha_equiv, get_env, all_beta_reductions, is_valid_reduction, is_simple
from lambda_calc.parser import parse
from lambda_calc.ast import Var, Fun, App


def test_get_env():
    f = parse('λx. λy.x (λz.wy)')
    #          ^f  ^g    ^h
    env = get_env(f)
    assert isinstance(f, Fun)
    g = f.body
    assert isinstance(g, Fun)
    g_body = g.body
    assert isinstance(g_body, App)
    x = g_body.fun
    assert isinstance(x, Var)
    assert env[id(x)][1] == f
    h = g_body.arg
    assert isinstance(h, Fun)
    h_body = h.body
    assert isinstance(h_body, App)
    w = h_body.fun
    assert isinstance(w, Var)
    # w is free
    assert env[id(w)][1] is None
    y = h_body.arg
    assert isinstance(y, Var)
    assert env[id(y)][1] == g


def test_alpha_equiv():
    assert alpha_equiv(parse('λx.x'), parse('λy.y'))
    assert not alpha_equiv(parse('λx.x'), parse('λy.x'))
    assert not alpha_equiv(parse('x'), parse('y'))
    assert alpha_equiv(parse('λxy.xy'), parse('λyx.yx'))
    assert not alpha_equiv(parse('λxy.xy'), parse('λyx.xy'))
    # explicit currying should work
    assert alpha_equiv(parse('λxy.xy'), parse('λx.λy.xy'))
    assert alpha_equiv(parse('λxy.xy'), parse('λy.λx.yx'))

    # source: week3 lambda calculus guide pdf
    assert alpha_equiv(parse('λa.λb.abb'), parse('λb.λa.baa'))
    assert not alpha_equiv(parse('λa.λb.abb'), parse('λi.λj.jji'))
    assert not alpha_equiv(parse('λx.xλy.x'), parse('λe.eλf.f'))
    assert alpha_equiv(parse('λx.xλy.x'), parse('λe.eλf.e'))


def test_all_beta_reductions():
    assert (list(map(str, all_beta_reductions(parse('(λxf.fx)(λz.z)((λq.q)(λr.r))'))))
            == snapshot(["((λf.(f(λz.z)))((λq.q)(λr.r)))", "(((λxf.(fx))(λz.z))(λr.r))"]))

    # alpha renaming
    e = parse('(λf.λa.λb.fab)((ab)(cd))(λabcd.abcd)')
    reduced = next(all_beta_reductions(e))
    assert alpha_equiv(reduced, parse('(λm.λn.(((ab)(cd)))mn)(λabcd.abcd)'))
