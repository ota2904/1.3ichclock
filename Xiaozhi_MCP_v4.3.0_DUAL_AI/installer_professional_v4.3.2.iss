; ==================================================================================
; miniZ MCP v4.3.2 - Professional Installer with License Security
; 3-Device MCP Support | YouTube Fix | JWT Persistence
; ==================================================================================

#define MyAppName "miniZ MCP Pro"
#define MyAppVersion "4.3.2"
#define MyAppPublisher "miniZ Technologies"
#define MyAppURL "https://miniz-mcp.com"
#define MyAppExeName "miniZ_MCP_v4.3.2_3Device.exe"
#define MyAppExeNameShort "miniZ_MCP_3Device.exe"

[Setup]
; App Information
AppId={{8F9D3C5E-1234-5678-9ABC-DEF012345678}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright=Copyright (C) 2025 {#MyAppPublisher}

; Installer Settings
DefaultDirName={autopf}\miniZ_MCP
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE_AGREEMENT.txt
InfoBeforeFile=INSTALLATION_INFO.txt
OutputDir=installer_output
OutputBaseFilename=miniZ_MCP_v4.3.2_3Device_Professional_Setup
SetupIconFile=logo.ico
UninstallDisplayIcon={app}\{#MyAppExeNameShort}

; Compression & Security
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMADictionarySize=1048576
LZMANumFastBytes=273
Encryption=yes
Password=miniZ2025

; Windows Compatibility
MinVersion=6.1sp1
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; UI Settings
WizardStyle=modern
WizardSizePercent=110
DisableWelcomePage=no
ShowLanguageDialog=auto

; Uninstall Settings
UninstallDisplayName={#MyAppName} {#MyAppVersion}
UninstallFilesDir={app}\uninstall

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "autostart"; Description: "Tự động khởi động cùng Windows"; GroupDescription: "Tùy chọn khởi động:"; Flags: unchecked

[Files]
; Main Application
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; DestName: "{#MyAppExeNameShort}"; Flags: ignoreversion

; Configuration Files
Source: "knowledge_index.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "xiaozhi_endpoints.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist uninsneveruninstall
Source: "knowledge_config.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist uninsneveruninstall

; License System (Encrypted)
Source: "license_manager.py"; DestDir: "{app}\license"; Flags: ignoreversion
Source: "license_system.py"; DestDir: "{app}\license"; Flags: ignoreversion
Source: "LICENSE_KEYS.json"; DestDir: "{app}\license"; Flags: ignoreversion
Source: "LICENSE_AGREEMENT.txt"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "CHANGELOG.md"; DestDir: "{app}"; DestName: "VERSION_v4.3.2_CHANGELOG.md"; Flags: ignoreversion isreadme
Source: "CUSTOMER_README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "GEMINI_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "GPT4_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion

; Icon
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu Icons
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeNameShort}"; IconFilename: "{app}\logo.ico"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{group}\User Guide"; Filename: "{app}\CUSTOMER_README.md"
Name: "{group}\Version History"; Filename: "{app}\VERSION_v4.3.2_CHANGELOG.md"

; Desktop Icon (optional)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeNameShort}"; IconFilename: "{app}\logo.ico"; Tasks: desktopicon

; Quick Launch Icon (optional)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeNameShort}"; Tasks: quicklaunchicon

[Registry]
; Application Registry Keys
Root: HKLM; Subkey: "Software\miniZ\MCP"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\miniZ\MCP"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"
Root: HKLM; Subkey: "Software\miniZ\MCP"; ValueType: string; ValueName: "ExeName"; ValueData: "{#MyAppExeNameShort}"
Root: HKLM; Subkey: "Software\miniZ\MCP"; ValueType: string; ValueName: "InstallDate"; ValueData: "{code:GetInstallDate}"

; Autostart Registry (optional)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "miniZ_MCP"; ValueData: """{app}\{#MyAppExeNameShort}"""; Tasks: autostart

; License Validation Registry (Encrypted)
Root: HKLM; Subkey: "Software\miniZ\MCP\License"; ValueType: string; ValueName: "LicenseKey"; ValueData: ""; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\miniZ\MCP\License"; ValueType: string; ValueName: "ActivationDate"; ValueData: ""
Root: HKLM; Subkey: "Software\miniZ\MCP\License"; ValueType: string; ValueName: "LicenseType"; ValueData: "TRIAL"

[Run]
; Launch after installation (optional)
Filename: "{app}\{#MyAppExeNameShort}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

; Create firewall exception
Filename: "netsh"; Parameters: "advfirewall firewall add rule name=""miniZ MCP"" dir=in action=allow program=""{app}\{#MyAppExeNameShort}"" enable=yes"; StatusMsg: "Configuring firewall..."; Flags: runhidden

[UninstallRun]
; Remove firewall exception
Filename: "netsh"; Parameters: "advfirewall firewall delete rule name=""miniZ MCP"""; Flags: runhidden

[UninstallDelete]
; Clean up temporary files (keep user config)
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\*.tmp"
Type: files; Name: "{app}\__pycache__\*"
Type: dirifempty; Name: "{app}\__pycache__"
Type: dirifempty; Name: "{app}\license"

[Code]
var
  LicenseKeyPage: TInputQueryWizardPage;
  LicenseValid: Boolean;

// Get current date for registry
function GetInstallDate(Param: String): String;
begin
  Result := GetDateTimeString('yyyy-mm-dd hh:nn:ss', #0, #0);
end;

// Initialize license key page
procedure InitializeWizard;
begin
  LicenseValid := False;
  
  // Create license key input page
  LicenseKeyPage := CreateInputQueryPage(wpLicense,
    'License Activation', 
    'Enter your license key to activate miniZ MCP Pro',
    'Please enter your license key. Trial version available without key.');
  
  LicenseKeyPage.Add('License Key:', False);
  LicenseKeyPage.Values[0] := '';
  
  // Add trial option description
  LicenseKeyPage.SubCaptionLabel.Caption := 
    'Enter your license key to unlock full features.' + #13#10 +
    'Leave empty to continue with 30-day trial version.' + #13#10#13#10 +
    'Pro Features:' + #13#10 +
    '  • 3-Device MCP Support' + #13#10 +
    '  • Unlimited AI Queries' + #13#10 +
    '  • Priority Support' + #13#10 +
    '  • Commercial Use';
end;

// Validate license key (simple validation)
function ValidateLicenseKey(Key: String): Boolean;
var
  i: Integer;
  ValidFormat: Boolean;
begin
  Result := False;
  
  // Allow empty key for trial
  if Key = '' then
  begin
    Result := True;
    Exit;
  end;
  
  // Check format: MINIZ-XXXXX-XXXXX-XXXXX-XXXXX (29 chars with dashes)
  if Length(Key) <> 29 then Exit;
  if (Copy(Key, 1, 6) <> 'MINIZ-') then Exit;
  if (Copy(Key, 12, 1) <> '-') then Exit;
  if (Copy(Key, 18, 1) <> '-') then Exit;
  if (Copy(Key, 24, 1) <> '-') then Exit;
  
  // Basic format validation passed
  Result := True;
end;

// Validate license page
function NextButtonClick(CurPageID: Integer): Boolean;
var
  LicenseKey: String;
begin
  Result := True;
  
  if CurPageID = LicenseKeyPage.ID then
  begin
    LicenseKey := Trim(LicenseKeyPage.Values[0]);
    
    if ValidateLicenseKey(LicenseKey) then
    begin
      if LicenseKey = '' then
      begin
        if MsgBox('Continue with trial version (30 days)?', mbConfirmation, MB_YESNO) = IDYES then
        begin
          LicenseValid := True;
          RegWriteStringValue(HKLM, 'Software\miniZ\MCP\License', 'LicenseType', 'TRIAL');
          RegWriteStringValue(HKLM, 'Software\miniZ\MCP\License', 'TrialStartDate', GetDateTimeString('yyyy-mm-dd', #0, #0));
          Result := True;
        end
        else
          Result := False;
      end
      else
      begin
        // Valid license key entered
        LicenseValid := True;
        RegWriteStringValue(HKLM, 'Software\miniZ\MCP\License', 'LicenseKey', LicenseKey);
        RegWriteStringValue(HKLM, 'Software\miniZ\MCP\License', 'LicenseType', 'PRO');
        RegWriteStringValue(HKLM, 'Software\miniZ\MCP\License', 'ActivationDate', GetDateTimeString('yyyy-mm-dd', #0, #0));
        MsgBox('License activated successfully!' + #13#10 + 'Thank you for purchasing miniZ MCP Pro!', mbInformation, MB_OK);
        Result := True;
      end;
    end
    else
    begin
      MsgBox('Invalid license key format!' + #13#10#13#10 + 
             'Expected format: MINIZ-XXXXX-XXXXX-XXXXX-XXXXX' + #13#10#13#10 +
             'Please check your license key or contact support.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

// Show completion message with activation status
procedure CurStepChanged(CurStep: TSetupStep);
var
  LicenseType: String;
begin
  if CurStep = ssPostInstall then
  begin
    RegQueryStringValue(HKLM, 'Software\miniZ\MCP\License', 'LicenseType', LicenseType);
    
    if LicenseType = 'PRO' then
    begin
      // Pro version activated
      Log('Pro license activated');
    end
    else
    begin
      // Trial version
      Log('Trial version installed (30 days)');
    end;
  end;
end;

// Custom messages on finish
function UpdateReadyMemo(Space, NewLine, MemoUserInfoInfo, MemoDirInfo, MemoTypeInfo, MemoComponentsInfo, MemoGroupInfo, MemoTasksInfo: String): String;
var
  S: String;
  LicenseType: String;
begin
  S := '';
  
  if MemoDirInfo <> '' then
    S := S + MemoDirInfo + NewLine + NewLine;
  
  if MemoGroupInfo <> '' then
    S := S + MemoGroupInfo + NewLine + NewLine;
    
  if MemoTasksInfo <> '' then
    S := S + MemoTasksInfo + NewLine + NewLine;
  
  // Add license information
  RegQueryStringValue(HKLM, 'Software\miniZ\MCP\License', 'LicenseType', LicenseType);
  
  S := S + 'License Information:' + NewLine;
  if LicenseType = 'PRO' then
    S := S + Space + 'Type: Professional (Full Features)' + NewLine
  else
    S := S + Space + 'Type: Trial (30 days)' + NewLine;
  
  S := S + NewLine + 'New Features in v4.3.2:' + NewLine;
  S := S + Space + '• 3-Device MCP Support (Simultaneous)' + NewLine;
  S := S + Space + '• Web UI: 3 Token Input Fields' + NewLine;
  S := S + Space + '• YouTube Auto-Play (2-word queries)' + NewLine;
  S := S + Space + '• JWT Endpoint Persistence' + NewLine;
  S := S + Space + '• API Key Configuration Save' + NewLine;
  
  Result := S;
end;
