import launchpad
import rtmidi
import asyncio
from itertools import product
from random import randrange
import argparse
import json

parser = argparse.ArgumentParser(description="Forward the Launchpad's input to a midi out, transforming it in the process")
parser.add_argument("definition")
parser.add_argument("--fps","-f",type=float,default=60)
parser.add_argument("--out","-o",default="Python2Synth")

args = parser.parse_args()

with open(args.definition) as f:
    definition = json.load(f)
fps = args.fps
outname = args.out

lp = launchpad.Launchpad()
md = rtmidi.MidiOut()

for i in range(md.get_port_count()):
    if md.get_port_name(i).find(outname) is not -1:
        md.open_port(i)
        break

def exit(x,y):
    global cont
    if x == 4 and y == 0:
        cont = False

notes = dict()
colors = dict()

for xy in product(range(8),repeat=2):
    notes[xy] = definition["notes"][xy[1]][xy[0]]
    lp.display[xy] = tuple(definition["colors"][xy[1]][xy[0]])

cont = True
line = "-"*33
names = ["C ","C#","D ","D#","E ","F ","F#","G ","G#","A ","A#","B "]  

def midi_to_name(note):
    octave = note//12-1
    return names[note%12]+str(octave)

def print_mapping(notes):
    print(line)
    for y in range(8):
        print("|",end="")
        print("|".join(map(midi_to_name,[notes[x,y] for x in range(8)])),end="|\n")
        print(line)



def playnote(x,y):
    md.send_message([144,notes[x,y],127])

def releasenote(x,y):
    md.send_message([144,notes[x,y],0])

lp.set_callback("controlpress",exit)
lp.set_callback("notepress",playnote)
lp.set_callback("noterelease",releasenote)

lp.display[4,-1] = (63,0,0)
lp.display.resolve()

print_mapping(notes)

async def loop():
    while cont:
        await asyncio.sleep(1/fps)

try:
    asyncio.run(loop())
finally:
    lp.close()
    md.close_port()