from typing import Generator, Literal, TypeAlias, List
from functools import reduce
from .ast import Var, Fun, App, LambdaExpr
import string

__all__ = ['alpha_equiv', 'substitute', 'get_env', 'curry', 'alpha_rename',
           'all_beta_reductions', 'is_valid_reduction', 'is_simple']

# env map variable ids to itself and bounding functions
Env: TypeAlias = dict[int, tuple[Var, Fun | None]]


def get_env(expr: LambdaExpr) -> Env:
    '''returns a mapping of variable ids to its bounding functions, in context of expr'''
    def get_env_helper(expr: LambdaExpr, scope: dict[str, Fun]) -> Env:
        match expr:
            case Var(name):
                if name in scope:
                    return {id(expr): (expr, scope[name])}
                else:
                    return {id(expr): (expr, None)}
            case Fun(args, body):
                return get_env_helper(body, scope | {arg.name: expr for arg in args})
            case App(fun, arg):
                return get_env_helper(fun, scope) | get_env_helper(arg, scope)
    return get_env_helper(expr, {})


def curry(expr: LambdaExpr) -> LambdaExpr:
    '''desugar curried arguments in the expression'''
    match expr:
        case Var():
            return expr
        case Fun(args, body) if len(args) > 1:
            return reduce(lambda acc, arg: Fun([arg], acc), reversed(args[:-1]), Fun([args[-1]], curry(body)))
        case Fun(arg, body):
            body_ = curry(body)
            if body_ is body:
                return expr
            return Fun(arg, body_)
        case App(fun, arg):
            return App(curry(fun), curry(arg))


def alpha_equiv(e1: LambdaExpr, e2: LambdaExpr) -> bool:
    '''checks if two expressions are alpha equivalent'''
    e1 = curry(e1)
    e2 = curry(e2)

    env1 = get_env(e1)
    env2 = get_env(e2)

    def alpha_equiv_helper(
            e1: LambdaExpr,
            e2: LambdaExpr,
            cycle: list[tuple[LambdaExpr, LambdaExpr]] = []) -> bool:
        if any(e1 is e1_ and e2 is e2_ for e1_, e2_ in cycle):
            return True
        match e1, e2:
            # both variables
            case Var(name1), Var(name2):
                match env1[id(e1)], env2[id(e2)]:
                    # both free variables
                    case (_, None), (_, None):
                        return name1 == name2
                    # both bounded variables
                    case (_, Fun() as s1), (_, Fun() as s2):
                        return alpha_equiv_helper(s1, s2, cycle + [(e1, e2)])
                    # one free, one bounded
                    case _, _:
                        return False
            # both functions
            case Fun(args1, body1), Fun(args2, body2):
                return len(args1) == len(args2) and alpha_equiv_helper(body1, body2, cycle)
            # both applications
            case App(fun1, arg1), App(fun2, arg2):
                return alpha_equiv_helper(fun1, fun2, cycle) and alpha_equiv_helper(arg1, arg2, cycle)
            # different types
            case _, _:
                return False
    return alpha_equiv_helper(e1, e2)


def substitute(expr: LambdaExpr, to_replace: Var, replacement: LambdaExpr, fun: Fun, env: Env) -> LambdaExpr:
    '''substitute a variable with another expression in the given env'''
    def substitute_helper(expr: LambdaExpr) -> LambdaExpr:
        match expr:
            case Var(name):
                if name != to_replace.name:
                    return expr
                if env[id(expr)][1] is fun:
                    return replacement
                return expr
            case Fun(args, body):
                if any(arg.name == to_replace.name for arg in args):
                    return expr
                return Fun(args, substitute_helper(body))
            case App(fun_, arg):
                return App(substitute_helper(fun_), substitute_helper(arg))
    return substitute_helper(expr)


