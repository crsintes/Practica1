from multiprocessing import Process
from multiprocessing import Condition, Lock, BoundedSemaphore, Value
from multiprocessing import Array, Manager
import time
import random


class Table():
    def __init__(self, nphil, manager):
        self.nphil = nphil
        self.phil = None
        self.mutex = Lock()
        self.fork = Array('i',[-1 for _ in range(nphil)])
        self.fork_free = Condition(self.mutex)

    def can_eat(self):
        return self.fork[self.phil] == -1 and self.fork[(self.phil-1)%self.nphil] == -1

    def wants_eat(self, num):
        self.mutex.acquire()
        self.fork_free.wait_for(lambda: self.can_eat())
        self.fork[self.phil] = self.phil
        self.fork[(self.phil-1)%self.nphil] = self.phil
        self.mutex.release()

    def wants_think(self, num):
        self.mutex.acquire()
        self.fork[self.phil] = -1
        self.fork[(self.phil-1)%self.nphil] = -1
        self.fork_free.notify()
        self.mutex.release()

    def set_current_phil(self, num):
        self.phil = num

    def get_current_phil(self):
        return self.phil


class CheatMonitor():
    def __init__(self):
        self.eating = Value('i', 0)
        self.mutex = Lock()
        self.think_free = Condition(self.mutex)

    def can_think(self):
        return self.eating.value == 2

    def wants_think(self, nphil):
        self.mutex.acquire()
        self.think_free.wait_for(lambda: self.can_think())
        self.eating.value -= 1
        self.mutex.release()

    def is_eating(self, nphil):
        self.mutex.acquire()
        self.eating.value += 1
        self.think_free.notify()
        self.mutex.release()


class AnticheatTable():
    def __init__(self, nphil, manager):
        self.nphil = nphil
        self.phil = None
        self.mutex = Lock()
        self.fork = Array('i',[-1 for _ in range(nphil)])
        self.fork_free = Condition(self.mutex)

    def can_eat(self):
        return self.fork[self.phil] == -1 \
            and self.fork[(self.phil-1)%self.nphil] == -1 \
            and self.fork[(self.phil+1)%self.nphil] == -1

    def wants_eat(self, num):
        self.mutex.acquire()
        self.fork_free.wait_for(lambda: self.can_eat())
        self.fork[self.phil] = self.phil
        self.fork[(self.phil-1)%self.nphil] = self.phil
        self.mutex.release()

    def wants_think(self, num):
        self.mutex.acquire()
        self.fork[self.phil] = -1
        self.fork[(self.phil-1)%self.nphil] = -1
        self.fork_free.notify()
        self.mutex.release()

    def set_current_phil(self, num):
        self.phil = num

    def get_current_phil(self):
        return self.phil