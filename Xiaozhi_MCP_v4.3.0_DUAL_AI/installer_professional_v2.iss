; ============================================================
; miniZ MCP Professional v4.3.5 - Professional Installer
; NO LICENSE KEY REQUIRED - AUTO STARTUP WITH WINDOWS
; ============================================================

#define MyAppName "miniZ MCP Professional"
#define MyAppVersion "4.3.5"
#define MyAppPublisher "miniZ Team"
#define MyAppExeName "miniZ_MCP.exe"
#define MyAppIcon "logo.ico"

[Setup]
AppId={{B5E6F4A2-8C9D-4E7F-A3B2-1C6D8E9F0A5B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=installer_output
OutputBaseFilename=miniZ_MCP_Professional_v{#MyAppVersion}_Setup
Compression=lzma2/ultra64
SolidCompression=yes
SetupIconFile={#MyAppIcon}
UninstallDisplayIcon={app}\{#MyAppExeName}
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
DisableWelcomePage=no
DisableDirPage=no
DisableProgramGroupPage=yes
VersionInfoVersion={#MyAppVersion}.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} - AI Assistant Platform
VersionInfoCopyright=Copyright (C) 2025 {#MyAppPublisher}
UninstallDisplayName={#MyAppName} {#MyAppVersion}
MinVersion=10.0
SetupLogging=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
english.LaunchProgram=Launch %1 after installation

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"
Name: "startupicon"; Description: "Start automatically with Windows (Recommended)"; GroupDescription: "Startup options:"; Flags: checkablealone

[Files]
; Main executable - from dist folder
Source: "dist\miniZ_MCP.exe"; DestDir: "{app}"; DestName: "{#MyAppExeName}"; Flags: ignoreversion

; Logo and assets (optional)
Source: "logo.png"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; Documentation for customer
Source: "CUSTOMER_README.md"; DestDir: "{app}"; DestName: "README.md"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\logo.ico"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\logo.ico"; Tasks: desktopicon
; Startup folder shortcut - THIS IS THE KEY FOR AUTO-START
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Registry]
; Alternative: Registry auto-start (backup method)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: startupicon
; App info
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent runascurrentuser

[UninstallDelete]
Type: filesandordirs; Name: "{app}\*.log"
Type: filesandordirs; Name: "{app}\*.tmp"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: files; Name: "{userstartup}\{#MyAppName}.lnk"

[UninstallRun]
; Remove from startup on uninstall
Filename: "{sys}\reg.exe"; Parameters: "delete ""HKCU\Software\Microsoft\Windows\CurrentVersion\Run"" /v ""{#MyAppName}"" /f"; Flags: runhidden

[Code]
function GetCurrentDateTime(Param: String): String;
begin
  Result := GetDateTimeString('yyyy-mm-dd hh:nn:ss', #0, #0);
end;

procedure CreateOfflineLicense();
var
  LicenseFile: String;
  LicenseDir: String;
  FileContent: TStringList;
begin
  LicenseDir := ExpandConstant('{localappdata}\miniZ_MCP');
  if not DirExists(LicenseDir) then
    ForceDirectories(LicenseDir);
  
  LicenseFile := LicenseDir + '\license.json';
  FileContent := TStringList.Create;
  try
    FileContent.Add('{');
    FileContent.Add('  "license_type": "offline",');
    FileContent.Add('  "customer_name": "Professional User",');
    FileContent.Add('  "activated": true,');
    FileContent.Add('  "activation_date": "' + GetCurrentDateTime('') + '",');
    FileContent.Add('  "version": "4.3.5",');
    FileContent.Add('  "features": ["all"]');
    FileContent.Add('}');
    FileContent.SaveToFile(LicenseFile);
  finally
    FileContent.Free;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  InfoFile: String;
  FileContent: TStringList;
begin
  if CurStep = ssPostInstall then
  begin
    InfoFile := ExpandConstant('{app}\INSTALL_INFO.txt');
    FileContent := TStringList.Create;
    try
      FileContent.Add('========================================');
      FileContent.Add('   miniZ MCP Professional v4.3.5');
      FileContent.Add('========================================');
      FileContent.Add('');
      FileContent.Add('Installation Date: ' + GetCurrentDateTime(''));
      FileContent.Add('Install Path: ' + ExpandConstant('{app}'));
      FileContent.Add('');
      FileContent.Add('GETTING STARTED:');
      FileContent.Add('1. Double-click miniZ_MCP.exe to start');
      FileContent.Add('2. Open browser: http://localhost:8000');
      FileContent.Add('3. Configure your API keys in the web interface');
      FileContent.Add('');
      FileContent.Add('FEATURES:');
      FileContent.Add('- 146+ AI Tools ready to use');
      FileContent.Add('- Multi-device support (up to 3 devices)');
      FileContent.Add('- Gemini + GPT-4 integration');
      FileContent.Add('- Smart KB Search with Gemini Filter');
      FileContent.Add('- Smart Analysis (Gemini + Google Search)');
      FileContent.Add('- VLC Music Player control');
      FileContent.Add('');
      FileContent.Add('AUTO-START:');
      if IsTaskSelected('startupicon') then
        FileContent.Add('- Enabled: App will start with Windows')
      else
        FileContent.Add('- Disabled: You can enable in Settings');
      FileContent.Add('');
      FileContent.Add('Thank you for using miniZ MCP Professional!');
      FileContent.SaveToFile(InfoFile);
    finally
      FileContent.Free;
    end;
    
    CreateOfflineLicense();
  end;
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  LicenseDir: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    LicenseDir := ExpandConstant('{localappdata}\miniZ_MCP');
    if DirExists(LicenseDir) then
    begin
      if MsgBox('Do you want to remove all user data and settings?', mbConfirmation, MB_YESNO) = IDYES then
      begin
        DelTree(LicenseDir, True, True, True);
      end;
    end;
  end;
end;
