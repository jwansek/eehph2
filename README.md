# eehph2
EEHPH Photo Viewer v2

A lite photo viewer optimised for Windows 10

Several .dlls are required for this program to work. Therefore I set the cwd to the one in which the
file is located. However the program doesn't know where the install location is. Therefore there is
on_install_setup.exe to put the install location in APPDATA/LOCAL/EEHPH2/location.txt. This is a simple
python script compiled using Pyinstaller. Then when the program is run, another script (TODO) is run
which changes the cwd to the one in location.txt and runs the main program as a module. After the user closes
it it switches back to the original cwd.
