import sys
# CFL Parser

RESERVED = ['$']
EPSILON = ""


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

TERMINALS = ['$']

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
    follow_set = {'$'} if variable == START else set()

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

with open(sys.argv[1], 'r') as g:
    string = "".join(g.read().split()) + '$'

remaining_string = list(string[::-1])
parse_string = ['$', START]

while remaining_string and parse_string:
    print ''.join(reversed(remaining_string)), ''.join(reversed(parse_string))
    
    string_sym = remaining_string.pop()
    parse_sym = parse_string.pop()
    
    if string_sym not in TERMINALS:
        print "ERROR:\033[1;31m", string_sym, "\033[0mis not a terminal of the given language."
        break;

    if parse_sym in VARIABLES:
        try:
            substitute = P_TABLE[parse_sym][string_sym]
        except KeyError:
            print "ERROR:\033[1;31m", string_sym, "\033[0mobtained; but variable\033[1;36m", parse_sym, "\033[0mexpects one of\033[1;32m", P_TABLE[parse_sym].keys(), "\033[0m."
            break
        
        remaining_string.append(string_sym)
        if substitute != EPSILON:
            for sym in substitute[::-1]:
                parse_string.append(sym)

    else:
        if parse_sym != string_sym:
            print "ERROR: Terminal mismatch."
            break


if remaining_string or parse_string:
    print "REJECTED"
else:
    print "ACCEPTED"
