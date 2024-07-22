import pytest
from inline_snapshot import snapshot

from lambda_calc.parser import parse
from lambda_calc.ast import Var, Fun, App


def test_parse_success():
    """Test parsing of valid lambda expressions."""
    assert repr(parse('x')) == snapshot("Var('x')")
    assert repr(parse('λx.x')) == snapshot("Fun([Var('x')],Var('x'))")
    assert repr(parse('λx.λy.x')) == snapshot("Fun([Var('x')],Fun([Var('y')],Var('x')))")
    assert repr(parse('λx.λy.λz.xz(yz)')) == snapshot("Fun([Var('x')],Fun([Var('y')],Fun([Var('z')],App(App(Var('x'),Var('z')),App(Var('y'),Var('z'))))))")
    assert repr(parse('λxyz.xz(yz)')) == snapshot("Fun([Var('x'),Var('y'),Var('z')],App(App(Var('x'),Var('z')),App(Var('y'),Var('z'))))")
    assert repr(parse('λx.λy.λz.xz(yz)(λw.w)')) == snapshot("Fun([Var('x')],Fun([Var('y')],Fun([Var('z')],App(App(App(Var('x'),Var('z')),App(Var('y'),Var('z'))),Fun([Var('w')],Var('w'))))))")
    assert repr(parse('λx.λy.λz.xz(yz)(λw.ww)')) == snapshot("Fun([Var('x')],Fun([Var('y')],Fun([Var('z')],App(App(App(Var('x'),Var('z')),App(Var('y'),Var('z'))),Fun([Var('w')],App(Var('w'),Var('w')))))))")
    assert repr(parse('λx.λy.λz.xz(y z)(λw.ww)(λv.vv)')) == snapshot("Fun([Var('x')],Fun([Var('y')],Fun([Var('z')],App(App(App(App(Var('x'),Var('z')),App(Var('y'),Var('z'))),Fun([Var('w')],App(Var('w'),Var('w')))),Fun([Var('v')],App(Var('v'),Var('v')))))))")
    assert repr(parse('λf.(λx.f(xx))(λx.f(xx))')) == snapshot("Fun([Var('f')],App(Fun([Var('x')],App(Var('f'),App(Var('x'),Var('x')))),Fun([Var('x')],App(Var('f'),App(Var('x'),Var('x'))))))")
    assert repr(parse('λx.(λy.(λz.((x(z(yz))))))')) == snapshot("Fun([Var('x')],Fun([Var('y')],Fun([Var('z')],App(Var('x'),App(Var('z'),App(Var('y'),Var('z')))))))")
    assert repr(parse('(λxf.fx)(λz.z)((λq.q)(λr.r))')) == snapshot("App(App(Fun([Var('x'),Var('f')],App(Var('f'),Var('x'))),Fun([Var('z')],Var('z'))),App(Fun([Var('q')],Var('q')),Fun([Var('r')],Var('r'))))")
    assert repr(parse('λf.(λx.f(xx))(λx.f(xx))')) == snapshot("Fun([Var('f')],App(Fun([Var('x')],App(Var('f'),App(Var('x'),Var('x')))),Fun([Var('x')],App(Var('f'),App(Var('x'),Var('x'))))))")


def test_parse_fail():
    """Test parsing of invalid lambda expressions"""
    with pytest.raises(Exception):
        # empty
        parse('')
    with pytest.raises(Exception):
        # unbalanced parentheses
        parse('λx.xz(yz')
    with pytest.raises(Exception):
        # invalid character
        parse('λx.xz(yz)!')
    with pytest.raises(Exception):
        # repeated arguments
        parse('λxx.x')


