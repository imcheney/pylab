# coding: utf-8

import time

def consumer():
    res = ''
    while True:
        n = yield res
        if not n:
            return
        print 'consumer got %d...' % n
        res = '200 ok'
        time.sleep(1.5)

def producer(c):
    c.next()
    for n in range(1, 6):
        res = c.send(n)
        print 'result: %s' % res

def main():
    c = consumer()
    producer(c)


if __name__ == '__main__':
	main()