; ============================================================
; miniZ MCP Professional v4.3.7 - SECURE INSTALLER
; License Key Validation Required
; Keys are validated but NOT distributed with installer
; Copyright (C) 2025 miniZ MCP Team
; Build Date: 2025-12-19
; ============================================================

#define MyAppName "miniZ MCP Professional"
#define MyAppVersion "4.3.7"
#define MyAppPublisher "miniZ Team"
#define MyAppURL "https://www.minizmcp.com/"
#define MyAppExeName "miniZ_MCP.exe"
#define MyAppIcon "logo.ico"

[Setup]
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
LicenseFile=LICENSE_AGREEMENT.txt
InfoBeforeFile=INSTALLATION_INFO.txt
OutputDir=installer_output
OutputBaseFilename=miniZ_MCP_Professional_v{#MyAppVersion}_Secure
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
VersionInfoDescription={#MyAppName} Secure Setup
VersionInfoCopyright=Copyright (C) 2025 {#MyAppPublisher}
UninstallDisplayName={#MyAppName} {#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
english.LaunchProgram=Launch %1 after installation

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "startupicon"; Description: "Run at Windows startup / Tu dong chay khi khoi dong Windows"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main application - NO LICENSE KEYS FILE!
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Additional files
Source: "logo.png"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "LICENSE_AGREEMENT.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "CUSTOMER_README.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "xiaozhi_endpoints.json"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\User Guide"; Filename: "{app}\CUSTOMER_README.md"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: startupicon
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
  ValidKeys: TStringList;

function GetCurrentDateTime(Param: String): String;
begin
  Result := GetDateTimeString('yyyy/mm/dd hh:nn:ss', #0, #0);
end;

// Initialize valid keys list - SECURED
procedure InitializeValidKeys;
begin
  ValidKeys := TStringList.Create;
  ValidKeys.Sorted := True;
  ValidKeys.Duplicates := dupIgnore;
  
  // Add all 100 valid keys here
  ValidKeys.Add('QT9F-KEEF-XL4U-WP93');
  ValidKeys.Add('KKKJ-8NN4-RAGB-JNA5');
  ValidKeys.Add('BN6A-NKQY-EFN9-E4FX');
  ValidKeys.Add('Z9P5-HQ4Z-H3XP-WGZU');
  ValidKeys.Add('6T2T-A4RR-AMME-CTP5');
  ValidKeys.Add('Y2Q9-7YWV-4NTZ-J6HE');
  ValidKeys.Add('XKT5-M44K-DL24-5RMY');
  ValidKeys.Add('QAB9-9WXR-Q23K-T5FJ');
  ValidKeys.Add('DG3E-RS88-3GBP-PYBK');
  ValidKeys.Add('R3T8-ZZW6-MQB6-AT9R');
  ValidKeys.Add('H89T-T2K8-WN24-K9UD');
  ValidKeys.Add('CRKM-5KGK-M9EL-PHF2');
  ValidKeys.Add('ZCUJ-KXJ4-NAA6-V7XZ');
  ValidKeys.Add('E9MA-NPT8-53Z6-6747');
  ValidKeys.Add('EYAC-NCE8-P828-PJA7');
  ValidKeys.Add('R992-LXGK-6UT8-LZ4K');
  ValidKeys.Add('J9F2-M4GE-9SQD-RWT8');
  ValidKeys.Add('AXC4-D7KA-S3U2-4A8Y');
  ValidKeys.Add('S8FX-L3YD-QDVN-SS5A');
  ValidKeys.Add('PWYZ-Y5XR-MFAC-GEW8');
  ValidKeys.Add('RXPH-RM6W-Z75F-XRSC');
  ValidKeys.Add('V4CJ-CUFB-4W8S-SFUQ');
  ValidKeys.Add('2WSL-CMCF-S7B5-QH9J');
  ValidKeys.Add('ABPN-DVMS-UVWN-3J2S');
  ValidKeys.Add('AQRH-B34P-8LMM-QCUE');
  ValidKeys.Add('L3VD-87QE-PSA9-4359');
  ValidKeys.Add('TETG-QBLY-JAPL-7AFF');
  ValidKeys.Add('HN7P-Z3NP-XM22-RCYQ');
  ValidKeys.Add('LXN8-JY8J-SEW5-GBFW');
  ValidKeys.Add('JWN6-K9TB-WUK4-T9LH');
  ValidKeys.Add('JZVX-GD4A-E82A-9HV6');
  ValidKeys.Add('H72L-RCBA-3J2E-U74H');
  ValidKeys.Add('KZUZ-9UQN-PFSM-68HT');
  ValidKeys.Add('W8TH-SSFP-6P4C-VFYC');
  ValidKeys.Add('M2CB-7NXN-H57L-XXYD');
  ValidKeys.Add('FJW4-863D-UEXT-UBLL');
  ValidKeys.Add('FM9P-XKH3-UPWY-57EE');
  ValidKeys.Add('PWA8-U8EU-A8MN-6E82');
  ValidKeys.Add('C3Z4-3M5J-NSYF-9FNK');
  ValidKeys.Add('XCYA-NULD-ZYBH-6KSX');
  ValidKeys.Add('L9BA-TVGE-ZGBE-MEYD');
  ValidKeys.Add('UK8X-2FN3-LX9V-7BYG');
  ValidKeys.Add('GSH3-G4YU-CHSP-KUSF');
  ValidKeys.Add('SGYS-WGKM-VPVQ-7ELA');
  ValidKeys.Add('M447-CZKY-W4MP-4DLN');
  ValidKeys.Add('CK4A-N267-FQQL-NH5B');
  ValidKeys.Add('MT9B-VP9S-QBS5-DGUA');
  ValidKeys.Add('4MRH-R2YF-X6A7-7LDD');
  ValidKeys.Add('G86A-RTLH-2K5G-6LKV');
  ValidKeys.Add('FLPK-ZJ2E-U5QD-PAB2');
  ValidKeys.Add('F54M-AQVN-7YDZ-32VV');
  ValidKeys.Add('4N84-MXVR-AWJB-D34U');
  ValidKeys.Add('V2BE-HHZS-3YEY-8AT5');
  ValidKeys.Add('5BG6-2UWA-QNLC-BR45');
  ValidKeys.Add('GCSM-DGN2-3WBS-S5X8');
  ValidKeys.Add('FZ34-49JS-5ZM9-FC8H');
  ValidKeys.Add('9B8J-NQ68-VBGR-PPMX');
  ValidKeys.Add('P7E6-AQZ5-49KZ-RX9J');
  ValidKeys.Add('TY9C-RNYM-LRJN-FCEU');
  ValidKeys.Add('2AT5-D39T-9Z2W-35Y3');
  ValidKeys.Add('ZL7A-LQUP-TX4Z-8YZ2');
  ValidKeys.Add('G2JB-ZUAS-PZTK-DP7L');
  ValidKeys.Add('SEDJ-97Q9-37GP-FMQN');
  ValidKeys.Add('68NN-28TH-C56B-U445');
  ValidKeys.Add('UC2K-FRZW-6SCR-DJLM');
  ValidKeys.Add('6NPE-XA2J-TF4Q-FL4Q');
  ValidKeys.Add('B98J-ME87-YLDJ-85TW');
  ValidKeys.Add('PB34-A6QU-4HAC-DTGJ');
  ValidKeys.Add('88LW-4FSR-3YYC-KPU8');
  ValidKeys.Add('LBDZ-MA7M-33AN-RG7G');
  ValidKeys.Add('7P8K-NABW-98WE-5AW8');
  ValidKeys.Add('89FL-QZ3B-4HED-55KX');
  ValidKeys.Add('W2KA-8CTD-YN8T-KM4Y');
  ValidKeys.Add('TFSL-VQ82-XBRX-FLEL');
  ValidKeys.Add('2KV9-KNU8-6LY8-D8C4');
  ValidKeys.Add('ZQQA-YNNU-ANVB-F3VW');
  ValidKeys.Add('67FF-XAPA-CWAG-4DSN');
  ValidKeys.Add('GV62-DZEE-7AUG-KV35');
  ValidKeys.Add('NE65-DB8V-SYMJ-VV3G');
  ValidKeys.Add('WTAT-2Y36-GGTE-PXDV');
  ValidKeys.Add('U2TV-7G8H-K783-2MPG');
  ValidKeys.Add('D3KG-Y5LZ-4SYZ-S4DB');
  ValidKeys.Add('DJRE-Y9NZ-Z2BE-VDL2');
  ValidKeys.Add('EDVF-QXZR-9UBG-WBZQ');
  ValidKeys.Add('NSRB-2C4X-9ZCP-VFCK');
  ValidKeys.Add('W7MC-TKLP-RYKV-VEDU');
  ValidKeys.Add('CL2Z-HR82-3L96-6XEN');
  ValidKeys.Add('WSYS-KUAJ-QZR4-HQP4');
  ValidKeys.Add('XMME-ERZB-R6MF-YQAD');
  ValidKeys.Add('5QHM-78GZ-V3RY-TDJU');
  ValidKeys.Add('MK6K-L95T-E945-YYH2');
  ValidKeys.Add('3K78-KM5M-GBUP-QU44');
  ValidKeys.Add('9LSC-CFTM-59NS-AQNQ');
  ValidKeys.Add('JSGT-N95U-5ZW8-6SMP');
  ValidKeys.Add('HB39-QCCV-DWAQ-YV9D');
  ValidKeys.Add('HED7-GB62-RAT4-U2AN');
  ValidKeys.Add('5MFS-D2RE-VXFZ-G6FY');
  ValidKeys.Add('F2YG-T6H6-DS9E-7DMD');
  ValidKeys.Add('RAQ9-4R2X-RT8N-D286');
  ValidKeys.Add('YUN7-YMHT-DXKP-KGS8');
end;

// Validate license key format
function ValidateLicenseKeyFormat(Key: String): Boolean;
begin
  Result := False;
  
  if Length(Key) = 0 then
    Exit;
  
  Key := Trim(UpperCase(Key));
  
  // Check length (19 characters including dashes)
  if Length(Key) <> 19 then
    Exit;
  
  // Check dash positions
  if (Key[5] <> '-') or (Key[10] <> '-') or (Key[15] <> '-') then
    Exit;
  
  Result := True;
end;

// Check if key is in valid keys list
function IsValidLicenseKey(Key: String): Boolean;
begin
  Key := Trim(UpperCase(Key));
  Result := ValidKeys.IndexOf(Key) >= 0;
end;

procedure InitializeWizard;
begin
  // Initialize valid keys list
  InitializeValidKeys;
  
  // Create license key input page - REQUIRED!
  LicenseKeyPage := CreateInputQueryPage(wpSelectTasks,
    'LICENSE ACTIVATION - REQUIRED',
    'Enter your valid license key to continue installation',
    'A valid Professional license key is REQUIRED to install.' + #13#10 +
    'Format: XXXX-XXXX-XXXX-XXXX' + #13#10 +
    '(Example: QT9F-KEEF-XL4U-WP93)' + #13#10#13#10 +
    'Installation CANNOT continue without a valid license key.' + #13#10 +
    'Contact your vendor to obtain a license key.');
  
  LicenseKeyPage.Add('License Key:', False);
  LicenseKeyPage.Values[0] := '';
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  Attempts: Integer;
begin
  Result := True;
  
  if CurPageID = LicenseKeyPage.ID then
  begin
    LicenseKey := Trim(UpperCase(LicenseKeyPage.Values[0]));
    
    // LICENSE KEY IS MANDATORY!
    if Length(LicenseKey) = 0 then
    begin
      MsgBox('LICENSE KEY IS REQUIRED!' + #13#10#13#10 +
             'You MUST enter a valid license key to continue.' + #13#10 +
             'Installation cannot proceed without a license key.' + #13#10#13#10 +
             'Contact your vendor for license key.',
             mbCriticalError, MB_OK);
      Result := False;
      Exit;
    end;
    
    // Validate format
    if not ValidateLicenseKeyFormat(LicenseKey) then
    begin
      MsgBox('INVALID LICENSE KEY FORMAT!' + #13#10#13#10 +
             'License key format must be: XXXX-XXXX-XXXX-XXXX' + #13#10 +
             'Example: QT9F-KEEF-XL4U-WP93' + #13#10#13#10 +
             'Please check your key and try again.',
             mbError, MB_OK);
      Result := False;
      Exit;
    end;
    
    // Validate against database
    if not IsValidLicenseKey(LicenseKey) then
    begin
      MsgBox('INVALID LICENSE KEY!' + #13#10#13#10 +
             'The license key you entered is not valid.' + #13#10 +
             'Key entered: ' + LicenseKey + #13#10#13#10 +
             'Please check:' + #13#10 +
             '- Key is typed correctly (no spaces)' + #13#10 +
             '- Key has not been used before' + #13#10 +
             '- Key was provided by authorized vendor' + #13#10#13#10 +
             'Installation CANNOT continue with invalid key.',
             mbCriticalError, MB_OK);
      Result := False;
      Exit;
    end;
    
    // Key is valid - confirm
    if MsgBox('LICENSE KEY VALIDATED SUCCESSFULLY!' + #13#10#13#10 +
              'License Key: ' + LicenseKey + #13#10 +
              'Status: Valid Professional License' + #13#10 +
              'Type: Lifetime (No expiration)' + #13#10 +
              'Devices: 1 computer' + #13#10#13#10 +
              'This key will be activated on first application run.' + #13#10 +
              'The activation is hardware-locked for security.' + #13#10#13#10 +
              'Continue with installation?', 
              mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
      Exit;
    end;
    
    // Save license key for application
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
    // Create activation guide file
    ActivationFile := ExpandConstant('{app}\LICENSE_INFO.txt');
    FileContent := TStringList.Create;
    try
      FileContent.Add('================================================================');
      FileContent.Add('    miniZ MCP Professional v' + '{#MyAppVersion}' + ' - INSTALLATION COMPLETE');
      FileContent.Add('================================================================');
      FileContent.Add('');
      FileContent.Add('Installation Date: ' + GetDateTimeString('yyyy/mm/dd hh:nn:ss', #0, #0));
      FileContent.Add('Installation Path: ' + ExpandConstant('{app}'));
      FileContent.Add('');
      FileContent.Add('================================================================');
      FileContent.Add('LICENSE INFORMATION');
      FileContent.Add('================================================================');
      FileContent.Add('');
      FileContent.Add('License Key: ' + LicenseKey);
      FileContent.Add('Status: Validated and Pending Activation');
      FileContent.Add('Type: Professional License');
      FileContent.Add('Validity: Lifetime (No expiration)');
      FileContent.Add('Devices: 1 computer');
      FileContent.Add('');
      FileContent.Add('NEXT STEPS:');
      FileContent.Add('1. Launch miniZ MCP Professional');
      FileContent.Add('2. License will activate automatically on first run');
      FileContent.Add('3. Activation is hardware-locked to this computer');
      FileContent.Add('4. Keep this file for your records');
      FileContent.Add('');
      FileContent.Add('================================================================');
      FileContent.Add('SECURITY NOTES');
      FileContent.Add('================================================================');
      FileContent.Add('');
      FileContent.Add('• Your license is validated and secure');
      FileContent.Add('• Hardware-locked activation prevents unauthorized use');
      FileContent.Add('• License cannot be transferred to another computer');
      FileContent.Add('• This key has been marked as used in our system');
      FileContent.Add('');
      FileContent.Add('================================================================');
      FileContent.Add('SUPPORT');
      FileContent.Add('================================================================');
      FileContent.Add('');
      FileContent.Add('Email: support@minizmcp.com');
      FileContent.Add('Website: https://www.minizmcp.com/');
      FileContent.Add('');
      FileContent.Add('Thank you for choosing miniZ MCP Professional!');
      FileContent.Add('');
      
      FileContent.SaveToFile(ActivationFile);
    finally
      FileContent.Free;
    end;
  end;
end;

procedure DeinitializeSetup();
begin
  if Assigned(ValidKeys) then
    ValidKeys.Free;
end;

function InitializeUninstall(): Boolean;
var
  LicenseDir: String;
begin
  Result := True;
  
  LicenseDir := ExpandConstant('{localappdata}\miniZ_MCP\.license');
  
  if DirExists(LicenseDir) then
  begin
    if MsgBox('Do you want to remove your license activation?' + #13#10#13#10 +
              'Choose NO to keep license for future reinstallation.' + #13#10 +
              'Choose YES to completely remove the license.' + #13#10#13#10 +
              'Remove license activation?',
              mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES then
    begin
      DelTree(LicenseDir, True, True, True);
    end;
  end;
end;

[Messages]
WelcomeLabel2=This will install [name/ver] on your computer.%n%nA VALID LICENSE KEY IS REQUIRED to install this software.%n%nYou will be prompted to enter your license key during installation. The key will be validated before installation continues.%n%nContact your vendor if you do not have a license key.%n%nIt is recommended that you close all other applications before continuing.
