from cx_Freeze import setup, Executable
import os

os.environ["TCL_LIBRARY"] = r"C:\Program Files (x86)\Python36_64\tcl\tcl8.6"
os.environ["TK_LIBRARY"] = r"C:\Program Files (x86)\Python36_64\tcl\tk8.6"

packages = [
    "tkinter",
    ]

include_files = [
    "Assets\\",
    "LICENSE.txt",
    "on_install_setup.exe",
    "cleanup.exe",
    "EEHPH2_app.py",
    r"C:\Program Files (x86)\Python36_64\DLLs\tcl86t.dll",
    r"C:\Program Files (x86)\Python36_64\DLLs\tk86t.dll",
    ]  

exec_ = Executable(
    script = "EEHPH2.py",
    base = "Win32GUI",
    icon = os.path.join("Assets", "icon.ico")
    )

setup(
    name = "EEHPH Photo Viewer v2",
    options = {"build_exe": {"packages": packages, "include_files": include_files}},
    version = "2.2.3",
    description = "EEHPH2 by AE computer vision",
    author = "Edward Attenborough",
    executables = [exec_]
) 

