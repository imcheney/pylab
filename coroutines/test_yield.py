# coding: utf-8


def create_generator():
    mylist = [10, 20, 30]
    for e in mylist:
        yield e*e


def main():
    g = create_generator()
    print g
    for val in g:
        print val


if __name__ == '__main__':
    main()