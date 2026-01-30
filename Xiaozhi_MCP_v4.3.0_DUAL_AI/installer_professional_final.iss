; ============================================================
; miniZ MCP Professional v4.3.5 - Professional Installer
; ✅ NO LICENSE KEY REQUIRED - AUTO ACTIVATION
; ✅ NO API KEYS EXPOSED - SECURE BUILD
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
VersionInfoCopyright=Copyright (C) 2026 {#MyAppPublisher}
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
; ============================================================
; MAIN EXECUTABLE ONLY - NO API KEYS INCLUDED
; ============================================================
Source: "dist\miniZ_MCP.exe"; DestDir: "{app}"; DestName: "{#MyAppExeName}"; Flags: ignoreversion

; Logo and assets (safe files)
Source: "logo.png"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; Documentation for customer (safe files)
Source: "CUSTOMER_README.md"; DestDir: "{app}"; DestName: "README.md"; Flags: ignoreversion skipifsourcedoesntexist

; ============================================================
; ⛔ KHÔNG BAO GỒM CÁC FILE SAU (CHỨA API KEY / THÔNG TIN NHẠY CẢM):
; ============================================================
; ❌ xiaozhi_endpoints.json - Chứa API endpoints và keys
; ❌ gemini_api_key.txt - Chứa Gemini API key
; ❌ serper_api_key.txt - Chứa Serper API key
; ❌ LICENSE_KEYS.json - Chứa license keys
; ❌ LICENSE_TRACKING.json - Chứa thông tin tracking
; ❌ .env files - Chứa environment variables
; ❌ *.log files - Chứa logs có thể có thông tin nhạy cảm
; ============================================================

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\logo.ico"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\logo.ico"; Tasks: desktopicon
; Startup folder shortcut for auto-start with Windows
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Registry]
; Auto-start with Windows via Registry (backup method)
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
; Remove from startup registry on uninstall
Filename: "{sys}\reg.exe"; Parameters: "delete ""HKCU\Software\Microsoft\Windows\CurrentVersion\Run"" /v ""{#MyAppName}"" /f"; Flags: runhidden; RunOnceId: "RemoveStartupReg"

[Code]
// ============================================================
// KILL RUNNING PROCESS BEFORE INSTALL
// ============================================================
function KillProcess(ProcessName: String): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  // Use taskkill to force close the process
  Exec('taskkill.exe', '/F /IM ' + ProcessName, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

// ============================================================
// CLEAN INSTALL - DELETE ALL USER DATA
// ============================================================
procedure CleanUserData();
var
  DataDir: String;
begin
  DataDir := ExpandConstant('{localappdata}\miniZ_MCP');
  if DirExists(DataDir) then
  begin
    DelTree(DataDir, True, True, True);
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  NeedsRestart := False;
  
  // Kill the running process before installation
  KillProcess('miniZ_MCP.exe');
  
  // Wait a moment for process to fully terminate
  Sleep(1000);
  
  // CLEAN INSTALL: Delete all previous user data (API keys, settings, etc.)
  CleanUserData();
end;

function GetCurrentDateTime(Param: String): String;
begin
  Result := GetDateTimeString('yyyy-mm-dd hh:nn:ss', #0, #0);
end;

// ============================================================
// AUTO LICENSE ACTIVATION - NO KEY REQUIRED
// ============================================================
procedure CreateOfflineLicense();
var
  LicenseFile: String;
  LicenseDir: String;
  FileContent: TStringList;
begin
  // Create license directory in AppData
  LicenseDir := ExpandConstant('{localappdata}\miniZ_MCP');
  if not DirExists(LicenseDir) then
    ForceDirectories(LicenseDir);
  
  // Create auto-activated license file
  LicenseFile := LicenseDir + '\license.json';
  FileContent := TStringList.Create;
  try
    FileContent.Add('{');
    FileContent.Add('  "license_type": "offline",');
    FileContent.Add('  "customer_name": "Professional User",');
    FileContent.Add('  "activated": true,');
    FileContent.Add('  "activation_date": "' + GetCurrentDateTime('') + '",');
    FileContent.Add('  "version": "4.3.5",');
    FileContent.Add('  "features": ["all"],');
    FileContent.Add('  "auto_activated": true');
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
    // Create installation info file
    InfoFile := ExpandConstant('{app}\INSTALL_INFO.txt');
    FileContent := TStringList.Create;
    try
      FileContent.Add('========================================');
      FileContent.Add('   miniZ MCP Professional v4.3.5');
      FileContent.Add('========================================');
      FileContent.Add('');
      FileContent.Add('Installation Date: ' + GetCurrentDateTime(''));
      FileContent.Add('Install Path: ' + ExpandConstant('{app}'));
      FileContent.Add('License: Auto-Activated (No Key Required)');
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
      if WizardIsTaskSelected('startupicon') then
        FileContent.Add('- ENABLED: App will start with Windows')
      else
        FileContent.Add('- Disabled: Enable in Settings if needed');
      FileContent.Add('');
      FileContent.Add('Thank you for using miniZ MCP Professional!');
      FileContent.SaveToFile(InfoFile);
    finally
      FileContent.Free;
    end;
    
    // Auto-activate license (NO KEY REQUIRED)
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
    // Ask to clean up user data
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
