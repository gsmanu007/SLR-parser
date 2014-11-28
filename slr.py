import graph
import sys
import os
import shlex
import copy
from prettytable import PrettyTable






def find_first(non_terminal, long_list, non_terminals, first_dict):
	first = []
	
	for list1 in long_list:
		for i in xrange(len(list1)):
			if list1[i] == ">" and list1[i+1] == " ":
				index = i+2
				
		##--------------------- Rule 1 implemented!-------------------- 
		if index < len(list1) and list1[index] != " " and list1[index] not in non_terminals:
			if list1[index] == 'i' and list1[index + 1] == 'd':
				first.append('id')
				continue
			first.append(list1[index])
			
		## -------------------- Rule 2 implemented!---------------------	
		else:
			for i in xrange(index, len(list1)):
				if list1[i] != " " and list1[i] not in non_terminals:
					first.append(list1[i])
				elif list1[i] != " " and '^' in first_dict[list1[i]]:
					first = list(set(first) | set(first_dict[list1[i]]))	
				elif list1[i] != " " and len(first_dict[list1[i]]) == 0: 	
					pass	
				elif list1[i] == " ":
					continue	
				else:
					for item in first_dict[list1[i]]:
						if item not in first:
							first.append(item) 
					break		
		
	print "First of", non_terminal, ":", first
	return first





def find_follow(non_terminal, productions, non_terminals, first_dict, follow_dict, start): 
	follow = []
	
	##-------------------------- Rule 1 implemented!-------------------------
	if non_terminal == start:
		follow.append('$')
		
	##-------------------------- Rule 2 implemented! -------------------------
	for key, value in productions.iteritems():
		for list1 in value:
			if non_terminal in list1:
				index = []
				
				for i in xrange(len(list1)):
					if list1[i] == non_terminal:
						index.append(i)
				for j in index:
					if j > 0:
						if (j + 1) < len(list1) and list1[j+2] != " ":
							if list1[j+2] not in non_terminals:
								follow.append(list1[j+2])
							else:	
								if not first_dict[list1[j+2]]:
									continue
								
								if '^' in first_dict[list1[j+2]]:
									for item1 in follow_dict[list1[0]]:
										if item1 != ' ':
											follow.append(item1)	
									
								for item in first_dict[list1[j+2]]:
									if item != '^' and item != ' ':
										follow.append(item)
						elif list1[i] != " ":
							if list1[j] != list1[0]:
							
								for item1 in follow_dict[list1[0]]:
									if item1 != ' ':
										follow.append(item1)
									
	follow = set(follow)
		
	print "Follow of", non_terminal, ":", list(follow)
	return list(follow)






