# CFL Parser

# 1. read in file with language
lines  = []
with open('conditional.grm', 'r') as g:
	for line in g:
		lines += line

print lines

# 2. extract variables
# 3. extract terminals
# 4. build parse table
# 5. parse String