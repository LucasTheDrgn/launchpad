import json

root = int(input("Root note (MIDI) >> "))
rightint = int(input("Rightward interval >> "))
downint = int(input("Downward interval >> "))

keygroups = int(input("Number of key color groups >> "))

keys = []
colors = []

for i in range(keygroups):
    notes = []
    while True:
        try:
            n = int(input("".join(["Note offset ",str(len(notes)+1)," for group ",str(i)," >> "])))
        except ValueError:
            break
        notes.append(n)
    if len(notes)>0:
        colors.append(tuple(map(int,input("".join(["R,G,B for group ",str(i)," >> "])).split(","))))
        keys.append(notes)
colors.append(tuple(map(int,input("R,G,B for default >> ").split(","))))

output = dict()

output["notes"] = list()
output["colors"] = list()

for y in range(8):
    output["notes"].append(list())
    output["colors"].append(list())
    for x in range(8):
        offset = y*downint+x*rightint
        output["notes"][-1].append(root+offset)
        for i in range(len(keys)):
            if offset%12 in keys[i]:
                output["colors"][-1].append(colors[i])
                break
        while len(output["colors"][-1])<len(output["notes"][-1]):
            output["colors"][-1].append(colors[-1])

with open(input("Output filename >> "),"w") as f:
    json.dump(output,f,indent=4)