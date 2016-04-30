"""
    LL(1) CFG parser
    
    Given an LL(1) grammar and a string,
    this program will determine whether the string belongs
    to the language defined by the grammar.
    
    If -e is given as an argument, any rejected input will
    be modified to produce a similar accepted string.

    Arguments:
    inputfile [grammarfile] [-e]
"""

import sys
from collections import deque

EPSILON = ""
END = '$'
RESERVED = [END]


# 0. handle arguments

parse_file = 'tests/accept.txt'
grammar_file = 'grammars/corrected.grm'
recovery = False

if len(sys.argv) >= 2:
    parse_file = sys.argv[1]

if len(sys.argv) == 4:
    grammar_file = sys.argv[2]
    if sys.argv[3] == "-e":
        recovery = True
elif len(sys.argv) == 3:
    if sys.argv[2] == "-e":
        recovery = True
    else:
        grammar_file = sys.argv[2]


# 1. extract grammar

LINES = []
with open(grammar_file, 'r') as g:
    for line in g:
        LINES.append("".join(line.split()).replace("epsilon", EPSILON))
        # whitespace is stripped, epsilon handled

#   rules, variables
RULES = {}
START = LINES[0][0]

for line in LINES:
    rule = line.split("->")
    assert len(rule[0]) == 1
    RULES[rule[0]] = set(rule[1].split("|"))

VARIABLES = RULES.keys()

#   terminals
TERMINALS = [END]

for line in LINES:
    for letter in line.replace("->", ""):
        if not (letter in VARIABLES or letter in TERMINALS or letter == "|"):
            if letter in RESERVED:
                print "Reserved symbol in grammar:", letter
                sys.exit(1)
            TERMINALS.append(letter)


# 2. build parse table

""" Returns the FIRST set of a given string. """
def first(string):
    symbol = string[:1]

    if symbol in VARIABLES:
        init_set = set()
        for rule in RULES[symbol]:
            if symbol != rule[:1]:
                init_set |= first(rule)
        
        if EPSILON in init_set:
            return (init_set - {EPSILON}) | first(string[1:])
        else:
            return init_set
    elif string == EPSILON:
        return {EPSILON}
    else:
        return {symbol}

""" Returns the FOLLOW set of a given variable. """
def follow(variable, used):
    follow_set = {END} if variable == START else set()

    for var in VARIABLES:
        for prod in RULES[var]:
            index = prod.find(variable)
            followed = False
            
            while index != -1:
                init_set = first(prod[index + 1:])
                
                if not followed and var != variable and EPSILON in init_set and var not in used:
                    init_set |= follow(var, used | {var})
                    followed = True

                follow_set |= (init_set - {EPSILON})

                index = prod.find(variable, index + 1)
    return follow_set

# Construct the parse table itself, which is a function (Variable, Terminal) -> String
P_TABLE = {var: {} for var in VARIABLES}

for var in RULES:
    for prod in RULES[var]:
        first_set = first(prod)
        follow_set = set()
        if EPSILON in first_set:
            follow_set = follow(var, set())
       
        if not first_set.isdisjoint(follow_set):
            print "First, Follow sets on",  var, "not disjoint; grammar not LL(1)"
            sys.exit(1)

        for term in (first_set | follow_set) - {EPSILON}:
            if term not in P_TABLE[var]:
                P_TABLE[var][term] = prod
            else:
                print "Production ambiguity on ["+var+","+term+"]; grammar not LL(1)"
                sys.exit(1)


# 3. Parse String

