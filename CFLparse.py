import sys
# CFL Parser

RESERVED = ['$']
EPSILON = ""
"""
# 1. read in file with language
lines = []
with open('conditional.grm', 'r') as g:
    for line in g:
        lines.append("".join(line.split()))

print lines

# 2. extract variables
variables = {}

for line in lines:
    rule = line.split("->")
    assert len(rule[0]) == 1
    variables[rule[0]] = set(rule[1].split("|"))

print variables

# 3. extract terminals
terminals = ['$']

for line in lines:
    for letter in line.replace("->", ""):
        if not (letter in variables.keys() or letter in terminals or letter == "|"):
            if letter in RESERVED:
                print "Reserved symbol in grammar:", letter
                sys.exit()
            terminals.append(letter)

print terminals
"""
# 4. build parse table
# Chomsky Normal Form:
# All rules of the form:
# A -> BC
# A -> a
# S -> epsilon if the language contains epsilon.
#   - eliminate epsilon rules
#   - eliminate unit rules
#   - reduce long rules to short rules
#   - move terminals to unit productions

# 5. parse String

# Default table:


# table maps (Variable, Terminal) -> String
start = 'S'

variables = list('SREFATVCDO')
terminals = list("if(){}els:=;abxy<>$")

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

def first(string):
    symbol = string[:1]

    if symbol in variables:
        init_set = set()
        for rule in table[symbol].values():
            init_set |= first(rule)
        
        if EPSILON in init_set:
            return (init_set - {EPSILON}) | first(string[1:])
        else:
            return init_set
    elif string == EPSILON:
        return {EPSILON}
    else:
        return {symbol}


for v in variables:
    print v + ":", first(v)

print '\n---\n'

with open(sys.argv[1], 'r') as g:
    string = "".join(g.read().split()) + '$'

remaining_string = list(string[::-1])
parse_string = ['$', start]

while remaining_string and parse_string:
    print ''.join(reversed(remaining_string)), ''.join(reversed(parse_string))
    
    string_sym = remaining_string.pop()
    parse_sym = parse_string.pop()

    if parse_sym in variables:
        try:
            substitute = table[parse_sym][string_sym]
        except KeyError:
            break
        
        remaining_string.append(string_sym)
        if substitute != EPSILON:
            for sym in substitute[::-1]:
                parse_string.append(sym)

    elif parse_sym in terminals:
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
