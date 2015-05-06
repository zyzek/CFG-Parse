import sys
# CFL Parser

RESERVED = ['$']
EPSILON = ""

# 1. read in file with language
lines = []
with open('corrected.grm', 'r') as g:
    for line in g:
        lines.append("".join(line.split()).replace("epsilon", EPSILON))

print lines

# 2. extract rules, variables
RULES = {}
START = lines[0][0]

for line in lines:
    rule = line.split("->")
    assert len(rule[0]) == 1
    RULES[rule[0]] = set(rule[1].split("|"))

print RULES
print RULES.keys()

VARIABLES = RULES.keys()

# 3. extract terminals
TERMINALS = ['$']

for line in lines:
    for letter in line.replace("->", ""):
        if not (letter in VARIABLES or letter in TERMINALS or letter == "|"):
            if letter in RESERVED:
                print "Reserved symbol in grammar:", letter
                sys.exit()
            TERMINALS.append(letter)

print TERMINALS

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


P_TABLE = {var: {} for var in VARIABLES}

print
for var in RULES:
    for prod in RULES[var]:
        first_set = first(prod)
        follow_set = set()
        if EPSILON in first_set:
            follow_set = follow(var)
       
        if not first_set.isdisjoint(follow_set):
            print "FI, FO NOT DISJOINT; GRAMMAR NOT LL(1)"
            exit(1)

        for term in (first_set | follow_set) - {EPSILON}:
            if term not in P_TABLE[var]:
                P_TABLE[var][term] = prod
            else:
                print P_TABLE[var], term, prod
                print "GRAMMAR NOT LL(1)"
                exit(1)


print P_TABLE

for v in VARIABLES:
    f = first(v)
    #if EPSILON not in f:
    #    print "Fi(" + v + "):", list(f)
    #else:
    print "Fi(" + v + "):", list(f), "  Fo(" + v + "):", list(follow(v))

print '\n---\n'



# table maps (Variable, Terminal) -> String

#VARIABLES = list('SREFATVCDO')
#TERMINALS = list("if(){}els:=;abxy<>$")
#START = 'S'

table = {}

table['S'] = {}
table['S']['i'] = "ER"
table['S']['x'] = "AR"
table['S']['y'] = "AR"

table['R'] = {}
table['R']['}'] = EPSILON
table['R']['x'] = "AR"
table['R']['y'] = "AR"
table['R']['$'] = EPSILON

table['E'] = {}
table['E']['i'] = "if(C){S}F"

table['F'] = {}
table['F']['e'] = "else{S}"
table['F']['x'] = EPSILON
table['F']['y'] = EPSILON
table['F']['}'] = EPSILON
table['F']['$'] = EPSILON

table['A'] = {}
table['A']['x'] = "V:=T;"
table['A']['y'] = "V:=T;"

table['T'] = {}
table['T']['a'] = "a"
table['T']['b'] = "b"

table['V'] = {}
table['V']['x'] = "x"
table['V']['y'] = "y"

table['C'] = {}
table['C']['a'] = "DOD"
table['C']['b'] = "DOD"
table['C']['x'] = "DOD"
table['C']['y'] = "DOD"

table['D'] = {}
table['D']['a'] = "T"
table['D']['b'] = "T"
table['D']['x'] = "V"
table['D']['y'] = "V"

table['O'] = {}
table['O']['<'] = "<"
table['O']['>'] = ">"

table = P_TABLE

# 5. parse String

with open(sys.argv[1], 'r') as g:
    string = "".join(g.read().split()) + '$'

remaining_string = list(string[::-1])
parse_string = ['$', START]

while remaining_string and parse_string:
    print ''.join(reversed(remaining_string)), ''.join(reversed(parse_string))
    
    string_sym = remaining_string.pop()
    parse_sym = parse_string.pop()

    if parse_sym in VARIABLES:
        try:
            substitute = table[parse_sym][string_sym]
        except KeyError:
            break
        
        remaining_string.append(string_sym)
        if substitute != EPSILON:
            for sym in substitute[::-1]:
                parse_string.append(sym)

    elif parse_sym in TERMINALS:
        if parse_sym == string_sym:
            continue
    else:
        print string_sym
        print "SYMBOL NOT RECOGNISED, YOU FUCKWIT."
        break


if remaining_string or parse_string:
    print remaining_string, parse_string
    print "REJECTED, YOU LOSER."
else:
    print "ACCEPTED, YOU ASSHOLE"
