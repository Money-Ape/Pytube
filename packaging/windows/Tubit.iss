#define MyAppName "Tubit"
#define MyAppVersion "1.2"
#define MyAppPublisher "Lovepreet Singh (Money-Ape)"
#define MyAppURL "https://github.com/Money-Ape"
#define MyAppExeName "Tubit.exe"

[Setup]
AppId={{1F91350C-0224-4D2F-8E99-6AF790237872}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
; "ArchitecturesAllowed=x64compatible" specifies that Setup cannot run
; on anything but x64 and Windows 11 on Arm.
ArchitecturesAllowed=x64compatible
; "ArchitecturesInstallIn64BitMode=x64compatible" requests that the
; install be done in "64-bit mode" on x64 or Windows 11 on Arm,
; meaning it should use the native 64-bit Program Files directory and
; the 64-bit view of the registry.
ArchitecturesInstallIn64BitMode=x64compatible
DefaultGroupName={#MyAppName}
LicenseFile=D:\DEV\Tubit\packaging\windows\LICENSE.txt
InfoBeforeFile=D:\DEV\Tubit\packaging\windows\README.txt
InfoAfterFile=D:\DEV\Tubit\packaging\windows\INIT.txt
;PrivilegesRequired=lowest
OutputDir=D:\DEV\Tubit\packaging\windows
OutputBaseFilename=Tubit_Setup_{#MyAppVersion}
SetupIconFile=D:\DEV\Tubit\assets\Tubit.ico
SolidCompression=yes
WizardStyle=modern dynamic polar

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "D:\DEV\Tubit\packaging\windows\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\DEV\Tubit\packaging\windows\INIT.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\DEV\Tubit\packaging\windows\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\DEV\Tubit\packaging\windows\README.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
