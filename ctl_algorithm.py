from enum import global_enum_repr
import ctlparser
import queue
import copy


class KripkeStructureNode:
    def __init__(self,v):
        self.v = v
        self.adj_list = set([])
        self.visited = False

class Graph:
    def __init__(self):
        self.size = 0
        self.graph = {}

    def add_vertex(self, v):
        self.graph[v] = KripkeStructureNode(v)
        self.size += 1

    def add_edge(self, u, v):
        self.graph[u].adj_list.add(v)

    def reverse(self):
        reversed = Graph()
        for vertex in self.graph:
            reversed.add_vertex(vertex)
        for vertex in self.graph:
            for outneighbour in self.graph[vertex].adj_list:
                reversed.add_edge(outneighbour, vertex)
        return reversed

    def dfs(self, v, stack):
        v = self.graph[v]
        v.visited = True
        for neighbour in self.graph[v.v].adj_list:
            if not self.graph[neighbour].visited:
                self.dfs(neighbour, stack)
        stack.append(v.v)

    def clear_visited(self):
        for ver in self.graph.values():
            ver.visited = False





no_of_states = int(input("Enter the number of states\n"))
kripke_structure = Graph()
for i in range(no_of_states):
    kripke_structure.add_vertex(i)

label_strings = {}
counter = 0
for state in kripke_structure.graph.values():
    label_strings[state.v] = set(['T'])
    print(f"Enter the transitions (0 - {no_of_states - 1}) for state {counter} and press Ctrl-D")
    try:
        while True:
            transition = (input())
            if transition == "EOF":
                break
            transition = int(transition)
            kripke_structure.add_edge(state.v, transition)

    except EOFError:
        pass

    print(f"Enter the propositions (a-z) and press Ctrl-D")
    try:
        while True:
            proposition = input()
            if proposition == "EOF":
                break
            label_strings[state.v].add(proposition)
    except EOFError:
        pass
    counter += 1

# p1 = "EX(p)"
# p1 = "EX(((p) & (~(q))) | ((q) & (~(p))))"
# p1 = "~ ((p) | (q))"
# p1 = "E [(T) U (q)]"
# p1 = "EG ((p) & (q))"
# p1 = "A [(p) U (r)]"
# p1 = "AX ( (q) & (r))"
# p1 = " A[ (p) U (q)]"
# p1 = "AG (F)"
# p1 = "EG (p)"
# p1 = "AG (AF (p))"
# p1 = "p"
# p1 = "E [ (~(q)) U (~ ((p) | (q)))]"

