import itertools
import sys

DEBUG = 0

class Node:
    """
    members:

    pos: (i, j) tuple
    destCount
    curCount
    edges: all edges, may include used edges
    availEdges
    """
    def __init__(self, pos, count):
        self.pos = pos[0], pos[1]
        self.destCount = count
        self.curCount = 0
        self.edges = []
        self.availEdges = set()
        self.handled = False

    def __hash__(self):
        return hash(self.pos)

    def neigs(self):
        for edge in self.edges:
            if edge.usedTime:
                yield edge.other(self)

    def choose_edges(self):
        es = list(self.availEdges)
        k = len(es)
        candis = []
        for dist in itertools.product(*(x.range for x in es)):
            if sum(dist) + self.curCount == self.destCount:
                item = list(zip(dist, es))
                if all(e.can_use(count) for count, e in zip(dist, es)):
                    conflictCount = sum(e.use(count) for count, e in item)
                    for e in reversed(es): e.unuse()
                    candis.append((conflictCount, item))
        candis.sort(key=lambda c_x: c_x[0])
        return [item for key, item in candis]

    def __repr__(self):
        return 'Node({}, dest={}, cur={})'.format(self.pos, self.destCount, self.curCount)
        # return 'N({})'.format(self.pos)

class Edge:
    """
    members:

    p1, p2: two end nodes of this edge
    crosses: all edges that cross with this edge
    usedTime: how many time this edge be used
    """
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.crosses = []
        self.usedTime = 0
        self.avail = True
        self.range = tuple(k for k in (0, 1, 2) if k <= p1.destCount and k <= p2.destCount)

    def can_use(self, count):
        p1, p2 = self.p1, self.p2
        return self.avail \
                and p1.curCount + count <= p1.destCount \
                and p2.curCount + count <= p2.destCount

    def use(self, count):
        self.usedTime = count
        if count > 0:
            self.p1.curCount += count
            self.p2.curCount += count
            self._backup = backup = []
            for edge in self.crosses:
                p1, p2 = edge.p1, edge.p2
                if edge.avail:
                    p1.availEdges.remove(edge)
                    p2.availEdges.remove(edge)
                    backup.append(edge)
                edge.avail = False
            if DEBUG and backup: print('backup:', backup)
            conflictCount = len(backup)
        else:
            conflictCount = 0
        self.avail = False
        self.p1.availEdges.discard(self)
        self.p2.availEdges.discard(self)
        return conflictCount

    def unuse(self):
        self.p1.availEdges.add(self)
        self.p2.availEdges.add(self)
        self.avail = True
        if self.usedTime > 0:
            for edge in self._backup:
                edge.p1.availEdges.add(edge)
                edge.p2.availEdges.add(edge)
                edge.avail = True
            self.p1.curCount -= self.usedTime
            self.p2.curCount -= self.usedTime
        self.usedTime = 0

    def other(self, node):
        if node == self.p1:
            return self.p2
        if node == self.p2:
            return self.p1

    def __hash__(self):
        return hash((self.p1, self.p2))

    def __repr__(self):
        return 'E({},{},{})'.format(self.p1.pos, self.p2.pos, self.usedTime)

class CSPChooser:
    def __init__(self):
        self._cache = {}

    def __call__(self, availNodes):
        # choose most constrainted then most constraining node
        return max(availNodes, key=self.key_func)

    def key_func(self, x):
        return self.get_constrainted_level(x), self.get_constraining_level(x)

    def get_constraining_level(self, node):
        return node.destCount - node.curCount

    def get_constrainted_level(self, node):
        # numEdges = sum(1 for e in node.edges if e.avail)
        numEdges = len(node.availEdges)
        key = (node.destCount - node.curCount, numEdges)
        value = self._cache.get(key, None)
        if value is not None:
            return value
        value = 0
        n, k = key
        for dist in itertools.product(*((0,1,2) for x in range(k))):
            if sum(dist) == n:
                value -= 1
        self._cache[key] = value
        return value

class BetterCSPChooser(CSPChooser):
    def __call__(self, availNodes):
        # choose most constrainted then most constraining node
        maxVal = None
        for node in availNodes:
            a = self.get_constrainted_level(node)
            if a >= -1:
                return node
            b = self.get_constraining_level(node)
            if maxVal is None or (a, b) > maxVal:
                maxVal = (a, b)
                maxNode = node
        return maxNode

    def get_constraining_level(self, node):
        # return 5 * len(node.availEdges) + (node.destCount - node.curCount)
        # return sum(1 for node1 in node.neigs() if node1.handled)
        return len(node.availEdges)

class UFSet:
    def __init__(self):
        self.father = {}

    def get_father(self, x):
        y = self.father.get(x, x)
        if y == x: return x
        fa = self.father[x] = self.get_father(y)
        return fa

    def union(self, fa1, fa2):
        self.father[fa1] = fa2

    def copy(self):
        x = UFSet()
        x.father = self.father.copy()
        return x

