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

    e = parse('(λx.xy(λx.x))')
    assert alpha_equiv(e, parse('(λz.zy(λx.x))'))

    e = parse('(λa.a(λa.a)(λa.b))')
    assert alpha_equiv(e, parse('(λa.a(λa.a)(λa.b))'))
    assert alpha_equiv(e, parse('(λa.a(λb.b)(λa.b))'))


def test_all_beta_reductions():
    all_reductions = [reduc for (_, reduc) in list(all_beta_reductions(parse('(λxf.fx)(λz.z)((λq.q)(λr.r))')))]
    assert (list(map(str, all_reductions))
            == snapshot(["((λf.fλz.z)((λq.q)(λr.r)))", "(((λxf.fx)(λz.z))(λr.r))"]))

    # alpha renaming
    e = parse('(λf.λa.λb.fab)((ab)(cd))(λabcd.abcd)')
    reduc_type, reduced = next(all_beta_reductions(e))
    assert(reduc_type == 'alpha')
    assert alpha_equiv(reduced, parse('(λf.λa.λb.fab)((ab)(cd))(λabcd.abcd)'))

    # alpha renaming nested
    e = parse('(λxab.abλab.x(ab)(λab.ab))(ab)')
    reduc_type, reduced = next(all_beta_reductions(e))
    reduc_type2, reduced2 = next(all_beta_reductions(reduced))
    assert((reduc_type == 'alpha') & (reduc_type2 == 'beta'))
    assert alpha_equiv(reduced, e)

    #Beta Reductions now
    e = parse('(λcba.cba)c(λx.x)')
    reduc_type, reduced = next(all_beta_reductions(e))
    reduc_type2, reduced2 = next(all_beta_reductions(reduced))
    assert((reduc_type == 'beta') & (reduc_type2 == 'beta'))
    assert alpha_equiv(reduced, parse('((λba.((cb)a))(λx.x))'))
    assert alpha_equiv(reduced2, parse('(λa.((c(λx.x))a))'))
    assert alpha_equiv(reduced2, parse('(λa.c(λx.x)a)'))

    #test case
    e = parse('(λx.λy.λz.yzx)(λx.x)(λx.λy.yx)(λy.z)')
    reduc_type, reduced = next(all_beta_reductions(e))
    reduc_type2, reduced2 = next(all_beta_reductions(reduced))
    reduc_type3, reduced3 = next(all_beta_reductions(reduced2))
    reduc_type4, reduced4 = next(all_beta_reductions(reduced3))
    reduc_type5, reduced5 = next(all_beta_reductions(reduced4))
    reduc_type6, reduced6 = next(all_beta_reductions(reduced5))
    assert alpha_equiv(reduced6, parse('(λy.z)'))

    e = parse('(λabc.cba)c(λx.x)')
    reduc_type, reduced = next(all_beta_reductions(e))
    reduc_type2, reduced2 = next(all_beta_reductions(reduced))
    assert((reduc_type == 'beta') & (reduc_type2 == 'beta'))
    assert alpha_equiv(reduced2,parse('λc.c(λx.x)c'))

    e = parse('(λab.a)(λcd.d)(λef.e)')
    reduc_type, reduced = next(all_beta_reductions(e))
    reduc_type2, reduced2 = next(all_beta_reductions(reduced))
    assert((reduc_type == 'beta') & (reduc_type2 == 'beta'))
    assert alpha_equiv(reduced2, parse('λcd.d'))

    #Testing support for y'
    e =  parse("(λx'.x')(λz.yz)(z)")
    reduc_type, reduced = next(all_beta_reductions(e))
    assert alpha_equiv(reduced, parse('((λz.(yz))z)'))

    #Testing support for y'''
    e =  parse("(λx'''.x''')(λz.yz)(z)")
    reduc_type, reduced = next(all_beta_reductions(e))
    assert alpha_equiv(reduced, parse('((λz.(yz))z)'))

    #Testing support for y'
    e =  parse("(λx.x)(λz'.yz')(z)")
    reduc_type, reduced = next(all_beta_reductions(e))
    assert alpha_equiv(reduced, parse("((λz'.(yz'))z)"))
    reduc_type2, reduced2 = next(all_beta_reductions(reduced))
    assert alpha_equiv(reduced2, parse('yz'))

    



    



    
    

