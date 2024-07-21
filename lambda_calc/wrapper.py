from typing import Generator, TypedDict, TypeAlias
from functools import reduce
import itertools
import string

from .core import alpha_equiv, get_env, all_beta_reductions, is_valid_reduction, is_simple
from .parser import parse
from .ast import Var, Fun, App


class Reducer:
    """
    Wrapper class that holds all the information of the reduced lambda expression
    
    lambdastring: Lambda string to evaluate
    candidatestring: prairelearn input string from candidate/student
    """

    alpha_error_list = []
    beta_error_list = []
    general_error_list = []

    def __init__(self, lambdastring : str, candidatestring : str):
        self.lambdastring = lambdastring
        self.candidatestring = candidatestring
        self.expr = parse(self.lambdastring)
        self.all_beta_reducs = self.store_all_reducs()
        self.candidate_beta_reducs = self.parse_candidate_str()
        #Check the beta reductions
        self.check_all_beta_reducs()

    def store_all_reducs(self):
        """
        To store all the reductions
        """
        reducs_list = []
        to_go = True
        current_expr = self.expr
        while to_go:
            try:
                curr_reduced = next(all_beta_reductions(current_expr))
                reducs_list.append(curr_reduced)
                current_expr = curr_reduced
            except:
                to_go = False
        return reducs_list

    @property
    def num_reductions(self):
        return len(self.all_reducs)

    def parse_candidate_str(self):

        """
        Will parse candidate string in this format:
        
        '(λx.x)(λ.z.yz)z'
        b-> ((λz.yz)z)
        a-> ((λx.yx)z)
        b-> (y x)
        '
        """
        list_lines = self.candidatestring.strip().strip('\n').split('\n')
        list_lines = [line for line in list_lines if line != '']
        if len(list_lines) == 0:
            raise(Exception("There are no lines"))
        #skip the first line since its the lambda expression
        line_num = 1
        beta_candidate_list = []
        blah = 0
        prev_line = list_lines[0]
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
                    self.alpha_error_list.append(f'Line {line_num} is not a valid alpha reduction')
                    prev_line = reduced_line
                    continue
                #This is an alpha reduction step. Check if the prev line is alpha equivalent to the current line
                check_alpha_reduc = alpha_equiv(parse(prev_line), reduced_line)
                if not check_alpha_reduc:
                    blah += 1
                    self.alpha_error_list.append(f'Line {line_num} is not a valid alpha reduction')

            elif 'b->' in line:
                line_lambda_exp = line.replace('b->', '')
                try:
                    reduced_line = parse(line_lambda_exp)
                except:
                    #Line cannot be parsed
                    self.beta_error_list.append(f'Line {line_num} is not a valid beta reduction')
                    prev_line = reduced_line
                    continue
                #check that the current reduced line is not the same as the previous line to make sure it is needed
                check_prev_beta_reduc = alpha_equiv(parse(prev_line), reduced_line)
                if check_prev_beta_reduc:
                    self.beta_error_list.append(f'Line {line_num} beta reduction is not needed')
                #Else it is a valid reduction
                beta_candidate_list.append((line_num, reduced_line))
                
            else:
                self.general_error_list.append(f'Line {line_num} is not a reduction')
            prev_line = line_lambda_exp
            
        return beta_candidate_list

    def check_all_beta_reducs(self):
        """
        Check that the beta reductions are equivalent
        """
        if len(self.all_beta_reducs) != len(self.candidate_beta_reducs):
            raise( Exception("Number of beta reductions do not match the correct answer"))

        for beta_num in range(len(self.all_beta_reducs)):
            correct_beta_reduc = self.all_beta_reducs[beta_num]
            line_num, candidate_beta_reduc = self.candidate_beta_reducs[beta_num]
            check_beta_reduc = alpha_equiv(correct_beta_reduc, candidate_beta_reduc)
            if not check_beta_reduc:
                self.beta_error_list.append(f'Line {line_num} is not a valid beta reduction')
        


    