class IslandChecker:
    def __init__(self):
        self.nodes = []

    def append(self, node):
        self.nodes.append(node)
        isNodeOpen = not all(e.other(node).handled for e in node.edges if e.usedTime)
        if isNodeOpen or not has_island(self.nodes):
            return True
        else:
            self.nodes.pop()

    def pop(self):
        self.nodes.pop()

class AdvancedIslandChecker: pass

def parse(data, EmptyLand=' '):
    a = data.split('\n')
    if a[-1] == '': del a[-1]
    n, m = len(a), len(a[0])

    a = {(i, j):a[i][j] for i in range(n) for j in range(m)}
    eslots = {p:[] for p in a}
    nodes = {p:Node(p, int(x)) for p, x in a.items() if x!=EmptyLand}
    edges = []
    for pos, node in nodes.items():
        i1, j1 = pos
        for di, dj in ((0, 1), (1, 0)):
            i2, j2 = i1 + di, j1 + dj
            path = []
            edge = node1 = None
            while (i2, j2) in a:
                if a[i2, j2] != EmptyLand:
                    node1 = nodes[i2, j2]
                    edge = Edge(node, node1)
                    break
                path.append((i2, j2))
                i2, j2 = i2 + di, j2 + dj
            if edge:
                node.edges.append(edge)
                node1.edges.append(edge)
                edges.append(edge)
                for p in path:
                    for edge1 in eslots[p]:
                        edge.crosses.append(edge1)
                        edge1.crosses.append(edge)
                    eslots[p].append(edge)
    return list(nodes.values()), edges, a

def solve(nodes, edges, a):
    for node in nodes:
        node.availEdges = set(node.edges)

    availNodes = set(nodes)
    handledNodes = []
    n, m = max(a.keys())
    n, m = n + 1, m + 1
    print('nodes count:', len(nodes))
    print('edges count:', len(edges))
    print('map size: {}x{}'.format(n, m))
    chooser = BetterCSPChooser()
    # chooser = CSPChooser()
    islandChecker = IslandChecker()
    for edges in search(availNodes, handledNodes, edges, chooser, islandChecker):
        print('-' * 80)
        b = a.copy()
        for edge in edges:
            if not edge.usedTime: continue
            (i1, j1), (i2, j2) = edge.p1.pos, edge.p2.pos
            if i1 == i2:
                # horizonal edge
                for j in range(min(j1, j2)+1, max(j1, j2)):
                    b[i1, j] = '-='[edge.usedTime-1]
            else:
                # vertical edge
                for i in range(min(i1, i2)+1, max(i1, i2)):
                    b[i, j1] = '|║'[edge.usedTime-1]
        print('found solution:')
        for i in range(n):
            print(' '.join(b[i, j] for j in range(m)))
        break

def is_connected(nodes):
    if not nodes: return True
    node = next(iter(nodes))
    stk = [node]
    avail = set(nodes)
    avail.remove(node)
    bfs(stk, avail)
    return len(avail) == 0

def bfs(stk, avail):
    while stk:
        node = stk.pop()
        for node1 in node.neigs():
            if node1.handled and node1 in avail:
                avail.remove(node1)
                stk.append(node1)

def has_island(nodes):
    stk = []
    avail = set(nodes)
    for node in nodes:
        if any(e.usedTime and not e.other(node).handled for e in node.edges):
            avail.remove(node)
            stk.append(node)
    bfs(stk, avail)
    return len(avail) > 0

def search(availNodes, handledNodes, solution, choose, islandChecker):
    if DEBUG: print('<search availNum={}>'.format(len(availNodes)))
    # choose one node pivotNode
    pivotNode = choose(availNodes)
    pivotNode.handled = True
    availNodes.remove(pivotNode)
    handledNodes.append(pivotNode)
    # choose edges for pivotNode
    # if DEBUG: print('<pivot node={}, availNums={}>'.format(pivotNode, len(pivotNode.availEdges)))
    for choosedEdges in pivotNode.choose_edges():
        # if DEBUG: print('<choosed>')
        # apply changes
        for count, edge in choosedEdges:
            # if DEBUG: print('<use edge={}>'.format(edge))
            edge.use(count)
            # if DEBUG: print('</use>')
        # resursive search
        if availNodes:
            if islandChecker.append(pivotNode):
                for solution in search(availNodes, handledNodes, edges, choose, islandChecker):
                    yield solution
                islandChecker.pop()
        elif is_connected(handledNodes):
            yield solution
        # revert changes, recover states of nodes and edges 
        for count, edge in choosedEdges:
            edge.unuse()
            # if DEBUG: print('<unuse>{}</unuse>'.format(edge))
        # if DEBUG: print('</choosed>')
    # if DEBUG: print('</pivot>')
    handledNodes.pop()
    availNodes.add(pivotNode)
    pivotNode.handled = False
    if DEBUG: print('</search>')

data = open(sys.argv[1]).read()
nodes, edges, a = parse(data)
solve(nodes, edges, a)
