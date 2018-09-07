# coding: utf-8

import Queue
import time
import functools


class Runner(object):
    tasks = Queue.Queue()

    @staticmethod
    def run():
        while True:
            task = Runner.tasks.get()
            task.run()


def coroutine(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        task = Task(func(*args, **kwargs))
        Runner.tasks.put(task)
        return task

    return wrapper


class Task(object):
    def __init__(self, gen=None):
        super(Task, self).__init__()
        self.gen = gen  # 输入是函数

    def run(self):
        if self._is_ready():
            try:
                task = next(self.gen)
                task.gen = self.gen
            except StopIteration:
                pass
            else:
                Runner.tasks.put(task)
        else:
            Runner.tasks.put(self)

    def _is_ready(self):
        return True


class Sleep(Task):
    def __init__(self, delay):
        super(Sleep, self).__init__()
        self._timeout = time.time() + delay

    def _is_ready(self):
        return time.time() >= self._timeout
