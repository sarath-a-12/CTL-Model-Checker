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




no_of_states = int(input("Enter the number of states\n"))
kripke_structure = Graph()
for i in range(no_of_states):
    kripke_structure.add_vertex(i)
    # print(kripke_structure.graph)
# reverse_graph = kripke_structure.reverse()
label_strings = {}
for key in kripke_structure.graph:
    state = kripke_structure.graph[key]
    label_strings[state.v] = set(['T'])
    print(f"Enter the transitions (1 - {no_of_states}) for state {i+1} and press Ctrl-D")
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


# for i in states:
#     print(i.adj_list)
# print("============")
# for i in reverse_graph:
#     print(i.adj_list)
# p1 = "EX(p)"
# p1 = "EX(((p) & (~(q))) | ((q) & (~(p))))"
# p1 = "~ ((p) | (q))"
# p1 = "E [(T) U (q)]"
p1 = "EG ((p) & (q))"
# p3 = "EF p"

form = ctlparser.parse_ctl_formula(p1)
parse_tree_nodes = ctlparser.find_leaf_nodes(form, 0)
parse_tree_nodes.reverse()
# print(parse_tree_nodes)
#
#
# q = queue.Queue()
#
# for i in leaf_nodes:
#     q.put(i)
#     i.visited = True
#
# while not q.empty():
#     for element in q.queue:
#         print(element.val, end = ' ')
#     print()
#     parse_tree_node = q.get()
#     # print(n.val)
for level in parse_tree_nodes:
    for parse_tree_node in level:
        
        if parse_tree_node.child == None and parse_tree_node.left == None and parse_tree_node.right == None: #leaf node
            for key in kripke_structure.graph: #find all states which satisfy the atomic proposition
                state = kripke_structure.graph[key]
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
            #creation of restricted graph
            restricted_graph = Graph()
            states_satisfying_psi = 0
            for key in kripke_structure.graph:
                state = kripke_structure.graph[key]
                if state.v in parse_tree_node.child.satisfying_states:
                    restricted_graph.add_vertex(state.v)

            for key in restricted_graph.graph:
                state = kripke_structure.graph[key]
                for neighbour in kripke_structure.graph[state.v].adj_list:
                    if neighbour in restricted_graph.graph:
                        restricted_graph.add_edge(state.v, neighbour)
            # for i in restricted_graph.graph:
            #     print(f"{i} - [{restricted_graph.graph[i].adj_list}]")

            # reverse_restricted_graph = [None for i in range(no_of_states + 1)]
            # for state in restricted_graph:
            #     if not state == None:
            #         reverse_restricted_graph[state.v] = KripkeStructureNode(state.v)
            # for state in restricted_graph:
            #     if not state == None:
            #         for neighbour in restricted_graph[state.v].adj_list:
            #             reverse_restricted_graph[neighbour].adj_list.add(state.v)
            reverse_restricted_graph = restricted_graph.reverse()

            # for i in reverse_restricted_graph:
            #     if i:
            #         print(f"{i.v} - [{i.adj_list}]")

            #dfs 1 for finding scc's
            # def dfs(node, stack, graph):
            #     node.visited = True
            #     for neighbour in node.adj_list:
            #         if not graph[neighbour].visited:
            #             dfs(graph[neighbour].v, stack, graph)
            #     stack.append(node)
            stack = []
            for key in restricted_graph.graph:
                state = restricted_graph.graph[key]
                if not state.visited:
                    restricted_graph.dfs(state.v, stack)

            # for i in stack:
            #     print(f"{i.v} - {i.adj_list}")
            for key in stack:
                state = restricted_graph.graph[key]
                state.visited = False

            sccs = []
            while stack:
                state = stack.pop()
                if not reverse_restricted_graph.graph[state].visited:
                    component = []
                    reverse_restricted_graph.dfs(state, component)
                    sccs.append(component)
            # print(sccs)

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

            # for component in sccs:
            #     if len(component) == 1 and component[0] not in restricted_graph.graph[component[0]].adj_list:
            comp_number = -1
            dictionary = {}
            for component in sccs:
                comp_number += 1
                for ver in component:
                    dictionary[ver] = comp_number
            # print(dictionary)
            meta_graph = Graph()
            for i in range(len(sccs)):
                meta_graph.add_vertex(i)
            for key in restricted_graph.graph:
                state = restricted_graph.graph[key]
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
            # for state in parse_tree_node.right.satisfying_states:
            #     if state in parse_tree_node.left.satisfying_states:
            #         parse_tree_node.satisfying_states.add(state)
            # print(parse_tree_node.right.satisfying_states)
            for state in range(1, no_of_states + 1):
                if state in parse_tree_node.left.satisfying_states and state in parse_tree_node.right.satisfying_states:
                    parse_tree_node.satisfying_states.add(state)


        elif parse_tree_node.val == 'OR':
            for state in parse_tree_node.right.satisfying_states:
                parse_tree_node.satisfying_states.add(state)
            for state in parse_tree_node.left.satisfying_states:
                parse_tree_node.satisfying_states.add(state)

        elif parse_tree_node.val == 'NOT':
            for state in range(1, no_of_states + 1):
                if not (state in parse_tree_node.child.satisfying_states):
                    parse_tree_node.satisfying_states.add(state)

        elif parse_tree_node.val == 'IMPLIES':
            for state in range(1, no_of_states + 1):
                if not (state in parse_tree_node.left.satisfying_states):
                    parse_tree_node.satisfying_states.add(state)
                if state in parse_tree_node.right.satisfying_states:
                    parse_tree_node.satisfying_states.add(state)

        # if parse_tree_node.parent and parse_tree_node.parent.visited == False:
        #         q.put(parse_tree_node.parent)
        #         parse_tree_node.parent.visited = True
#

# print(form.left.right.satisfying_states)
print(form.satisfying_states)
