import sys
from collections import deque

# CFL Parser

EPSILON = ""
END = '$'
RESERVED = [END]


# 1. read grammar file

LINES = []
with open('corrected.grm', 'r') as g:
    for line in g:
        LINES.append("".join(line.split()).replace("epsilon", EPSILON))


# 2. extract rules, variables

RULES = {}
START = LINES[0][0]

for line in LINES:
    rule = line.split("->")
    assert len(rule[0]) == 1
    RULES[rule[0]] = set(rule[1].split("|"))

VARIABLES = RULES.keys()


# 3. extract terminals

TERMINALS = [END]

for line in LINES:
    for letter in line.replace("->", ""):
        if not (letter in VARIABLES or letter in TERMINALS or letter == "|"):
            if letter in RESERVED:
                print "Reserved symbol in grammar:", letter
                sys.exit(1)
            TERMINALS.append(letter)


# 4. build parse table

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


def follow(variable):
    follow_set = {END} if variable == START else set()

    for var in VARIABLES:
        for prod in RULES[var]:
            index = prod.find(variable)
            followed = False
            
            while index != -1:
                init_set = first(prod[index + 1:])
                
                if not followed and var != variable and EPSILON in init_set:
                    init_set |= follow(var)
                    followed = True

                follow_set |= (init_set - {EPSILON})

                index = prod.find(variable, index + 1)
    return follow_set

# P_TABLE maps (Variable, Terminal) -> String
P_TABLE = {var: {} for var in VARIABLES}

for var in RULES:
    for prod in RULES[var]:
        first_set = first(prod)
        follow_set = set()
        if EPSILON in first_set:
            follow_set = follow(var)
       
        if not first_set.isdisjoint(follow_set):
            print "First, Follow sets on",  prod, "not disjoint; grammar not LL(1)"
            sys.exit(1)

        for term in (first_set | follow_set) - {EPSILON}:
            if term not in P_TABLE[var]:
                P_TABLE[var][term] = prod
            else:
                print "Production ambiguity on [" + var + "," + term + "]; grammar not LL(1)"
                sys.exit(1)


# 5. Parse String

def find_close_valid(string, stack):
    tried = []
    queue = deque([[string, stack, []]])

    while True:
        current = queue.popleft()

        result = parse_string(*(current[:2]))
       
        #print
        #print "------"
        #print 
        #print "current: ", current 
        #print "result: ", result
        #print "queue: ", queue
        #print "tried", tried
        #print

        """if result[0][0] != END:
            print
            print string
            print stack
            print result
            print current
            print tried
            print queue
            print"""

        if result != -1:
            result = list(result)

        if result == -1:
            return current[0] + current[2]
        else:
            tried.append(current[:2])
            string_sym = result[0][-1]
            parse_sym = result[1][-1]
           
            # reversing insertion
            # delete one character from result[0]
            # leave result[1] the same
            if string_sym != END:
                #print "insertions"
                candidate = [ list(result[0][:-1]), list(result[1]), list(current[0][len(result[0][:-1]) + 1:] + current[2]) ]
                if candidate not in tried:
                    queue.append(candidate)
                    #print "added", queue[-1]

            # reversing deletion
            # If symbol not in terminals, must have gotten there by an insertion
            # so don't do the deletion procedure for this symbol.
            if string_sym in TERMINALS:
                # leave result[1] the same, but stick whatever is at the head of result[1] on the head of result[0]
                if parse_sym in TERMINALS:
                    #print "terminal deletions"
                    #insert the character which was expected -- super naive, but should catch point removals
                    candidate = [ list(result[0]) + [result[1][-1]], list(result[1]), current[0][len(result[0]):] + current[2] ]
                    if candidate not in tried:
                        queue.append(candidate)
                        #print "added", queue[-1]
                # leave result[1] the same, but stick whatever the expanded variable is at the front of result[0]
                else:
                    #print "variable deletions"
                    for term in P_TABLE[parse_sym].keys():
                        candidate = [ list(result[0]) + [term], list(result[1]), current[0][len(result[0]):] + current[2] ]
                        if candidate not in tried:
                            queue.append(candidate)
                            #print "added", queue[-1]
            
# Attempts to parse a string. 
# If no initial string is given, the file given in the first argument is consulted.
# If no initial stack is specified, the start symbol is used as the initialiser.
# If correct_errors is true, invalid strings will be corrected, and the new string printed.
def parse_string(init_string = None, init_stack = None, correct_errors=False, verbose=False):
    
    if init_string is None:
        with open(sys.argv[1], 'r') as g:
            string = "".join(g.read().split()) + END

        remaining = list(string[::-1])
    else:
        remaining = list(init_string)
    parse_stack = [END, START] if init_stack is None else list(init_stack)
    index = 0

    while remaining and parse_stack:
        if verbose:
            print ''.join(reversed(remaining)), ''.join(reversed(parse_stack))
        
        string_sym = remaining.pop()
        parse_sym = parse_stack.pop()
        
        if string_sym not in TERMINALS:
            if verbose:
                print "ERROR:\033[1;31m", string_sym, "\033[0mis not a terminal of the given language."
            
            remaining.append(string_sym)
            parse_stack.append(parse_sym)

            if not correct_errors:
                break
            else:
                prev = remaining
                remaining = find_close_valid(remaining, parse_stack)
                if verbose:
                    print "Modifying remaining string:", ''.join(reversed(prev)), "->", ''.join(reversed(remaining))
                continue

        if parse_sym in VARIABLES:
            try:
                substitute = P_TABLE[parse_sym][string_sym]
            except KeyError:
                if verbose:
                    print "ERROR:\033[1;31m", string_sym, "\033[0mobtained; but variable\033[1;36m", parse_sym, "\033[0mexpects one of\033[1;32m", P_TABLE[parse_sym].keys(), "\033[0m"

                remaining.append(string_sym)
                parse_stack.append(parse_sym)

                if not correct_errors:
                    break
                else:
                    prev = remaining
                    remaining = find_close_valid(remaining, parse_stack)
                    if verbose:
                        print "Modifying remaining string:", ''.join(reversed(prev)), "->", ''.join(reversed(remaining))
                    continue
            
            remaining.append(string_sym)
            if substitute != EPSILON:
                for sym in substitute[::-1]:
                    parse_stack.append(sym)

        else:
            if parse_sym != string_sym:
                if verbose:
                    print "ERROR: Terminal mismatch."
                remaining.append(string_sym)
                parse_stack.append(parse_sym)
                
                if not correct_errors:
                    break
                else:
                    prev = remaining
                    remaining = find_close_valid(remaining, parse_stack)
                    if verbose:
                        print "Modifying remaining string:", ''.join(reversed(prev)), "->", ''.join(reversed(remaining))
                    continue

            index += 1

    if remaining or parse_stack:
        if verbose:
            print "REJECTED"
        return (remaining, parse_stack)
    else:
        if verbose:
            print "ACCEPTED"
        return -1


print parse_string(correct_errors = True, verbose = True)
#parse_string(verbose = True)
#parse_string(["$", "}"], ["$", "R", "F", "}", "R"], verbose = True)
