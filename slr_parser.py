#Write a program to provide an implementation of SLR(1) parser. Construct the table and read a sentence and check if parsing is successful or not. No need to check validity of grammar. Give an error in case of a conflict in table construction

#Tasks:
#1. Augmentation of Grammar
#2. Construct items
#3. Closure and Goto Function
#4. 


import sys
import shlex
import copy
from prettytable import PrettyTable


def closure(kernel, grammar_dict):
	K = [kernel]
	J = []
	
	J.append(K)
	dot_location = 3
	add = True
	
	n = 0
	while add:
		add = False
		
		#----------------------------------First Item--------------------------------------
		if n == 0:
			dot_list = []
			dot_list.append(3)
			next_list = []
				
			for rule in J[n]:
				if dot_location < len(rule):
					if rule[dot_location] in grammar_dict.keys():
						for rule1 in grammar_dict[rule[dot_location]]:
							if rule1 not in J[n]: 
								J[n].append(rule1)
								dot_list.append(dot_location)
								next_list.append(rule1[dot_location])
								add = True	
		
			J.append(dot_list)
			dot_location += 1
			n += 2
			
			print J
	
		else:
			add = True
			temp_list = []
			dot_prev = dot_list
			
			print "J[n-1]", J[n-1]
			dot_list1 = copy.deepcopy(J[n-1])
			
			for j in xrange(len(J[n-1])):
				
				dot_list1[j] += 1
				print j, dot_list1, dot_list1[j], J[n-2][j], len(J[n-2][j])
				if dot_list1[j] < len(J[n-2][j]):
					indexes = []
					
					for i in xrange(len(next_list)):
						if J[n-2][i][dot_list1[i] - 1] == next_list[i]:
							 print "---------", J[n-2][i], dot_list1[i]
							 indexes.append(i)
							 
						if not indexes:
							J[n].append(J[n-2][i])
							dot_list1 = J[n-1]
				elif dot_list1[j] == len(J[n-2][j]):
					print J[n-2][j], kernel
					if J[n-2][j] == kernel:
						J.append([kernel])
					break
			if temp_list:
				J.append(temp_list)
			
			J.append(dot_list1)
			print J
			n += 2	
			dot_list = dot_list1			
			del dot_list1
			
			a = input()
			if a == "0":
				add = False
			
			
	print J
	return J



'''def next_item(free_list, non_terminal, productions):
	item = []
	for rule in free_list:
		for i in xrange(len(rule)):
			if rule[i] == '.' and rule[i+1:i+3] != "id1": #and rule[i+1] == non_terminal:
				string = rule[0:i]+non_terminal+'.'+ rule[i+2:len(rule)]
			elif rule[i] == '.' and rule[i+1:i+3] == "id1":
				string = rule[0:i]+"id1."
			elif rule[i] == '.' and rule[i+1:i+3] != "id1" and rule[i+1]:
				temp = rule[0:i]+rule[i+1]+"."+rule[i+2:len(rule)-1]
				temp_list = [temp]
				character = rule[i+2]
				string = next_item(temp_list, character, productions)
		item.append(string)
	
		print "fn", rule, item
	return item



def closure(first_item, productions, non_terminals_list):
	item_counter = 0
	item_tableau = []
	relation_table = []
	production = []
	
	item_tableau.append(first_item)	
	
	
	for rule in first_item:
		print rule
		free_list = []
		for i in xrange(len(rule)):
			if rule[i] == "." and rule[i+1]:
				#print i, rule[i+1]
				break
					
		if rule[i+1] and (rule[i+1] in non_terminals_list):
			free_list.append(rule)	
			for rule2 in first_item:
				if ("."+rule[i+1] in rule2) and rule2 != rule:
					free_list.append(rule2)
					#print rule2
			item = next_item(free_list, rule[i+1], productions)
			item_tableau.append(item)
		elif rule[i+1] and ((rule[i+1] not in non_terminals_list) or rule[i+1:i+3] == "id1"):
			free_list.append(rule)
		if free_list:
			del free_list	
			#print item	
		#for each production B -> gamma of G
		#add B -> .gamma to  
			
			
			#free_list = next_item(rule, rule[i+1], productions)
			
		#for 
	print item_tableau
	return 2 #item_tableau
	
	
	


def first_item(productions):
	#replace grammar by production map
	temp_list = []
	
	for key, values in productions.iteritems():
		for symbol in values:
			for i in xrange(len(symbol)):
				if symbol[i] == "-" and symbol[i+1] == ">":
					symbol = symbol[0:i+2] + "." + symbol[i+2: len(symbol)]
					temp_list.append(symbol)
					continue
					
	print "first item", temp_list				
	return temp_list'''




def main():
	#-----------------------Taking input and appending $ at the end----------------------------
	input_string = sys.argv[1]
	input_string_list = list(shlex.shlex(input_string))
	input_string_list.append('$')

	
	
	#-------------------------------Constructing grammmar--------------------------------------
	non_terminals = [] 
	productions = {}  #List of list of productions sorted by non-terminals
	grammar_rules = [] #All grammar rules 
	new_list = [] #temp variable
	
	grammar = open('slr_grammar.txt', 'r')
	
	for row in grammar:
		if '->' in row:
			#------------------------new production------------------------------------
			if len(new_list) == 0:
				start_state = row[0]
				augmented_string = 'Z->' + start_state
				augmented_rule_list = [augmented_string]
				grammar_rules.append(augmented_rule_list)
				non_terminals.append("Z")
				non_terminals.append(start_state)
				new_list = []
				new_list.append(row.rstrip('\n'))
			else:
				grammar_rules.append(new_list)
				del new_list
				new_list = []
				new_list.append(row.rstrip('\n'))
				non_terminals.append(row[0])
				
		elif '|' in row:
			new_list.append(row.rstrip('\n\|'))	
	
	
	non_terminals_list = list(set(non_terminals))
	grammar_rules.append(new_list)	
	del new_list
	print "\nGrammar Rules list", grammar_rules, "\n"
	print "Non-terminals:", non_terminals_list, "\n"
	
	
	##----------------------Finding productions from Grammar-----------------------------------
	for x in xrange(len(non_terminals)):
		productions[non_terminals[x]] = []
		
	
	for x in xrange(len(grammar_rules)):
		for y in xrange(len(grammar_rules[x])):
			
			grammar_rules[x][y] = [s.replace('|', '') for s in grammar_rules[x][y]]
			grammar_rules[x][y] = ''.join(grammar_rules[x][y])
			productions[non_terminals[x]].append(grammar_rules[x][y]) 
	
	for non_terminal in non_terminals:
		for i in xrange(len(productions[non_terminal])):
			if '->' not in productions[non_terminal][i]:
				list1 = productions[non_terminal][i]
				productions[non_terminal].pop(i)
				
				string = non_terminal + '->' + list1
				list1 = string
				productions[non_terminal].append(list1)
	
	print "Production map:", productions, "\n"
	
	
	#--------------------------------Item tableau---------------------------------------------
	
	'''initial_item = first_item(productions)
	
	item_table = closure(initial_item, productions, non_terminals_list)'''
	
	set_of_items = closure(augmented_string, productions)
	
	
	
	return 2
	
	


if __name__ == "__main__":
	sys.exit(main())
