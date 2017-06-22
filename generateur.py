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
    for c in composition(n, arity, size):
        for k in product(*[generator(arity, l) for l in c]):
            yield [i for j in k for i in j]


def add_composition(arity, size):
    for t in range(1, size - 1):
        for a in range(size - t - 1, size):
            for g in generator(a, t):
                for e in add_compound(a, arity, size - t - 1):
                    yield [Composition] + g + e


def add_left_right(arity, size):
    for f in generator(arity - 1, size - 1):
        yield [Left] + f
        yield [Right] + f


def add_recursion(arity, size):
    for i in range(1, size - 1):
        for p in generator(arity - 1, i):
            for g in generator(arity + 1, size - i - 1):
                yield [Recursion] + p + g


def generator(arity, size):
    if (arity, size) in atom:
        for i in atom[(arity, size)]:
            yield i
    elif arity == 0:
        for i in add_composition(arity, size):
            yield i
    else:
        for i in add_composition(arity, size):
            yield i
        for i in add_left_right(arity, size):
            yield i
        for i in add_recursion(arity, size):
            yield i


def main():
    n = 12
    for i in generator(1, n):
        print(display_tree(Tree(iter(i))))
        if len(i) != n:
            exit(1)


if __name__ == '__main__':
    main()
