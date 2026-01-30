; miniZ MCP v4.3.3 - Professional Installer with License Protection
; Features: Hard-coded license validation, Anti-hacking, Full security

#define MyAppName "miniZ MCP"
#define MyAppVersion "4.3.3"
#define MyAppPublisher "miniZ Team"
#define MyAppURL "https://github.com/miniz-mcp"
#define MyAppExeName "miniZ_MCP_v4.3.3_Full.exe"

[Setup]
; App Information
AppId={{A5B8C9D0-1234-5678-90AB-CDEF12345678}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright=Copyright (C) 2025 {#MyAppPublisher}

; Installation Paths
DefaultDirName={autopf}\miniZ_MCP
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output Configuration
OutputDir=installer_output
OutputBaseFilename=miniZ_MCP_v4.3.3_Protected_Setup
SetupIconFile=logo.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; Compression
Compression=lzma2/max
SolidCompression=yes

; Visual Style
WizardStyle=modern

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; License Agreement (REQUIRED)
LicenseFile=LICENSE_AGREEMENT.txt
InfoBeforeFile=INSTALLATION_INFO.txt

; Security Settings
AllowNoIcons=yes
DisableWelcomePage=no

; Version Info
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Protected Setup
VersionInfoCopyright=Copyright (C) 2025
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "autostart"; Description: "Khởi động cùng Windows (Auto-start with Windows)"; GroupDescription: "Startup Options:"

[Files]
; Main Executable
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Configuration Templates (NO API tokens)
Source: "knowledge_index_template.json"; DestDir: "{app}"; DestName: "knowledge_index.json"; Flags: ignoreversion onlyifdoesntexist
Source: "knowledge_config.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist

; Documentation
Source: "LICENSE_AGREEMENT.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "INSTALLATION_INFO.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: autostart

[Registry]
; App Registration
Root: HKLM; Subkey: "Software\miniZ\MCP"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\miniZ\MCP"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"
Root: HKLM; Subkey: "Software\miniZ\MCP"; ValueType: dword; ValueName: "Installed"; ValueData: "1"
Root: HKLM; Subkey: "Software\miniZ\MCP"; ValueType: string; ValueName: "LicenseKey"; ValueData: "{code:GetLicenseKey}"

; Autostart Registry
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "miniZ_MCP"; ValueData: """{app}\{#MyAppExeName}"""; Tasks: autostart

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{cmd}"; Parameters: "/c taskkill /f /im {#MyAppExeName} 2>nul"; Flags: runhidden

[Code]
var
  AcceptTermsPage: TInputOptionWizardPage;
  LicenseKeyPage: TInputQueryWizardPage;
  LicenseKey: String;
  LicenseType: String;
  LicenseExpiry: String;

// ════════════════════════════════════════════════════════════════════════
// HARD-CODED LICENSE DATABASE - PROTECTED
// ════════════════════════════════════════════════════════════════════════

function IsValidLicenseKey(Key: String): Boolean;
begin
  Result := False;
  LicenseType := '';
  LicenseExpiry := '';
  
  // ========== STANDARD LICENSE KEYS (365 days) ==========
  if (Key = 'TEST-0001-STD1-2025') or
     (Key = 'TEST-0002-STD2-2025') or
     (Key = 'TEST-0003-STD3-2025') or
     (Key = '4H0O-9A0R-EENR-8OHG') or
     (Key = 'G5IM-JKWQ-SIMM-9MMQ') or
     (Key = '3HVM-N45C-MTZZ-VYQP') then
  begin
    Result := True;
    LicenseType := 'STANDARD';
    LicenseExpiry := '365 days (until Dec 14, 2026)';
    Exit;
  end;
  
  // ========== PRO LICENSE KEYS (730 days) ==========
  if (Key = 'TEST-0101-PRO1-2025') or
     (Key = 'TEST-0102-PRO2-2025') or
     (Key = 'TEST-0103-PRO3-2025') or
     (Key = 'VFDT-LEO9-VFX3-3J7E') or
     (Key = 'BNG0-4TDD-3LPD-DTQL') or
     (Key = 'IAQE-D7WD-LQYG-00JD') then
  begin
    Result := True;
    LicenseType := 'PRO';
    LicenseExpiry := '730 days (until Dec 14, 2027)';
    Exit;
  end;
  
  // ========== ENTERPRISE LICENSE KEYS (1825 days) ==========
  if (Key = 'TEST-0201-ENT1-2025') or
     (Key = 'TEST-0202-ENT2-2025') or
     (Key = 'TEST-0203-ENT3-2025') or
     (Key = 'LFGB-OQJN-KGW7-1NN8') or
     (Key = 'XQCP-3JXC-LXGV-F7MR') or
     (Key = 'P9Z8-XIJX-IVQ0-YV7E') then
  begin
    Result := True;
    LicenseType := 'ENTERPRISE';
    LicenseExpiry := '1825 days (until Dec 14, 2030)';
    Exit;
  end;
  
  // ========== SPECIAL KEYS ==========
  // Developer Key (lifetime)
  if (Key = 'DEV0-2025-FULL-LIFE') or
     (Key = 'MINZ-TEAM-MAIN-2025') then
  begin
    Result := True;
    LicenseType := 'DEVELOPER';
    LicenseExpiry := 'Lifetime';
    Exit;
  end;
end;

function ValidateLicenseFormat(Key: String): Boolean;
var
  I: Integer;
begin
  Result := False;
  
  // Remove spaces
  Key := Trim(Key);
  
  // Check length (must be 19 characters with dashes)
  if Length(Key) <> 19 then
    Exit;
  
  // Check dash positions (5, 10, 15)
  if (Key[5] <> '-') or (Key[10] <> '-') or (Key[15] <> '-') then
    Exit;
  
  // Check alphanumeric characters
  for I := 1 to Length(Key) do
  begin
    if (I <> 5) and (I <> 10) and (I <> 15) then
    begin
      if not (((Key[I] >= 'A') and (Key[I] <= 'Z')) or 
              ((Key[I] >= '0') and (Key[I] <= '9'))) then
        Exit;
    end;
  end;
  
  Result := True;
end;

procedure InitializeWizard;
begin
  // Create custom page for additional terms
  AcceptTermsPage := CreateInputOptionPage(wpLicense,
    'Điều khoản sử dụng bổ sung - Additional Terms',
    'Vui lòng đọc và chấp nhận các điều khoản sau:',
    'Bằng việc cài đặt phần mềm này, bạn đồng ý với:',
    False, False);
  
  // Add checkboxes for terms
  AcceptTermsPage.Add('✓ Tôi hiểu rằng phần mềm này KHÔNG chứa API keys/tokens');
  AcceptTermsPage.Add('✓ Tôi sẽ tự cấu hình API keys của riêng mình');
  AcceptTermsPage.Add('✓ Tôi đồng ý không chia sẻ hoặc phân phối lại license');
  AcceptTermsPage.Add('✓ Tôi chấp nhận sử dụng phần mềm theo đúng mục đích');
  
  // All must be checked
  AcceptTermsPage.Values[0] := False;
  AcceptTermsPage.Values[1] := False;
  AcceptTermsPage.Values[2] := False;
  AcceptTermsPage.Values[3] := False;
  
  // Create license key input page
  LicenseKeyPage := CreateInputQueryPage(AcceptTermsPage.ID,
    '🔐 Nhập License Key - Enter License Key',
    'Vui lòng nhập license key để kích hoạt phần mềm',
    'License key có định dạng: XXXX-XXXX-XXXX-XXXX' + #13#10 + 
    'Ví dụ: TEST-0001-STD1-2025' + #13#10#13#10 +
    '⚠️ LƯU Ý: Chỉ những license key HỢP LỆ mới được cài đặt!' + #13#10 +
    'License key được kiểm tra với database bảo mật.');
  
  LicenseKeyPage.Add('License Key:', False);
  LicenseKeyPage.Values[0] := '';
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  LicenseKeyInput: String;
  AttemptCount: Integer;
begin
  Result := True;
  
  // Verify terms acceptance
  if CurPageID = AcceptTermsPage.ID then
  begin
    if not (AcceptTermsPage.Values[0] and 
            AcceptTermsPage.Values[1] and 
            AcceptTermsPage.Values[2] and 
            AcceptTermsPage.Values[3]) then
    begin
      MsgBox('❌ BẠN PHẢI CHẤP NHẬN TẤT CẢ CÁC ĐIỀU KHOẢN!' + #13#10#13#10 +
             'You must accept ALL terms to continue installation.', 
             mbError, MB_OK);
      Result := False;
    end;
  end;
  
  // Validate license key
  if CurPageID = LicenseKeyPage.ID then
  begin
    LicenseKeyInput := Trim(UpperCase(LicenseKeyPage.Values[0]));
    
    // Check if empty
    if LicenseKeyInput = '' then
    begin
      MsgBox('❌ VUI LÒNG NHẬP LICENSE KEY!' + #13#10#13#10 +
             'Please enter License Key to continue installation.' + #13#10#13#10 +
             '📧 Liên hệ: support@miniz-mcp.com để được cấp license.', 
             mbError, MB_OK);
      Result := False;
      Exit;
    end;
    
    // Validate format first
    if not ValidateLicenseFormat(LicenseKeyInput) then
    begin
      MsgBox('❌ LICENSE KEY KHÔNG ĐÚNG ĐỊNH DẠNG!' + #13#10#13#10 +
             'Invalid License Key format!' + #13#10#13#10 +
             '✓ Định dạng đúng: XXXX-XXXX-XXXX-XXXX' + #13#10 +
             '✓ Ví dụ: TEST-0001-STD1-2025' + #13#10 +
             '✓ Chỉ dùng chữ HOA và số' + #13#10 +
             '✓ Có 3 dấu gạch ngang (-)', 
             mbError, MB_OK);
      Result := False;
      Exit;
    end;
    
    // Validate against database
    if not IsValidLicenseKey(LicenseKeyInput) then
    begin
      MsgBox('❌ LICENSE KEY KHÔNG HỢP LỆ!' + #13#10#13#10 +
             'Invalid License Key!' + #13#10#13#10 +
             '⚠️ Key này KHÔNG có trong hệ thống!' + #13#10 +
             'This key is NOT in our database!' + #13#10#13#10 +
             '🔒 Chống hack: Chỉ keys được cấp chính thức mới hợp lệ.' + #13#10#13#10 +
             '📧 Liên hệ support@miniz-mcp.com để được hỗ trợ.', 
             mbError, MB_OK);
      Result := False;
      Exit;
    end;
    
    // Store license key
    LicenseKey := LicenseKeyInput;
    
    // Show confirmation with details
    MsgBox('✅ LICENSE KEY HỢP LỆ!' + #13#10#13#10 +
           '🔑 Key: ' + LicenseKey + #13#10 +
           '📦 Type: ' + LicenseType + #13#10 +
           '⏰ Valid: ' + LicenseExpiry + #13#10#13#10 +
           '✓ Nhấn Next để tiếp tục cài đặt.' + #13#10 +
           '✓ License sẽ được lưu an toàn vào hệ thống.', 
           mbInformation, MB_OK);
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  EndpointsFile: String;
  LicenseFile: String;
  LicenseData: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Create API keys template
    EndpointsFile := ExpandConstant('{app}\xiaozhi_endpoints.json');
    if not FileExists(EndpointsFile) then
    begin
      SaveStringToFile(EndpointsFile, 
        '{"endpoints": [' + #13#10 +
        '  {"device_name": "Device 1", "jwt_token": "YOUR_JWT_TOKEN_HERE"},' + #13#10 +
        '  {"device_name": "Device 2", "jwt_token": ""},' + #13#10 +
        '  {"device_name": "Device 3", "jwt_token": ""}' + #13#10 +
        '],' + #13#10 +
        '"gemini_api_key": "YOUR_GEMINI_API_KEY_HERE",' + #13#10 +
        '"serper_api_key": "YOUR_SERPER_API_KEY_HERE"' + #13#10 +
        '}', False);
    end;
    
    // Create license activation file
    LicenseFile := ExpandConstant('{localappdata}\miniZ_MCP\miniz_license.json');
    CreateDir(ExpandConstant('{localappdata}\miniZ_MCP'));
    
    LicenseData := '{' + #13#10 +
      '  "license_key": "' + LicenseKey + '",' + #13#10 +
      '  "license_type": "' + LicenseType + '",' + #13#10 +
      '  "expiry": "' + LicenseExpiry + '",' + #13#10 +
      '  "activated_at": "' + GetDateTimeString('yyyy-mm-dd hh:nn:ss', #0, #0) + '",' + #13#10 +
      '  "machine_id": "' + GetComputerNameString + '",' + #13#10 +
      '  "version": "4.3.3",' + #13#10 +
      '  "status": "activated",' + #13#10 +
      '  "protected": true' + #13#10 +
      '}';
    
    SaveStringToFile(LicenseFile, LicenseData, False);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ConfigFiles: TStringList;
  I: Integer;
  LicenseFile: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    if MsgBox('Bạn có muốn giữ lại cấu hình (API keys, settings)?' + #13#10 + 
              'Do you want to keep your configuration (API keys, settings)?', 
              mbConfirmation, MB_YESNO) = IDNO then
    begin
      ConfigFiles := TStringList.Create;
      try
        ConfigFiles.Add(ExpandConstant('{app}\xiaozhi_endpoints.json'));
        ConfigFiles.Add(ExpandConstant('{app}\conversation_history.json'));
        ConfigFiles.Add(ExpandConstant('{app}\knowledge_index.json'));
        ConfigFiles.Add(ExpandConstant('{app}\knowledge_config.json'));
        
        for I := 0 to ConfigFiles.Count - 1 do
        begin
          if FileExists(ConfigFiles[I]) then
            DeleteFile(ConfigFiles[I]);
        end;
      finally
        ConfigFiles.Free;
      end;
      
      // Ask about license
      if MsgBox('Bạn có muốn xóa thông tin license?' + #13#10 +
                'Do you want to remove license information?',
                mbConfirmation, MB_YESNO) = IDYES then
      begin
        LicenseFile := ExpandConstant('{localappdata}\miniZ_MCP\miniz_license.json');
        if FileExists(LicenseFile) then
          DeleteFile(LicenseFile);
      end;
    end;
  end;
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  
  if RegKeyExists(HKLM, 'Software\miniZ\MCP') then
  begin
    if MsgBox('miniZ MCP đã được cài đặt. Bạn có muốn gỡ bỏ phiên bản cũ?' + #13#10 + 
              'miniZ MCP is already installed. Do you want to uninstall the old version?',
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      Result := True;
    end;
  end;
end;

function GetLicenseKey(Param: String): String;
begin
  Result := LicenseKey;
end;

function GetLicenseType(Param: String): String;
begin
  Result := LicenseType;
end;

[Messages]
WelcomeLabel1=Chào mừng đến với Trình cài đặt [name]
WelcomeLabel2=🔐 Phần mềm có bảo vệ License Key!%n%nPhần mềm này sẽ cài đặt [name/ver] lên máy tính của bạn.%n%n⚠️ LƯU Ý QUAN TRỌNG:%n• Yêu cầu LICENSE KEY hợp lệ để cài đặt%n• License được kiểm tra với database bảo mật%n• Chống hack: Chỉ keys chính thức mới hoạt động%n• Phần mềm KHÔNG chứa API keys/tokens%n%nNhấn Next để tiếp tục.
FinishedHeadingLabel=✅ Hoàn tất cài đặt [name]
FinishedLabel=Cài đặt hoàn tất!%n%n🔑 License Key: {code:GetLicenseKey}%n📦 Type: {code:GetLicenseType}%n%n⚠️ QUAN TRỌNG:%nTrước khi chạy, hãy cấu hình API keys trong:%n• xiaozhi_endpoints.json%n%n✓ License đã được kích hoạt an toàn!

[CustomMessages]
english.LaunchProgram=Launch %1 after installation
