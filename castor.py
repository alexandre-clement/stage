from time import time

from generator import *


def castor(cls, length):
    t0 = time()
    printer = Printer()

    for i in cls:
        maxi = -1
        to_prove = []
        result = []
        timing = []
        for program in Main(1, i):
            t1 = time()
            for j in range(length):
                try:
                    # print(printer.print(program))
                    if program.execute(j, bin_output=True)[1]:
                        if j > maxi:
                            maxi = j
                            result = [program]
                        elif j == maxi:
                            result.append(program)
                        break
                except Exception as e:
                    print(program)
                    print(e)
            else:
                to_prove.append(program)
            tf = time() - t1
            timing.append((tf, printer.print(program)))

        print("classe ", i, ":", maxi, [printer.print(p) for p in result])
        print(len(to_prove), [str(printer.print(p)) for p in to_prove])
        print(sorted(timing, key=lambda x: x[0], reverse=True))


def main():
    castor(range(20), 8)


if __name__ == '__main__':
    main()
