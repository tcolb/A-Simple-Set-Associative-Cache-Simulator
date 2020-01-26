from Cache import WT_SACache, WB_SACache
from Memory import HashMemory
from TraceParser import TraceParser
from random import randint
from time import time

class Listener:

    def __init__(self):
        self.reset()

    def report(self, hit : bool):
        if hit:
            self.hits += 1
        else:
            self.misses += 1

    def reset(self):
        self.hits = 0
        self.misses = 0


class Driver:

    randomIntBound = 1000000

    def __init__(self):
        self.Memory = HashMemory(32)
        self.ICache = None
        self.DCache = None
        self.Parser = None
        self.listener = Listener()
        self.setAssoc = 0

    def initializeParser(self, path):
        if self.Parser is not None:
            self.Parser.close()
        self.Parser = TraceParser(path)

    def initializeWTCaches(self, setSize):
        self.setAssoc = setSize
        self.Memory = None
        self.ICache = None
        self.DCache = None
        self.Parser = None
        self.Memory = HashMemory(32)
        self.ICache = WT_SACache(1024, 32, setSize, self.Memory)
        self.DCache = WT_SACache(1024, 32, setSize, self.Memory)
        self.ICache.listener = self.listener
        self.DCache.listener = self.listener

    def initializeWBCaches(self, setSize):
        self.setAssoc = setSize
        self.Memory = None
        self.ICache = None
        self.DCache = None
        self.Parser = None
        self.Memory = HashMemory(32)
        self.ICache = WB_SACache(1024, 32, setSize, self.Memory)
        self.DCache = WB_SACache(1024, 32, setSize, self.Memory)
        self.ICache.listener = self.listener
        self.DCache.listener = self.listener

    def simulate(self):
        # H = hit time = typically 1
        # M = miss penalty = assume 100
        # AMAT = H + missrate * M
        print("Starting simulation with set assoc of %d..." % self.setAssoc)

        i = 0

        startTime = time()
        while True:
            op, addr = self.Parser.parseLine()
            if op == "" or addr == "":
                break

            if op == 0: # data read
                self.DCache.read(addr)
            elif op == 1: # data write
                self.DCache.write(addr, randint(0, Driver.randomIntBound))
            elif op == 2: # instruction read
                self.ICache.read(addr)
            
            i += 1
        endTime = time()

        missRate = self.listener.misses / (self.listener.misses + self.listener.hits)
        print("Traces simulated :", i)
        print("Time elapsed : %04s seconds" % (endTime - startTime))
        print("Misses :", self.listener.misses)
        print("Hits :", self.listener.hits)
        print("Miss rate :", missRate)
        print("AMAT :", 1 + missRate * 100)

        print("Simulation finished")

    def runWT(self, path):
        i = 1
        while i <= 32:
            self.initializeWTCaches(i)
            self.initializeParser(path)
            self.listener.reset()
            self.simulate()
            i *= 2

    def runWB(self, path):
        i = 1
        while i <= 32:
            self.initializeWBCaches(i)
            self.initializeParser(path)
            self.listener.reset()
            self.simulate()
            i *= 2

    def done(self):
        self.Parser.close()