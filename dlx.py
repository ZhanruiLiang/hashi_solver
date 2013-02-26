class Unit:
    """
    Data unit of DLX algorithm.
    """
    def __init__(self):
        self.left = self.right = self.up = self.down = self

    def remove_h(self):
        "Remove this unit from horizonal list."
        # stt[curLevel[0]] += 1
        self.left.right, self.right.left = self.right, self.left

    def remove_v(self):
        "Remove this unit from vertical list."
        # stt[curLevel[0]] += 1
        self.up.down, self.down.up = self.down, self.up

    def undo_h(self):
        "Add back this unit to horizonal list."
        self.left.right, self.right.left = self, self

    def undo_v(self):
        "Add back this unit to vertical list."
        self.up.down, self.down.up = self, self

    def iter(self, dir):
        y = getattr(self, dir)
        while y != self:
            yield y
            y = getattr(y, dir)

    def insert_left(self, p):
        self.left.right, p.right = p, self
        self.left, p.left = p, self.left

    def insert_up(self, p):
        self.up.down, p.down = p, self
        self.up, p.up = p, self.up

IterLeft, IterRight, IterUp, IterDown = 'left', 'right', 'up', 'down'

class Node(Unit):
    def __init__(self, colHeader, grid):
        super().__init__()
        self.header = colHeader
        self.grid = grid

class Header(Unit):
    def __init__(self):
        super().__init__()
        self.size = 0

    def cover(self):
        self.remove_h()
        for r in self.iter(IterDown):
            for x in r.iter(IterRight):
                x.remove_v()
                x.header.size -= 1

    def uncover(self):
        for r in self.iter(IterUp):
            for x in r.iter(IterLeft):
                x.header.size += 1
                x.undo_v()
        self.undo_h()

def build(mat):
    root = Header()
    if not mat: return root
    n, m = len(mat), len(mat[0])
    for j in range(m):
        p = Header()
        root.insert_left(p)
    for i, row in enumerate(mat):
        p0 = None # the first node of the row
        for j, header in enumerate(root.iter(IterRight)):
            if row[j] == 0: continue
            p = Node(header, (i, j))
            header.insert_up(p)
            header.size += 1
            if p0: p0.insert_left(p)
            else: p0 = p
    return root

def build_rows(rows, numCols):
    root = Header()
    headers = []
    for j in range(numCols):
        p = Header()
        root.insert_left(p)
        headers.append(p)
    for i, row in enumerate(rows):
        p0 = None
        for j in sorted(row):
            p = Node(headers[j], (i, j))
            headers[j].insert_up(p)
            headers[j].size += 1
            if p0: p0.insert_left(p)
            else: p0 = p
    return root

def broke(root):
    "Break reference cycle"
    for header in root.iter(IterRight):
        for x in header.iter(IterDown):
            x.left = x.right = x.header = None
        header.up = header.down = None
    root.left = root.right = None

def print_lmat(root):
    rows = set()
    numCols = 0
    for header in root.iter(IterRight):
        numCols += 1
        for x in header.iter(IterDown):
            rows.add(x.grid[0])
    pos = {}
    for i, r in enumerate(sorted(rows)):
        pos[r] = i
    mat = [[0] * numCols for x in rows]
    for j, header in enumerate(root.iter(IterRight)):
        for x in header.iter(IterDown):
            mat[pos[x.grid[0]]][j] = 1
    print('\n'.join(' '.join(map(str, row)) for row in mat))

# stt = [0] * 10000
# curLevel = [0]
def search(root, level=0):
    if root.right == root:
        yield []
        return
    # curLevel[0] = level
    # choose a column with minimum size to cover
    c = root.right
    # if level < 100:
    if 1:
        for c1 in root.iter(IterRight):
            if c1.size < c.size:
                c = c1
            if c.size <= 1: break
        # c = min(root.iter(IterRight), key=lambda c:c.size)
    # the the column and related row out of the list matrix
    c.cover()
    # choose a row to cover the column
    for r in c.iter(IterDown):
        for x in r.iter(IterRight):
            x.header.cover()
        for solution in search(root, level+1):
            solution.append(r.grid[0])
            yield solution
        for x in r.iter(IterLeft):
            x.header.uncover()
    c.uncover()

def dump_stt(outfile):
    total = 0
    for i in range(len(stt)):
        if stt[i] == 0: break
        print('level {0:5d}:{1:10d}'.format(i, stt[i]), file=outfile)
        total += stt[i]
    print('total:', total)

def test():
    mat = [
        [0, 1, 0],
        [1, 0, 0],
        [0, 0, 1],
        [1, 0, 1],
        ]
    root = build(mat)
    print_lmat(root)
    for sol in search(root):
        print('solution:', sol)

    rows = [[1], [0], [2], [0, 2]]
    numCols = 3
    root = build_rows(rows, numCols)
    print_lmat(root)
    for sol in search(root):
        print('solution:', sol)
