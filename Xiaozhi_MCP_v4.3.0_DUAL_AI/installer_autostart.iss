[Setup]
AppName=miniZ MCP v4.3.0
AppVersion=4.3.0
AppPublisher=miniZ Technologies
AppPublisherURL=https://miniz.ai
AppSupportURL=https://miniz.ai/support
AppUpdatesURL=https://miniz.ai/updates
DefaultDirName={pf}\miniZ MCP v4.3.0
DefaultGroupName=miniZ MCP
OutputDir=installer_output
OutputBaseFilename=miniZ_MCP_v4.3.0_Setup
Compression=lzma
SolidCompression=yes
AllowNoIcons=yes
PrivilegesRequired=admin
ShowLanguageDialog=no
LanguageDetectionMethod=uilanguage
DisableProgramGroupPage=no
DisableReadyPage=no
UninstallDisplayIcon={app}\miniZ_MCP_v4.3.0.exe
ChangesAssociations=no
WizardStyle=modern
VersionInfoVersion=4.3.0.0
VersionInfoProductVersion=4.3.0
VersionInfoProductName=miniZ MCP

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "autostart"; Description: "Start with Windows"; GroupDescription: "Startup Options"; Flags: checkedonce

[Files]
Source: "output\miniZ_MCP_v4.3.0.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "rag_config.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "knowledge_config.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist

[Icons]
Name: "{group}\miniZ MCP v4.3.0"; Filename: "{app}\miniZ_MCP_v4.3.0.exe"; IconFileName: "{app}\miniZ_MCP_v4.3.0.exe"; IconIndex: 0
Name: "{group}\{cm:UninstallProgram,miniZ MCP v4.3.0}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\miniZ MCP v4.3.0"; Filename: "{app}\miniZ_MCP_v4.3.0.exe"; IconFileName: "{app}\miniZ_MCP_v4.3.0.exe"; IconIndex: 0; Tasks: desktopicon
Name: "{commonstartup}\miniZ MCP v4.3.0"; Filename: "{app}\miniZ_MCP_v4.3.0.exe"; IconFileName: "{app}\miniZ_MCP_v4.3.0.exe"; IconIndex: 0; Tasks: autostart

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueName: "miniZ MCP v4.3.0"; ValueType: string; ValueData: "{app}\miniZ_MCP_v4.3.0.exe"; Flags: uninsdeletevalue; Tasks: autostart

[Run]
Filename: "{app}\miniZ_MCP_v4.3.0.exe"; Description: "Launch miniZ MCP v4.3.0"; Flags: nowait postinstall skipifsilent

[InstallDelete]
Type: files; Name: "{app}\*.*"

[Code]
procedure InitializeWizard;
begin
  WizardForm.Caption := 'miniZ MCP v4.3.0 - Setup';
  WizardForm.LicenseAcceptedRadio.Checked := True;
end;