def vars_need_renaming(expr: LambdaExpr, free_vars: set[Var], to_replace: Var, fun: Fun, env: Env) -> list[tuple[int, str]]:
    '''returns a list of variables that need renaming to avoid name conflicts with free variables'''
    if not free_vars:
        return []

    def vars_need_renaming_helper(expr: LambdaExpr, scope: dict[str, list[int]]) -> list[tuple[int, str]]:
        match expr:
            case Var(name):
                if name == to_replace.name and env[id(expr)][1] is fun:
                    return [(fun, free.name) for free in free_vars for fun in scope.get(free.name, [])]
                # if env[id(expr)][1] == None and expr in free_vars:
                #     return [(fun, name) for fun in scope.get(name, [])]
                return []
            case Fun(args, body):
                return vars_need_renaming_helper(body, scope |
                                                 {arg.name: scope.get(arg.name, []) + [id(expr)] for arg in args})
            case App(fun_, arg):
                return vars_need_renaming_helper(fun_, scope) + vars_need_renaming_helper(arg, scope)
    return vars_need_renaming_helper(expr, {})


def alpha_rename(expr: LambdaExpr, vars_to_rename: list[tuple[int, str]], env: Env):
    '''rename variables in the expression to avoid name conflicts with free variables'''

    # Get all chars from a to z and from a' to z'
    available_names = iter(set(list(string.ascii_lowercase) + [char + "'" for char in list(string.ascii_lowercase)]) - {var.name for (var, _) in env.values()})

    def get_new_name(): return next(available_names)

    if not vars_to_rename:
        return expr

    def rename_helper(expr: LambdaExpr, rename_to: dict[str, str]) -> LambdaExpr:
        match expr:
            case Var(name):
                # if not a free variable and needs renaming
                if env[id(expr)][1] and name in rename_to:
                    return Var(rename_to[name])
                return expr
            case Fun(args, body):
                #! will error if name runs out
                new_names = {
                    arg.name: get_new_name() for arg in args if (id(expr), arg.name) in vars_to_rename
                }
                # no new names also means no renaming needed
                if not new_names:
                    return expr
                return Fun([Var(new_names.get(arg.name, arg.name)) for arg in args],
                           rename_helper(body, rename_to | new_names))
            case App(fun, arg):
                return App(rename_helper(fun, rename_to), rename_helper(arg, rename_to))
    return rename_helper(expr, {})


def all_beta_reductions(expr: LambdaExpr) -> Generator[tuple[Literal["alpha"] | Literal["beta"], LambdaExpr], None, None]:
    env = get_env(expr)

    def all_beta_reductions_helper(expr: LambdaExpr):
        match expr:
            case Fun(args, body):
                yield from ((t, Fun(args, body)) for t, body in all_beta_reductions_helper(body))
            case App(Fun(args, body) as fun, arg):
                to_replace, *tail = args
                arg_env = get_env(arg)
                arg_free_vars = {var for (var, env) in arg_env.values() if env is None}
                vars_to_rename = vars_need_renaming(body, arg_free_vars, to_replace, fun, env)
                if vars_to_rename:
                    # alpha-reduction
                    yield "alpha", App(Fun(args, alpha_rename(body, vars_to_rename, env)), arg)
                elif tail:
                    # beta-reduction
                    yield "beta", Fun(tail, substitute(body, to_replace, arg, fun, env))
                else:
                    # beta-reduction
                    yield "beta", substitute(body, to_replace, arg, fun, env)
                yield from ((t, App(fun, arg)) for t, arg in all_beta_reductions_helper(arg))
            case App(fun, arg):
                yield from ((t, App(fun, arg)) for t, fun in all_beta_reductions_helper(fun))
                yield from ((t, App(fun, arg)) for t, arg in all_beta_reductions_helper(arg))
            case _:
                # no need to reduce variables
                pass
    yield from all_beta_reductions_helper(expr)


def is_valid_reduction(expr: LambdaExpr, reduction: LambdaExpr) -> bool:
    return any(alpha_equiv(reduction, reduced) for _, reduced in all_beta_reductions(expr))


def is_simple(expr: LambdaExpr) -> bool:
    return not any(True for _ in all_beta_reductions(expr))


def return_reducs_only(beta_reduc: Generator) -> List[LambdaExpr]:
    reduc_list = [reduc for (_, reduc) in beta_reduc]
    return reduc_list
