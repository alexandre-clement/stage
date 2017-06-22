from itertools import product

from abstract_syntax_tree import Zero, Identity, Successor, Left, Right, Composition, Recursion, Tree, display_tree

atom = {(0, 1): [[Zero]], (1, 1): [[Identity], [Successor]]}


def composition(n, arity, size):
    t = max(1, arity)
    if n == 1:
        yield [size]
    else:
        for i in range(t, size - (n - 1) * t + 1):
            for j in composition(n - 1, arity, size - i):
                yield [i] + j


def add_compound(n, arity, size):
    return [product(*[generator(arity, l) for l in c]) for c in composition(n, arity, size)]


def add_composition(arity, size):
    result = []
    for t in range(1, size - 1):
        for a in range(size - t - 1, size):
            for g in generator(a, t):
                for e in add_compound(a, arity, size - t - 1):
                    for f in e:
                        result.append([Composition] + g + [w for j in f for w in j])
    return result


def add_left_right(arity, size):
    result = []
    for f in generator(arity - 1, size - 1):
        result.append([Left] + f)
        result.append([Right] + f)
    return result


def add_recursion(arity, size):
    result = []
    for i in range(1, size - 1):
        for p in generator(arity - 1, i):
            for g in generator(arity + 1, size - i - 1):
                result.append([Recursion] + p + g)
    return result


def generator(arity, size):
    if (arity, size) in atom:
        return atom[(arity, size)]
    if arity == 0:
        return add_composition(arity, size)
    return add_composition(arity, size) + add_left_right(arity, size) + add_recursion(arity, size)


def main():
    n = 20
    for i in generator(0, n):
        if n != len(i):
            print(display_tree(Tree(iter(i))))
        display_tree(Tree(iter(i)))


if __name__ == '__main__':
    main()
