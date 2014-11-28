import sys, re, getopt

class GrammarError(Exception):
    def __init__(self, value, arg):
        self.value = value
        self.arg = arg
    def __str__(self):
        if self.value == "NORULE":
            return "No rule for {0}".format(self.arg)
        elif self.value == "NORH":
            return "{0} does not appear in the right-hand side of any " \
                    "rule".format(self.arg)
        elif self.value == "BADRULE":
            return "Malformed rule:\t{0}".format(self.arg)
        elif self.value == "NONDECLARED":
            return "Undeclared non-terminal symbol: {0}\t{1}".format(
                arg[0], arg[1])

class SLR1Checker:
    """Check if a given grammar is SLR(1)"""

    def __init__(self, filecontent, separator='->'):
        """Initialization
        Paramaters:
            filecontent := File as a list of lines (readlines)"""
        # Constants
        self._end = -1 # $
        self._epsilon = -2

        self._file = filecontent
        self._symbols = list() # list of string of symbols
        self._n_nt_symbols = 1 # number of non terminal symbols
        self.separator = separator

        # rule = [position, [symbols]] where position is the lookahead position
        # In all this data structures, a symbol is represented as the position
        # of the "string symbol" in self._symbols. E.g. S'(axiom) is 0
        self._productions = dict()
        self._rules = list()
        self._firstset = dict()
        self._followset = dict()
        self._connections = list()
        self._itemsets = list() # Parser states


    def check(self):
        """Check if the grammar is SLR(1), return 0 if the grammar is SLR(1), 1
        if it has a reduce/reduce conflict, 2 if it has a shift/reduce conflict
        """
        self._process_file()

        # Populate firstset and followset
        self._first()
        self._follow()

        return self._get_item_sets()


    def _process_file(self):
        """Turn a file into a set of rules"""
        # strip comments and ignore empty lines
        file_cont = list()
        for line in self._file:
            if len(line.split()) != 0 and line[0] != '#':
                file_cont.append(line)
        self._file = file_cont

        # Populate symbol table (non terminal symbols)
        self._symbols = [sym for sym in self._file[0].split()]
        self._symbols.insert(0, self._symbols[0] + '\'') # S'
        self._symbols = unique(self._symbols)
        self._n_nt_symbols = len(self._symbols)

        # Add rules
        self._rules.append([0, [0, 1]]) # 0. S' -> S
        self._productions[0] = [[1]]
        for line in self._file[1:]:
            self._rules.append(self._process_line(line))

        # Check if grammar is correct
        if len(self._rules) == 1: # just has 0. S' -> S
            raise EOFError("File does not contain any rules")
        for symbol in range(0, self._n_nt_symbols):
            if symbol not in self._productions:
                raise GrammarError("NORULE", self._symbols[symbol])
            nofollow = True
            if symbol < 2: # don't check for S' and S
                continue
            for prod in self._productions:
                for p_right in self._productions[prod]:
                    if symbol in p_right:
                        nofollow = False
            if nofollow:
                raise GrammarError("NORH", self._symbols[symbol])


    def _process_line(self, line):
        """Turn a line into a rule"""
        # Check line
        pattern = re.compile('\s*\S+\s+' + self.separator + '\s+.*')
        if pattern.match(line) is None:
            raise GrammarError("BADRULE", line)
        rule = line.split()
        rule.pop(1) # Remove separator
        if rule[0] not in self._symbols[:self._n_nt_symbols]:
            raise GrammarError("NONDECLARED", [rule[0], line])
        for pos, symbol in enumerate(rule[:]):
            if symbol not in self._symbols:
                self._symbols.append(symbol)
            rule[pos] = self._symbols.index(symbol)
        # populate productions
        if rule[0] in self._productions:
            self._productions[rule[0]].append(rule[1:])
        else:
            self._productions[rule[0]] = [rule[1:]]
        return [0, rule]


    def _get_item_sets(self):
        """Generate the item sets of the grammar, return 0 if the grammar is
        SLR(1), 1 if it has a reduce/reduce conflict, 2 if it has a shift/reduce
        conflict"""
        # Initialize the DFA
        self._itemsets.append(self._closure([self._rules[0]]))
        itemset = self._itemsets[0]

        for pos, itemset in enumerate(self._itemsets):
            symbols = self._get_lookaheads(itemset)
            for symbol in symbols:
                new = self._closure(self._goto(itemset, symbol))
                if new is None:
                    continue
                elif new not in self._itemsets:
                    self._itemsets.append(new)
                    ret = self._check_conflicts(new, len(self._itemsets) - 1)
                    if  ret != 0:
                        return ret # there is a conflict
                self._connections.append([pos, self._itemsets.index(new)])
        return 0 # grammar is SLR(1)


    def _closure(self, rules_list):
        """Generate the parser state of a given list of rules"""
        if len(rules_list) == 0:
            return None
        closure = rules_list
        change = True
        while change: # Stop if nothing is added to closure
            change = False
            lookaheads = self._get_lookaheads(closure)
            for rule in self._rules:
                if rule[1][0] in lookaheads and rule not in closure:
                    closure.append(rule)
                    change = True
        return closure


    def _get_lookaheads(self, rules):
        """Return the lookaheads of a set of rules"""
        lookaheads = []
        for rule in rules:
            if len(rule[1]) == rule[0] + 1:
                continue
            symbol = rule[1][rule[0] + 1]
            if symbol not in lookaheads:
                lookaheads.append(symbol)
        return lookaheads


    def _goto(self, rules, symbol):
        """Generate the parser state of GOTO(rules, symbol)"""
        goto = list()
        for rule in rules:
            if len(rule[1]) == rule[0] + 1: # Rule is not expecting any symbol
                continue
            if rule[1][rule[0] + 1] == symbol: # Lookahead == symbol
                goto.append(rule[:]) # append a shallow-copy (will be modified)
        for rule in goto:
            rule[0] += 1
        return goto


    def _check_conflicts(self, itemset, nset):
        """ Check for Reduction-Reduction and Shift-Reduction conflicts in a
        given itemset, return 0 if no conflict, 1 if reduce/reduce conflict, and
        2 if shift/reduce conflict"""
        assert len(self._followset) != 0, "firstset & followset not populated"
        reductions = []
        shifts = []
        for rule in itemset:
            if len(rule[1]) == rule[0] + 1: # Rule is not expecting any symbol
                reductions.append([self._followset[rule[1][0]], rule])
            elif rule[1][rule[0] + 1] >= self._n_nt_symbols:
                shifts.append([[rule[1][rule[0] + 1]], rule])
        # Reduction/Reduction conflicts
        for i in range(len(reductions)):
            for j in range(i + 1, len(reductions)):
                if len(set(reductions[i][0]) & set(reductions[j][0])) != 0:
                    print "{0}\nReduce/Reduce conflict between:" \
                            "\t{1}\tand\t{2}".format(
                                    self.get_string_rules(itemset, nset),
                                    self._string_rule(reductions[i][1]),
                                    self._string_rule(reductions[j][1]))
                    print "Intersection of FOLLOW({0}) with FOLLOW({1}) is " \
                            "not empty".format(
                            self._symbols[reductions[i][1][1][0]],
                            self._symbols[reductions[j][1][1][0]])
                    self.print_first_follow()
                    return 1
        # Shift/Reduction conflicts
        for shift in shifts:
            for red in reductions:
                if len(set(shift[0]) & set(red[0])) != 0:
                    print "{0}\nShift/Reduce conflict between:" \
                            "\t{1}\tand\t{2}".format(
                                    self.get_string_rules(itemset, nset),
                                    self._string_rule(shift[1]),
                                    self._string_rule(red[1]))
                    print "{0} in FOLLOW({1})".format(
                            self._symbols[shift[1][1][0]],
                            self._symbols[red[1][1][0]])
                    self.print_first_follow()
                    return 2
        return 0


    def _follow(self):
        """Compute the FOLLOW of all non-terminal grammar symbols"""
        assert len(self._firstset) != 0, "firstset is not populated"

        self._followset[0] = [self._end]
        self._followset[1] = [self._end]
        for symbol in range(2, self._n_nt_symbols):
            self._followset[symbol] = []

        change = True
        while change:
            change = False
            for symbol in range(0, self._n_nt_symbols):
                for rule in self._rules:
                    right = rule[1][1:] # right-hand side of the production rule
                    if len(right) == 0 or symbol not in right:
                        continue
                    index = rule[1].index(symbol)
                    first = self._first_production(rule[1][index + 1:])
                    if self._epsilon in first:
                        # If "symbol" is the last symbol of the production,
                        # _first(symbol) returns EPSILON too
                        first.remove(self._epsilon)
                        for follow in self._followset[rule[0]]:
                            if follow not in self._followset[symbol]:
                                self._followset[symbol].append(follow)
                                change = True
                    for follow in first:
                        if follow not in self._followset[symbol]:
                            self._followset[symbol].append(follow)
                            change = True

        for follow in self._followset:
            assert len(self._followset.get(follow)) > 0, "Empty follow" + \
                    self._symbols[follow]


    def _first_production(self, production):
        """Compute the first of a production, uses the values at _firstset, so
        the result may not be complete"""
        res = []
        i = 0
        return_epsilon = True
        while i < len(production) and return_epsilon:
            return_epsilon = False
            first = self._firstset[production[i]]
            res.extend(first)
            if self._epsilon in first:
                return_epsilon = True
                res.remove(self._epsilon)
            i += 1
        # if all firstsets have epsilon, res have it too
        # notice that if len(production) == 0, this get executed too
        if i == len(production) and return_epsilon:
            res.append(self._epsilon)
        return(list(set(res)))


    def _first(self):
        """Compute the FIRST of all grammar symbols"""
        # first(x) = x if x is a terminal symbol grammar
        for symbol in range(self._n_nt_symbols, len(self._symbols)):
            self._firstset[symbol] = [symbol]

        # first(x) of non terminal symbols
        # initialization
        for symbol in range(0, self._n_nt_symbols):
            self._firstset[symbol] = []

        change = True
        while change:
            change = False
            for symbol in range(0, self._n_nt_symbols):
                for production in self._productions[symbol]:
                    for first in self._first_production(production):
                        if first not in self._firstset[symbol]:
                            self._firstset[symbol].append(first)
                            change = True
        for first in self._firstset:
            assert len(self._firstset.get(first)) > 0, "Empty first " \
                    + self._symbols[first]


    def get_string_rules(self, rules, nset):
        """Print a list of rules"""
        str_ret = ' '.join(['I' + str(nset), '\n'])
        for rule in rules:
            str_ret = ' '.join([str_ret, self._string_rule(rule), '\n'])
        return str_ret


    def _string_rule(self, rule):
        """Translate a rule (list of positions of symbol table) into a string,
        and print it"""
        str_rule = self._symbols[rule[1][0]] + ' ' + self.separator + ' '
        str_rule += ' '.join([self._symbols[i] for i in rule[1][1:rule[0] + 1]])
        str_rule += ' .'
        str_rule += ' '.join([self._symbols[i] for i in rule[1][rule[0] + 1:]])
        return str_rule


    def _strsymbol(self, symbol):
        """Return the string representation for a given symbol(position of
        _symbols)"""
        if symbol == self._epsilon:
            return '<Epsilon>'
        elif symbol == self._end:
            return '<$>'
        else:
            return self._symbols[symbol]


    def print_first_follow(self):
        """Print the first and follow of the non-terminal symbols of the
        grammar"""
        print "\nNON-TERMINAL SYMBOLS:\n"
        for symbol in range(self._n_nt_symbols):
            print "Symbol:", self._symbols[symbol]
            print "\tFIRST:\t",
            for first in self._firstset[symbol]:
                print self._strsymbol(first),
            print ""
            print "\tFOLLOW:\t",
            for follow in self._followset[symbol]:
                print self._strsymbol(follow),
            print ""


    def get_representation(self):
        """Return a dictionary with the internal data structures"""
        representation = dict()
        representation['end'] = self._end
        representation['epsilon'] = self._epsilon
        representation['symbols'] = self._symbols
        representation['n_nt_symbols'] = self._n_nt_symbols
        representation['productions'] = self._productions
        representation['rules'] = self._rules
        representation['firstset'] = self._firstset
        representation['followset'] = self._followset
        representation['connections'] = self._connections
        representation['itemsets'] = self._itemsets
        return representation

def main():
    """Parse arguments, open/close files and execute the checker"""
    separator = '->'
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:", ["help", "separator="])
    except getopt.GetoptError as err:
        print "ERROR:", err
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif opt in ("-s", "--separator"):
            separator = arg
    if len(args) == 0:
        print("WARNING: No file supplied, doing nothing")
    for filex in args:
        with open(filex, 'r') as fpt:
            if SLR1Checker(fpt.readlines(), separator).check() == 0:
                print "{0}: Grammar is SLR(1)".format(filex)

def usage():
    """Help message"""
    help_msg = """
    Help:
    {0} [-h|--help]
    {0} [-s<sep>|--separator=<sep>] FILES

    Options:
    help: Display this information
    separator: Change the separator to be used

    Notice that options should ever precede FILES
    """.format(sys.argv[0])
    print help_msg

def unique(seq):
    """Remove all duplicates preserving the order.
    http://www.peterbe.com/plog/uniqifiers-benchmark"""
    seen = set()
    seen_add = seen.add
    return [elem for elem in seq if elem not in seen and not seen_add(elem)]



if __name__ == "__main__":
    main()
