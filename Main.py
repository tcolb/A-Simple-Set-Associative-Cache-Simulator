import TraceParser
import Cache
import Drivers

p2 = Drivers.Problem2_Driver()
"""
p2.initializeCaches(16)
p2.initializeParser("./traces/cc.trace")
p2.simulate()
"""
p2.run("./traces/cc.trace")

p2.run("./traces/spice.trace")

p2.run("./traces/tex.trace")

p2.done()