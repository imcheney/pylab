import time

from coroutines.co_queue import Executor
from coroutines.co_work import World

if __name__ == '__main__':
    # executor = Executor()
    world1 = World()
    world2 = World()
    next_task = world1.run_world()
    time.sleep(2.0)
    next_task1 = world2.run_world()
    Executor.get_instance().execute()
