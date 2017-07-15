
from threading import Thread, Event
from generator import *


def test(program, length, result, stop_it, to_delete):
    for j in range(length):
        if stop_it.is_set():
            to_delete.append(program)
            return
        try:
            if program.execute(j, bin_output=True)[1]:
                if j > result[0]:
                    result.clear()
                    result.append(j)
                    result.append(program)
                elif j == result[0]:
                    result.append(program)
                return
        except Exception as e:
            print(program)
            print(e)


def castor(cls, length):
    for i in cls:
        print(i, end=' : ')
        result = [-1]
        to_delete = []
        step = 0
        total = (4**(i-5)) // 100
        if total < 1:
            total = 1
        for program in Main(1, i):
            step += 1
            if not step % total:
                print('|', end='', flush=True)
            stop_it = Event()
            stuff_doing_thread = Thread(target=test, args=(program, length, result, stop_it, to_delete))
            stuff_doing_thread.start()
            stuff_doing_thread.join(timeout=1)
            stop_it.set()
        print()
        print(result)
        print(to_delete)
        print()



def main():
    castor(range(20), 20)


if __name__ == '__main__':
    main()
