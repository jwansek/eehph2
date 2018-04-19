import os

location = input("Please copy in the path of the installation directory: ")
appdata = os.path.join(os.environ['ALLUSERSPROFILE'], "EEHPH2")

try:
    if not os.path.exists(appdata):
        os.mkdir(appdata)

    file = open(os.path.join(appdata, "location.txt"), "w")
    file.write(location)
    file.close()

    print("location saved to %s. You can change it by running this program again." % location)
    
except PermissionError as e:
    print("Failed because of insufficeint permissions. Try running as admin. Error:[%s]" % e)

input("Press any key to close...")