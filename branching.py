"""
Tools for esamining code branches
"""
import re


C_BRANCH_RE_TEXT=r"""(if|else if|else|switch|case)(\s*)\((.*)\)(\s*)"""
C_BRANCH_RE=re.compile(C_BRANCH_RE_TEXT)
def branches(codeBlock:str):
    """
    extract c/c++ branching statements from a block of code

    TODO: it is currently untested
    """
    branches = []
    for match in C_BRANCH_RE.finditer(codeBlock):
        branches.append(match.group(3))

    # Return the list of branches
    return branches
