from math import sqrt, log

from abstract_syntax_tree import Zero, Identity, Successor, Left, Right, Composition, Recursion, Tree

import sys
sys.setrecursionlimit(10000)


def newton(n):
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


def cantor(value):
    n = newton(2 * value)
    if n * (n + 1) // 2 > value:
        n -= 1
    p = n * (n + 1) // 2
    x = value - p
    return x, n - x


def cantor_inverse(x, y):
    return ((x + y) * (x + y) + 3 * x + y) // 2


def cantor_n(value, n):
    if n == 1:
        return value,
    if n == 2:
        return cantor(value)
    mid = n // 2
    i, j = cantor(value)
    return cantor_n(i, mid) + cantor_n(j, n-mid)


def cantor_inverse_n(*args):
    n = len(args)
    if n == 1:
        return args[0]
    if n == 2:
        return cantor_inverse(*args)
    mid = n // 2
    return cantor_inverse(cantor_inverse_n(*args[:mid]), cantor_inverse_n(*args[mid:]))


def pairing_exp2(n):
    if not n:
        return 0, 0
    x = n
    while not x & 1:
        x = x // 2
    v = (x + 1) // 2
    y = n // x
    return int(log(y, 2)), v


def pairing_exp2_inverse(u, v):
    if not u and not v:
        return 0
    return 2 ** u * (2 * v - 1)


class Generator:
    atom = {(0, 0): Zero, (1, 0): Identity, (1, 1): Successor}

    def __init__(self):
        self.sub_function = [self._add_right, self._add_left, self._add_recursion, self._add_composition]

    def create_program(self, arity, fid):
        if (arity, fid) in self.atom:
            return [self.atom[(arity, fid)]]

        if arity == 0:
            return self._add_composition(arity, fid - 1)

        a, b = divmod(fid, 4)
        return self.sub_function[b](arity, a)

    def _add_left(self, arity, fid):
        return [Left] + self.create_program(arity - 1, fid)

    def _add_right(self, arity, fid):
        return [Right] + self.create_program(arity - 1, fid)

    def _add_recursion(self, arity, fid):
        i, j = cantor(fid)
        return [Recursion] + self.create_program(arity - 1, i) + self.create_program(arity + 1, j)

    def _add_composition(self, arity, fid):
        b, x = pairing_exp2(fid)
        b += 1
        i, *a = cantor_n(x, b+1)
        result = [Composition] + self.create_program(b, i)
        for i in range(b):
            result += self.create_program(arity, a[i])
        return result


class HashFunction:
    atom = {Zero: (0, 0), Identity: (1, 0), Successor: (1, 1)}

    def __init__(self):
        self.func = {Left: self._left_value, Right: self._right_value,
                     Recursion: self._recursion_value, Composition: self._composition_value}

    def value(self, program):
        f = next(program)
        if f in self.atom:
            return self.atom[f]
        return self.func[f](program)

    def _right_value(self, program):
        arity, fid = self.value(program)
        return arity + 1, fid * 4

    def _left_value(self, program):
        arity, fid = self.value(program)
        return arity + 1, fid * 4 + 1

    def _recursion_value(self, program):
        zero_arity, zero_fid = self.value(program)
        recursion_arity, recursion_fid = self.value(program)
        return zero_arity + 1, cantor_inverse(zero_fid, recursion_fid) * 4 + 2

    def _composition_value(self, program):
        b, i = self.value(program)
        a = []
        arity = 0
        fid = 0
        for j in range(b):
            arity, fid = self.value(program)
            a.append(fid)
        fid = cantor_inverse_n(i, *a)
        fid = pairing_exp2_inverse(b - 1, fid)
        if arity == 0:
            return arity, fid + 1
        return arity, fid * 4 + 3


def generate(func, iterable):
    def generation_range():
        k = 2
        while True:
            yield k
            k += 1
            yield k
            k += 3

    generator = Generator()
    target = tuple(func(j) for j in iterable)
    for i in generation_range():
        program = generator.create_program(1, i)
        tree = Tree(program)
        for j in iterable:
            if tree.node(j,)[0] != target[j]:
                break
        else:
            return program


def fibonacci(n):
    a = 0
    b = 1
    for i in range(n):
        b = a + b
        a = b - a
    return b


def main():
    from math import factorial
    result = [factorial(x) for x in range(10)]
    generator = Generator()
    hashfunction = HashFunction()
    for i in range(0, 100000000, 4):
        for j in range(0, 4):
            program = generator.create_program(1, i+j)
            if i+j != hashfunction.value(iter(program))[1]:
                print(i+j, hashfunction.value(iter(program)))
            tree = Tree(iter(program))
            for k in range(10):
                if tree.node(k,)[0] != result[k]:
                    if k > 4:
                        print(i+j, k)
                    break
            else:
                print(i+j)
                exit(0)


if __name__ == '__main__':
    main()
