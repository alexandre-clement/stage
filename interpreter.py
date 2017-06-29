class Expression:
    def __init__(self, what):
        self.what = what

    def __call__(self):
        return self.what

    def __repr__(self):
        return str(self.what)


class Zero:
    def __call__(self, step=0):
        return 0, step + 1


class Identity:
    def __call__(self, expression, step=0):
        return expression(), step + 1


class Successor:
    def __call__(self, expression, step=0):
        return expression() + 1, step + 1


class Left:
    def __init__(self, f):
        self.f = f

    def __call__(self, *expression, step=0):
        return self.f(*expression[1:], step=step + 1)


class Right:
    def __init__(self, f):
        self.f = f

    def __call__(self, *expression, step=0):
        return self.f(*expression[:-1], step=step + 1)


class Recursion:
    def __init__(self, f, g):
        self.g = g
        self.f = f
        self.n = -1
        self.result = -1
        self.step = 0

    def __call__(self, n, *x, step=0):
        self.n = n()
        self.args = x
        self.step = step
        if self.n == 0:
            self.result, step = self.f(*x, step=step + 1)
        else:
            self.n -= 1
            self.result, step = self.g(Expression(self.n), self.recursive_call, *x, step=step + 1)
        return self.result, step

    def recursive_call(self):
        self.result, self.step = self(Expression(self.n), *self.args, step=self.step+1)
        return self.result


def main():
    print(Recursion(Identity(), Right(Left(Successor())))(Expression(8), Expression(10)))


if __name__ == '__main__':
    main()
