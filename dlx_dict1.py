def build_rows(rows, numCols):
    X = {j:set() for j in range(numCols)}
    Y = {}
    for i, row in enumerate(rows):
        Y[i] = list(row)
        for j in row:
            X[j].add(i)
    return X, Y

def print_lmat(root):
    X, Y = root
    numCols = len(X)
    mat = []
    for i, row in Y.items():
        r = [0] * numCols
        for j in row:
            r[j] = 1
        mat.append(r)
    print('\n'.join(' '.join(map(str, row)) for row in mat))

def search(root):
    cols, rows = root
    if cols:
        c, rs = min(cols.items(), key=lambda c_rs: len(c_rs[1]))
        cover(cols, rows, c)
        for r in list(rs):
            coveredCols = [(j, cover(cols, rows, j)) for j in rows[r] if j != c]
            for sol in search(root):
                yield sol + [r]
            for (j, col) in reversed(coveredCols):
                uncover(cols, rows, j, col)
        uncover(cols, rows, c, rs)
    else:
        yield []

def cover(cols, rows, j):
    for r in cols[j]:
        for c in rows[r]:
            if c != j:
                cols[c].remove(r)
    return cols.pop(j)

def uncover(cols, rows, j, col):
    cols[j] = col
    for r in col:
        for c in rows[r]:
            cols[c].add(r)

def test():
    mat = [
        [0, 1, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [0, 1, 0, 1, 1],
        [1, 0, 1, 0, 0],
        ]
    rows = [[j for j, x in enumerate(row) if x] for row in mat]
    numCols = len(mat[0])
    root = build_rows(rows, numCols)
    print_lmat(root)
    for sol in search(root):
        print('solution:', sol)

if __name__ == '__main__':
    test()
