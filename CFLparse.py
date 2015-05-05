import sys
# CFL Parser

RESERVED = ['$']

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
terminals = []

for line in lines:
    for letter in line.replace("->", ""):
        if not (letter in variables.keys() or letter in terminals or letter == "|"):
            if letter in RESERVED:
                print "Reserved symbol in grammar:", letter
                sys.exit()
            terminals.append(letter)

print terminals

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

table = {}

table['S','i'] = "ER"
table['S','x'] = "AR"
table['S','y'] = "AR"

table['R','}'] = "epsilon"
table['R','x'] = "AR"
table['R','y'] = "AR"
table['R','$'] = "epsilon"

table['E','i'] = "if(C){S}F"

table['F','e'] = "else{S}"
table['F','x'] = "epsilon"
table['F','y'] = "epsilon"
table['F','}'] = "epsilon"
table['F','$'] = "epsilon"

table['A','x'] = "V:=T;"
table['A','y'] = "V:=T;"

table['T','a'] = "a"
table['T','b'] = "b"

table['V','x'] = "x"
table['V','y'] = "y"

table['C','a'] = "DOD"
table['C','b'] = "DOD"
table['C','x'] = "DOD"
table['C','y'] = "DOD"

table['D','a'] = "T"
table['D','b'] = "T"
table['D','x'] = "V"
table['D','y'] = "V"

table['O','<'] = "<"
table['O','>'] = ">"

with open(sys.argv[1], 'r') as g:
    string = "".join(g.read().split()) + '$'

remaining_string = list(string)
parse_string = [start, '$']

while remaining_string and parse_string:
    string_sym = remaining_string.pop()
    parse_sym = parse_string.pop()

    if parse_sym in variables:
        try:
            substitute = table[parse_sym, string_sym]
        except KeyError:
            parse_string.push(parse_sym)
            break

        for sym in substitute[::-1]:
            parse_sym.push(sym)

    elif parse_sym in terminals:
        if parse_sym == string_sym:
            continue
    else:
        print string_sym
        print "SYMBOL NOT RECOGNISED, YOU FUCKWIT."
        break

if remaining_string or parse_string:
    print "REJECTED, YOU LOSER."
else:
    print "ACCEPTED, YOU ASSHOLE"
