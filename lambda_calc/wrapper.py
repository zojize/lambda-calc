from typing import Generator, TypedDict, TypeAlias
from functools import reduce
import itertools
import string

from .core import alpha_equiv, get_env, all_beta_reductions, is_valid_reduction, is_simple, return_reducs_only
from .parser import parse
from .ast import Var, Fun, App, LambdaExpr


def check_candidate_str(candidatestring: str):
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

    reduced_line = None
    #Iterate through the line numbers
    for line_num in range(1, len(list_lines)):
        line = list_lines[line_num]
        line = line.strip().replace(" ", "")
        #Reduce the previous line
        prev_line_reduced = list(all_beta_reductions(prev_line))
        prev_line_reduc_list = return_reducs_only(prev_line_reduced)
        #Previous line was a simple expression. Subsequent lines are unecessary now
        if len(prev_line_reduc_list) == 0:
            error_lines.append(f'Line {line_num} onwards is unnecessary')
            break
        #Get the reduction type
        expected_reduc_type = prev_line_reduced[0][0]

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
            #Verify that alpha reduction is expected
            if expected_reduc_type != 'alpha':
                error_lines.append(f'Line {line_num} alpha reduction is not necessary')

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
            if not is_valid_reduction(expr = prev_line, reduction = reduced_line) :
                error_lines.append(f'Line {line_num} is not a valid beta reduction')
            else:
                #Previous line will only be set to current line if beta reduction check is successful
                prev_line = reduced_line
            
            #Verify that beta reduction is expected
            if expected_reduc_type != 'beta':
                error_lines.append(f'Line {line_num} alpha reduction is not necessary')

    #Check if last expression is a simple expression
    if (reduced_line is not None ) and not is_simple(reduced_line):
        error_lines.append(f'Line {len(list_lines) - 1} is not a simple expression')
    return error_lines

