from threading import Thread


class ThreadRet(Thread):
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


def sum_fun(arr, start, end):
    summ = 0
    for i in arr[start:end]:
        summ += i

    return summ


plate = [x for x in range(2**21)]


num_threads = int(input("Enter threads num: "))

block_size = len(plate) // num_threads

threads = []

for i in range(num_threads):
    threads.append(ThreadRet(target=sum_fun, args=(plate, i * block_size, (i + 1) * block_size)))
    threads[-1].start()

summ = 0
for a in threads:
    summ += a.join()

print(summ)
