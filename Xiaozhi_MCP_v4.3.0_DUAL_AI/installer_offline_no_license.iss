; ============================================================
; miniZ MCP Professional v4.3.0 - Offline Installer (NO LICENSE)
; Completely offline, no license validation
; ============================================================

#define MyAppName "miniZ MCP Professional"
#define MyAppVersion "4.3.0"
#define MyAppPublisher "miniZ Team"
#define MyAppExeName "miniZ_MCP_Professional.exe"
#define MyAppIcon "logo.ico"

[Setup]
AppId={{B5E6F4A2-8C9D-4E7F-A3B2-1C6D8E9F0A5B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
LicenseFile=LICENSE_AGREEMENT.txt
OutputDir=installer_output
OutputBaseFilename=miniZ_MCP_Offline_Setup_v{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
SetupIconFile={#MyAppIcon}
UninstallDisplayIcon={app}\{#MyAppExeName}
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern
DisableWelcomePage=no
DisableDirPage=no
DisableProgramGroupPage=no
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Offline Installer
VersionInfoCopyright=Copyright (C) 2025 {#MyAppPublisher}
UninstallDisplayName={#MyAppName} {#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
english.LaunchProgram=Launch %1 after installation

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "startupicon"; Description: "Run at Windows startup (recommended)"; GroupDescription: "Startup Options:"; Flags: unchecked

[Files]
; Main executable
Source: "dist\miniZ_MCP_v4.3.3_Full.exe"; DestDir: "{app}"; DestName: "{#MyAppExeName}"; Flags: ignoreversion
; Assets
Source: "logo.png"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
; Documentation
Source: "LICENSE_AGREEMENT.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "CUSTOMER_README.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Registry]
; Startup registry (if selected)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: startupicon
; App settings
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstalledDate"; ValueData: "{code:GetCurrentDateTime}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\*.log"
Type: filesandordirs; Name: "{app}\*.tmp"

[Code]
function GetCurrentDateTime(Param: String): String;
begin
  Result := GetDateTimeString('yyyy-mm-dd hh:nn:ss', #0, #0);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  InfoFile: String;
  FileContent: TStringList;
begin
  if CurStep = ssPostInstall then
  begin
    // Create installation info file
    InfoFile := ExpandConstant('{app}\INSTALLATION_INFO.txt');
    FileContent := TStringList.Create;
    try
      FileContent.Add('════════════════════════════════════════════════════════════');
      FileContent.Add('                                                            ');
      FileContent.Add('   miniZ MCP Professional v' + '{#MyAppVersion}' + ' - INSTALLED   ');
      FileContent.Add('                                                            ');
      FileContent.Add('════════════════════════════════════════════════════════════');
      FileContent.Add('');
      FileContent.Add('Installation Date: ' + GetDateTimeString('yyyy-mm-dd hh:nn:ss', #0, #0));
      FileContent.Add('Installation Path: ' + ExpandConstant('{app}'));
      FileContent.Add('Installation Mode: OFFLINE (No License Required)');
      FileContent.Add('');
      FileContent.Add('════════════════════════════════════════════════════════════');
      FileContent.Add('NEW FEATURES IN v4.3.0');
      FileContent.Add('════════════════════════════════════════════════════════════');
      FileContent.Add('');
      FileContent.Add('✨ YouTube Direct Open - Fixed!');
      FileContent.Add('   • Now opens videos directly instead of search page');
      FileContent.Add('   • Try: "mở youtube Lạc Trôi Sơn Tùng M-TP"');
      FileContent.Add('');
      FileContent.Add('✨ Enhanced Knowledge Base System');
      FileContent.Add('   • Auto-search your documents when you ask questions');
      FileContent.Add('   • AI-powered summarization of long documents');
      FileContent.Add('   • Smart context extraction and ranking');
      FileContent.Add('');
      FileContent.Add('✨ Improved AI Integration');
      FileContent.Add('   • 141 powerful AI tools at your command');
      FileContent.Add('   • Dual AI support (Gemini 2.0 + GPT-4)');
      FileContent.Add('   • Better accuracy and response time');
      FileContent.Add('');
      FileContent.Add('════════════════════════════════════════════════════════════');
      FileContent.Add('GETTING STARTED');
      FileContent.Add('════════════════════════════════════════════════════════════');
      FileContent.Add('');
      FileContent.Add('1. Launch from Start Menu or Desktop icon');
      FileContent.Add('2. Configure AI API keys (Gemini/OpenAI)');
      FileContent.Add('3. Start chatting with your AI assistant!');
      FileContent.Add('');
      FileContent.Add('No license activation required - ready to use!');
      FileContent.Add('');
      FileContent.Add('════════════════════════════════════════════════════════════');
      FileContent.Add('');
      FileContent.Add('Thank you for using miniZ MCP Professional!');
      FileContent.Add('');
      
      FileContent.SaveToFile(InfoFile);
    finally
      FileContent.Free;
    end;
  end;
end;

[Messages]
WelcomeLabel2=This will install [name/ver] on your computer.%n%nIt is recommended that you close all other applications before continuing.
