# Serial PSU API
import serial

from StringIO import StringIO

class FakePSU(object):
    """
    Fake PSU serial object for testing
    """
    def __init__(self, port, baud):
        self.port = port
        self.baud = baud
        self.serbuf = StringIO()
        self.outbuf = StringIO()
        self.in_waiting = 0
        self.cmd_lookup = {
            1: self.setTE,
            2: self.setOEP,
            3: self.setOEN,
            4: self.setVP,
            5: self.setAP,
            6: self.setVN,
            7: self.setAN,
            8: self.getSettings,
            9: self.setACH,
            10: self.setACL
        }

        self.vals = [0] * 11

    def setTE(self, val):
        self.vals[4] = val
        self.writeOut('ACK\n')

    def setOEP(self, val):
        self.vals[5] = val
        self.writeOut('ACK\n')

    def setOEN(self, val):
        self.vals[6] = val
        self.writeOut('ACK\n')

    def setVP(self, val):
        self.vals[0] = val
        self.writeOut('ACK\n')

    def setVN(self, val):
        self.vals[1] = val
        self.writeOut('ACK\n')

    def setAP(self, val):
        self.vals[2] = val
        self.writeOut('ACK\n')

    def setAN(self, val):
        self.vals[3] = val
        self.writeOut('ACK\n')

    def setACH(self, chan):
        self.vals[6+chan] = 1
        self.writeOut('ACK\n')

    def setACL(self, chan):
        self.vals[6+chan] = 0
        self.writeOut('ACK\n')

    def getSettings(self, val):
        self.writeOut("V:%s,%s A:%s,%s S:%s,%s,%s,%s,%s,%s,%s\n" % tuple(self.vals))

    def runCmd(self, cmd):
        if ',' in cmd:
            c, p = cmd.split(',', 1)
            c, p = int(c), int(p)
            self.cmd_lookup[c](p)

    def write(self, string):
        self.serbuf.write(string)
        if '\n' in string:
            # Execute a command
            b = self.serbuf.getvalue().split('\n', 1)
            q = b[0]
            self.serbuf = StringIO(b[-1])
            self.serbuf.seek(self.serbuf.len)
            self.runCmd(q)

    def writeOut(self, string):
        cur = self.outbuf.tell()
        self.outbuf.seek(self.outbuf.len)
        self.outbuf.write(string)
        self.outbuf.seek(cur)

        self.in_waiting = self.outbuf.len - cur

    def readline(self):
        bread = self.outbuf.readline()
        self.in_waiting -= len(bread)
        return bread

    def read(self, n=-1):
        bread = self.outbuf.read(n=n)
        self.in_waiting -= len(bread)
        return bread

class PSU(object):
    def __init__(self, s):
        self.s = s
        self.serialBuffer = ""
        
        # Set all the internal attributes 
        (self.voltageP, self.voltageN, self.currentP, self.currentN,
         self.transformer, self.outputP, self.outputN, self.ac1, self.ac2,
         self.ac3, self.ac4) = [0] * 11

    def outputEnable(self, chan):
        self.s.write('%s,1\n' % (chan+1))

    def updateState(self):
        self.s.write('8,1\n')

    def lineReceived(self, line):
        if line.startswith('V:'):
            vals = []
            blocks = line.split()
            for block in blocks:
                vals.extend([int(i) for i in block.split(':')[-1].split(',')])

            (self.voltageP, self.voltageN, self.currentP, self.currentN,
             self.transformer, self.outputP, self.outputN, self.ac1, self.ac2,
             self.ac3, self.ac4) = vals

        print "lR: ", line

    def tick(self):
        # Hook into event loop here
        if self.s.in_waiting:
            bs = self.s.read()
            self.serialBuffer += bs
            if '\n' in bs:
                bl = self.serialBuffer.split('\n')

                self.lineReceived(bl.pop(0))

                if len(bl) > 1:
                    for shard in bl[:-1]:
                        self.lineReceived(shard)

                self.serialBuffer = bl[-1]
