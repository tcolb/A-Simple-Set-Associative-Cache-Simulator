from copy import deepcopy
import math


class Block:

    def __init__(self, size : int, startAddress : int):
        self._size = size
        self._data = [0] * size
        self.startAddress = startAddress
        self.valid = True
        self.dirty = False

    def __getitem__(self, key : int):
        if key < self._size and key >= 0:
            return self._data[key]
        else:
            raise IndexError

    def __setitem__(self, key : int, value : int):
        if key < self._size and key >= 0:
            self._data[key] = value
        else:
            raise IndexError

    def __eq__(self, other):
        return (self.startAddress == other.startAddress)

    def replaceWith(self, other):
        self.startAddress = deepcopy(other.startAddress)
        self._data = deepcopy(other._data)

    def containsAddr(self, addr : int):
        return (addr >= self.startAddress) and (addr < (self.startAddress + self._size))
    

class HashMemory:
    def __init__(self, blockSize : int):
        self._blockSize = blockSize
        self._data = dict()
        self._newValue = 0

    def blockIndexFromAddr(self, addr : int):
        return math.floor(addr / self._blockSize)

    def readBlock(self, addr : int):
        blockAddr = self.blockIndexFromAddr(addr)

        if blockAddr in self._data:
            return self._data[blockAddr]
        
        # create newBlock and populate with nonsense data
        newBlock = Block(self._blockSize, blockAddr * self._blockSize)
        newBlock._data = [ i + self._newValue for i in range(self._blockSize)]
        self._newValue += self._blockSize

        self._data[blockAddr] = newBlock

        return self._data[blockAddr]

    def writeBlock(self, addr : int, block : Block):
        localBlock = self.readBlock(addr)
        localBlock.replaceWith(block)