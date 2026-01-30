; ============================================================
; miniZ MCP Professional v4.3.7 - Setup Installer
; With License Keys Batch Integration
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
OutputBaseFilename=miniZ_MCP_Professional_v{#MyAppVersion}_With_Keys
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
VersionInfoDescription={#MyAppName} Setup with License Keys
VersionInfoCopyright=Copyright (C) 2025 {#MyAppPublisher}
UninstallDisplayName={#MyAppName} {#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
english.LaunchProgram=Launch %1 after installation

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "startupicon"; Description: "Run at Windows startup / Tự động chạy khi khởi động Windows"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main application
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; License keys file - IMPORTANT!
Source: "NEW_LICENSE_KEYS.txt"; DestDir: "{app}"; Flags: ignoreversion
; Additional files
Source: "logo.png"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "LICENSE_AGREEMENT.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "CUSTOMER_README.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "xiaozhi_endpoints.json"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\License Keys"; Filename: "{app}\NEW_LICENSE_KEYS.txt"
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
  KeySelectPage: TInputOptionWizardPage;

function GetCurrentDateTime(Param: String): String;
begin
  Result := GetDateTimeString('yyyy/mm/dd hh:nn:ss', #0, #0);
end;

// Hàm kiểm tra định dạng license key mới (XXXX-XXXX-XXXX-XXXX)
function ValidateLicenseKeyFormat(Key: String): Boolean;
var
  I: Integer;
begin
  Result := False;
  
  if Length(Key) = 0 then
  begin
    Result := True;
    Exit;
  end;
  
  Key := Trim(UpperCase(Key));
  
  // Kiểm tra độ dài (19 ký tự bao gồm 3 dấu gạch ngang)
  if Length(Key) <> 19 then
  begin
    MsgBox('Dinh dang license key khong hop le!' + #13#10 +
           'Format: XXXX-XXXX-XXXX-XXXX', mbError, MB_OK);
    Exit;
  end;
  
  // Kiểm tra vị trí dấu gạch ngang
  if (Key[5] <> '-') or (Key[10] <> '-') or (Key[15] <> '-') then
  begin
    MsgBox('Dinh dang license key khong hop le!' + #13#10 +
           'Dau gach ngang phai o vi tri chinh xac' + #13#10 +
           'Format: XXXX-XXXX-XXXX-XXXX', mbError, MB_OK);
    Exit;
  end;
  
  Result := True;
end;

procedure InitializeWizard;
begin
  // Trang lựa chọn phương thức nhập key
  KeySelectPage := CreateInputOptionPage(wpSelectTasks,
    'Phương thức kích hoạt License / License Activation Method',
    'Chọn cách bạn muốn nhập license key',
    'File NEW_LICENSE_KEYS.txt chứa 100 license keys đã được tích hợp sẵn trong installer.',
    True, False);
  
  KeySelectPage.Add('Tôi sẽ chọn key từ file sau khi cài đặt (Khuyến nghị)');
  KeySelectPage.Add('Tôi muốn nhập license key ngay bây giờ');
  KeySelectPage.Values[0] := True;
  
  // Trang nhập license key thủ công
  LicenseKeyPage := CreateInputQueryPage(KeySelectPage.ID,
    'Nhập License Key / Enter License Key',
    'Nhập license key của bạn',
    'Định dạng: XXXX-XXXX-XXXX-XXXX' + #13#10 +
    '(Ví dụ: QT9F-KEEF-XL4U-WP93)' + #13#10#13#10 +
    '⚠️ Bạn có thể bỏ qua bước này và chọn key từ file sau khi cài đặt.');
  
  LicenseKeyPage.Add('License Key:', False);
  LicenseKeyPage.Values[0] := '';
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;
  
  // Skip license key input page nếu chọn cách chọn từ file
  if PageID = LicenseKeyPage.ID then
  begin
    if KeySelectPage.Values[0] then
      Result := True;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if CurPageID = LicenseKeyPage.ID then
  begin
    LicenseKey := Trim(UpperCase(LicenseKeyPage.Values[0]));
    
    // Cho phép bỏ qua nếu không nhập key
    if Length(LicenseKey) = 0 then
    begin
      if MsgBox('Bạn chưa nhập license key.' + #13#10#13#10 +
                'Bạn có thể chọn key từ file NEW_LICENSE_KEYS.txt sau khi cài đặt.' + #13#10#13#10 +
                'Tiếp tục cài đặt mà không nhập key?',
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
    
    if not ValidateLicenseKeyFormat(LicenseKey) then
    begin
      Result := False;
      Exit;
    end;
    
    if MsgBox('✅ License Key hợp lệ: ' + LicenseKey + #13#10#13#10 +
              'Key này sẽ được kích hoạt khi chạy lần đầu.' + #13#10 +
              'Tiếp tục cài đặt?', 
              mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
      Exit;
    end;
    
    // Lưu key vào registry
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
    ActivationFile := ExpandConstant('{app}\ACTIVATION_GUIDE.txt');
    FileContent := TStringList.Create;
    try
      FileContent.Add('════════════════════════════════════════════════════════════════');
      FileContent.Add('    miniZ MCP Professional v' + '{#MyAppVersion}' + ' - CÀI ĐẶT THÀNH CÔNG!');
      FileContent.Add('════════════════════════════════════════════════════════════════');
      FileContent.Add('');
      FileContent.Add('📅 Ngày cài đặt: ' + GetDateTimeString('yyyy/mm/dd hh:nn:ss', #0, #0));
      FileContent.Add('📁 Thư mục cài đặt: ' + ExpandConstant('{app}'));
      FileContent.Add('');
      FileContent.Add('════════════════════════════════════════════════════════════════');
      FileContent.Add('🔑 HƯỚNG DẪN KÍCH HOẠT LICENSE');
      FileContent.Add('════════════════════════════════════════════════════════════════');
      FileContent.Add('');
      
      if Length(LicenseKey) > 0 then
      begin
        FileContent.Add('✅ BẠN ĐÃ NHẬP LICENSE KEY');
        FileContent.Add('────────────────────────────────────────────────────────────────');
        FileContent.Add('License Key: ' + LicenseKey);
        FileContent.Add('Trạng thái: Chờ kích hoạt');
        FileContent.Add('');
        FileContent.Add('BƯỚC TIẾP THEO:');
        FileContent.Add('1. Khởi động ứng dụng miniZ MCP Professional');
        FileContent.Add('2. License sẽ tự động được kích hoạt');
        FileContent.Add('3. Kích hoạt bị khóa với phần cứng để bảo mật');
      end
      else
      begin
        FileContent.Add('📋 FILE LICENSE KEYS ĐÃ ĐƯỢC CÀI ĐẶT');
        FileContent.Add('────────────────────────────────────────────────────────────────');
        FileContent.Add('📄 File: NEW_LICENSE_KEYS.txt');
        FileContent.Add('📍 Vị trí: ' + ExpandConstant('{app}\NEW_LICENSE_KEYS.txt'));
        FileContent.Add('🔢 Số lượng keys: 100 keys');
        FileContent.Add('💎 Loại: Professional License (Vô thời hạn)');
        FileContent.Add('');
        FileContent.Add('CÁC BƯỚC KÍCH HOẠT:');
        FileContent.Add('────────────────────────────────────────────────────────────────');
        FileContent.Add('1. Mở file NEW_LICENSE_KEYS.txt (có shortcut trong Start Menu)');
        FileContent.Add('2. Chọn 1 license key bất kỳ (mỗi key chỉ dùng được 1 lần)');
        FileContent.Add('3. Copy license key (định dạng: XXXX-XXXX-XXXX-XXXX)');
        FileContent.Add('4. Khởi động ứng dụng miniZ MCP Professional');
        FileContent.Add('5. Dán license key vào ô kích hoạt');
        FileContent.Add('6. Nhấn "Activate" để hoàn tất');
        FileContent.Add('');
        FileContent.Add('VÍ DỤ LICENSE KEY:');
        FileContent.Add('   QT9F-KEEF-XL4U-WP93');
        FileContent.Add('   KKKJ-8NN4-RAGB-JNA5');
        FileContent.Add('   BN6A-NKQY-EFN9-E4FX');
      end;
      
      FileContent.Add('');
      FileContent.Add('════════════════════════════════════════════════════════════════');
      FileContent.Add('⚠️ LƯU Ý QUAN TRỌNG');
      FileContent.Add('════════════════════════════════════════════════════════════════');
      FileContent.Add('• Mỗi license key chỉ có thể kích hoạt trên 1 máy tính duy nhất');
      FileContent.Add('• License key bị khóa với Hardware ID sau khi kích hoạt');
      FileContent.Add('• Không chia sẻ license key với người khác');
      FileContent.Add('• Keys có hiệu lực vĩnh viễn (100 năm)');
      FileContent.Add('• Giữ file NEW_LICENSE_KEYS.txt bảo mật');
      FileContent.Add('');
      FileContent.Add('════════════════════════════════════════════════════════════════');
      FileContent.Add('✨ TÍNH NĂNG MỚI TRONG V4.3.0');
      FileContent.Add('════════════════════════════════════════════════════════════════');
      FileContent.Add('');
      FileContent.Add('🔍 Hệ thống Knowledge Base nâng cao');
      FileContent.Add('   • Tự động tìm kiếm khi bạn đặt câu hỏi');
      FileContent.Add('   • Tóm tắt tài liệu bằng AI');
      FileContent.Add('   • Trích xuất ngữ cảnh thông minh');
      FileContent.Add('   • Xếp hạng TF-IDF thông minh');
      FileContent.Add('');
      FileContent.Add('🤖 Tích hợp Gemini cải tiến');
      FileContent.Add('   • Tự động phát hiện knowledge base');
      FileContent.Add('   • Kích hoạt thông minh cho tìm kiếm tài liệu');
      FileContent.Add('   • Phản hồi nhận biết ngữ cảnh');
      FileContent.Add('   • Phân tích đa tài liệu');
      FileContent.Add('');
      FileContent.Add('🛠️ Trợ lý AI nâng cao');
      FileContent.Add('   • 141 công cụ AI mạnh mẽ');
      FileContent.Add('   • Hỗ trợ Dual AI (Gemini + GPT-4)');
      FileContent.Add('   • Tích hợp điều khiển giọng nói');
      FileContent.Add('   • Tìm kiếm web thời gian thực');
      FileContent.Add('');
      FileContent.Add('⚡ Hiệu suất & Bảo mật');
      FileContent.Add('   • Tối ưu thời gian phản hồi');
      FileContent.Add('   • Mã hóa nâng cao');
      FileContent.Add('   • Cải thiện độ ổn định');
      FileContent.Add('   • Sửa lỗi và cải tiến');
      FileContent.Add('');
      FileContent.Add('════════════════════════════════════════════════════════════════');
      FileContent.Add('📞 HỖ TRỢ');
      FileContent.Add('════════════════════════════════════════════════════════════════');
      FileContent.Add('• Email: support@minizmcp.com');
      FileContent.Add('• Website: https://www.minizmcp.com/');
      FileContent.Add('• Tài liệu: Xem User Guide trong Start Menu');
      FileContent.Add('');
      FileContent.Add('Cảm ơn bạn đã chọn miniZ MCP Professional!');
      FileContent.Add('');
      FileContent.Add('════════════════════════════════════════════════════════════════');
      
      FileContent.SaveToFile(ActivationFile);
    finally
      FileContent.Free;
    end;
    
    // Show activation guide after installation
    MsgBox('✅ CÀI ĐẶT THÀNH CÔNG!' + #13#10#13#10 +
           '📋 File license keys đã được cài đặt:' + #13#10 +
           '   ' + ExpandConstant('{app}\NEW_LICENSE_KEYS.txt') + #13#10#13#10 +
           '🔑 100 license keys Professional có sẵn!' + #13#10#13#10 +
           '📄 Xem file ACTIVATION_GUIDE.txt để biết hướng dẫn chi tiết.',
           mbInformation, MB_OK);
  end;
end;

function InitializeUninstall(): Boolean;
var
  LicenseDir: String;
begin
  Result := True;
  
  LicenseDir := ExpandConstant('{localappdata}\miniZ_MCP\.license');
  
  if DirExists(LicenseDir) then
  begin
    if MsgBox('Bạn có muốn xóa kích hoạt license?' + #13#10#13#10 +
              'Chọn KHÔNG để giữ license cho lần cài đặt lại sau này.' + #13#10 +
              'Chọn CÓ để xóa hoàn toàn license.' + #13#10#13#10 +
              'Xóa kích hoạt license?',
              mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES then
    begin
      DelTree(LicenseDir, True, True, True);
    end;
  end;
end;

[Messages]
WelcomeLabel2=Chương trình sẽ cài đặt [name/ver] trên máy tính của bạn.%n%n✅ 100 LICENSE KEYS ĐÃ ĐƯỢC TÍCH HỢP SẴN!%n%nBạn sẽ chọn 1 trong 100 license keys Professional (vô thời hạn) sau khi cài đặt.%n%nNên đóng tất cả các ứng dụng khác trước khi tiếp tục.

