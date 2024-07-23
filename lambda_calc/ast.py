from dataclasses import dataclass
from typing import TypeAlias

__all__ = ['LambdaExpr', 'Var', 'Fun', 'App', 'compile']

LambdaExpr: TypeAlias = 'Var | Fun | App'


@dataclass
class Var:
    name: str

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f"Var({self.name!r})"
    
    def __format__(self, format_spec: str) -> str:
        if format_spec != 'terse':
            return super().__format__(format_spec)
        return self.name
            

    def __str__(self):
        return self.name


@dataclass
class Fun:
    args: list[Var]
    body: LambdaExpr

    def __hash__(self):
        return hash((tuple(self.args), self.body))

    def __repr__(self):
        return f"Fun([{','.join(map(repr, self.args))}],{self.body!r})"

    def __format__(self, format_spec: str) -> str:
        if format_spec != 'terse':
            return super().__format__(format_spec)
        return f"λ{''.join(map(str, self.args))}.{self.body:terse}"

    def __str__(self):
        return f"(λ{''.join(map(str, self.args))}.{self.body:terse})"

    def __call__(self, *args, **_):
        if not hasattr(self, 'fun'):
            self.__fun = eval(compile(self))
        return self.__fun(*args)


@dataclass
class App:
    fun: LambdaExpr
    arg: LambdaExpr

    def __hash__(self):
        return hash((self.fun, self.arg))

    def __repr__(self):
        return f"App({self.fun!r},{self.arg!r})"

    def __format__(self, format_spec: str) -> str:
        if format_spec != 'terse':
            return super().__format__(format_spec)
            
        match self.fun, self.arg:
            case (App(), Var()) | (App(), Fun()) | (Var(), Fun()):
                return f"{self.fun:terse}{self.arg:terse}"
            case (App(), App()):
                return f"{self.fun:terse}{self.arg}"
            case (Fun(), _): 
                return f"{self.fun}{self.arg:terse}"
            case _:
                return f"{self.fun}{self.arg}"

    def __str__(self):
        return f"({self.fun}{self.arg})"


def compile(expr: LambdaExpr):
    match expr:
        case Var(name):
            return name
        case Fun(args, body):
            return f"lambda {','.join(arg.name for arg in args)}: {compile(body)}"
        case App(fun, arg):
            return f"({compile(fun)})({compile(arg)})"
