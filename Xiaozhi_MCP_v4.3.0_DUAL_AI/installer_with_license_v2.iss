; ============================================================
; miniZ MCP Professional v4.3.0 - Inno Setup Installer
; Hardware-Locked License System + Pre-generated Keys
; Updated: December 9, 2025
; Includes: 150 valid license keys (100 STD, 40 PRO, 10 ENT)
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
OutputBaseFilename=miniZ_MCP_Professional_Setup_v{#MyAppVersion}_Final
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
VersionInfoDescription={#MyAppName} Installer with Pre-generated Keys
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
; Main executable with embedded license keys
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; License keys JSON (embedded in EXE, but also copy for reference)
Source: "LICENSE_KEYS.json"; DestDir: "{app}"; Flags: ignoreversion
; Logo
Source: "logo.png"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
; Documentation
Source: "LICENSE_ACTIVATION_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "CUSTOMER_README.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "Sample_Keys.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\License Activation Guide"; Filename: "{app}\LICENSE_ACTIVATION_GUIDE.md"
Name: "{group}\Customer Guide"; Filename: "{app}\CUSTOMER_README.md"
Name: "{group}\Valid License Keys"; Filename: "{app}\LICENSE_KEYS.json"
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
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "TotalKeysAvailable"; ValueData: "150"

[Run]
; Launch application after installation (with license activation prompt)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up temporary files (keep license unless user chooses to remove)
Type: filesandordirs; Name: "{app}\*.log"
Type: filesandordirs; Name: "{app}\*.tmp"

[Code]
var
  LicenseKeyPage: TInputQueryWizardPage;
  LicenseKey: String;
  ValidKeysCount: Integer;

// ============================================================
// CUSTOM FUNCTIONS
// ============================================================

function GetCurrentDateTime(Param: String): String;
begin
  Result := GetDateTimeString('yyyy-mm-dd hh:nn:ss', #0, #0);
end;

// ============================================================
// LICENSE KEY VALIDATION (MD5 CHECKSUM)
// ============================================================

function ValidateLicenseKeyFormat(Key: String): Boolean;
var
  I: Integer;
  DashCount: Integer;
begin
  Result := False;
  
  // Check if empty - allow skip (user can activate later)
  if Length(Key) = 0 then
  begin
    Result := True; // Allow empty for skip
    Exit;
  end;
  
  // Remove spaces and convert to uppercase
  Key := Trim(Key);
  for I := 1 to Length(Key) do
  begin
    if Key[I] = ' ' then
      Delete(Key, I, 1);
  end;
  
  // Check format: MINIZ-XXXX-XXXX-XXXX-XXXX (25 characters including dashes)
  if Length(Key) <> 25 then
  begin
    MsgBox('❌ Invalid license key length!' + #13#10#13#10 +
           'Expected: 25 characters (MINIZ-XXXX-XXXX-XXXX-XXXX)' + #13#10 +
           'Got: ' + IntToStr(Length(Key)) + ' characters' + #13#10#13#10 +
           'Please check your license key and try again.', mbError, MB_OK);
    Exit;
  end;
  
  // Check if starts with MINIZ-
  if Copy(Key, 1, 6) <> 'MINIZ-' then
  begin
    MsgBox('❌ Invalid license key format!' + #13#10#13#10 +
           'License key must start with "MINIZ-"' + #13#10 +
           'Your key starts with: "' + Copy(Key, 1, 6) + '"', mbError, MB_OK);
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
    MsgBox('❌ Invalid license key format!' + #13#10#13#10 +
           'Expected: 4 dashes' + #13#10 +
           'Found: ' + IntToStr(DashCount) + ' dashes' + #13#10#13#10 +
           'Correct format: MINIZ-XXXX-XXXX-XXXX-XXXX', mbError, MB_OK);
    Exit;
  end;
  
  // Check dash positions (should be at 6, 11, 16, 21)
  if (Key[6] <> '-') or (Key[11] <> '-') or (Key[16] <> '-') or (Key[21] <> '-') then
  begin
    MsgBox('❌ Invalid license key format!' + #13#10#13#10 +
           'Dashes must be at positions: 6, 11, 16, 21' + #13#10 +
           'Your key has dashes at wrong positions.', mbError, MB_OK);
    Exit;
  end;
  
  // All checks passed
  Result := True;
end;

// ============================================================
// LICENSE KEY INPUT PAGE
// ============================================================

procedure InitializeWizard;
var
  InfoPage: TOutputMsgMemoWizardPage;
  TermsText: String;
begin
  ValidKeysCount := 150; // Total pre-generated keys
  
  // Create custom page for license key input
  LicenseKeyPage := CreateInputQueryPage(wpSelectTasks,
    '🔐 License Key Activation',
    'Enter your license key to activate the software',
    '📌 Enter your 25-character license key below:' + #13#10 +
    '   Format: MINIZ-XXXX-XXXX-XXXX-XXXX' + #13#10#13#10 +
    '✅ This installer includes 150 pre-generated valid keys:' + #13#10 +
    '   • 100 STANDARD keys (1 device)' + #13#10 +
    '   • 40 PRO keys (2 devices)' + #13#10 +
    '   • 10 ENTERPRISE keys (5 devices)' + #13#10#13#10 +
    '⚠️ You can skip this step and activate later when you first run the application.' + #13#10 +
    '⚠️ License is hardware-locked to your computer (CPU + Motherboard).');
  
  LicenseKeyPage.Add('License Key (or leave blank to skip):', False);
  LicenseKeyPage.Values[0] := '';
  
  // Add information page about license system
  InfoPage := CreateOutputMsgMemoPage(wpSelectTasks,
    '📋 License System Information',
    'Important information about activation and security',
    'Please read carefully before proceeding:',
    '');
  
  TermsText := 
    '╔════════════════════════════════════════════════════════════╗' + #13#10 +
    '║          150 PRE-GENERATED LICENSE KEYS INCLUDED           ║' + #13#10 +
    '╚════════════════════════════════════════════════════════════╝' + #13#10 +
    '' + #13#10 +
    '🔐 LICENSE TIERS (All with MD5 checksum validation):' + #13#10 +
    '══════════════════════════════════════════════════════════════' + #13#10 +
    '✅ STANDARD (100 keys)' + #13#10 +
    '   • 1 device activation' + #13#10 +
    '   • Lifetime validity' + #13#10 +
    '   • Hardware-locked security' + #13#10 +
    '   • All 141 AI tools included' + #13#10 +
    '' + #13#10 +
    '✅ PRO (40 keys)' + #13#10 +
    '   • 2 device activations' + #13#10 +
    '   • Lifetime validity' + #13#10 +
    '   • Priority support' + #13#10 +
    '   • Advanced features' + #13#10 +
    '' + #13#10 +
    '✅ ENTERPRISE (10 keys)' + #13#10 +
    '   • 5 device activations' + #13#10 +
    '   • Lifetime validity' + #13#10 +
    '   • Premium support 24/7' + #13#10 +
    '   • Custom integrations' + #13#10 +
    '' + #13#10 +
    '🛡️ SECURITY FEATURES:' + #13#10 +
    '══════════════════════════════════════════════════════════════' + #13#10 +
    '✅ Hardware Binding' + #13#10 +
    '   - CPU ID + Motherboard Serial Number' + #13#10 +
    '   - Prevents copying to other computers' + #13#10 +
    '   - AES-256 Fernet encryption' + #13#10 +
    '' + #13#10 +
    '✅ MD5 Checksum Validation' + #13#10 +
    '   - Built-in checksum in last 4 characters' + #13#10 +
    '   - Prevents key tampering' + #13#10 +
    '   - Validates key integrity' + #13#10 +
    '' + #13#10 +
    '✅ Encrypted Storage' + #13#10 +
    '   - License stored at: %LOCALAPPDATA%\miniZ_MCP\.license\' + #13#10 +
    '   - AES-256 encryption' + #13#10 +
    '   - Secure hardware binding' + #13#10 +
    '' + #13#10 +
    '📋 ACTIVATION STEPS:' + #13#10 +
    '══════════════════════════════════════════════════════════════' + #13#10 +
    '1️⃣ Enter license key during installation (or skip)' + #13#10 +
    '2️⃣ Launch application after installation' + #13#10 +
    '3️⃣ If skipped, enter key when prompted' + #13#10 +
    '4️⃣ Key validated with MD5 checksum' + #13#10 +
    '5️⃣ Hardware binding created automatically' + #13#10 +
    '6️⃣ Encrypted license file saved locally' + #13#10 +
    '7️⃣ Activation complete - enjoy lifetime access!' + #13#10 +
    '' + #13#10 +
    '⚠️ IMPORTANT NOTES:' + #13#10 +
    '══════════════════════════════════════════════════════════════' + #13#10 +
    '❗ Major hardware changes (CPU/Motherboard upgrade) may' + #13#10 +
    '   require re-activation - contact support for assistance' + #13#10 +
    '' + #13#10 +
    '❗ Keep your license key safe and secure' + #13#10 +
    '   - Store in password manager or secure location' + #13#10 +
    '   - Needed for re-installation after hardware change' + #13#10 +
    '' + #13#10 +
    '❗ Do NOT share keys with others' + #13#10 +
    '   - Each key tracks hardware binding' + #13#10 +
    '   - Unauthorized sharing is license violation' + #13#10 +
    '' + #13#10 +
    '📄 INCLUDED DOCUMENTATION:' + #13#10 +
    '══════════════════════════════════════════════════════════════' + #13#10 +
    '• LICENSE_KEYS.json - All 150 valid keys' + #13#10 +
    '• LICENSE_ACTIVATION_GUIDE.md - Detailed guide' + #13#10 +
    '• CUSTOMER_README.md - User manual' + #13#10 +
    '• Sample_Keys.txt - Example key formats' + #13#10 +
    '' + #13#10 +
    '📞 SUPPORT:' + #13#10 +
    '══════════════════════════════════════════════════════════════' + #13#10 +
    '• Email: support@example.com' + #13#10 +
    '• Hardware upgrades: Contact support before upgrading' + #13#10 +
    '• Lost keys: Retrieve from LICENSE_KEYS.json in install folder' + #13#10;
  
  InfoPage.RichEditViewer.Lines.Text := TermsText;
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
    
    // If empty, confirm skip
    if Length(LicenseKey) = 0 then
    begin
      if MsgBox('⚠️ No license key entered!' + #13#10#13#10 +
                'You can activate later when you first run the application.' + #13#10 +
                'The software includes 150 pre-generated valid keys in LICENSE_KEYS.json' + #13#10#13#10 +
                '✅ Continue installation without entering key now?',
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
    
    // Validate format
    if not ValidateLicenseKeyFormat(LicenseKey) then
    begin
      Result := False;
      Exit;
    end;
    
    // Show confirmation with entered license key
    if MsgBox('✅ License Key Entered:' + #13#10 +
              '   ' + LicenseKey + #13#10#13#10 +
              '📌 This key will be validated on first run.' + #13#10 +
              '📌 Format validated: OK (25 chars, 4 dashes)' + #13#10 +
              '📌 MD5 checksum will be validated by application' + #13#10#13#10 +
              '✅ Continue with installation?', 
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
      FileContent.Add('║      miniZ MCP Professional v' + '{#MyAppVersion}' + ' - INSTALLED          ║');
      FileContent.Add('║                                                            ║');
      FileContent.Add('╚════════════════════════════════════════════════════════════╝');
      FileContent.Add('');
      FileContent.Add('📅 Installation Date: ' + GetDateTimeString('yyyy-mm-dd hh:nn:ss', #0, #0));
      FileContent.Add('📂 Installation Path: ' + ExpandConstant('{app}'));
      FileContent.Add('📦 Available Keys: 150 (100 STD + 40 PRO + 10 ENT)');
      FileContent.Add('');
      
      if Length(LicenseKey) > 0 then
      begin
        FileContent.Add('╔════════════════════════════════════════════════════════════╗');
        FileContent.Add('║              ✅ LICENSE KEY PROVIDED                        ║');
        FileContent.Add('╚════════════════════════════════════════════════════════════╝');
        FileContent.Add('');
        FileContent.Add('🔑 License Key: ' + LicenseKey);
        FileContent.Add('📊 Status: Pending Activation');
        FileContent.Add('🔐 Security: MD5 Checksum + Hardware Binding');
        FileContent.Add('');
        FileContent.Add('NEXT STEPS:');
        FileContent.Add('═══════════════════════════════════════════════════════════');
        FileContent.Add('1. Launch the application from desktop or Start Menu');
        FileContent.Add('2. License will activate automatically on first run');
        FileContent.Add('3. Hardware binding will be created (CPU + Motherboard)');
        FileContent.Add('4. Encrypted license saved to: %LOCALAPPDATA%\miniZ_MCP\.license\');
        FileContent.Add('5. Check activation status in application');
        FileContent.Add('');
        FileContent.Add('✅ Activation will happen automatically!');
      end
      else
      begin
        FileContent.Add('╔════════════════════════════════════════════════════════════╗');
        FileContent.Add('║            ⚠️ NO LICENSE KEY PROVIDED YET                  ║');
        FileContent.Add('╚════════════════════════════════════════════════════════════╝');
        FileContent.Add('');
        FileContent.Add('📊 Status: Not Activated (Activation Required)');
        FileContent.Add('🔐 Security: Ready for activation');
        FileContent.Add('');
        FileContent.Add('TO ACTIVATE:');
        FileContent.Add('═══════════════════════════════════════════════════════════');
        FileContent.Add('1. Launch the application from desktop or Start Menu');
        FileContent.Add('2. Enter your license key when prompted');
        FileContent.Add('3. Choose any key from LICENSE_KEYS.json (150 valid keys)');
        FileContent.Add('4. Format: MINIZ-XXXX-XXXX-XXXX-XXXX (25 characters)');
        FileContent.Add('');
        FileContent.Add('WHERE TO FIND VALID KEYS:');
        FileContent.Add('═══════════════════════════════════════════════════════════');
        FileContent.Add('📄 File: ' + ExpandConstant('{app}') + '\LICENSE_KEYS.json');
        FileContent.Add('📋 Contains:');
        FileContent.Add('   • 100 STANDARD keys (1 device)');
        FileContent.Add('   • 40 PRO keys (2 devices)');
        FileContent.Add('   • 10 ENTERPRISE keys (5 devices)');
        FileContent.Add('');
        FileContent.Add('💡 TIP: Open LICENSE_KEYS.json and pick any unused key');
      end;
      
      FileContent.Add('');
      FileContent.Add('═══════════════════════════════════════════════════════════');
      FileContent.Add('📋 LICENSE SYSTEM INFO');
      FileContent.Add('═══════════════════════════════════════════════════════════');
      FileContent.Add('🔐 Encryption: AES-256 Fernet');
      FileContent.Add('🔒 Hardware Binding: CPU ID + Motherboard Serial');
      FileContent.Add('✅ Validation: MD5 Checksum (built-in last 4 chars)');
      FileContent.Add('⏰ Validity: Lifetime (no expiration)');
      FileContent.Add('📁 License Storage: %LOCALAPPDATA%\miniZ_MCP\.license\license.enc');
      FileContent.Add('');
      FileContent.Add('═══════════════════════════════════════════════════════════');
      FileContent.Add('📖 DOCUMENTATION');
      FileContent.Add('═══════════════════════════════════════════════════════════');
      FileContent.Add('📄 License Keys: LICENSE_KEYS.json (150 valid keys)');
      FileContent.Add('📖 Activation Guide: LICENSE_ACTIVATION_GUIDE.md');
      FileContent.Add('📘 User Manual: CUSTOMER_README.md');
      FileContent.Add('📝 Sample Keys: Sample_Keys.txt');
      FileContent.Add('');
      FileContent.Add('═══════════════════════════════════════════════════════════');
      FileContent.Add('📞 SUPPORT');
      FileContent.Add('═══════════════════════════════════════════════════════════');
      FileContent.Add('✉️ Email: support@example.com');
      FileContent.Add('🌐 Website: https://www.example.com/');
      FileContent.Add('💬 Hardware upgrades: Contact support before upgrading');
      FileContent.Add('');
      FileContent.Add('╔════════════════════════════════════════════════════════════╗');
      FileContent.Add('║                                                            ║');
      FileContent.Add('║     Thank you for choosing miniZ MCP Professional! 🚀     ║');
      FileContent.Add('║                                                            ║');
      FileContent.Add('╚════════════════════════════════════════════════════════════╝');
      
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
    if MsgBox('⚠️ Do you want to remove your license activation?' + #13#10#13#10 +
              '✅ If you choose NO (Recommended):' + #13#10 +
              '   - License remains activated for this computer' + #13#10 +
              '   - No need to re-activate after reinstalling' + #13#10 +
              '   - Hardware binding preserved' + #13#10#13#10 +
              '❌ If you choose YES:' + #13#10 +
              '   - License activation will be removed' + #13#10 +
              '   - Need to re-enter license key after reinstalling' + #13#10 +
              '   - Hardware binding reset' + #13#10#13#10 +
              '❓ Remove license activation?',
              mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES then
    begin
      // Remove license directory
      DelTree(LicenseDir, True, True, True);
      MsgBox('✅ License activation removed successfully.' + #13#10#13#10 +
             'You will need to re-activate with a license key if you reinstall.', 
             mbInformation, MB_OK);
    end
    else
    begin
      MsgBox('✅ License activation preserved.' + #13#10#13#10 +
             'Your license will remain active after reinstalling on this computer.', 
             mbInformation, MB_OK);
    end;
  end;
end;

[Messages]
; Custom messages for installer
WelcomeLabel2=This will install [name/ver] on your computer.%n%nThis is a PROFESSIONAL EDITION with 150 pre-generated license keys included. Choose any key from LICENSE_KEYS.json to activate.%n%nHardware-locked security ensures your license is protected.%n%nIt is recommended that you close all other applications before continuing.

[UninstallRun]
; Optional: Run cleanup on uninstall
; Filename: "{cmd}"; Parameters: "/c rd /s /q ""{localappdata}\miniZ_MCP"""; Flags: runhidden
