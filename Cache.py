import math
from collections import deque
from Memory import HashMemory, Block
import gc


class SACache:

    def __init__(self, size : int, blockSize : int, setSize : int, master : HashMemory):

        if size % blockSize != 0:
            raise ValueError("Block size must be a multiple of the cache size")

        self._sizeInBytes = size
        self._blockSize = blockSize
        self._blocksPerSet = setSize
        self._numberOfBlocks = size // blockSize
        self._numberOfSets = (self._numberOfBlocks // setSize) if setSize != 0 else 1
        self._data = []
        for i in range(self._numberOfSets):
            self._data.append(deque( [None] * self._blocksPerSet ))
        self.master = master
        self.listener = None

    def __getitem__(self, key : int):
        if key < self._numberOfSets and key >= 0:
            return self._data[key]
        else:
            raise IndexError

    def __setitem__(self, key : int, value : int):
        if key < self._numberOfSets and key >= 0:
            self._data[key] = value
        else:
            raise IndexError

    def read(self, addr : int):
        raise NotImplementedError

    def write(self, addr : int, data : int):
        raise NotImplementedError

    def _loadBlockContainingAddr(self, addr : int):
        return NotImplementedError

    def _searchForBlockContainingAddr(self, addr : int):
        setIndex = self.master.blockIndexFromAddr(addr) % self._numberOfSets

        for block in self._data[setIndex]:
            if block is not None and block.containsAddr(addr):
                return True, block

        return False, None



class WT_SACache(SACache):

    def _loadBlockContainingAddr(self, addr : int):
        setIndex = self.master.blockIndexFromAddr(addr) % self._numberOfSets
        curSet = self[setIndex] # get which set to load into 

        blockLRU = curSet.popleft() # get the LRU block
        if blockLRU is None: # if not already loaded
            blockLRU = Block(self._blockSize, 0)

        blockLRU.replaceWith(self.master.readBlock(addr)) # set LRU block to mainmem data

        curSet.append(blockLRU) # append LRU to end of queue

        return blockLRU

    def read(self, addr):
        hit, block = self._searchForBlockContainingAddr(addr)

        if self.listener is not None:
            self.listener.report(hit)

        """
        kept this here incase the new implementation doesn't work!
        if hit:
            return block[addr - block.startAddress]
        else:
            loadedBlock = self._loadBlockContainingAddr(addr)
            return loadedBlock[addr - loadedBlock.startAddress]
        """

        if not hit:
            block = self._loadBlockContainingAddr(addr)

        return block[addr - block.startAddress]

    def write(self, addr, value):
        hit, block = self._searchForBlockContainingAddr(addr)

        if self.listener is not None:
            self.listener.report(False) # always a miss with a wt cache
            
        """
        kept this here incase the new implementation doesn't work!
        if hit:
            block[addr - block.startAddress] = value
        else:
            block = self._loadBlockContainingAddr(addr)
            block[addr - block.startAddress] = value
        """

        if not hit:
            block = self._loadBlockContainingAddr(addr)

        block[addr - block.startAddress] = value

        # write through
        self.master.writeBlock(addr, block)


class WB_SACache(SACache):

    def _loadBlockContainingAddr(self, addr : int):
        setIndex = self.master.blockIndexFromAddr(addr) % self._numberOfSets
        curSet = self[setIndex] # get which set to load into 

        blockLRU = curSet.popleft() # get the LRU block
        if blockLRU is None: # if not already loaded
            blockLRU = Block(self._blockSize, 0)

        # write back
        if blockLRU.dirty:
            self.master.writeBlock(addr, blockLRU)
            blockLRU.dirty = False

        blockLRU.replaceWith(self.master.readBlock(addr)) # set LRU block to mainmem data

        curSet.append(blockLRU) # append LRU to end of queue

        return blockLRU

    def read(self, addr):
        hit, block = self._searchForBlockContainingAddr(addr)

        if self.listener is not None:
            self.listener.report(hit)

        if not hit:
            block = self._loadBlockContainingAddr(addr)

        return block[addr - block.startAddress]

    def write(self, addr, value):
        hit, block = self._searchForBlockContainingAddr(addr)

        if self.listener is not None:
            self.listener.report(False) # always a miss with a wt cache

        if not hit:
            block = self._loadBlockContainingAddr(addr)
        
        block[addr - block.startAddress] = value
        block.dirty = True