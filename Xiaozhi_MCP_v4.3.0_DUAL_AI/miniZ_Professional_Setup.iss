; ============================================================
; miniZ MCP v4.3.0 - Professional Windows Installer
; Inno Setup Script - Enterprise Grade Installation
; ============================================================

#define MyAppName "miniZ MCP"
#define MyAppVersion "4.3.2"
#define MyAppPublisher "miniZ MCP Team"
#define MyAppURL "https://miniz-mcp.com"
#define MyAppExeName "START.bat"
#define MyAppDescription "MCP Server with AI Integration"

[Setup]
; ========== Application Identity ==========
AppId={{B8E9D4F2-7C3A-4E1B-9F2D-8A5C6E7D9F1B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/support
AppUpdatesURL={#MyAppURL}/updates
AppCopyright=Copyright (C) 2024-2025 miniZ MCP Team
VersionInfoVersion=4.3.2.0
VersionInfoCompany=miniZ MCP Team
VersionInfoDescription={#MyAppDescription}
VersionInfoTextVersion=4.3.2 Professional (AI Knowledge Base)

; ========== Installation Paths ==========
DefaultDirName={autopf}\miniZ_MCP
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=no

; ========== Output Settings ==========
OutputDir=installer_output
OutputBaseFilename=miniZ_MCP_v4.3.2_Professional_Setup
SetupIconFile=logo.ico
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMADictionarySize=65536
InternalCompressLevel=ultra64

; ========== User Interface ==========
WizardStyle=modern
WizardSizePercent=120,110
WizardImageFile=compiler:WizModernImage.bmp
WizardSmallImageFile=compiler:WizModernSmallImage.bmp

; ========== License & Documentation ==========
LicenseFile=LICENSE_VI.txt
InfoBeforeFile=README_INSTALL.txt
InfoAfterFile=POST_INSTALL_INFO.txt

; ========== Privileges & Security ==========
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
SignedUninstaller=no

; ========== Uninstall Settings ==========
UninstallDisplayIcon={app}\logo.ico
UninstallDisplayName={#MyAppName} v{#MyAppVersion}
UninstallFilesDir={app}\uninstall

; ========== Misc Settings ==========
AllowNoIcons=yes
DisableWelcomePage=no
DisableReadyPage=no
DisableFinishedPage=no
ShowLanguageDialog=no
CloseApplications=yes
RestartApplications=no
SetupLogging=yes
MinVersion=10.0

[Languages]
Name: "vietnamese"; MessagesFile: "compiler:Default.isl"; LicenseFile: "LICENSE_VI.txt"

[CustomMessages]
vietnamese.NameAndVersion=%1 phiên bản %2
vietnamese.AdditionalIcons=Tùy chọn shortcuts:
vietnamese.CreateDesktopIcon=Tạo shortcut trên Desktop
vietnamese.CreateQuickLaunchIcon=Tạo shortcut Quick Launch
vietnamese.ProgramOnTheWeb=%1 trên Web
vietnamese.UninstallProgram=Gỡ cài đặt %1
vietnamese.LaunchProgram=Khởi động %1
vietnamese.AssocFileExtension=Liên kết %1 với định dạng %2
vietnamese.AssocingFileExtension=Đang liên kết %1 với định dạng %2...
vietnamese.AutoStartProgram=Tự động khởi động cùng Windows
vietnamese.ConfigureStartup=Cấu hình khởi động cùng hệ thống

[Tasks]
Name: "desktopicon"; Description: "🖥️ Tạo shortcut trên Desktop"; GroupDescription: "Shortcuts:"
Name: "quicklaunchicon"; Description: "⚡ Tạo Quick Launch icon"; GroupDescription: "Shortcuts:"; Flags: unchecked
Name: "startmenu"; Description: "📋 Thêm vào Start Menu"; GroupDescription: "Shortcuts:"
Name: "autostart"; Description: "🚀 Tự động khởi động cùng Windows"; GroupDescription: "Tùy chọn nâng cao:"; Flags: unchecked

[Files]
; ========== Core Application ==========
Source: "xiaozhi_final.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "rag_system.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "security_module.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "startup_manager.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "tray_app.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "license_manager.py"; DestDir: "{app}"; Flags: ignoreversion

; ========== Launch Scripts ==========
Source: "START.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "START_HIDDEN.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "CHECK.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "INSTALL.bat"; DestDir: "{app}"; Flags: ignoreversion

; ========== Configuration ==========
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "xiaozhi_endpoints.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "xiaozhi_endpoints_template.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "knowledge_config.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist skipifsourcedoesntexist
Source: "knowledge_index_template.json"; DestDir: "{app}"; DestName: "knowledge_index.json"; Flags: ignoreversion onlyifdoesntexist
Source: "rag_config.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist skipifsourcedoesntexist
Source: "youtube_playlists.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist skipifsourcedoesntexist

; ========== Documentation ==========
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "QUICKSTART.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "CHANGELOG.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "GEMINI_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "GPT4_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "MUSIC_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "RAG_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "VLC_INSTALL_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "HUONG_DAN_THONG_TIN_MOI.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; ========== License Files ==========
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE_VI.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE_AGREEMENT.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "DISCLAIMER.md"; DestDir: "{app}"; Flags: ignoreversion

; ========== Post Install Info ==========
Source: "POST_INSTALL_INFO.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "README_INSTALL.txt"; DestDir: "{app}"; Flags: ignoreversion

; ========== Icon ==========
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "logo.png"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; ========== Music Library ==========
Source: "music_library\*"; DestDir: "{app}\music_library"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
; ========== App Directories ==========
Name: "{app}\logs"; Flags: uninsneveruninstall
Name: "{app}\data"; Flags: uninsneveruninstall
Name: "{app}\cache"; Flags: uninsneveruninstall
Name: "{app}\knowledge_base"; Flags: uninsneveruninstall
Name: "{app}\backups"; Flags: uninsneveruninstall

; ========== User Data in AppData (persistent across reinstalls) ==========
Name: "{localappdata}\miniZ_MCP"; Flags: uninsneveruninstall
Name: "{localappdata}\miniZ_MCP\conversations"; Flags: uninsneveruninstall
Name: "{localappdata}\miniZ_MCP\user_profiles"; Flags: uninsneveruninstall
Name: "{localappdata}\miniZ_MCP\task_memory"; Flags: uninsneveruninstall
Name: "{localappdata}\miniZ_MCP\rag_cache"; Flags: uninsneveruninstall
Name: "{localappdata}\miniZ_MCP\config"; Flags: uninsneveruninstall

; ========== Documents folder for exports ==========
Name: "{userdocs}\miniZ_Conversations"; Flags: uninsneveruninstall

[Icons]
; ========== Start Menu ==========
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\logo.ico"; Comment: "Khởi động miniZ MCP Server"; Tasks: startmenu
Name: "{group}\{#MyAppName} (Hidden)"; Filename: "{app}\START_HIDDEN.bat"; WorkingDir: "{app}"; IconFilename: "{app}\logo.ico"; Comment: "Khởi động miniZ MCP ẩn"; Tasks: startmenu
Name: "{group}\Kiểm tra cài đặt"; Filename: "{app}\CHECK.bat"; WorkingDir: "{app}"; Comment: "Kiểm tra dependencies"; Tasks: startmenu
Name: "{group}\Hướng dẫn sử dụng"; Filename: "{app}\QUICKSTART.md"; Comment: "Tài liệu hướng dẫn"; Tasks: startmenu
Name: "{group}\Gỡ cài đặt {#MyAppName}"; Filename: "{uninstallexe}"; IconFilename: "{app}\logo.ico"; Tasks: startmenu

; ========== Desktop ==========
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\logo.ico"; Comment: "miniZ MCP Server"; Tasks: desktopicon

; ========== Quick Launch ==========
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\logo.ico"; Tasks: quicklaunchicon

[Registry]
; ========== Auto Start ==========
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "miniZ_MCP"; ValueData: """{app}\START_HIDDEN.bat"""; Flags: uninsdeletevalue; Tasks: autostart

; ========== App Registration ==========
Root: HKLM; Subkey: "Software\miniZ_MCP"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\miniZ_MCP"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\miniZ_MCP"; ValueType: string; ValueName: "InstallDate"; ValueData: "{code:GetInstallDate}"; Flags: uninsdeletekey

[Run]
; ========== Post-Install Actions ==========
Filename: "{app}\POST_INSTALL_INFO.txt"; Description: "📖 Xem hướng dẫn sau cài đặt"; Flags: postinstall shellexec skipifsilent unchecked nowait
Filename: "{win}\explorer.exe"; Parameters: """{app}"""; Description: "📂 Mở thư mục cài đặt"; Flags: postinstall skipifsilent nowait unchecked
Filename: "{app}\{#MyAppExeName}"; Description: "🚀 Khởi động {#MyAppName} ngay"; Flags: postinstall skipifsilent nowait; WorkingDir: "{app}"

[UninstallRun]
; ========== Pre-Uninstall Actions ==========
Filename: "taskkill"; Parameters: "/F /IM python.exe /T"; Flags: runhidden; RunOnceId: "KillPython"

[UninstallDelete]
; ========== Cleanup (App folder only - keep user data in AppData) ==========
Type: files; Name: "{app}\.license_key"
Type: files; Name: "{app}\license_info.json"
Type: files; Name: "{app}\*.pyc"
Type: files; Name: "{app}\*.log"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\cache"
Type: filesandordirs; Name: "{app}\logs"
; NOTE: Conversation history in {localappdata}\miniZ_MCP is PRESERVED
; User can manually delete if needed

[Code]
var
  LicenseKeyPage: TInputQueryWizardPage;
  LicenseKey: String;
  
function GetInstallDate(Param: String): String;
begin
  Result := GetDateTimeString('yyyy-mm-dd hh:nn:ss', #0, #0);
end;

function ValidateLicenseKey(Key: String): Boolean;
var
  i, dashCount: Integer;
begin
  Result := False;
  
  // Check length (24 chars with dashes or 20 without)
  if (Length(Key) <> 24) and (Length(Key) <> 20) then
    Exit;
    
  // Count dashes
  dashCount := 0;
  for i := 1 to Length(Key) do
  begin
    if Key[i] = '-' then
      dashCount := dashCount + 1
    else if not ((Key[i] >= 'A') and (Key[i] <= 'Z')) and
            not ((Key[i] >= 'a') and (Key[i] <= 'z')) and
            not ((Key[i] >= '0') and (Key[i] <= '9')) then
      Exit; // Invalid character
  end;
  
  // Valid format: XXXX-XXXX-XXXX-XXXX-XXXX (4 dashes) or no dashes
  if (dashCount = 4) or (dashCount = 0) then
    Result := True;
end;

procedure InitializeWizard;
begin
  // Create custom license key input page
  LicenseKeyPage := CreateInputQueryPage(wpLicense,
    '🔑 License Key Activation', 
    'Nhập License Key để kích hoạt miniZ MCP',
    'Vui lòng nhập License Key bạn đã nhận từ nhà cung cấp.' + #13#10 +
    'Nếu chưa có key, vui lòng liên hệ để được hỗ trợ.' + #13#10#13#10 +
    'Format: XXXX-XXXX-XXXX-XXXX-XXXX');
    
  LicenseKeyPage.Add('License Key:', False);
  LicenseKeyPage.Values[0] := '';
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if CurPageID = LicenseKeyPage.ID then
  begin
    LicenseKey := Trim(LicenseKeyPage.Values[0]);
    
    // Validate license key
    if not ValidateLicenseKey(LicenseKey) then
    begin
      MsgBox('❌ License Key không hợp lệ!' + #13#10#13#10 + 
             'Vui lòng nhập key theo format:' + #13#10 +
             'XXXX-XXXX-XXXX-XXXX-XXXX' + #13#10#13#10 +
             'Liên hệ nhà cung cấp nếu bạn chưa có key.', 
             mbError, MB_OK);
      Result := False;
      Exit;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
  AppPath, JsonContent: String;
begin
  if CurStep = ssPostInstall then
  begin
    AppPath := ExpandConstant('{app}');
    
    // Create license activation file
    JsonContent := '{' + #13#10 +
      '  "license_key": "' + LicenseKey + '",' + #13#10 +
      '  "activated_date": "' + GetDateTimeString('yyyy-mm-dd hh:nn:ss', #0, #0) + '",' + #13#10 +
      '  "version": "4.3.0",' + #13#10 +
      '  "edition": "Professional",' + #13#10 +
      '  "install_path": "' + AppPath + '"' + #13#10 +
      '}';
      
    SaveStringToFile(AppPath + '\license_info.json', JsonContent, False);
    
    // Save license key separately
    SaveStringToFile(AppPath + '\.license_key', LicenseKey, False);
    
    // Log installation
    SaveStringToFile(AppPath + '\install.log', 
      'Installation completed at: ' + GetDateTimeString('yyyy-mm-dd hh:nn:ss', #0, #0) + #13#10 +
      'Version: 4.3.0 Professional' + #13#10 +
      'Path: ' + AppPath + #13#10,
      False);
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
begin
  Result := '';
  
  // Kill any running instances
  Exec('taskkill', '/F /IM python.exe /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  
  // Small delay to ensure processes are terminated
  Sleep(1000);
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  
  // Check Windows version
  if not IsWin64 then
  begin
    MsgBox('⚠️ miniZ MCP yêu cầu Windows 64-bit.' + #13#10 +
           'Hệ thống của bạn không được hỗ trợ.', 
           mbError, MB_OK);
    Result := False;
    Exit;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  if CurUninstallStep = usUninstall then
  begin
    // Remove from startup if exists
    RegDeleteValue(HKEY_CURRENT_USER, 
      'Software\Microsoft\Windows\CurrentVersion\Run', 
      'miniZ_MCP');
      
    // Kill processes before uninstall
    Exec('taskkill', '/F /IM python.exe /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;
