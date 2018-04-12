import sys
import os

def find_location():
    filelocation = os.path.join(os.environ['ALLUSERSPROFILE'], "EEHPH2", "location.txt")
    file = open(filelocation, "r")
    applocation = file.readline()
    file.close()

    return applocation

initcwd = os.getcwd()

try:
    start = sys.argv[1]
except:
    start = None

os.chdir(find_location())

import EEHPH2_app

root = EEHPH2_app.App(start)
root.mainloop()

os.chdir(initcwd)