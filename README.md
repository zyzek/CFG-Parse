# LL(1) CFG parser

Given an LL(1) grammar and a string,
this program will determine whether the string belongs
to the language defined by the grammar.

The grammar will be rejected if it is not LL(1)

If -e is given as an argument, any rejected input will
be modified to produce the nearest similar accepted string.

# Invocation
    inputfile [grammarfile] [-e]