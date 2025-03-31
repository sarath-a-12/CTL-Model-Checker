from sly import Parser
from ctllex import CTLLexer
import copy
import queue


class ParseTreeNode():
    def __init__(self, binary = False, left = None, right = None, child = None, parent = None, val = ""):
        self.binary = binary 
        self.left = left 
        self.right = right
        self.child = child  
        self.parent = parent 
        self.val = val
        self.number_of_nodes = 0 # number of nodes for the subtree from the current node
        self.subformula = ""
        self.depth = -1
        self.visited = False
        self.satisfying_states = set([]) 

class CTLParser(Parser):
    tokens = CTLLexer.tokens

    @_('"(" phi ")" "&" "(" phi ")"', '"(" phi ")" "|" "(" phi ")"', '"(" phi ")" IMPLIES "(" phi ")"')
    def phi(self, t):
        match t[3]:
            case '&':
                val = 'AND'
            case '|':
                val = 'OR'
            case _:
                val = 'IMPLIES'
        x = ParseTreeNode(binary = True, val = val, left = t[1], right = t[5])
        t[1].parent = x
        t[5].parent = x
        x.number_of_nodes = t[1].number_of_nodes + t[5].number_of_nodes + 1
        x.subformula = f"( {t[1].subformula} ) {t[3]} ( {t[5].subformula} )"
        return x

    @_('"~" "(" phi ")"')
    def phi(self, t):
        x = ParseTreeNode(val = 'NOT', child = t.phi)
        t.phi.parent = x
        x.number_of_nodes = t.phi.number_of_nodes + 1
        x.subformula = f"~ ( {t.phi.subformula} )"
        return x

    @_(' "A" "[" "(" phi ")" "U" "(" phi ")" "]" ')
    def phi(self, t):
        phi1 = t[3]
        phi1_copy = copy.deepcopy(phi1)
        phi2 = t[7]
        phi2_copy = copy.deepcopy(phi2)
        phi2_copy2 = copy.deepcopy(phi2)
        n1 = ParseTreeNode(val = 'NOT', child = phi2_copy2)
        n1.subformula = f"~ ( {phi2_copy2.subformula} )"
        phi1.parent = n1
        n2 = ParseTreeNode(val = 'NOT', child = phi2)
        n2.subformula = f"~ ( {phi2.subformula} )"
        phi2.parent = n2
        n3 = ParseTreeNode(val = 'OR', binary = True, left = phi1_copy, right = phi2_copy)
        n3.subformula = f"( {phi1_copy.subformula} ) | ( {phi2_copy.subformula} )"
        phi1_copy.parent = n3
        phi2_copy.parent = n3
        n4 = ParseTreeNode(val = 'NOT', child = n3)
        n4.subformula = f"~ ( {n3.subformula} )"
        n3.parent = n4
        n5 = ParseTreeNode(val = 'EG', child = n1)
        n5.subformula = f"EG ( {n1.subformula} )"
        n1.parent = n5
        n6 = ParseTreeNode(val = 'EU', binary = True, left = n2, right = n4)
        n6.subformula = f"E [ ( {n2.subformula} ) U ( {n4.subformula} ) ]"
        n2.parent = n6
        n4.parent = n6
        n7 = ParseTreeNode(val = 'OR', binary = True, left = n5, right = n6)
        n7.subformula = f"( {n5.subformula} ) | ( {n6.subformula} )"
        n5.parent = n7
        n6.parent = n7
        n8 = ParseTreeNode(val = 'NOT', child = n7)
        n7.parent = n8
        n8.number_of_nodes = 2 * phi1.number_of_nodes + 2 * phi2.number_of_nodes + 8
        n8.subformula = f"~ ( {n7.subformula} )"
        return n8


    @_(' "E" "[" "(" phi ")" "U" "(" phi ")" "]" ')
    def phi(self, t):
        x = ParseTreeNode(val = 'EU', binary = True, left = t[3], right = t[7])
        t[3].parent = x
        t[7].parent = x
        x.number_of_nodes = t[3].number_of_nodes + t[7].number_of_nodes + 1
        x.subformula = f"E [ ( {t[3].subformula} ) U ( {t[7].subformula} ) ]"
        return x


    @_('AX "(" phi ")" ')
    def phi(self, t):
        z = ParseTreeNode(val = 'NOT', child = t.phi)
        z.subformula = f"~ ( {t.phi.subformula} )"
        t.phi.parent = z
        y = ParseTreeNode(val = 'EX', child = z)
        y.subformula = f"EX ( {z.subformula} )"
        z.parent = y
        x = ParseTreeNode(val = 'NOT', child = y)
        y.parent = x
        x.number_of_nodes = t.phi.number_of_nodes + 3
        x.subformula = f"~ ( {y.subformula} )"
        return x

    @_('EX "(" phi ")" ')
    def phi(self, t):
        x = ParseTreeNode(val = 'EX', child = t.phi)
        t.phi.parent = x
        x.number_of_nodes = t.phi.number_of_nodes + 1
        x.subformula = f"EX ( {t.phi.subformula} )"
        return x


    @_('AG "(" phi ")" ')
    def phi(self, t):
        n1 = ParseTreeNode(val = 'NOT', child = t.phi)
        n1.subformula = f"~ ( {t.phi.subformula} )"
        t.phi.parent = n1
        n2 = ParseTreeNode(val = 'TRUE')
        n2.subformula = f" TRUE "
        n3 = ParseTreeNode(val = 'EU', left = n2, right = n1)
        n3.subformula = f"E [ ( {n2.subformula} ) U ( {n1.subformula} ) ]"
        n2.parent = n3
        n1.parent = n3
        n4 = ParseTreeNode(val = 'NOT', child = n3)
        n3.parent = n4
        n4.number_of_nodes = t.phi.number_of_nodes + 4
        n4.subformula = f"~ ( {n3.subformula} )"
        return n4

    @_('EG "(" phi ")" ')
    def phi(self, t):
        x = ParseTreeNode(val = 'EG', child = t.phi)
        t.phi.parent = x
        x.number_of_nodes = t.phi.number_of_nodes + 1
        x.subformula = f"EG ( {t.phi.subformula} )"
        return x



    @_('AF "(" phi ")" ')
    def phi(self, t):
        z = ParseTreeNode(val = 'NOT', child = t.phi)
        z.subformula = f"~ ( {t.phi.subformula} )"
        t.phi.parent = z
        y = ParseTreeNode(val = 'EG', child = z)
        y.subformula = f"EG ( {z.subformula} )"
        z.parent = y
        x = ParseTreeNode(val = 'NOT', child = y)
        y.parent = x
        x.number_of_nodes = t.phi.number_of_nodes + 3
        x.subformula = f"~ ( {y.subformula} )"

        return x

    @_('EF "(" phi ")" ')
    def phi(self, t):
        x = ParseTreeNode(val = 'EU',binary = True, right = t.phi)
        y = ParseTreeNode(val = 'TRUE', parent = x)
        y.subformula = "T"
        x.left = y
        t.phi.parent = x
        x.number_of_nodes = t.phi.number_of_nodes + 2
        x.subformula = f"E [ ({y.subformula}) U ({t.phi.subformula}) ]"
        return x


    @_('VAR', 'TRUE', 'FALSE')
    def phi(self, t):
        x = ParseTreeNode(val = t[0])
        x.number_of_nodes = 1
        var = t[0]
        match t[0]:
            case "T":
                var = "TRUE"
            case "F":
                var = "FALSE"
        x.subformula = var
        return x


