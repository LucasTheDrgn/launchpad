import launchpad
from PIL import Image,ImageMath
from itertools import product
import argparse
import asyncio

parser = argparse.ArgumentParser(description="Display an image on the Launchpad's LEDs")
parser.add_argument("image",type=Image.open)
parser.add_argument("--loop","-l",action="store_true")
parser.add_argument("--fps","-f",type=float,default=5)
parser.add_argument("--pause","-p",type=float,default=1)

args = parser.parse_args()

img = args.image.convert("RGB")

if img.height == 8:
    horiz = True
elif img.width == 8:
    horiz = False
else:
    print("Wrong size: use a image with at least one dimension = 8")
    exit()

img = Image.eval(img,lambda x: x//4)

lp = launchpad.Launchpad()
data = list(img.getdata())

def find(x,y,img):
    return (x%img.width)+(y%img.height)*img.width

def disp(offx,offy):
    for xy in product(range(8),repeat=2):
        lp.display[xy] = data[find(xy[0]+offx,xy[1]+offy,img)]

    lp.display.resolve()

direction = 1
if not args.loop:
    if img.size == (8,8):
        direction = 0
x = 0
y = 0

cont = True

async def picture():
    global x
    global y
    global direction
    while cont:
        disp(x,y)
        await asyncio.sleep(1/args.fps)
        if args.loop:
            if horiz:
                x = (x+direction)%img.width
            else:
                y = (y+direction)%img.height
        else:
            if horiz:
                if x+direction >= (img.width-7) or x+direction < 0:
                    direction *= -1
                    await asyncio.sleep(args.pause-(1/args.fps))
                else:
                    x += direction
            else:
                if y+direction >= (img.height-7) or y+direction < 0:
                    direction *= -1
                    await asyncio.sleep(args.pause-(1/args.fps))
                else:
                    y += direction

def exit(*args):
    global cont
    cont = False

lp.set_callback("controlpress",exit)

try:
    asyncio.run(picture())
finally:
    lp.close()