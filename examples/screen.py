import launchpad
from itertools import product
import asyncio
from mss.windows import MSS as mss
import pyautogui

lp = launchpad.Launchpad()
sct = mss()

def mouseregion():
    r = dict()
    pos = pyautogui.position()
    r["mon"] = -1
    r["top"] = pos[1]-3
    r["left"] = pos[0]-3
    r["width"] = 8
    r["height"] = 8
    return r

cont = True

async def picture():
    while cont:
        scr = sct.grab(mouseregion())
        for xy in product(range(8),repeat=2):
            pix = scr.pixel(*xy)
            lp.display[xy] = (pix[0]//4,pix[1]//4,pix[2]//4)

        lp.display.resolve()
        await asyncio.sleep(1/60)

def exit(*args):
    global cont
    cont = False

lp.set_callback("controlpress",exit)

try:
    asyncio.run(picture())
finally:
    lp.close()