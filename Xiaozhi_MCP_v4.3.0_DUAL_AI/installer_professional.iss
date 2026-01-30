; ============================================================
; miniZ MCP v4.3.0 - PROFESSIONAL INSTALLER
; Inno Setup Script - Customer Edition
; 
; Features:
; - Full Python + dependencies installation
; - Auto-startup with Windows
; - System tray integration
; - Web dashboard
; - Smart Analyzer v1.0
; - Multi-device sync
; ============================================================

#define MyAppName "miniZ MCP Professional"
#define MyAppVersion "4.3.0"
#define MyAppPublisher "miniZ Team"
#define MyAppURL "https://github.com/your-repo"
#define MyAppExeName "START.bat"
#define MyAppPythonScript "xiaozhi_final.py"

[Setup]
; App Identity
AppId={{8F9A3B2C-1D4E-5F6A-7B8C-9D0E1F2A3B4C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation paths
DefaultDirName={autopf}\miniZ_MCP
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
DisableProgramGroupPage=yes

; Output configuration
OutputDir=installer_output
OutputBaseFilename=miniZ_MCP_Professional_Setup_v{#MyAppVersion}
;SetupIconFile=miniz_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Visual style (using default images)
;WizardImageFile=compiler:WizModernImage-IS.bmp
;WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp

; Minimum Windows version
MinVersion=10.0.17763

; Architecture
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; License & Info
LicenseFile=LICENSE
InfoBeforeFile=README.md
InfoAfterFile=QUICKSTART.md

; Uninstall
;UninstallDisplayIcon={app}\miniz_icon.ico
UninstallDisplayName={#MyAppName} {#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
;Name: "vietnamese"; MessagesFile: "compiler:Languages\Vietnamese.isl"

[Types]
Name: "full"; Description: "Cài đặt đầy đủ (Recommended)"
Name: "minimal"; Description: "Cài đặt tối thiểu"
Name: "custom"; Description: "Tùy chỉnh"; Flags: iscustom

[Components]
Name: "core"; Description: "Ứng dụng chính"; Types: full minimal custom; Flags: fixed
Name: "python"; Description: "Python 3.11.9 (Portable)"; Types: full; Flags: checkablealone
Name: "dependencies"; Description: "Thư viện Python (FastAPI, VLC, etc.)"; Types: full minimal
Name: "smartanalyzer"; Description: "Smart Conversation Analyzer v1.0"; Types: full
Name: "musicplayer"; Description: "VLC Music Player Integration"; Types: full
Name: "autostart"; Description: "Khởi động cùng Windows"; Types: full
Name: "desktop"; Description: "Tạo shortcut Desktop"; Types: full minimal
Name: "startmenu"; Description: "Tạo shortcut Start Menu"; Types: full minimal

[Tasks]
Name: "desktopicon"; Description: "Tạo biểu tượng trên Desktop"; GroupDescription: "Shortcuts:"; Components: desktop
Name: "quicklaunchicon"; Description: "Tạo biểu tượng Quick Launch"; GroupDescription: "Shortcuts:"; Flags: unchecked
Name: "autostart"; Description: "Tự động khởi động cùng Windows"; GroupDescription: "Startup Options:"; Components: autostart
Name: "startoninstall"; Description: "Khởi động ngay sau khi cài đặt"; GroupDescription: "Post-Installation:"

[Files]
; ===== CORE APPLICATION FILES =====
Source: "xiaozhi_final.py"; DestDir: "{app}"; Components: core; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Components: core; Flags: ignoreversion
Source: "xiaozhi_endpoints.json"; DestDir: "{app}"; Components: core; Flags: ignoreversion
;Source: "miniz_icon.ico"; DestDir: "{app}"; Components: core; Flags: ignoreversion

; ===== BATCH FILES =====
Source: "START.bat"; DestDir: "{app}"; Components: core; Flags: ignoreversion
Source: "START_HIDDEN.bat"; DestDir: "{app}"; Components: core; Flags: ignoreversion
Source: "INSTALL.bat"; DestDir: "{app}"; Components: core; Flags: ignoreversion
Source: "CHECK.bat"; DestDir: "{app}"; Components: core; Flags: ignoreversion

; ===== DOCUMENTATION =====
Source: "README.md"; DestDir: "{app}"; Components: core; Flags: ignoreversion isreadme
Source: "QUICKSTART.md"; DestDir: "{app}"; Components: core; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Components: core; Flags: ignoreversion
Source: "CHANGELOG.md"; DestDir: "{app}"; Components: core; Flags: ignoreversion
Source: "SMART_ANALYZER_GUIDE.md"; DestDir: "{app}"; Components: smartanalyzer; Flags: ignoreversion
Source: "CONVERSATION_MEMORY_ARCHITECTURE.md"; DestDir: "{app}"; Components: smartanalyzer; Flags: ignoreversion
Source: "README_INSTALLATION.md"; DestDir: "{app}"; Components: core; Flags: ignoreversion

; ===== MUSIC LIBRARY =====
Source: "music_library\*"; DestDir: "{app}\music_library"; Components: musicplayer; Flags: ignoreversion recursesubdirs createallsubdirs

; ===== TEST FILES =====
Source: "TEST_SMART_ANALYZER.py"; DestDir: "{app}"; Components: smartanalyzer; Flags: ignoreversion

; ===== PYTHON PORTABLE (if selected) =====
; Note: Python portable package should be downloaded separately
; Source: "python-3.11.9-embed-amd64\*"; DestDir: "{app}\python"; Components: python; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
; Create AppData directories
Name: "{localappdata}\miniZ_MCP"; Flags: uninsneveruninstall
Name: "{localappdata}\miniZ_MCP\conversations"; Flags: uninsneveruninstall
Name: "{localappdata}\miniZ_MCP\knowledge"; Flags: uninsneveruninstall

; App directories
Name: "{app}\logs"
Name: "{app}\temp"
Name: "{app}\music_library"

[Icons]
; Start Menu shortcuts
Name: "{group}\miniZ MCP"; Filename: "{app}\START.bat"; WorkingDir: "{app}"; Components: startmenu
Name: "{group}\miniZ MCP (Hidden)"; Filename: "{app}\START_HIDDEN.bat"; WorkingDir: "{app}"; Components: startmenu
Name: "{group}\Web Dashboard"; Filename: "http://localhost:8000"; Components: startmenu
Name: "{group}\Uninstall miniZ MCP"; Filename: "{uninstallexe}"; Components: startmenu

; Desktop shortcut
Name: "{autodesktop}\miniZ MCP"; Filename: "{app}\START.bat"; WorkingDir: "{app}"; Tasks: desktopicon

; Quick Launch shortcut
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\miniZ MCP"; Filename: "{app}\START.bat"; WorkingDir: "{app}"; Tasks: quicklaunchicon

[Registry]
; Auto-startup registry key
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "miniZ_MCP"; ValueData: """{app}\START_HIDDEN.bat"""; Flags: uninsdeletevalue; Tasks: autostart

; App registry keys
Root: HKCU; Subkey: "Software\miniZ_MCP"; Flags: uninsdeletekeyifempty
Root: HKCU; Subkey: "Software\miniZ_MCP\Settings"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\miniZ_MCP\Settings"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\miniZ_MCP\Settings"; ValueType: dword; ValueName: "AutoStart"; ValueData: "1"; Flags: uninsdeletevalue; Tasks: autostart

[Run]
; ===== INSTALLATION STEPS =====

; Step 1: Check Python
Filename: "cmd.exe"; Parameters: "/c python --version > nul 2>&1 && echo Python OK || echo Python NOT FOUND"; StatusMsg: "Đang kiểm tra Python..."; Flags: runhidden waituntilterminated

; Step 2: Install dependencies
Filename: "cmd.exe"; Parameters: "/c cd /d ""{app}"" && python -m pip install --upgrade pip --quiet && pip install -r requirements.txt --quiet --disable-pip-version-check"; StatusMsg: "Đang cài đặt thư viện Python (có thể mất 2-3 phút)..."; Flags: runhidden waituntilterminated; Components: dependencies; Check: CheckPythonInstalled

; Step 3: Verify installation
Filename: "cmd.exe"; Parameters: "/c cd /d ""{app}"" && python -c ""import fastapi, uvicorn, psutil, websockets; print('All OK')"""; StatusMsg: "Đang xác minh cài đặt..."; Flags: runhidden waituntilterminated; Check: CheckPythonInstalled

; Step 4: Create config file if not exists
Filename: "{app}\CHECK.bat"; WorkingDir: "{app}"; StatusMsg: "Đang kiểm tra cấu hình..."; Flags: runhidden waituntilterminated

; Step 5: Open web dashboard
Filename: "http://localhost:8000"; Description: "Mở Web Dashboard"; Flags: postinstall shellexec skipifsilent nowait; Tasks: startoninstall

; Step 6: Start application
Filename: "{app}\START.bat"; Description: "Khởi động miniZ MCP ngay bây giờ"; WorkingDir: "{app}"; Flags: postinstall nowait skipifsilent; Tasks: startoninstall

[UninstallRun]
; Stop server before uninstall
Filename: "taskkill"; Parameters: "/F /IM python.exe /FI ""WINDOWTITLE eq *xiaozhi_final*"""; Flags: runhidden; RunOnceId: "StopServer"
Filename: "taskkill"; Parameters: "/F /IM uvicorn.exe"; Flags: runhidden; RunOnceId: "StopUvicorn"

[UninstallDelete]
; Clean up generated files
Type: files; Name: "{app}\*.pyc"
Type: files; Name: "{app}\*.log"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\temp"
Type: filesandordirs; Name: "{app}\logs"

; Note: User data in AppData is preserved

[Code]
var
  PythonInstallPage: TInputOptionWizardPage;
  PythonPath: String;
  DownloadPage: TDownloadWizardPage;

function OnDownloadProgress(const Url, FileName: String; const Progress, ProgressMax: Int64): Boolean;
begin
  if Progress = ProgressMax then
    Log(Format('Successfully downloaded %s to %s', [Url, FileName]));
  Result := True;
end;

procedure InitializeWizard;
begin
  // Create custom page for Python installation
  PythonInstallPage := CreateInputOptionPage(wpWelcome,
    'Cài đặt Python', 'miniZ MCP yêu cầu Python 3.11 hoặc mới hơn',
    'Vui lòng chọn cách cài đặt Python:',
    True, False);
  
  PythonInstallPage.Add('Python đã được cài đặt sẵn');
  PythonInstallPage.Add('Tự động tải và cài Python 3.11.9 (Recommended)');
  PythonInstallPage.Add('Tôi sẽ tự cài Python sau');
  
  PythonInstallPage.Values[0] := True;

  // Download page
  DownloadPage := CreateDownloadPage(SetupMessage(msgWizardPreparing), SetupMessage(msgPreparingDesc), @OnDownloadProgress);
end;

function CheckPythonInstalled: Boolean;
var
  ResultCode: Integer;
begin
  // Check if Python is installed
  Result := Exec('cmd.exe', '/c python --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
  
  if not Result then
  begin
    Log('Python not found');
    if MsgBox('Python chưa được cài đặt. Bạn có muốn mở trang tải Python không?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      ShellExec('open', 'https://www.python.org/downloads/', '', '', SW_SHOW, ewNoWait, ResultCode);
    end;
  end
  else
    Log('Python is installed');
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  
  if CurPageID = wpReady then
  begin
    // Final check before installation
    if not CheckPythonInstalled then
    begin
      if PythonInstallPage.Values[2] then
      begin
        // User chose to install Python later
        if MsgBox('Bạn cần cài đặt Python trước khi sử dụng miniZ MCP. Tiếp tục cài đặt?', mbConfirmation, MB_YESNO) = IDNO then
          Result := False;
      end;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
  PythonInstaller: String;
begin
  if CurStep = ssInstall then
  begin
    // Download Python if needed
    if PythonInstallPage.Values[1] then
    begin
      try
        DownloadPage.Clear;
        DownloadPage.Add('https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe', 'python-installer.exe', '');
        DownloadPage.Show;
        try
          DownloadPage.Download;
          PythonInstaller := ExpandConstant('{tmp}\python-installer.exe');
          
          if FileExists(PythonInstaller) then
          begin
            // Install Python silently
            if Exec(PythonInstaller, '/quiet InstallAllUsers=0 PrependPath=1 Include_pip=1', '', SW_SHOW, ewWaitUntilTerminated, ResultCode) then
            begin
              Log('Python installed successfully');
            end
            else
            begin
              MsgBox('Không thể cài đặt Python tự động. Vui lòng cài thủ công từ python.org', mbError, MB_OK);
            end;
          end;
        finally
          DownloadPage.Hide;
        end;
      except
        MsgBox('Lỗi khi tải Python. Vui lòng cài thủ công từ python.org', mbError, MB_OK);
      end;
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  if CurUninstallStep = usUninstall then
  begin
    // Stop all Python processes running xiaozhi_final.py
    Exec('taskkill', '/F /IM python.exe /FI "WINDOWTITLE eq *xiaozhi_final*"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Sleep(1000);
  end;
  
  if CurUninstallStep = usPostUninstall then
  begin
    // Ask if user wants to keep data
    if MsgBox('Bạn có muốn giữ lại dữ liệu conversation và knowledge base không?', mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDNO then
    begin
      DelTree(ExpandConstant('{localappdata}\miniZ_MCP'), True, True, True);
    end;
  end;
end;

[Messages]
; Custom messages
WelcomeLabel2=Chương trình sẽ cài đặt [name/ver] lên máy tính của bạn.%n%nChức năng:%n• Smart Conversation Analyzer v1.0%n• 141 AI Tools%n• Multi-Device Sync (3 thiết bị)%n• VLC Music Player%n• Web Dashboard%n• Conversation Memory%n%nKhuyến nghị: Đóng tất cả ứng dụng khác trước khi tiếp tục.

FinishedLabel=Đã cài đặt xong [name] lên máy tính của bạn.%n%nBạn có thể khởi động ứng dụng bằng cách chọn các biểu tượng đã được tạo.

FinishedHeadingLabel=Hoàn tất cài đặt miniZ MCP Professional

ClickFinish=Nhấn Finish để hoàn tất và thoát khỏi Setup.

SelectDirLabel3=Setup sẽ cài đặt [name] vào thư mục sau.

SelectDirBrowseLabel=Để tiếp tục, nhấn Next. Nếu bạn muốn chọn thư mục khác, nhấn Browse.

DiskSpaceGBLabel=Cần ít nhất [mb] GB dung lượng trống.

StatusExtractFiles=Đang giải nén files...
StatusCreateDirs=Đang tạo thư mục...
StatusInstallFiles=Đang cài đặt files...

[CustomMessages]
; Custom messages (English only - Vietnamese language file not available)
english.PythonRequired=Python 3.11+ is required
;vietnamese.PythonRequired=Yêu cầu Python 3.11 trở lên

english.InstallingDependencies=Installing Python dependencies...
;vietnamese.InstallingDependencies=Đang cài đặt thư viện Python...

english.VerifyingInstallation=Verifying installation...
;vietnamese.VerifyingInstallation=Đang xác minh cài đặt...

english.InstallationComplete=Installation completed successfully!
;vietnamese.InstallationComplete=Cài đặt hoàn tất!

english.OpenDashboard=Open Web Dashboard
;vietnamese.OpenDashboard=Mở Web Dashboard

english.StartNow=Start miniZ MCP now
;vietnamese.StartNow=Khởi động miniZ MCP ngay
