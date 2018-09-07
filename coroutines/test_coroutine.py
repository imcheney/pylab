# coding: utf-8

import time


def consumer():
    r = ''
    while True:
        n = yield r  # 最重要的一行代码, 出去和回来都最在这里
        if not n:
            return
        print('[CONSUMER] Consuming %s...' % n)
        time.sleep(1)
        r = '200 OK'


def produce(c):
    c.next()  # 一开始通过调用iterator的next方法来开始一个cycle. 注意这里第一个从consumer yield返回的r是被扔掉的.
    n = 0
    while n < 5:  # Note: 协程最重要的特点, 与普通return函数调用的区别是, 它保存了函数内的临时变量的值, 也就是一个执行的进度, 而不是每次再进入该函数都重新创建!!!
        n = n + 1
        print('[PRODUCER] Producing %s...' % n)
        r = c.send(n)
        print('[PRODUCER] Consumer return: %s' % r)
    c.close()


if __name__=='__main__':
    c = consumer()
    produce(c)