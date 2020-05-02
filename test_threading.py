#! /usr/bin/python3

from threading import Thread
from multiprocessing import Process
from multiprocessing import Manager
import sys


class ThreadRet(Process):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            print("start thread:", self.name)
            self._return = self._target(*self._args,
                                        **self._kwargs)

    def join(self):
        Thread.join(self)
        print("end thread:", self.name)
        return self._return


def sum_fun(arr, start, end, return_dict):
    summ = 0
    for i in arr[start:end]:
        summ += i

    return_dict[start] = summ


if __name__ == "__main__":
    manager = Manager()
    return_dict = manager.dict()

    plate = [x for x in range(2**21)]

    num_threads = int(sys.argv[1])

    block_size = len(plate) // num_threads
    threads = []

    for i in range(num_threads):
        threads.append(Process(target=sum_fun, args=(plate, i * block_size, (i + 1) * block_size, return_dict)))
        threads[-1].start()

    for a in threads:
        a.join()

    print(sum(return_dict.values()))
