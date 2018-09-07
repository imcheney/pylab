# coding=utf-8

import functools
import time
from collections import deque


class Executor(object):
    """
    单例模式的Executor执行者
    """
    instance = None

    def __init__(self):
        Executor.instance = self
        self.queue = deque()

    @staticmethod
    def get_instance():
        if Executor.instance is None:
            Executor.instance = Executor()
            return Executor.instance
        else:
            return Executor.instance

    def execute(self):
        while True:
            # print 'executing...{}'.format(len(self.queue))
            task = self.queue.popleft()
            task.run()


class Task(object):
    def __init__(self, work_func=None, delay=0.0, executor=None):
        super(Task, self).__init__()

        self.work_func = work_func
        self.delay = delay
        self.executor = executor
        if delay:
            self.do_time = time.time() + delay
            print 'self.do_time: ', self.do_time

    def run(self):
        if (not self.delay) or (self.do_time and self.do_time <= time.time()):
            next_task = self.work_func()  # Return the next item from the iterator.
            # next_task.executor = self.executor
            # self.executor.queue.append(next_task)
        else:
            self.executor.queue.appendleft(self)
            sleep_time = self.do_time - time.time()
            print 'sleep_time:', sleep_time
            time.sleep(sleep_time)


def loop_task(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        executor = Executor.get_instance()
        next_task = func(*args, **kwargs)
        next_task.executor = executor
        executor.queue.append(next_task)
        return next_task  # 记得要返回原先函数的结果
    return wrapper


if __name__ == '__main__':
    pass
