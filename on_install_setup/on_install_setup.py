import sys
import os

location = sys.argv[1]

appdata = os.path.join(os.getenv("LOCALAPPDATA"), "EEPHPH2")

if not os.path.exists(appdata):
    os.mkdir(appdata)

file = open(os.path.join(appdata, "location.txt"), "w")
file.write(location)
file.close()