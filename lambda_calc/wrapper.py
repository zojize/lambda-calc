from typing import Generator, TypedDict, TypeAlias
from functools import reduce
import itertools
import string
from typing import List

from .core import alpha_equiv, get_env, all_beta_reductions, is_valid_reduction, is_simple
from .parser import parse
from .ast import Var, Fun, App, LambdaExpr


def check_candidate_str(candidatestring: str) -> List[str]:
    """
    Takes in the candidate string and returns a list of all possible errors
    """
    list_lines = candidatestring.strip().strip('\n').split('\n')
    list_lines = [line for line in list_lines if line != '']
    error_lines = []
    if len(list_lines) == 0:
        raise(Exception("There are no lines"))

    #Parse the first lambda expression
    try:
        prev_line = parse(list_lines[0])
    except:
        Raise(Exception("Line 0: Cannot parse initial lambda expression"))
    
    #Iterate through the line numbers
    for line_num in range(1, len(list_lines)):
        line = list_lines[line_num]
        line = line.strip().replace(" ", "")
        #Tag the candidate string (alpha or beta)
        if 'a->' in line:
            line_lambda_exp = line.replace('a->', '')
            try:
                reduced_line = parse(line_lambda_exp)
            except:
                #Line cannot be parsed
                error_lines.append(f'Line {line_num} could not be parsed')
                prev_line = reduced_line
                continue
            #This is an alpha reduction step. Check if the prev line is alpha equivalent to the current line
            check_alpha_reduc = alpha_equiv(prev_line, reduced_line)
            if not check_alpha_reduc:
                #Alpha reduction is invalid.
                error_lines.append(f'Line {line_num} is not a valid alpha reduction')
            else:
                #Previous line will only be set to current line if alpha reduction check is successful
                prev_line = reduced_line

        elif 'b->' in line:
            line_lambda_exp = line.replace('b->', '')
            try:
                reduced_line = parse(line_lambda_exp)
            except:
                #Line cannot be parsed
                error_lines.append(f'Line {line_num} could not be parsed')
                prev_line = reduced_line
                continue
            #check that the current reduced line is not the same as the previous line to make sure it is needed
            prev_beta_reduc = list(all_beta_reductions(prev_line))
            check_prev_beta_reduc = any(alpha_equiv(prev_reduc, reduced_line) for prev_reduc in prev_beta_reduc)
            if not check_prev_beta_reduc:
                error_lines.append(f'Line {line_num} is not a valid beta reduction')
            else:
                #Previous line will only be set to current line if beta reduction check is successful
                prev_line = reduced_line
    return error_lines

