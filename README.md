# eehph2
EEHPH Photo Viewer v2

A light photo viewer designed for Windows 10.

The program can be run anywhere by right clicking and opening with this
file. This is a problem because with program requires several .ddls to work.
The solution is to set the program to a run a small script which changes the
cwd to the one in which the app is located (EEHPH2.py) and then run the main 
app (EEHPH2_app.py) as a module. However the program doens't know where the
installation directory is. The solution is to use a script (on_install_setup.exe) 
which sets the location of the installation directory in 
%ALLUSERSPROFILE%/EEHPH2/location.txt. This script was compiled using pyinstaller
and it's source is on_install_setup/on_install_setup.py. There is a another script,
cleanup.exe, which was made in a similar way which deletes this file on uninstall.

This program in written in Python3, compiled using cx_Freeze, and packaged using
inno. The inno script is at setup.iss. The setup for the cx_Freeze is setup.py.
This was done for the functionality of intallation and uninstallation scripts.