import sys, getopt
import check

PYDOT = True
try:
    import pydot
except ImportError:
    print "Couldn't import pydot, plotting will not be possible"
    PYDOT = False


class SLR1Graph:
    """Plot the parser states graph of a given grammar"""

    def __init__(self, filecontent, separator='->'):
        """Initialization
        Paramaters:
            filecontent := File as a list of lines (readlines)"""
        # Graph variables
        self._graph = None
        self._nodes = list()
        self._checker = check.SLR1Checker(filecontent, separator)
        self._checker.check()
        representation = self._checker.get_representation()
        self._symbols = representation['symbols']
        self._itemsets = representation['itemsets']
        self._connections = representation['connections']
        self._labeled_connections = self._get_labeled_connections()

    def _get_labeled_connections(self):
        """Return the list of connections labeled by the symbol which caused the
        transition"""
        labeled_connections = list()
        for connection in self._connections:
            # symbol: the grammar symbol of GOTO(Itemset, Grammar_symbol)
            label = self._symbols[self._itemsets[connection[1]][0][1]
                    [self._itemsets[connection[1]][0][0]]]
            labeled_connections.append([connection[0], connection[1], label])
        return labeled_connections


    def plot_graph(self, name='graph'):
        """If the grammar is SLR(1), output the corresponding DFA"""
        graph = pydot.Dot(graph_type='digraph')
        gsr = self._checker.get_string_rules
        # Create nodes and add them to the graph
        for pos, itemset in enumerate(self._itemsets):
            self._nodes.append(pydot.Node(gsr(itemset, pos).encode(
                'string-escape')))
            self._nodes[pos].set_shape("box")
            graph.add_node(self._nodes[pos])
        # Create edges and add them to the graph
        for labeled_connection in self._labeled_connections:
            graph.add_edge(pydot.Edge(self._nodes[labeled_connection[0]],
                self._nodes[labeled_connection[1]],
                label=labeled_connection[2]))
        graph.write(name + ".png", format="png")
        print "Image generated as", name + ".png"


    def print_graph(self):
        """If the grammar is SLR(1), print the parser states graph"""
        for pos, itemset in enumerate(self._itemsets):
            print self._checker.get_string_rules(itemset, pos)
            print "Connected to (GOTO, itemset):"
            for labeled_connection in self._labeled_connections:
                if labeled_connection[0] == pos:
                    print labeled_connection[2], ",", str(labeled_connection[1])
            print "\n" + "-"*80 + "\n"

def main():
    """Main"""
    separator = '->'
    out = 'graph'
    mode = None # default 'plot'
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hps:o:",
                ["help", "separator=", "print", "out="])
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
        elif opt in ("-p", "--print"):
            mode = 'print'
        elif opt in ("-o", "--out"):
            out = arg
    if len(args) == 0:
        print("WARNING: No file supplied, doing nothing")
    for filex in args:
        with open(filex, 'r') as fpt:
            gen = SLR1Graph(fpt.readlines(), separator)
            if mode is None:
                if True:
                    print "Unable to generate image, printing instead"
                    gen.print_graph()
                else:
                    gen.plot_graph(out)
            else:
                gen.print_graph()

def usage():
    """Help message"""
    help_msg = """
    Help:
    {0} [-h|--help]
    {0} [-s<sep>|--separator=<sep>] [-p|--print] [-o<file>|--out=<file>] FILES

    Options:
    help: Display this information
    separator <sep>: Change the separator to be used to <sep>
    print: Print the parser state graph instead of plotting it
    out <file>: Output the graph image into <file>

    Notice that options should ever precede FILES
    """.format(sys.argv[0])
    print help_msg

if __name__ == "__main__":
    main()
