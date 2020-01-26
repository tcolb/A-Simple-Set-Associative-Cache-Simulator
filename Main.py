import TraceParser
import Cache
import Drivers

prob = Drivers.Driver()

prob.runWT("./traces/cc.trace")
prob.runWT("./traces/spice.trace")
prob.runWT("./traces/tex.trace")

prob.runWB("./traces/cc.trace")
prob.runWB("./traces/spice.trace")
prob.runWB("./traces/tex.trace")

prob.done()
"""