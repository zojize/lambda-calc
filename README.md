
# lambda_calc

`lambda_calc` parses, reduces and compares alpha-equivalence of lambda calculus expressions.

## Usage

See `lambda_calc.core/parser` and `tests`

### Library

There are several files in `lambda_calc`:
+ `ast.py`: Contains the dataclasses `Var`, `Fun`, `App`
+ `repl.py`: A simple lambda calculus repl in the terminal
+ `parser.py`: Contains the structure for a lambda expression
    - Note that the parser allows for variables like `x`, ``x` `` and even ```x`` ```
    - So lambda expressions like : `λx'.x'`, `λx.x` and `λx''.x''` will be accepted by the parser
+ `core.py`: Contains the functions used for alpha reduction and beta reduction
+ `wrapper.py`: Contains the function `check_candidate_str(candidatestring: str) -> List[str]` that can be called to parse a candidate string\

The python code below shows how `check_candidate_str` can be used:
~~~python
candidate_str = """
(λx.x)(λz.yz)(z)\n
b-> ((λz.yz)z)\n
a-> ((λx.yx)z)\n
b-> (y z)\n
"""
errors = check_candidate_str(candidate_str)
~~~

* `line 0`: Contains the lambda expression to parse: `(λx.x)(λz.yz)(z)`
* A beta reduction can be initiated in a line starting with `b ->` like in `line 1`: `b-> ((λz.yz)z)`
* An alpha reduction can be initiated in a starting with `a->` like in `line 2`: `a-> ((λx.yx)z)`
* `check_candidate_str` returns a list of errors detected in the candidate string\

**List of Errors:**
+ `Cannot parse initial lambda expression`: The lambda expression in `line 0` cannot be parsed
+  `Line x could not be parsed`: The reduction in `line x` cannot be parsed
+  `Line x: Invalid reduction type`: The reduction in `line x` does not start with `a->` or `b->`
+ `Line x: Alpha reduction is not valid`: The reduction in `line x` is not alpha equivalent to `line x-1`
+ `Line x: Alpha reduction not necessary`: The alpha reduction in `line x` is not needed
+ `Line x: Invalid beta reduction`: The reduction in `line x` is invalid and is not alpha equivalent to `line x-1`
+ `Last expression is not a simple expression`: The last line in the candidate string is not a simple expression



