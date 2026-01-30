; miniZ MCP v4.3.3 - Professional Installer with Security
; Features: License agreement, No API token exposure, Auto-startup, Full terms

#define MyAppName "miniZ MCP"
#define MyAppVersion "4.3.3"
#define MyAppPublisher "miniZ Team"
#define MyAppURL "https://github.com/miniz-mcp"
#define MyAppExeName "miniZ_MCP_v4.3.3_Full.exe"

[Setup]
; App Information
AppId={{ECA8CBFB-B21D-3486-071B-F46ECCB7FA3C}
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
OutputBaseFilename=miniZ_MCP_v4.3.3_Secure_Setup
SetupIconFile=logo.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; Compression
Compression=lzma2/max
SolidCompression=yes

; Visual Style
WizardStyle=modern
; WizardImageFile=compiler:WizModernImage-IS.bmp
; WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; License Agreement (REQUIRED - User must accept)
LicenseFile=LICENSE_AGREEMENT.txt
InfoBeforeFile=INSTALLATION_INFO.txt

; Security Settings
; Disable modification of installation
AllowNoIcons=yes
DisableWelcomePage=no

; Version Info
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Professional Setup
VersionInfoCopyright=Copyright (C) 2025
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
; Name: "vietnamese"; MessagesFile: "compiler:Languages\Vietnamese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "autostart"; Description: "Khởi động cùng Windows (Auto-start with Windows)"; GroupDescription: "Startup Options:"
Name: "createshortcuts"; Description: "Tạo shortcuts trong Start Menu"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main Executable (v4.3.3 with all new features)
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Configuration Templates (WITHOUT API tokens)
Source: "knowledge_index_template.json"; DestDir: "{app}"; DestName: "knowledge_index.json"; Flags: ignoreversion onlyifdoesntexist
Source: "knowledge_config.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist

; Documentation
Source: "LICENSE_AGREEMENT.txt"; DestDir: "{app}"; Flags: ignoreversion
; Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "INSTALLATION_INFO.txt"; DestDir: "{app}"; Flags: ignoreversion
; Source: "CUSTOMER_README.md"; DestDir: "{app}"; Flags: ignoreversion

; SECURITY: Exclude files containing API tokens/keys
; NOT INCLUDED:
; - xiaozhi_endpoints.json (contains JWT tokens)
; - .env (environment variables)
; - conversation_history.json (user data)
; - license_database.json (license keys)
; - LICENSE_KEYS.txt (activation keys)
; - Any *_token.txt or *_key.txt files

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

; Autostart Registry (if user selected)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "miniZ_MCP"; ValueData: """{app}\{#MyAppExeName}"""; Tasks: autostart

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Stop running process before uninstall
Filename: "{cmd}"; Parameters: "/c taskkill /f /im {#MyAppExeName} 2>nul"; Flags: runhidden

[Code]
var
  AcceptTermsPage: TInputOptionWizardPage;
  LicenseKeyPage: TInputQueryWizardPage;
  LicenseKey: String;
  
procedure InitializeWizard;
begin
  // Create custom page for additional terms
  AcceptTermsPage := CreateInputOptionPage(wpLicense,
    'Điều khoản sử dụng bổ sung - Additional Terms',
    'Vui lòng đọc và chấp nhận các điều khoản sau:',
    'Bằng việc cài đặt phần mềm này, bạn đồng ý với:',
    False, False);
  
  // Add checkboxes for terms
  AcceptTermsPage.Add('Tôi hiểu rằng phần mềm này KHÔNG chứa API keys/tokens');
  AcceptTermsPage.Add('Tôi sẽ tự cấu hình API keys của riêng mình');
  AcceptTermsPage.Add('Tôi đồng ý không chia sẻ hoặc phân phối lại license');
  AcceptTermsPage.Add('Tôi chấp nhận sử dụng phần mềm theo đúng mục đích');
  
  // All must be checked
  AcceptTermsPage.Values[0] := False;
  AcceptTermsPage.Values[1] := False;
  AcceptTermsPage.Values[2] := False;
  AcceptTermsPage.Values[3] := False;
  
  // Create license key input page
  LicenseKeyPage := CreateInputQueryPage(AcceptTermsPage.ID,
    'Nhập License Key - Enter License Key',
    'Vui lòng nhập license key để kích hoạt phần mềm',
    'License key có định dạng: XXXX-XXXX-XXXX-XXXX' + #13#10 + 
    'Nếu chưa có, hãy liên hệ support để được cấp license.');
  
  LicenseKeyPage.Add('License Key:', False);
  LicenseKeyPage.Values[0] := '';
end;

function ValidateLicenseKey(Key: String): Boolean;
var
  I: Integer;
  DashCount: Integer;
begin
  Result := False;
  
  // Remove spaces
  Key := Trim(Key);
  
  // Check format: XXXX-XXXX-XXXX-XXXX (19 characters)
  if Length(Key) <> 19 then
    Exit;
  
  // Check dash positions (4, 9, 14)
  if (Key[5] <> '-') or (Key[10] <> '-') or (Key[15] <> '-') then
    Exit;
  
  // Check other characters are alphanumeric
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

function NextButtonClick(CurPageID: Integer): Boolean;
var
  LicenseKeyInput: String;
begin
  Result := True;
  
  if CurPageID = AcceptTermsPage.ID then
  begin
    // Verify all terms are accepted
    if not (AcceptTermsPage.Values[0] and 
            AcceptTermsPage.Values[1] and 
            AcceptTermsPage.Values[2] and 
            AcceptTermsPage.Values[3]) then
    begin
      MsgBox('Bạn phải chấp nhận TẤT CẢ các điều khoản để tiếp tục cài đặt.' + #13#10 + 
             'You must accept ALL terms to continue installation.', 
             mbError, MB_OK);
      Result := False;
    end;
  end;
  
  if CurPageID = LicenseKeyPage.ID then
  begin
    LicenseKeyInput := Trim(LicenseKeyPage.Values[0]);
    
    // Check if license key is empty
    if LicenseKeyInput = '' then
    begin
      MsgBox('Vui lòng nhập License Key để tiếp tục cài đặt.' + #13#10 + 
             'Please enter License Key to continue installation.' + #13#10#13#10 +
             'Liên hệ support@miniz-mcp.com để được cấp license.', 
             mbError, MB_OK);
      Result := False;
      Exit;
    end;
    
    // Validate license key format
    if not ValidateLicenseKey(LicenseKeyInput) then
    begin
      MsgBox('License Key không đúng định dạng!' + #13#10 + 
             'Invalid License Key format!' + #13#10#13#10 +
             'Định dạng đúng: XXXX-XXXX-XXXX-XXXX' + #13#10 +
             'Ví dụ: AB12-CD34-EF56-GH78', 
             mbError, MB_OK);
      Result := False;
      Exit;
    end;
    
    // Store license key
    LicenseKey := LicenseKeyInput;
    
    // Show confirmation
    MsgBox('License Key hợp lệ!' + #13#10 + 
           'Valid License Key!' + #13#10#13#10 +
           'Key: ' + LicenseKey + #13#10#13#10 +
           'Nhấn Next để tiếp tục cài đặt.', 
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
    // Create empty endpoints file with template
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
    
    // Create license file with activation info
    LicenseFile := ExpandConstant('{localappdata}\miniZ_MCP\miniz_license.json');
    CreateDir(ExpandConstant('{localappdata}\miniZ_MCP'));
    
    LicenseData := '{' + #13#10 +
      '  "license_key": "' + LicenseKey + '",' + #13#10 +
      '  "activated_at": "' + GetDateTimeString('yyyy-mm-dd hh:nn:ss', #0, #0) + '",' + #13#10 +
      '  "version": "4.3.3",' + #13#10 +
      '  "status": "pending_activation"' + #13#10 +
      '}';
    
    SaveStringToFile(LicenseFile, LicenseData, False);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ConfigFiles: TStringList;
  I: Integer;
  ResultCode: Integer;
  LicenseFile: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Ask user if they want to keep configuration
    if MsgBox('Bạn có muốn giữ lại cấu hình (API keys, settings)?' + #13#10 + 
              'Do you want to keep your configuration (API keys, settings)?', 
              mbConfirmation, MB_YESNO) = IDNO then
    begin
      // Delete configuration files
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
      
      // Ask about license file
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
  
  // Check if already installed
  if RegKeyExists(HKLM, 'Software\miniZ\MCP') then
  begin
    if MsgBox('miniZ MCP đã được cài đặt. Bạn có muốn gỡ bỏ phiên bản cũ?' + #13#10 + 
              'miniZ MCP is already installed. Do you want to uninstall the old version?',
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      // User will need to manually uninstall first
      Result := True;
    end;
  end;
end;

function GetLicenseKey(Param: String): String;
begin
  Result := LicenseKey;
end;

[Messages]
WelcomeLabel1=Chào mừng đến với Trình cài đặt [name]
WelcomeLabel2=Phần mềm này sẽ cài đặt [name/ver] lên máy tính của bạn.%n%nLƯU Ý QUAN TRỌNG:%n• Phần mềm KHÔNG chứa API keys/tokens%n• Bạn cần cấu hình API keys của riêng mình%n• Đọc kỹ điều khoản trước khi cài đặt%n• License key bắt buộc để kích hoạt%n%nNhấn Next để tiếp tục.
FinishedHeadingLabel=Hoàn tất cài đặt [name]
FinishedLabelNoIcons=Cài đặt [name] hoàn tất.%n%nLICENSE KEY: {code:GetLicenseKey}%n%nCẤU HÌNH TIẾP THEO:%n1. Mở file: xiaozhi_endpoints.json%n2. Thêm JWT tokens của bạn%n3. Thêm Gemini API key%n4. Thêm Serper API key%n5. Khởi động ứng dụng
FinishedLabel=Cài đặt hoàn tất!%n%nLicense Key: {code:GetLicenseKey}%n%n⚠️ QUAN TRỌNG:%nTrước khi chạy, hãy cấu hình API keys trong xiaozhi_endpoints.json

[CustomMessages]
english.LaunchProgram=Launch %1 after installation
; vietnamese.LaunchProgram=Khởi động %1 sau khi cài đặt
