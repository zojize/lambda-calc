import re
from .ast import App, Fun, LambdaExpr, Var
from .core import all_beta_reductions
from .parser import parse


def main():
    env: dict[str, LambdaExpr] = {}

    def eval(expr: LambdaExpr):
        match expr:
            case Var(name):
                return env.get(name, expr)
            case Fun():
                return expr
            case App(fun, arg):
                match eval(fun):
                    case Fun():
                        return eval(arg)
                    case _:
                        raise ValueError('Invalid application')

    binding_pattern = re.compile(r'(?P<name>[a-z]+)\s*=(?P<expr>.+)')
    reductions = []

    while True:
        try:
            user_input = input('λ> ').strip()

            if user_input.startswith(':r'):
                try:
                    index = int(user_input[2:])
                    expr = reductions[index]
                except Exception:
                    expr = parse(user_input[2:])
                reductions = list(all_beta_reductions(expr))
                if not reductions:
                    print('No reductions possible')
                else:
                    print("\n".join(f"{i}. {reduction}" for i, reduction in enumerate(reductions)))
                continue

            reductions = []
            if not user_input:
                continue

            if user_input == ':q':
                break

            match = binding_pattern.match(user_input)
            if match:
                name = match.group('name')
                expr = parse(match.group('expr'))
                env[name] = expr
                print(env)
                continue

            if user_input.startswith(':i'):
                expr = parse(user_input[2:])
                print(repr(expr))
                continue

            if user_input.startswith(':e'):
                expr = parse(user_input[2:])
                print(eval(expr))
                continue

            expr = parse(user_input)
            print(f'{expr:terse}')
        except Exception as e:
            print(e)
