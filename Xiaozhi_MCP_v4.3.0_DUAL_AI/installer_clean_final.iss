; ============================================================
; miniZ MCP Professional v4.3.0 - Clean Installer (Customer Edition)
; NO INTERNAL INFORMATION EXPOSED
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
InfoBeforeFile=INSTALLATION_INFO_CLEAN.txt
OutputDir=installer_output
OutputBaseFilename=miniZ_MCP_Professional_Setup_v{#MyAppVersion}
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
VersionInfoDescription={#MyAppName} Installer
VersionInfoCopyright=Copyright (C) 2025 {#MyAppPublisher}
UninstallDisplayName={#MyAppName} {#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
english.LaunchProgram=Launch %1 after installation

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "startupicon"; Description: "Run at Windows startup (recommended)"; GroupDescription: "Startup Options:"; Flags: unchecked

[Files]
; Main executable
Source: "dist\miniZ_MCP_v4.3.3_Full.exe"; DestDir: "{app}"; DestName: "{#MyAppExeName}"; Flags: ignoreversion
; Assets
Source: "logo.png"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
; Documentation (only customer-facing files)
Source: "LICENSE_AGREEMENT.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "CUSTOMER_README.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
; NOTE: Do NOT copy LICENSE_KEYS.json or LICENSE_TRACKING.json

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
var
  LicenseKeyPage: TInputQueryWizardPage;
  LicenseKey: String;

function GetCurrentDateTime(Param: String): String;
begin
  Result := GetDateTimeString('yyyy-mm-dd hh:nn:ss', #0, #0);
end;

function ValidateLicenseKeyFormat(Key: String): Boolean;
var
  I: Integer;
  DashCount: Integer;
begin
  Result := False;
  
  // Empty key is OK (activate later)
  if Length(Key) = 0 then
  begin
    Result := True;
    Exit;
  end;
  
  Key := Trim(Key);
  
  // Check length
  if Length(Key) <> 25 then
  begin
    MsgBox('Invalid license key format.' + #13#10 + 'Expected format: MINIZ-XXXX-XXXX-XXXX-XXXX', mbError, MB_OK);
    Exit;
  end;
  
  // Check prefix
  if Copy(Key, 1, 6) <> 'MINIZ-' then
  begin
    MsgBox('Invalid license key.' + #13#10 + 'Key must start with MINIZ-', mbError, MB_OK);
    Exit;
  end;
  
  // Count dashes
  DashCount := 0;
  for I := 1 to Length(Key) do
  begin
    if Key[I] = '-' then
      DashCount := DashCount + 1;
  end;
  
  if DashCount <> 4 then
  begin
    MsgBox('Invalid license key format.' + #13#10 + 'Expected 4 dashes in the key.', mbError, MB_OK);
    Exit;
  end;
  
  // Verify dash positions
  if (Key[6] <> '-') or (Key[11] <> '-') or (Key[16] <> '-') or (Key[21] <> '-') then
  begin
    MsgBox('Invalid license key format.' + #13#10 + 'Dashes must be at correct positions.', mbError, MB_OK);
    Exit;
  end;
  
  Result := True;
end;

procedure InitializeWizard;
begin
  // Create license activation page
  LicenseKeyPage := CreateInputQueryPage(wpSelectTasks,
    'License Activation',
    'Activate miniZ MCP Professional',
    'Enter your license key to activate the software.' + #13#10#13#10 +
    'Format: MINIZ-XXXX-XXXX-XXXX-XXXX' + #13#10#13#10 +
    'You can skip this step and activate later when you first run the application.');
  
  LicenseKeyPage.Add('License Key (optional):', False);
  LicenseKeyPage.Values[0] := '';
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if CurPageID = LicenseKeyPage.ID then
  begin
    LicenseKey := Trim(LicenseKeyPage.Values[0]);
    
    // Handle empty key (skip activation)
    if Length(LicenseKey) = 0 then
    begin
      if MsgBox('No license key entered.' + #13#10#13#10 +
                'You can activate later when you first run the application.' + #13#10#13#10 +
                'Continue without activating now?',
                mbConfirmation, MB_YESNO) = IDYES then
      begin
        Result := True;
        Exit;
      end
      else
      begin
        Result := False;
        Exit;
      end;
    end;
    
    // Validate key format
    if not ValidateLicenseKeyFormat(LicenseKey) then
    begin
      Result := False;
      Exit;
    end;
    
    // Confirm key
    if MsgBox('License Key: ' + LicenseKey + #13#10#13#10 +
              'This key will be activated when you first run the application.' + #13#10#13#10 +
              'Continue?', 
              mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
      Exit;
    end;
    
    // Save pending key to registry
    RegWriteStringValue(HKCU, 'Software\{#MyAppPublisher}\{#MyAppName}', 
                        'PendingLicenseKey', LicenseKey);
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ActivationFile: String;
  FileContent: TStringList;
begin
  if CurStep = ssPostInstall then
  begin
    // Create activation info file
    ActivationFile := ExpandConstant('{app}\ACTIVATION_INFO.txt');
    FileContent := TStringList.Create;
    try
      FileContent.Add('════════════════════════════════════════════════════════════');
      FileContent.Add('                                                            ');
      FileContent.Add('   miniZ MCP Professional v' + '{#MyAppVersion}' + ' - INSTALLED SUCCESSFULLY  ');
      FileContent.Add('                                                            ');
      FileContent.Add('════════════════════════════════════════════════════════════');
      FileContent.Add('');
      FileContent.Add('Installation Date: ' + GetDateTimeString('yyyy-mm-dd hh:nn:ss', #0, #0));
      FileContent.Add('Installation Path: ' + ExpandConstant('{app}'));
      FileContent.Add('');
      
      if Length(LicenseKey) > 0 then
      begin
        FileContent.Add('✅ LICENSE KEY PROVIDED');
        FileContent.Add('════════════════════════════════════════════════════════════');
        FileContent.Add('License Key: ' + LicenseKey);
        FileContent.Add('Status: Ready for Activation');
        FileContent.Add('');
        FileContent.Add('NEXT STEPS:');
        FileContent.Add('  1. Launch miniZ MCP Professional');
        FileContent.Add('  2. License will activate automatically');
        FileContent.Add('  3. Start using all features immediately');
        FileContent.Add('');
      end
      else
      begin
        FileContent.Add('⚠️ LICENSE ACTIVATION REQUIRED');
        FileContent.Add('════════════════════════════════════════════════════════════');
        FileContent.Add('Status: Not Activated');
        FileContent.Add('');
        FileContent.Add('TO ACTIVATE:');
        FileContent.Add('  1. Launch miniZ MCP Professional');
        FileContent.Add('  2. Enter your license key when prompted');
        FileContent.Add('  3. Format: MINIZ-XXXX-XXXX-XXXX-XXXX');
        FileContent.Add('');
        FileContent.Add('Contact your vendor if you need a license key.');
        FileContent.Add('');
      end;
      
      FileContent.Add('════════════════════════════════════════════════════════════');
      FileContent.Add('NEW FEATURES IN v4.3.0');
      FileContent.Add('════════════════════════════════════════════════════════════');
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
      FileContent.Add('   • Context-aware conversations');
      FileContent.Add('');
      FileContent.Add('✨ Performance & Reliability');
      FileContent.Add('   • Faster response times');
      FileContent.Add('   • Enhanced security and encryption');
      FileContent.Add('   • Improved stability');
      FileContent.Add('   • Bug fixes and optimizations');
      FileContent.Add('');
      FileContent.Add('════════════════════════════════════════════════════════════');
      FileContent.Add('GETTING STARTED');
      FileContent.Add('════════════════════════════════════════════════════════════');
      FileContent.Add('');
      FileContent.Add('1. Launch the application from Start Menu or Desktop');
      FileContent.Add('2. Activate with your license key (if not done yet)');
      FileContent.Add('3. Configure your AI API keys (Gemini/OpenAI)');
      FileContent.Add('4. Start chatting with your AI assistant!');
      FileContent.Add('');
      FileContent.Add('Check the User Guide in Start Menu for more information.');
      FileContent.Add('');
      FileContent.Add('════════════════════════════════════════════════════════════');
      FileContent.Add('');
      FileContent.Add('Thank you for choosing miniZ MCP Professional!');
      FileContent.Add('');
      
      FileContent.SaveToFile(ActivationFile);
    finally
      FileContent.Free;
    end;
  end;
end;

function InitializeUninstall(): Boolean;
var
  LicenseDir: String;
begin
  Result := True;
  
  // Check for license data
  LicenseDir := ExpandConstant('{localappdata}\miniZ_MCP\.license');
  
  if DirExists(LicenseDir) then
  begin
    if MsgBox('Do you want to keep your license activation for future use?' + #13#10#13#10 +
              'Choose YES to keep your license (recommended).' + #13#10 +
              'Choose NO to completely remove the license.' + #13#10#13#10 +
              'Keep license activation?',
              mbConfirmation, MB_YESNO or MB_DEFBUTTON1) = IDNO then
    begin
      // User chose to remove license
      DelTree(LicenseDir, True, True, True);
    end;
  end;
end;

[Messages]
WelcomeLabel2=This will install [name/ver] on your computer.%n%nYou will need a valid license key to use the software.%n%nIt is recommended that you close all other applications before continuing.