""" Given a string and a parsing stack, returns a 'similar' string satisfying the stack"""
def find_close_valid(string, stack):
    tried = []
    
    # each queue entry is as follows:
    # [invalid substring, stack at point of invalidation, initial valid substring] 
    queue = deque([[string, stack, []]])

    while True:
        current = queue.popleft()
        
        # result[0] = invalid substring; result[1] = stack at point of invalidation
        result = parse_string(*(current[:2]), verbose=False)
       
        if result != -1:
            result = list(result)

        if result == -1:
            return current[0] + current[2]
        else:
            tried.append(current[:2])
            string_head = result[0][-1]
            stack_head = result[1][-1]
           
            # insertion reversal
            # delete one character from result[0], leave result[1] the same
            if string_head != END:
                candidate = [ list(result[0][:-1]), 
                              list(result[1]), 
                              list(current[0][len(result[0][:-1]) + 1:] + current[2]) ]
                
                if candidate not in tried:
                    queue.append(candidate)

            # deletion reversal
            # If symbol not in the grammar, must have been inserted, so don't reverse deletion
            if string_head in TERMINALS and stack_head != END:
                
                # retain result[1], prepend head of result[1] to result[0]
                if stack_head in TERMINALS:
                    
                    #insert what was expected -- naive, but catches point removals
                    candidate = [ list(result[0]) + [result[1][-1]], 
                                  list(result[1]), 
                                  current[0][len(result[0]):] + current[2] ]
                    
                    if candidate not in tried:
                        queue.append(candidate)
                
                # retain result[1], prepend valid terminals to result[0]
                else:
                    for term in P_TABLE[stack_head].keys():
                        if term == END:
                            continue
                        candidate = [ list(result[0]) + [term], 
                                      list(result[1]), 
                                      current[0][len(result[0]):] + current[2] ]
                        
                        if candidate not in tried:
                            queue.append(candidate)
            
""" 
 Attempts to parse a string. 
 
 If no initial string is given, the file given in the first argument is consulted.
 If no initial stack is specified, the start symbol is used as the initialiser.
 If correct_errors is true, invalid substrings will be corrected.
 If verbose is false, no trace will be printed. 
 
 If the string was parsed successfully, returns -1,
 otherwise, returns the last state of its remaining string and stack."""
def parse_string(init_string = None, init_stack = None, correct_errors=False, verbose=True):
    
    # Obtain input string
    if init_string is None:
        with open(parse_file, 'r') as g:
            string = "".join(g.read().split()) + END

        remaining = list(string[::-1])
    else:
        remaining = list(init_string)
    parse_stack = [END, START] if init_stack is None else list(init_stack)
   
    # Parse the string
    error = False
    corrected = False
    while remaining and parse_stack:
        if verbose:
            print ''.join(reversed(remaining)), ''.join(reversed(parse_stack))
        
        error_string = "\n"
        string_head = remaining[-1]
        stack_head = parse_stack[-1]

        # Reached a symbol not in the grammar
        if string_head not in TERMINALS:
            if verbose:
                error_string += "ERROR:\033[1;31m "+string_head+" \033[0mis not a terminal of the given language.\n"
            error = True

        if stack_head in VARIABLES:
            try:
                substitute = P_TABLE[stack_head][string_head]
            except KeyError:
                if verbose:
                    error_string += "ERROR:\033[1;31m "+string_head+" \033[0mobtained; but variable\033[1;36m "+stack_head+" \033[0mexpects one of\033[1;32m "+str(P_TABLE[stack_head].keys())+" \033[0m\n"
                error = True
            
            # Update the stack if a production rule was found
            if not error:
                parse_stack.pop()
                for sym in substitute[::-1]:
                    parse_stack.append(sym)

        # If the stack symbol is not a variable, it must be a terminal
        else:
            if stack_head != string_head:
                if verbose:
                    error_string += "ERROR: Terminal mismatch.\n"
                error = True
            else:
                remaining.pop()
                parse_stack.pop()
        
        if error:
            if verbose:
                print error_string

            # Correct the error and carry on as if nothing happened.
            if correct_errors:
                prev = remaining
                remaining = find_close_valid(remaining, parse_stack)
                string = string[:-len(prev)] + ''.join(reversed(remaining[1:]))
                
                if verbose:
                    print "Correcting remaining string:", ''.join(reversed(prev)), "->", ''.join(reversed(remaining)), "\n"
                
                corrected = True
                error = False
                continue
            else:
                break

    if remaining or parse_stack:
        if verbose:
            print "REJECTED"
        return (remaining, parse_stack)
    else:
        if verbose:
            print "ACCEPTED"
            if corrected:
                print "\nCorrected surrogate string:\n" + string
        return -1


parse_string(correct_errors = recovery)
