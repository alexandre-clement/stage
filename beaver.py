from generator import Main


def beaver(values, value_range, max_step):
    for value in values:
        print(value, end=': ')
        score = -1
        champions = []
        overflow = []
        counter = 0
        total = 3.2 ** (value - 5)
        mod = total // 100 or 1
        for program in Main(1, value):
            counter += 1
            if not counter % mod:
                print('|', end='', flush=True)
            for param in range(value_range):
                step, result = program.execute(param, step=max_step, bin_output=True)
                if step == max_step:
                    overflow.append(program)
                    break
                if result:
                    if param > score:
                        score = param
                        champions = [program]
                    elif param == score:
                        champions.append(program)
                    break
        print()
        print('score: ', score, champions)
        print(overflow)


def main():
    beaver(range(20), 20, 10000)


if __name__ == '__main__':
    main()
