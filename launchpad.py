import rtmidi
from itertools import product

SYSEX_HEADER = [0xf0,0x00,0x20,0x29,0x02,0x18]
SYSEX_TERMINATOR = [0xf7]

def getkey(x,y):
    if y >= 0:
        return 10*(8-y)+x+1
    else:
        return 104+x

class Display:
    def __init__(self,launchpad=None):
        self.board = {x:(0,0,0) for x in product(range(9),range(-1,8))}
        del self.board[8,-1]
        self.buffer = dict()
        self.lp = launchpad

    def __getitem__(self, key):
        return self.buffer.get(key,self.board[key])

    def __setitem__(self, key, value):
        if self.board[key] != value:
            self.buffer[key] = value

    def resolve(self):
        cmds = []
        for key in self.buffer:
            cmds.append((0x0B,(getkey(*key),)+self.buffer[key]))
            self.board[key] = self.buffer[key]

        self.buffer.clear()

        if self.lp:
            self.lp.send_batch_cmd(cmds)
        else:
            return cmds

    def close(self):
        self.lp.send_cmd(0x0E,[0])

    def clear(self):
        self.board = {x:(0,0,0) for x in product(range(9),range(-1,8))}
        del self.board[8,-1]
        self.buffer = dict()
        self.lp.send_cmd(0x0E,[0])


class Launchpad:
    def __init__(self,inputname="Launchpad",outputname="Launchpad"):
        self.midiin = rtmidi.MidiIn()

        for i in range(self.midiin.get_port_count()):
            if self.midiin.get_port_name(i).find(inputname) is not -1:
                self.midiin.open_port(i)
                break

        if not self.midiin.is_port_open:
            raise RuntimeError('"'.join(["Midi input device with name ",inputname," not found."]))

        self.midiin.set_callback(self.__callback__)

        self.midiout = rtmidi.MidiOut()

        for i in range(self.midiout.get_port_count()):
            if self.midiout.get_port_name(i).find(outputname) is not -1:
                self.midiout.open_port(i)
                break

        if not self.midiout.is_port_open:
            raise RuntimeError('"'.join(["Midi output device with name ",outputname," not found."]))

        self.display = Display(self)
        self.callbacks = {
            "notepress":[],
            "noterelease":[],
            "controlpress":[],
            "controlrelease":[],
            "press":[],
            "release":[]
        }

    def send_cmd(self,cmdbyte,data):
        self.midiout.send_message(SYSEX_HEADER+[cmdbyte]+list(data)+SYSEX_TERMINATOR)

    def send_batch_cmd(self,commands):
        """Commands should be tuples of [cmdbyte,data]"""
        msg = []
        for command in commands:
            cmdbyte,data = command
            msg += SYSEX_HEADER+[cmdbyte]+list(data)+SYSEX_TERMINATOR
        if len(msg)>0:
            self.midiout.send_message(msg)

    def close(self):
        self.display.close()
        self.midiin.close_port()
        self.midiout.close_port()

    def __iter__(self):
        ms = []
        nm = self.midiin.get_message()
        while nm:
            ms.append(nm)
            nm = self.midiin.get_message()
        return ms.__iter__()

    def set_callback(self,event,callback):
        """Callback function will be called as such: callback(x, y)
        for control keys, x = 0 is the buttons along the top of the device, and x = 1 is the buttons along the right side of the device.
        for generic press and release, y = -1 is the top row of control keys, and x = 8 is the right side column of control keys."""
        self.callbacks[event].append(callback)

    def remove_callback(self,event,callback):
        self.callbacks[event].remove(callback)

    def __callback__(self,msg,data):
        ev = msg[0]
        press = ev[2] > 64
        if ev[0] == 176:
            y = 0
            x = ev[1]-104
            if press:
                cbl = self.callbacks["controlpress"]
            else:
                cbl = self.callbacks["controlrelease"]
        elif ev[1]%10 == 9:
            y = 1
            x = 8-(ev[1]//10)
            if press:
                cbl = self.callbacks["controlpress"]
            else:
                cbl = self.callbacks["controlrelease"]
        else:
            y = 8-(ev[1]//10)
            x = (ev[1]%10)-1
            if press:
                cbl = self.callbacks["notepress"]
            else:
                cbl = self.callbacks["noterelease"]

        for cb in cbl:
            cb(x,y)

        y = -1 if ev[0] == 176 else 8-(ev[1]//10)
        x = ev[1]-104 if ev[0] == 176 else (ev[1]%10)-1
        if press:
            cbl = self.callbacks["press"]
        else:
            cbl = self.callbacks["release"]

        for cb in cbl:
            cb(x,y)

        

