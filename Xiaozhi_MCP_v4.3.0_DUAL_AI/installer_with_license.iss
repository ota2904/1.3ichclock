; ============================================================
; miniZ MCP Professional v4.3.0 - Inno Setup Installer
; Hardware-Locked License System + Terms & Conditions
; ============================================================

#define MyAppName "miniZ MCP Professional"
#define MyAppVersion "4.3.0"
#define MyAppPublisher "miniZ MCP Team"
#define MyAppURL "https://www.example.com/"
#define MyAppExeName "miniZ_MCP_Professional.exe"
#define MyAppIcon "logo.ico"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
AppId={{B5E6F4A2-8C9D-4E7F-A3B2-1C6D8E9F0A5B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
; License file - điều khoản sử dụng
LicenseFile=LICENSE_AGREEMENT.txt
; Info file - hướng dẫn
InfoBeforeFile=INSTALLATION_INFO.txt
InfoAfterFile=LICENSE_ACTIVATION_GUIDE.md
; Output
OutputDir=installer_output
OutputBaseFilename=miniZ_MCP_Professional_Setup_v{#MyAppVersion}
; Compression
Compression=lzma2/ultra64
SolidCompression=yes
; Icon
SetupIconFile={#MyAppIcon}
UninstallDisplayIcon={app}\{#MyAppExeName}
; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
; Architecture
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
; UI
WizardStyle=modern
DisableWelcomePage=no
DisableDirPage=no
DisableProgramGroupPage=no
; Version Info
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Installer
VersionInfoCopyright=Copyright (C) 2025 {#MyAppPublisher}
; Uninstall
UninstallDisplayName={#MyAppName} {#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
english.LaunchProgram=Launch %1 after installation
english.LicenseKeyRequired=License key is required to use this software
english.ActivationRequired=You need to activate your license on first run
english.HardwareLocked=License is locked to your computer hardware
english.LifetimeLicense=Lifetime license - no expiration

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "startupicon"; Description: "Run at Windows startup"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main executable
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Logo (optional)
Source: "logo.png"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
; NOTE: All license key files are EXCLUDED for security reasons

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\License Activation Guide"; Filename: "{app}\LICENSE_ACTIVATION_GUIDE.md"
Name: "{group}\Customer Guide"; Filename: "{app}\CUSTOMER_README.md"
Name: "{group}\Sample License Keys"; Filename: "{app}\Sample_Keys.txt"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Registry]
; Windows startup (optional task)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: startupicon
; Application settings
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstalledDate"; ValueData: "{code:GetCurrentDateTime}"

[Run]
; Launch application after installation (with license activation prompt)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up license files (optional - keep commented to preserve license)
; Type: filesandordirs; Name: "{localappdata}\miniZ_MCP\.license"
Type: filesandordirs; Name: "{app}\*.log"
Type: filesandordirs; Name: "{app}\*.tmp"

[Code]
var
  LicenseKeyPage: TInputQueryWizardPage;
  LicenseKey: String;
  AcceptedTerms: Boolean;

// ============================================================
// CUSTOM FUNCTIONS
// ============================================================

function GetCurrentDateTime(Param: String): String;
begin
  Result := GetDateTimeString('yyyy-mm-dd hh:nn:ss', #0, #0);
end;

// ============================================================
// LICENSE KEY INPUT PAGE
// ============================================================

procedure InitializeWizard;
var
  InfoPage: TOutputMsgMemoWizardPage;
  TermsText: String;
begin
  // Create custom page for license key input
  LicenseKeyPage := CreateInputQueryPage(wpSelectTasks,
    'License Key Activation',
    'Enter your license key to activate the software',
    'Please enter the license key you received. ' +
    'Format: MINIZ-XXXX-XXXX-XXXX-XXXX' + #13#10#13#10 +
    'If you don''t have a license key yet, you can skip this step and activate later when you first run the application.' + #13#10#13#10 +
    'Note: License is hardware-locked to your computer.');
  
  LicenseKeyPage.Add('License Key:', False);
  LicenseKeyPage.Values[0] := '';
  
  // Add information page about license system
  InfoPage := CreateOutputMsgMemoPage(wpSelectTasks,
    'License Information',
    'Important information about the license system',
    'Please read the following information carefully:',
    '');
  
  TermsText := 
    '🔐 LICENSE SYSTEM FEATURES:' + #13#10 +
    '══════════════════════════════════════════════' + #13#10 +
    '✅ Hardware-Locked Security' + #13#10 +
    '   - License bound to CPU ID + Motherboard Serial' + #13#10 +
    '   - Cannot be copied to another computer' + #13#10 +
    '   - AES-256 encryption for maximum security' + #13#10 +
    '' + #13#10 +
    '✅ Lifetime Validity' + #13#10 +
    '   - No expiration date' + #13#10 +
    '   - One-time activation' + #13#10 +
    '   - Free updates for minor versions' + #13#10 +
    '' + #13#10 +
    '✅ Three License Tiers:' + #13#10 +
    '   - STANDARD: 1 device' + #13#10 +
    '   - PRO: 2 devices' + #13#10 +
    '   - ENTERPRISE: 5 devices' + #13#10 +
    '' + #13#10 +
    '📋 ACTIVATION PROCESS:' + #13#10 +
    '══════════════════════════════════════════════' + #13#10 +
    '1. Run the application after installation' + #13#10 +
    '2. Enter your license key when prompted' + #13#10 +
    '3. Key format: MINIZ-XXXX-XXXX-XXXX-XXXX' + #13#10 +
    '4. License will be activated automatically' + #13#10 +
    '5. Encrypted license file stored in:' + #13#10 +
    '   %LOCALAPPDATA%\miniZ_MCP\.license\' + #13#10 +
    '' + #13#10 +
    '⚠️ IMPORTANT NOTES:' + #13#10 +
    '══════════════════════════════════════════════' + #13#10 +
    '• Hardware changes may invalidate license' + #13#10 +
    '• Keep your license key safe and secure' + #13#10 +
    '• Do NOT share license keys with others' + #13#10 +
    '• Contact support for hardware upgrade assistance' + #13#10 +
    '' + #13#10 +
    '📞 SUPPORT:' + #13#10 +
    '══════════════════════════════════════════════' + #13#10 +
    '• Email: support@example.com' + #13#10 +
    '• Documentation: See LICENSE_ACTIVATION_GUIDE.md' + #13#10 +
    '• Sample keys available in: Sample_Keys.txt' + #13#10;
  
  InfoPage.RichEditViewer.Lines.Text := TermsText;
end;

// ============================================================
// VALIDATE LICENSE KEY FORMAT
// ============================================================

function ValidateLicenseKeyFormat(Key: String): Boolean;
var
  I: Integer;
  DashCount: Integer;
begin
  Result := False;
  
  // Check if empty - NOT ALLOWED (must enter license key)
  if Length(Key) = 0 then
  begin
    MsgBox('License key is required!' + #13#10#13#10 +
           'Please enter a valid license key to continue installation.' + #13#10 +
           'Format: MINIZ-XXXX-XXXX-XXXX-XXXX', mbError, MB_OK);
    Result := False;
    Exit;
  end;
  
  // Check format: MINIZ-XXXX-XXXX-XXXX-XXXX (25 characters including dashes)
  if Length(Key) <> 25 then
  begin
    MsgBox('Invalid license key length. Expected format: MINIZ-XXXX-XXXX-XXXX-XXXX', mbError, MB_OK);
    Exit;
  end;
  
  // Check if starts with MINIZ-
  if Copy(Key, 1, 6) <> 'MINIZ-' then
  begin
    MsgBox('Invalid license key format. Must start with MINIZ-', mbError, MB_OK);
    Exit;
  end;
  
  // Count dashes - should have exactly 4
  DashCount := 0;
  for I := 1 to Length(Key) do
  begin
    if Key[I] = '-' then
      DashCount := DashCount + 1;
  end;
  
  if DashCount <> 4 then
  begin
    MsgBox('Invalid license key format. Expected 4 dashes.', mbError, MB_OK);
    Exit;
  end;
  
  // Check dash positions (should be at 6, 11, 16, 21)
  if (Key[6] <> '-') or (Key[11] <> '-') or (Key[16] <> '-') or (Key[21] <> '-') then
  begin
    MsgBox('Invalid license key format. Dashes in wrong positions.', mbError, MB_OK);
    Exit;
  end;
  
  Result := True;
end;

// ============================================================
// VALIDATE LICENSE KEY PAGE
// ============================================================

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if CurPageID = LicenseKeyPage.ID then
  begin
    LicenseKey := Trim(LicenseKeyPage.Values[0]);
    
    // Validate format
    if not ValidateLicenseKeyFormat(LicenseKey) then
    begin
      Result := False;
      Exit;
    end;
    
    // Show confirmation with entered license key
    if MsgBox('License Key: ' + LicenseKey + #13#10#13#10 +
              'This key will be validated and activated on first run.' + #13#10 +
              'Continue with installation?', 
              mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
      Exit;
    end;
    
    // Save license key to registry for later use
    RegWriteStringValue(HKCU, 'Software\{#MyAppPublisher}\{#MyAppName}', 
                        'PendingLicenseKey', LicenseKey);
  end;
end;

// ============================================================
// POST-INSTALL: CREATE ACTIVATION INFO FILE
// ============================================================

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
      FileContent.Add('╔════════════════════════════════════════════════════════════╗');
      FileContent.Add('║                                                            ║');
      FileContent.Add('║    miniZ MCP Professional v' + '{#MyAppVersion}' + ' - ACTIVATION INFO      ║');
      FileContent.Add('║                                                            ║');
      FileContent.Add('╚════════════════════════════════════════════════════════════╝');
      FileContent.Add('');
      FileContent.Add('Installation Date: ' + GetDateTimeString('yyyy-mm-dd hh:nn:ss', #0, #0));
      FileContent.Add('Installation Path: ' + ExpandConstant('{app}'));
      FileContent.Add('');
      
      if Length(LicenseKey) > 0 then
      begin
        FileContent.Add('✅ LICENSE KEY PROVIDED DURING INSTALLATION');
        FileContent.Add('═══════════════════════════════════════════');
        FileContent.Add('License Key: ' + LicenseKey);
        FileContent.Add('Status: Pending Activation');
        FileContent.Add('');
        FileContent.Add('NEXT STEP:');
        FileContent.Add('1. Launch the application');
        FileContent.Add('2. License will activate automatically');
        FileContent.Add('3. Check activation status in app');
      end
      else
      begin
        FileContent.Add('⚠️ NO LICENSE KEY PROVIDED');
        FileContent.Add('═══════════════════════════════════════════');
        FileContent.Add('Status: Not Activated');
        FileContent.Add('');
        FileContent.Add('TO ACTIVATE:');
        FileContent.Add('1. Launch the application');
        FileContent.Add('2. Enter your purchased license key when prompted');
        FileContent.Add('3. Format: MINIZ-XXXX-XXXX-XXXX-XXXX');
        FileContent.Add('');
        FileContent.Add('⚠️ Contact your vendor for license key');
      end;
      
      FileContent.Add('');
      FileContent.Add('═══════════════════════════════════════════');
      FileContent.Add('📋 LICENSE INFORMATION');
      FileContent.Add('═══════════════════════════════════════════');
      FileContent.Add('• Hardware-Locked: Yes (CPU + Motherboard)');
      FileContent.Add('• Encryption: AES-256 Fernet');
      FileContent.Add('• Validity: Lifetime (no expiration)');
      FileContent.Add('• License File Location:');
      FileContent.Add('  %LOCALAPPDATA%\miniZ_MCP\.license\license.enc');
      FileContent.Add('');
      FileContent.Add('═══════════════════════════════════════════');
      FileContent.Add('📖 DOCUMENTATION');
      FileContent.Add('═══════════════════════════════════════════');
      FileContent.Add('• License Guide: LICENSE_ACTIVATION_GUIDE.md');
      FileContent.Add('• User Guide: CUSTOMER_README.md');
      FileContent.Add('• Sample Keys: Sample_Keys.txt');
      FileContent.Add('');
      FileContent.Add('═══════════════════════════════════════════');
      FileContent.Add('📞 SUPPORT');
      FileContent.Add('═══════════════════════════════════════════');
      FileContent.Add('• Email: support@example.com');
      FileContent.Add('• Website: https://www.example.com/');
      FileContent.Add('');
      FileContent.Add('Thank you for choosing miniZ MCP Professional!');
      
      FileContent.SaveToFile(ActivationFile);
    finally
      FileContent.Free;
    end;
  end;
end;

// ============================================================
// UNINSTALL: CONFIRM LICENSE REMOVAL
// ============================================================

function InitializeUninstall(): Boolean;
var
  LicenseDir: String;
begin
  Result := True;
  
  LicenseDir := ExpandConstant('{localappdata}\miniZ_MCP\.license');
  
  if DirExists(LicenseDir) then
  begin
    if MsgBox('Do you want to remove your license activation?' + #13#10#13#10 +
              'If you choose YES, you will need to re-activate with your license key after reinstalling.' + #13#10 +
              'If you choose NO, your license will remain activated for future installations.' + #13#10#13#10 +
              'Remove license activation?',
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      // Remove license directory
      DelTree(LicenseDir, True, True, True);
    end;
  end;
end;

[Messages]
; Custom messages for installer
WelcomeLabel2=This will install [name/ver] on your computer.%n%nThis is a PROFESSIONAL EDITION with hardware-locked license system. You will need a valid license key to use the software.%n%nIt is recommended that you close all other applications before continuing.

[UninstallRun]
; Optional: Run cleanup on uninstall
; Filename: "{cmd}"; Parameters: "/c rd /s /q ""{localappdata}\miniZ_MCP"""; Flags: runhidden

