; CEMICODE Setup — Inno Setup script (paso dos profesional)
; Requiere Inno Setup 6 (iscc). Compila: iscc installer\cemicode-setup.iss
; Fuente: dist-portable-cemicode\  Salida: dist\CEMICODE-Setup-Inno.exe
#define MyAppName "CEMICODE"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "CEMICODE Coding Agent"
#define MyAppExeName "bin\cemicode.exe"

[Setup]
AppId={{CEMICODE-CODING-AGENT-2026}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=..\dist
OutputBaseFilename=CEMICODE-Setup-Inno
SetupIconFile=..\cemicode-branding\icons\cemicode.ico
UninstallDisplayIcon={app}\cemicode.ico
WizardImageFile=..\cemicode-branding\icons\icon-192.png
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
DisableProgramGroupPage=yes

[Files]
Source: "..\dist-portable-cemicode\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\cemicode-branding\icons\cemicode.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\CEMICODE"; Filename: "{app}\ejecutar-cemicode.bat"; WorkingDir: "{app}"; IconFilename: "{app}\cemicode.ico"
Name: "{group}\CEMICODE Web"; Filename: "{app}\ejecutar-cemicode-web.bat"; WorkingDir: "{app}"; IconFilename: "{app}\cemicode.ico"
Name: "{autodesktop}\CEMICODE"; Filename: "{app}\ejecutar-cemicode.bat"; WorkingDir: "{app}"; IconFilename: "{app}\cemicode.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear icono en el escritorio"; GroupDescription: "Accesos directos:"

[Run]
Filename: "{app}\ejecutar-cemicode.bat"; Description: "Ejecutar CEMICODE ahora"; Flags: postinstall skipifsilent shellexec
