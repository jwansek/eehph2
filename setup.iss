#define MyAppName "EEHPH Photo Viewer v2"
#define MyAppVersion "2.2.5"
#define MyAppPublisher "AE Computer Vision"
#define MyAppURL "https://aecomputervision.blogspot.co.uk/"
#define MyAppExeName "EEHPH2.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{0AF01912-BAF0-42B8-822C-B17BDE553B36}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=C:\Users\Edward\Documents\workingdir\eehph2\build\exe.win-amd64-3.6\LICENSE.txt
OutputDir=C:\Users\Edward\Documents\workingdir\eehph2\inno
OutputBaseFilename=EEHPH2_installer
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon=C:\Users\Edward\Documents\workingdir\eehph2\build\exe.win-amd64-3.6\Assets\icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}";

[Files]
Source: "C:\Users\Edward\Documents\workingdir\eehph2\build\exe.win-amd64-3.6\EEHPH2.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Edward\Documents\workingdir\eehph2\build\exe.win-amd64-3.6\EEHPH2_app.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Edward\Documents\workingdir\eehph2\build\exe.win-amd64-3.6\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Edward\Documents\workingdir\eehph2\build\exe.win-amd64-3.6\on_install_setup.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Edward\Documents\workingdir\eehph2\build\exe.win-amd64-3.6\cleanup.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Edward\Documents\workingdir\eehph2\build\exe.win-amd64-3.6\python36.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Edward\Documents\workingdir\eehph2\build\exe.win-amd64-3.6\tcl86t.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Edward\Documents\workingdir\eehph2\build\exe.win-amd64-3.6\tk86t.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Edward\Documents\workingdir\eehph2\build\exe.win-amd64-3.6\VCRUNTIME140.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Edward\Documents\workingdir\eehph2\build\exe.win-amd64-3.6\Assets\*"; DestDir: "{app}\Assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\Edward\Documents\workingdir\eehph2\build\exe.win-amd64-3.6\lib\*"; DestDir: "{app}\lib"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\Edward\Documents\workingdir\eehph2\build\exe.win-amd64-3.6\tcl\*"; DestDir: "{app}\tcl"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\Edward\Documents\workingdir\eehph2\build\exe.win-amd64-3.6\tk\*"; DestDir: "{app}\tk"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{commonprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\on_install_setup.exe"; Parameters: """{app}\"
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{app}\cleanup.exe";


