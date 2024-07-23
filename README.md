
# lambda_calc

`lambda_calc` parses, reduces and compares alpha-equivalence of lambda calculus expressions.

## Usage

See `lambda_calc.core/parser` and `tests`

### Library

`ast.py`: Contains the dataclasses `Var`, `Func`, `App`\
`repl.py`: Contains the `eval` function\
`parser.py`: Contains the structure for a lambda expression\
`core.py`: Contains the functions used for alpha reduction and beta reduction\