depths = []
leaf_nodes = []
def find_leaf_nodes(node, depth):
    if depth < len(depths):
        depths[depth].append(node)
    else:
        depths.append([node])
    if not (node.left or node.right or node.child):
        return depths
    if node.left:
        find_leaf_nodes(node.left, depth + 1)
    if node.right:
        find_leaf_nodes(node.right, depth + 1)
    if node.child:
        find_leaf_nodes(node.child, depth + 1)
    return depths


def bottom_up_traversal(leaf_nodes): #do a bottom up traversal starting from leaf nodes
    levels = [[]]
    q = queue.Queue()
    ctr = 0
    for i in leaf_nodes:
        q.put(i)
        i.visited = True
    q.put(None)
    
    while not q.empty():
        n = q.get()
        if n is None:
            levels.append([])
            ctr += 1
            if not q.empty():
                q.put(None)
            continue

        levels[ctr].append(n)
        if n.parent and n.parent.visited == False:
                q.put(n.parent)
                n.parent.visited = True

    # print(levels)
    return levels


def parse_ctl_formula(data):
    lexer = CTLLexer()
    parser = CTLParser()
    final = parser.parse(lexer.tokenize(data))
    # print(final)
    # leaf_nodes = find_leaf_nodes(final)
    # print(leaf_nodes)
    # bottom_up_traversal()
    # print(leaf_nodes)
    return final

    # print()
    # print(f"Total number of nodes = {final.number_of_nodes}")
    # print(final.subformula)
    # levels.reverse()
    # for i in levels:
    #         for j in i:
    #             print(f"Node = {j.val} - Subformula at node = {j.subformula}")
    # print(final.child.right.child.val)
