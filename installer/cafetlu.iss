; ============================================================
; Inno Setup — bộ cài Windows cho CafeTLU
;
; Build:  scripts/build_installer.sh   (hoặc make build-installer)
; Kết quả: installer/Output/CafeTLU-Setup-v<version>.exe
;
; Version KHÔNG gõ tay ở đây: script truyền /DMyAppVersion=<shared/version.py>.
; ============================================================

#define MyAppName "CafeTLU"
#define MyAppPublisher "Nhóm 5 — Đại học Thăng Long"
#define MyAppURL "https://github.com/Haianh4705/cafe-tlu"
#define MyAppExeName "CafeTLU.exe"

#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif

[Setup]
; AppId CỐ ĐỊNH — đổi là thành app khác, mất đường gỡ cài đặt cũ.
AppId={{cd150c56-2511-493c-a188-bf8dcbd4e815}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
; Cài cho từng user, không cần quyền admin (máy lab hay bị khoá).
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=CafeTLU-Setup-v{#MyAppVersion}
SetupIconFile=app.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
; PyInstaller onedir: toàn bộ thư mục dist/CafeTLU
Source: "..\dist\CafeTLU\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Gỡ cài đặt {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Chỉ xoá file do app sinh ra trong thư mục cài; dữ liệu người dùng nằm ở DB, không đụng.
Type: filesandordirs; Name: "{app}\logs"
