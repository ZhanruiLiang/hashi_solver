import dlx
# import dlx_dict1 as dlx

# marker generators
def marker(p1, p2):
    i1, j1 = p1
    i2, j2 = p2
    j = p1[1]
    def marker_(a, adja):
        if j1 == j2:
            j = j1
            for i in range(min(i1, i2)+1, max(i1, i2)):
                a[i][j] = '|║'[a[i][j]=='|']
        else:
            i = i1
            for j in range(min(j1, j2)+1, max(j1, j2)):
                a[i][j] = '-='[a[i][j]=='-']
        adja[p1].append(p2)
        adja[p2].append(p1)
    return marker_
marker_none = lambda *xs:None

def is_connected(islands, adja):
    """
    islands: set of positions
    adja: adjacency list, like {p1:[p2, p4], p2:[p1, p4], ...}
    """
    p = next(iter(islands))
    stk = [p]
    vis = {p}
    while stk:
        p = stk.pop()
        for p1 in adja[p]:
            if p1 not in vis:
                vis.add(p1)
                stk.append(p1)
    return len(vis) == len(islands)

def hashi_solve(data):
    import itertools
    EmptyLand = ' '
    a = data.split('\n')[:-1]
    n, m = len(a), len(a[0])

    # important sets: 
    #   eslots
    #   islands
    #   edges
    #   crosses
    #   actions
    positions = list(itertools.product(range(n), range(m)))
    eslots = {p:[] for p in positions}
    islands = set(p for p in positions if a[p[0]][p[1]]!=EmptyLand)
    counts = {p:int(a[p[0]][p[1]]) for p in islands}
    edges = []
    # this loop to build edges and eslots
    for p1 in islands:
        i1, j1 = p1
        for di, dj in ((0, 1), (1, 0)):
            i2, j2 = i1 + di, j1 + dj
            path = [p1]
            while (i2, j2) in positions:
                path.append((i2, j2))
                if (i2, j2) in islands:
                    e = (p1, (i2, j2))
                    edges.append(e)
                    for p in path:
                        eslots[p].append(e)
                    break
                i2, j2 = i2 + di, j2 + dj
    # build crosses
    crosses = []
    for p, es in eslots.items():
        if len(es) > 1 and p not in islands:
            crosses.append(es)
    # build matrix and actions
    rows = []
    actions = []
    numCols = len(islands) + 4 * len(edges) + len(crosses)
    # order the islands
    leftCol = {}
    nextLeftCol = 0
    for p in sorted(islands):
        leftCol[p] = nextLeftCol
        nextLeftCol += len(eslots[p]) * 2 + 1
    # consider edges first
    for e in edges:
        p1, p2 = e
        c1 = leftCol[p1] + eslots[p1].index(e)*2
        c2 = leftCol[p2] + eslots[p2].index(e)*2
        # crosses
        crs = [(numCols - len(crosses) + j) for j, es in enumerate(crosses) if e in es]
        rows.append([c1, c2] + crs)
        rows.append([c1 + 1, c2 + 1])
        actions.append(marker(p1, p2))
        actions.append(marker(p1, p2))
    # consider paddings
    for p in sorted(islands):
        c0 = leftCol[p]
        for t in itertools.product(*((0,1,2) for i in eslots[p])):
            if sum(t) == counts[p]:
                row = []
                for i, c in enumerate(t):
                    row += ([c0+i*2, c0+i*2+1], [c0+i*2+1], [])[c]
                row.append(c0 + len(eslots[p])*2)
                rows.append(row)
                actions.append(marker_none)
    # pad crosses, since not every cross column will be filled by edge rows
    for j in range(len(crosses)):
        rows.append([numCols - len(crosses) + j])
        actions.append(marker_none)

    # conv = lambda x:x
    conv = len
    print('islands:', conv(list(sorted(islands))))
    print('edges:', conv(edges))
    print('cross count:', len(crosses))
    print('mat size:{}x{}'.format(len(rows), numCols))
    root = dlx.build_rows(rows, numCols)
    # header = [' ']*numCols
    # for p in islands:
    #     header[leftCol[p]] = '['
    # print(' '.join(header))
    # dlx.print_lmat(root)
    for sol in dlx.search(root):
        b = list(map(list, a))
        adja = {p:[] for p in islands}
        for r in sol:
            actions[r](b, adja)
        print('-' * 80)
        if is_connected(islands, adja):
            print('\n'.join(' '.join(row) for row in b))
            # break
        else:
            print('invalid solution, not connected')

    # dlx.dump_stt(sys.stdout)

    # dlx.broke(root)

# test()
import sys
hashi_solve(open(sys.argv[1]).read())
