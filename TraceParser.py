class TraceParser:

    def __init__(self, path):
        self._path = path
        self._file = open(self._path)

    def _innerParse(self, datastr):
        if datastr == "":
            return "", ""
        data = datastr.split()
        return int(data[0], 16), int(data[1], 16)

    def parseLine(self):
        return self._innerParse(self._file.readline())

    def parseAll(self): # probably don't use this on the trace files
        trace_list = []

        for line in self._file:
            trace_list.append(self._innerParse(line))
        
        return trace_list
            
    def close(self):
        if self._file is not None:
            self._file.close()
            self._file = None