def main():

	string = "python graph.py "
	input_string1 = sys.argv[1]
	file_command = string + input_string1
	
	os.system(file_command)

	#-----------------------Taking input and appending $ at the end----------------------------
	input_string2 = sys.argv[2]
	input_string_list = list(shlex.shlex(input_string2))
	input_string_list.append('$')

	#-------------------------------Constructing grammmar--------------------------------------
	non_terminals = [] 
	grammar = open("slr.txt", 'r')
	closure = open("closure.txt", 'r')
	
	input_line = grammar.readline()
	input_line = input_line.rsplit()
	
	for element in input_line:
		non_terminals.append(element)
		
	start_state = non_terminals[0]
		
	productions = {}
	production_counter = {} 
	inverse_production = {}
	
	for i in xrange(len(non_terminals)):
		productions[non_terminals[i]] = []
	
	i = 1
	for line in grammar:
		line = line.rsplit('\n')
		if line[0]:
			if '->' in line[0]:
				productions[line[0][0]].append(line[0])
				temp_string = line[0].replace(" ", "") 	
				production_counter[temp_string] = i
				inverse_production[i] = temp_string
				i += 1
		
	no_items = int(closure.readline())
	
	
	
	closure_dict = {}
	goto_dict = {}
	hash_all = {}
	first = {}
	follow = {}
	
	
	new = 1
	for line in closure:
		line = line.rsplit('\n')
		if line[0] and '->' not in line[0] and new == 1:
			var = line[0]
			closure_dict[line[0]] = []
			goto_dict[line[0]] = []
			new = 0
			
		elif line[0] and '->' in line[0] and new == 0:
			closure_dict[var].append(line[0])
			
		elif line[0] and '->' not in line[0] and new == 0 and ',' in line[0]:
			goto_dict[var].append(line[0])
							
		elif not line[0]:
			new = 1
				
	
	action_set = []
	
	for keys, values in goto_dict.iteritems():
		for value in values:
			if value[0] not in non_terminals and value[0] != 'i':
				action_set.append(value[0])
			elif value[0] == 'i':
				action_set.append('id')
		
	action_set = list(set(action_set))
	action_set.append('$')
	print action_set
	
	
	#--------------------------------------Table-----------------------------------------------
	
	table = [[0 for i in xrange(len(action_set)+ len(non_terminals) + 1)] for j in xrange(no_items + 1)]
	table[0][0] = 'State'

	for i in xrange(1, len(action_set) + 1):
		table[0][i] = action_set[i-1]
		hash_all[action_set[i-1]] = i
		
	for j in xrange(i+1, i + len(non_terminals)+1):
		table[0][j] = non_terminals[j - i - 1]	
		hash_all[non_terminals[j - i - 1]] = j
			
	for keys,values in goto_dict.iteritems():
		row_number = keys[1:]
		table[int(row_number)+1][0] = row_number
		for value in values:
			for position in xrange(len(value)):
				if value[position] == ',':
					symbol, act = value.split(',')	
					table[int(row_number)+1][hash_all[symbol]] =  "S" + act
					break
	
	print hash_all
		
	##----------------------------- First and Follow functions:--------------------------------
	
	for nt in non_terminals:
		first[nt] = []
		follow[nt] = []
	
	for nt in non_terminals[::-1]:
		first[nt] = find_first(nt, productions[nt], non_terminals, first)
	print "\n"
	
	for nt1 in non_terminals:
		follow[nt1] = find_follow(nt1, productions, non_terminals, first, follow, start_state)
	print "\n"
	
	
	print production_counter
	print inverse_production
	
	##------------------------------------Reduce Action----------------------------------------
	for key, values in closure_dict.iteritems():
		for value in values:
			temp_string = value.replace(" ", "")
			temp_string2 = temp_string.replace(".", "")
			if temp_string2 in production_counter.keys():
				k = production_counter[temp_string2]
		
			if value[len(value) - 2] == "." and value[2] == " ":
				
				nt = value[1]
				if nt in non_terminals:
					for i in follow[nt]:
						table[int(key[1:]) + 1][int(hash_all[i])] = "R"+ str(k)  
			elif value[len(value) - 2] == "." and value[1] == start_state and value[2] != " ":
				table[int(key[1]) + 1][int(hash_all['$'])] = "Accept"
	
	
	
	##--------------------------------Output in form of Table----------------------------------
	print "\n\nParsing table\n" 
			
	xz = PrettyTable([x for x in table[0]])
	xz.padding_width = 1		
	
	for i in xrange(1, no_items + 1):				
		xz.add_row([x for x in table[i]])
	
	print xz

	
	
	#---------------------------------Validating output----------------------------------------
	
	stack = [0]
	
	input_string2 = sys.argv[2]
	input_stack = list(shlex.shlex(input_string2))
	input_stack.append('$')
	
	table2 = [["Stack", "Input Stack", "Action"]]
	xy = PrettyTable([x for x in table2[0]])
	xy.padding_width = 1
	
	stack_copy = copy.deepcopy(stack)
	input_stack_copy = copy.deepcopy(input_stack)
	
	xy.add_row([stack_copy,input_stack_copy,[""]])
	
	
	i = 0
	condition = True
	counter = 1
	while condition:
		try:
			action_string = table[int(stack[-1]) + 1][int(hash_all[input_stack[0]])]
			action = action_string[0]
			state = action_string[1:]
		except:	
			print "Invalid input\n"
			return 2	
		
		if action_string == "Accept":
			exit = 1
			condition = False
			break
						
		if action == "S":
			stack.append(input_stack[0])
			stack.append(state)
			
			del input_stack[0]
			
		elif action == "R":
			location = int(state)
			production = inverse_production[location]
				
			for i in xrange(len(production)):
				if production[i] == "-" and production[i+1] == ">":
					break
			length = 0
			j = i+2
			while j < len(production):
				if j+1 < len(production):
					if production[j] == "i" and production[j+1] == "d":
						length += 1
						j += 2
					else:
						length +=1
						j += 1	
				else:
					length +=1
					j += 1
			for k in xrange(2*length):
				stack.pop()
			char = stack[-1]
			
			nt = production[:i]
			stack.append(nt)
			to_append = table[int(char)+1][int(hash_all[nt])]
			to_append2 = to_append[1:]
			stack.append(to_append2)
		
		counter += 1
		stack_copy = copy.deepcopy(stack)
		input_stack_copy = copy.deepcopy(input_stack)
	
		xy.add_row([stack_copy,input_stack_copy,[action_string]])
	
	print "\n\nAction table\n" 
	print xy
	
	if exit == 1:
		print "Input Accepted!!"
	
	
	return 2
	
	
	
	
if __name__ == "__main__":
	sys.exit(main()) 
