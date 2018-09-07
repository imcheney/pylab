import datetime
import time


class World():
    serial_num = 0

    def __init__(self):
        World.serial_num += 1

        self.id = World.serial_num
        self.count = 0

    def tick(self):
        self.count += 1
        print '{} -- tick {} is done {} - time:{}'.format(self.id, self.count, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                        time.time())

    from coroutines.co_queue import loop_task
    @loop_task
    def run_world(self):
        self.tick()
        from coroutines.co_queue import Task
        return Task(work_func=self.run_world, delay=4.0)
