; miniZ MCP v4.3.0 - Professional Installer Script
; Inno Setup Script - Creates professional Windows installer with Next/Next/Finish flow

#define MyAppName "miniZ MCP"
#define MyAppVersion "4.3.0"
#define MyAppPublisher "miniZ MCP Team"
#define MyAppURL "https://github.com/miniz-mcp"
#define MyAppExeName "START.bat"

[Setup]
; Application Info
AppId={{B8E9D4F2-7C3A-4E1B-9F2D-8A5C6E7D9F1B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation Directories
DefaultDirName={autopf}\miniZ_MCP
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output
OutputDir=installer_output
OutputBaseFilename=miniZ_MCP_Setup_v4.3.0_NEW
; SetupIconFile=icon.ico
Compression=lzma2/max
SolidCompression=yes

; UI
WizardStyle=modern
; WizardImageFile=installer_banner.bmp
; WizardSmallImageFile=installer_icon.bmp

; License and Info
LicenseFile=LICENSE_AGREEMENT.txt
InfoBeforeFile=README_INSTALL.txt
InfoAfterFile=POST_INSTALL_INFO.txt

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Uninstall
; UninstallDisplayIcon={app}\icon.ico
UninstallDisplayName={#MyAppName} v{#MyAppVersion}

; Misc
AllowNoIcons=yes
DisableWelcomePage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Tạo shortcut trên Desktop"; GroupDescription: "Shortcuts:"; Flags: unchecked
Name: "quicklaunchicon"; Description: "Tạo Quick Launch icon"; GroupDescription: "Shortcuts:"; Flags: unchecked
Name: "startmenu"; Description: "Thêm vào Start Menu"; GroupDescription: "Shortcuts:"

[Files]
; Main application files
Source: "xiaozhi_final.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "START.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "CHECK.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "INSTALL.bat"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "QUICKSTART.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "CHANGELOG.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "GEMINI_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "GPT4_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "MUSIC_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "INSTALLER_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion

; Configuration files
Source: "xiaozhi_endpoints.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

; Music library
Source: "music_library\*"; DestDir: "{app}\music_library"; Flags: ignoreversion recursesubdirs createallsubdirs

; License keys
Source: "LICENSE_KEYS.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "licenses_all.json"; DestDir: "{app}"; Flags: ignoreversion

; Icon (if exists)
; Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion; Tasks: desktopicon

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startmenu
Name: "{group}\Check Installation"; Filename: "{app}\CHECK.bat"; Tasks: startmenu
Name: "{group}\Documentation"; Filename: "{app}\README.md"; Tasks: startmenu
Name: "{group}\Quick Start Guide"; Filename: "{app}\QUICKSTART.md"; Tasks: startmenu
Name: "{group}\License Keys"; Filename: "{app}\LICENSE_KEYS.txt"; Tasks: startmenu
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; Tasks: startmenu

; Desktop
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Quick Launch
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; NOTE: INSTALL.bat sẽ được user chạy thủ công sau cài đặt
; Không chạy tự động vì pip install mất rất lâu và có thể bị treo

; Show readme after install
Filename: "{app}\POST_INSTALL_INFO.txt"; Description: "Xem hướng dẫn sau cài đặt"; Flags: postinstall shellexec skipifsilent unchecked

; Open install folder
Filename: "{win}\explorer.exe"; Parameters: """{app}"""; Description: "Mở thư mục cài đặt"; Flags: postinstall skipifsilent nowait

[Code]
var
  LicenseKeyPage: TInputQueryWizardPage;
  LicenseKey: String;

procedure InitializeWizard;
begin
  // Create custom license key input page
  LicenseKeyPage := CreateInputQueryPage(wpLicense,
    'License Key Activation', 
    'Nhập License Key để kích hoạt miniZ MCP',
    'Vui lòng nhập License Key bạn đã nhận. ' +
    'Nếu chưa có key, vui lòng liên hệ nhà cung cấp.' + #13#10#13#10 +
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
    
    // Validate license key format
    if Length(LicenseKey) < 20 then
    begin
      MsgBox('License Key không hợp lệ!' + #13#10 + 
             'Vui lòng nhập key theo format: XXXX-XXXX-XXXX-XXXX-XXXX', 
             mbError, MB_OK);
      Result := False;
      Exit;
    end;
    
    // License key will be saved in CurStepChanged after files are installed
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Create activation file with license info
    SaveStringToFile(ExpandConstant('{app}\license_info.json'),
      '{"license_key": "' + LicenseKey + '", ' +
      '"activated_date": "' + GetDateTimeString('yyyy-mm-dd hh:nn:ss', #0, #0) + '", ' +
      '"version": "4.3.0"}',
      False);
  end;
end;

[UninstallDelete]
Type: files; Name: "{app}\.license_key"
Type: files; Name: "{app}\license_info.json"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\*.pyc"
