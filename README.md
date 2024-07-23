
# lambda_calc

`lambda_calc` parses, reduces and compares alpha-equivalence of lambda calculus expressions.

## Usage

See `lambda_calc.core/parser` and `tests`

### Library

`ast.py`: Contains the dataclasses `Var`, `Fun`, `App`
`repl.py`: A simple lambda calculus repl in the terminal
`parser.py`: Contains the structure for a lambda expression
`core.py`: Contains the functions used for alpha reduction and beta reduction
