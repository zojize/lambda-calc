from .core import alpha_equiv, all_beta_reductions, is_simple
from .parser import parse


def check_candidate_str(candidate_string: str, initial_expr: str):
    '''Takes in the candidate string and returns a list of all possible errors'''
    lines = candidate_string.split('\n')

    error_lines: list[str] = []
    if not lines:
        error_lines.append("There are no lines")
        return error_lines

    prev_expr = None
    current_expr = None
    # Iterate through the line numbers
    for line_num in range(1, len(lines)):
        line = lines[line_num].strip()

        if not line:
            continue

        # Parse the first lambda expression
        if not prev_expr:
            try:
                prev_expr = parse(line)
            except:
                error_lines.append("Line 0: Cannot parse initial lambda expression")
                return error_lines

            if prev_expr != parse(initial_expr):
                error_lines.append("Line 0: Initial expression does not match")
                return error_lines

            continue

        if line.startswith('a->'):
            reduction_type = 'alpha'
        elif line.startswith('b->'):
            reduction_type = 'beta'
        else:
            error_lines.append(f'Line {line_num}: Invalid reduction type')
            break

        try:
            current_expr = parse(line[3:])
        except:
            error_lines.append(f'Line {line_num}: Could not parse lambda expression')
            break

        if reduction_type == 'alpha' and not alpha_equiv(prev_expr, current_expr):
            error_lines.append(f'Line {line_num}: Alpha reduction is not valid')
            break

        for reduced_reduction_type, reduced_expr in all_beta_reductions(prev_expr):
            if reduced_reduction_type == reduction_type and alpha_equiv(reduced_expr, current_expr):
                prev_expr = reduced_expr
                break
        else:
            if reduction_type == 'alpha':
                error_lines.append(f'Line {line_num}: Alpha reduction not necessary')
            else:
                error_lines.append(f'Line {line_num}: Invalid beta reduction')
                break
    else:
        if not current_expr:
            error_lines.append('No reduction found')
        elif not is_simple(current_expr):
            error_lines.append('Last expression is not a simple expression')

    return error_lines
