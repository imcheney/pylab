# coding: utf-8


def mylog(func):
    def wrapper(*args, **kwargs):
        print 'before func'
        func(*args, **kwargs)
        print 'after func'
    return wrapper


@mylog
def my_func(aname):
    print '{} hello world!'.format(aname)


def deco_maker(mode):
    def real_deco(func):
        def wrapper(*args, **kwargs):
            print '{} - extra1 '.format(mode)
            print '{} - extra2 '.format(mode)
            return func(*args, **kwargs)  # 此处根据情况, 一般可以返回真正函数的执行结果
        return wrapper  # 此处只返回函数
    return real_deco  # 此处也只返回的是函数


@deco_maker('debug')
def my_func1(aname):
    return '{} hello world!'.format(aname)


if __name__ == '__main__':
    print my_func1('Liu')