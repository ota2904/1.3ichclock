; ============================================
; miniZ MCP v4.3.0 Professional Edition
; Inno Setup Installer Script
; ============================================
; Requirements: Inno Setup 6.0+ (https://jrsoftware.org/isinfo.php)

#define MyAppName "miniZ MCP Professional"
#define MyAppVersion "4.3.0"
#define MyAppPublisher "miniZ Software"
#define MyAppURL "https://miniz-mcp.com"
#define MyAppExeName "miniZ_MCP_v4.3.0_Professional.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
AppId={{F4A9B2C1-D8E5-F3A7-B4C9-D2E6F1A8B3C5}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\miniZ_MCP
DefaultGroupName={#MyAppName}
LicenseFile=LICENSE
InfoBeforeFile=README.md
OutputDir=installer_output
OutputBaseFilename=miniZ_MCP_v4.3.0_Professional_Setup
SetupIconFile=
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName} v{#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; License system files (chỉ bao gồm file cần thiết cho khách hàng)
Source: "license_manager.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "activation_window.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE_SYSTEM_README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "license_database.json"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: license_generator.py KHÔNG được bao gồm - chỉ dành cho Admin

; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "QUICKSTART.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "CHANGELOG.md"; DestDir: "{app}"; Flags: ignoreversion

; Music library
Source: "music_library\*"; DestDir: "{app}\music_library"; Flags: ignoreversion recursesubdirs createallsubdirs

; Configuration
Source: "xiaozhi_endpoints.json"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Documentation"; Filename: "{app}\LICENSE_SYSTEM_README.md"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\miniz_license.json"
Type: dirifempty; Name: "{app}"

[Code]
var
  LicenseInfoPage: TOutputMsgMemoWizardPage;
  DisclaimerPage: TOutputMsgMemoWizardPage;

procedure InitializeWizard;
begin
  // Create disclaimer page FIRST (before license info)
  DisclaimerPage := CreateOutputMsgMemoPage(wpLicense,
    'CẢNH BÁO MIỄN TRỪ TRÁCH NHIỆM', 
    '⚠️ VUI LÒNG ĐỌC KỸ TRƯỚC KHI TIẾP TỤC ⚠️',
    '════════════════════════════════════════════════════════════' + #13#10 +
    '           MIỄN TRỪ TRÁCH NHIỆM VỀ DỮ LIỆU NGƯỜI DÙNG' + #13#10 +
    '════════════════════════════════════════════════════════════' + #13#10#13#10 +
    '❌ CHÚNG TÔI KHÔNG CHỊU TRÁCH NHIỆM VỀ:' + #13#10#13#10 +
    '   • Mất mát dữ liệu cá nhân, tài liệu, hình ảnh, video' + #13#10 +
    '   • Mất thông tin đăng nhập, mật khẩu, tài khoản' + #13#10 +
    '   • Mất API Keys (OpenAI, Google, v.v.)' + #13#10 +
    '   • Mất lịch sử chat hoặc tin nhắn với AI' + #13#10 +
    '   • Mất dữ liệu kinh doanh hoặc tài chính' + #13#10 +
    '   • Bất kỳ thiệt hại trực tiếp hoặc gián tiếp nào' + #13#10#13#10 +
    '════════════════════════════════════════════════════════════' + #13#10#13#10 +
    '✅ TRÁCH NHIỆM CỦA NGƯỜI DÙNG:' + #13#10#13#10 +
    '   • Sao lưu (backup) dữ liệu quan trọng TRƯỚC khi sử dụng' + #13#10 +
    '   • Bảo vệ thông tin đăng nhập và API keys của mình' + #13#10 +
    '   • Không chia sẻ License Key với người khác' + #13#10 +
    '   • Chấp nhận mọi rủi ro khi sử dụng phần mềm' + #13#10#13#10 +
    '════════════════════════════════════════════════════════════' + #13#10#13#10 +
    '⚠️ PHẦN MỀM ĐƯỢC CUNG CẤP "NGUYÊN TRẠNG" (AS-IS)' + #13#10 +
    '   Không có bất kỳ bảo đảm nào về tính phù hợp hoặc an toàn.' + #13#10#13#10 +
    '════════════════════════════════════════════════════════════' + #13#10 +
    '   Bằng việc tiếp tục cài đặt, bạn ĐỒNG Ý với các điều khoản trên.' + #13#10 +
    '════════════════════════════════════════════════════════════',
    '');

  // Create custom page with license information
  LicenseInfoPage := CreateOutputMsgMemoPage(wpInfoBefore,
    'Thông tin Kích hoạt License', 
    'Hướng dẫn kích hoạt phần mềm',
    '════════════════════════════════════════════════════════════' + #13#10 +
    '              HƯỚNG DẪN KÍCH HOẠT LICENSE' + #13#10 +
    '════════════════════════════════════════════════════════════' + #13#10#13#10 +
    'Phần mềm này yêu cầu LICENSE KEY để kích hoạt.' + #13#10 + 
    'Vui lòng liên hệ nhà phân phối để nhận key kích hoạt.' + #13#10#13#10 +
    '────────────────────────────────────────────────────────────' + #13#10 +
    'CÁC BƯỚC KÍCH HOẠT:' + #13#10 +
    '────────────────────────────────────────────────────────────' + #13#10#13#10 +
    '  BƯỚC 1: Sau khi cài đặt, chạy phần mềm lần đầu' + #13#10 +
    '  BƯỚC 2: Cửa sổ kích hoạt sẽ hiển thị HARDWARE ID' + #13#10 +
    '  BƯỚC 3: Gửi HARDWARE ID cho nhà cung cấp để nhận LICENSE KEY' + #13#10 +
    '  BƯỚC 4: Nhập LICENSE KEY vào cửa sổ kích hoạt' + #13#10 +
    '  BƯỚC 5: Nhấn "Activate" để hoàn tất' + #13#10#13#10 +
    '────────────────────────────────────────────────────────────' + #13#10 +
    'LƯU Ý QUAN TRỌNG:' + #13#10 +
    '────────────────────────────────────────────────────────────' + #13#10#13#10 +
    '  ⚠️ Mỗi LICENSE KEY chỉ có thể kích hoạt trên 1 máy tính' + #13#10 +
    '  ⚠️ Để chuyển sang máy khác, liên hệ support để deactivate' + #13#10 +
    '  ⚠️ Không chia sẻ License Key với người khác' + #13#10#13#10 +
    '════════════════════════════════════════════════════════════' + #13#10 +
    'Xem thêm chi tiết: LICENSE_SYSTEM_README.md' + #13#10 +
    '════════════════════════════════════════════════════════════',
    '');
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  // Không cần kiểm tra Python - khách hàng chỉ sử dụng file .exe
  Result := '';
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  // Không cần tạo license_database.json - file này chỉ dành cho admin
  // Khách hàng chỉ cần miniz_license.json (được tạo khi activate)
end;

function InitializeUninstall(): Boolean;
begin
  Result := True;
  if MsgBox('Bạn có muốn xóa dữ liệu kích hoạt không?' + #13#10 + 
            '(miniz_license.json)' + #13#10#13#10 +
            'Chọn YES: Xóa (cài lại sẽ phải kích hoạt lại)' + #13#10 +
            'Chọn NO: Giữ lại (cài lại không cần kích hoạt lại)',
            mbConfirmation, MB_YESNO) = IDNO then
  begin
    // Don't delete license file
    DeleteFile(ExpandConstant('{app}\miniz_license.json'));
  end;
end;
