import ctlparser
import queue
import copy


class KripkeStructureNode:
    def __init__(self,v):
        self.v = v
        self.adj_list = set([])
        self.visited = False

no_of_states = int(input("Enter the number of states\n"))
states = [KripkeStructureNode(i) for i in range(no_of_states+1)]
reverse_graph = copy.deepcopy(states)
label_strings = {}
for i in range(no_of_states):
    node = states[i+1]
    label_strings[i+1] = set(['T'])
    print(f"Enter the transitions (1 - {no_of_states}) for state {i+1} and press Ctrl-D")
    try:
        while True:
            transition = (input())
            if transition == "EOF":
                break
            transition = int(transition)
            node.adj_list.add(transition)
            reverse_graph[transition].adj_list.add(node.v) #Adding a backedge for reverse graph

    except EOFError:
        pass

    print(f"Enter the propositions (a-z) and press Ctrl-D")
    try:
        while True:
            proposition = input()
            if proposition == "EOF":
                break
            label_strings[node.v].add(proposition)
    except EOFError:
        pass


# for i in states:
#     print(i.adj_list)
# print("============")
# for i in reverse_graph:
#     print(i.adj_list)
# p1 = "EX(p)"
p1 = "(p) & (q)"
# p1 = "E [(p) U (q)]"
# p3 = "EF p"

form = ctlparser.parse_ctl_formula(p1)
leaf_nodes = ctlparser.find_leaf_nodes(form)
#
#
q = queue.Queue()

for i in leaf_nodes:
    q.put(i)
    i.visited = True

while not q.empty():
    parse_tree_node = q.get()
    # print(n.val)

    if parse_tree_node.child == None and parse_tree_node.left == None and parse_tree_node.right == None: #leaf node
        for state in states: #find all states which satisfy the atomic proposition
            if state.v in label_strings and parse_tree_node.val in label_strings[state.v]:
                # print(f"{n.val} in {state.v}")
                parse_tree_node.satisfying_states.add(state.v)

    elif parse_tree_node.val == 'EX':
        q2 = queue.Queue()
        for st in parse_tree_node.child.satisfying_states:
            q2.put(st)
        while not q2.empty():
            n2 = q2.get()
            for neighbour in reverse_graph[n2].adj_list:
                if reverse_graph[neighbour].visited == False:
                    reverse_graph[neighbour].visited = True
                    parse_tree_node.satisfying_states.add(neighbour)

    elif parse_tree_node.val == 'EU':
        q2 = queue.Queue()
        for st in parse_tree_node.right.satisfying_states:
            parse_tree_node.satisfying_states.add(st)
            q2.put(st)
            reverse_graph[st].visited = True

        while not q2.empty():
            n = q2.get()
            for neighbour in reverse_graph[n].adj_list:
                if reverse_graph[neighbour].visited == False and (neighbour in parse_tree_node.left.satisfying_states):
                    reverse_graph[neighbour].visited = True
                    q2.put(neighbour)
                    parse_tree_node.satisfying_states.add(neighbour)

    if parse_tree_node.parent and parse_tree_node.parent.visited == False:
            q.put(parse_tree_node.parent)
            parse_tree_node.parent.visited = True

for h in form.satisfying_states:
    print(h)
