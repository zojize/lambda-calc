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
    TODO: we can store all the alpha and beta reduction labels here. We will need to change alpha_rename and all_beta_reductions to tag each reduction
    """

    def __init__(self, lambdastring : str):
        self.lambdastring = lambdastring
        self.expr = parse(self.lambdastring)
        self.all_reducs = self.store_all_reducs()

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


    