def compute(ctl_formula):
    form = ctlparser.parse_ctl_formula(ctl_formula)
    if form == None:
        print("Formula is syntactically invalid. Try again!")
        return
    print("\n\n===================================\nEquivalent formula using minimal set of operators (EG, EU, EX, &, |, ~, ->) is : ")
    print(form.subformula)
    print("\n\n===================================\nNumber of nodes in psi is : ", end = ' ')
    print(form.number_of_nodes)
    parse_tree_nodes = ctlparser.find_leaf_nodes(form, 0, [])
    parse_tree_nodes.reverse()
    for level in parse_tree_nodes:
        for parse_tree_node in level:
            kripke_structure.clear_visited()
            
            if parse_tree_node.child == None and parse_tree_node.left == None and parse_tree_node.right == None: #leaf node
                if parse_tree_node.val == "TRUE":
                    for state in kripke_structure.graph.values():
                        parse_tree_node.satisfying_states.add(state.v)
                for state in kripke_structure.graph.values(): #find all states which satisfy the atomic proposition
                    if state.v in label_strings and parse_tree_node.val in label_strings[state.v]:
                        # print(f"{n.val} in {state.v}")
                        parse_tree_node.satisfying_states.add(state.v)

            elif parse_tree_node.val == 'EX':
                q2 = queue.Queue()
                reverse_kripke_structure = kripke_structure.reverse()
                for st in parse_tree_node.child.satisfying_states:
                    q2.put(st)
                while not q2.empty():
                    n2 = q2.get()
                    for neighbour in reverse_kripke_structure.graph[n2].adj_list: 
                        if reverse_kripke_structure.graph[neighbour].visited == False:
                            reverse_kripke_structure.graph[neighbour].visited = True
                            parse_tree_node.satisfying_states.add(neighbour)

            elif parse_tree_node.val == 'EU':
                q2 = queue.Queue()
                reverse_kripke_structure = kripke_structure.reverse()
                for st in parse_tree_node.right.satisfying_states:
                    parse_tree_node.satisfying_states.add(st)
                    q2.put(st)
                    reverse_kripke_structure.graph[st].visited = True

                while not q2.empty():
                    n = q2.get()
                    for neighbour in reverse_kripke_structure.graph[n].adj_list:
                        if reverse_kripke_structure.graph[neighbour].visited == False and (neighbour in parse_tree_node.left.satisfying_states):
                            reverse_kripke_structure.graph[neighbour].visited = True
                            q2.put(neighbour)
                            parse_tree_node.satisfying_states.add(neighbour)

            elif parse_tree_node.val == 'EG':
                restricted_graph = Graph()
                for state in kripke_structure.graph.values():
                    if state.v in parse_tree_node.child.satisfying_states:
                        restricted_graph.add_vertex(state.v)

                for state in restricted_graph.graph.values():
                    for neighbour in kripke_structure.graph[state.v].adj_list:
                        if neighbour in restricted_graph.graph:
                            restricted_graph.add_edge(state.v, neighbour)

                reverse_restricted_graph = restricted_graph.reverse()

                stack = []
                for state in restricted_graph.graph.values():
                    if not state.visited:
                        restricted_graph.dfs(state.v, stack)

                for state in stack:
                    restricted_graph.graph[state].visited = False

                sccs = []
                while stack:
                    state = stack.pop()
                    if not reverse_restricted_graph.graph[state].visited:
                        component = []
                        reverse_restricted_graph.dfs(state, component)
                        sccs.append(component)

                good_sccs = []
                for component in sccs:
                    if len(component) >= 2:
                        good_sccs.append(component)
                        for vertex in component:
                            parse_tree_node.satisfying_states.add(vertex)
                    else: #size of the component is 1
                        ver = component[0]
                        if ver in restricted_graph.graph[ver].adj_list: #checking for self-looped sccs
                            parse_tree_node.satisfying_states.add(ver)
                            good_sccs.append(component)

                comp_number = -1
                dictionary = {}
                for component in sccs:
                    comp_number += 1
                    for ver in component:
                        dictionary[ver] = comp_number
                
                meta_graph = Graph()
                for i in range(len(sccs)):
                    meta_graph.add_vertex(i)
                for state in restricted_graph.graph.values():
                    for neighbour in state.adj_list:
                        if not dictionary[state.v] == dictionary[neighbour]:
                            meta_graph.add_edge(dictionary[state.v], dictionary[neighbour])

                reverse_meta_graph = meta_graph.reverse()
                visitable = []
                for component in good_sccs:
                    v = dictionary[component[0]]
                    if not reverse_meta_graph.graph[v].visited:
                        reverse_meta_graph.graph[v].visited = True
                        reverse_meta_graph.dfs(v, visitable)
                for visitable_vertex in visitable:
                    if len(sccs[visitable_vertex]) == 1:
                        for vertices in sccs[visitable_vertex]:
                            parse_tree_node.satisfying_states.add(vertices)

            elif parse_tree_node.val == 'AND':
                for state in range(no_of_states):
                    if state in parse_tree_node.left.satisfying_states and state in parse_tree_node.right.satisfying_states:
                        parse_tree_node.satisfying_states.add(state)

            elif parse_tree_node.val == 'OR':
                for state in parse_tree_node.right.satisfying_states:
                    parse_tree_node.satisfying_states.add(state)
                for state in parse_tree_node.left.satisfying_states:
                    parse_tree_node.satisfying_states.add(state)

            elif parse_tree_node.val == 'NOT':
                for state in range(no_of_states):
                    if not (state in parse_tree_node.child.satisfying_states):
                        parse_tree_node.satisfying_states.add(state)

            elif parse_tree_node.val == 'IMPLIES':
                for state in range(no_of_states):
                    if not (state in parse_tree_node.left.satisfying_states): parse_tree_node.satisfying_states.add(state)
                    if state in parse_tree_node.right.satisfying_states:
                        parse_tree_node.satisfying_states.add(state)


    counter = 0
    for level in parse_tree_nodes:
        for parse_tree_node in level:
            print(f"Level = {counter}\tNode - id = {parse_tree_node.val}\tSubformula of node = {parse_tree_node.subformula}")
            if len(parse_tree_node.satisfying_states) == 0:
                print(f"No state satisfies this node\n")
            else:
                print(f"The states satisfying the node are : {parse_tree_node.satisfying_states}\n")
        counter += 1



    if len(form.satisfying_states):
        print(f"\n\n===================================\nSet of states satisfying the formula are : {form.satisfying_states}\n")
    else:
        print("\n\n===================================\nNo states satisfy the CTL formula\n")

while True:
    try:
        form = input("Enter the fully bracketed CTL formula to be checked\n")
        compute(form)

    except EOFError:
        continue
