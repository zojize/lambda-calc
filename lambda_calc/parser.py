from functools import partial, reduce
from parsy import Parser, forward_declaration, generate, fail, regex, string, seq
from .ast import LambdaExpr, Var, Fun, App
from typing import Callable

__all__ = ['parse']

ws = regex(r'\s*').desc('whitespace')
def lexeme(p: Parser) -> Parser: return p << ws


lambda_ = lexeme(regex(r'[λ\\L]')).desc('lambda')
var = lexeme(regex(r"[a-z]\'*",)).map(Var).desc('variable')
dot = lexeme(string('.')).desc('dot')
lparen = lexeme(string('(')).desc('left paren')
rparen = lexeme(string(')')).desc('right paren')


@generate
def args():
    vars = yield var.at_least(1)
    if len(set(vars)) != len(vars):
        # !this error doesn't actually show up, fix it somehow
        return fail('duplicate variable names')
    return vars


# todo: better error messages
lambda_expr = forward_declaration()
application = forward_declaration()

atom = (lparen >> lambda_expr << rparen) | var
abstraction = (seq(lambda_ >> args << dot, lambda_expr)
               .combine(Fun).desc('function'))
application.become((atom | abstraction)
                   .at_least(1).map(partial(reduce, App)))
lambda_expr.become(ws >> (
    application
    | abstraction
))

parse: Callable[[str], LambdaExpr] = lambda_expr.parse
