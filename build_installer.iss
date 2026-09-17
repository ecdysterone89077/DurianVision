#define MyAppName "DurianVision"
#define MyAppVersion "1.0"
#define MyAppPublisher "Faunas Wisnhu Aji"
#define MyAppExeName "DurianVision.exe"
#define BuildDir "dist\DurianVision"

[Setup]
; AppId ini unik, jangan diubah agar saat update versi 2.1, sistem menimpa instalasi lama dengan benar
AppId={{2A8B5F9E-8C4D-4F3A-B6E7-1D2C3B4A5F6E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
VersionInfoVersion=1.0.0.0
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=admin
OutputDir=Output
OutputBaseFilename=DurianVision_Setup_v1
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
;SetupIconFile=ui\styles\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Memasukkan file eksekusi utama
Source: "{#BuildDir}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Memasukkan SELURUH file pendukung (DLL, model YOLO, dll) secara rekursif
Source: "{#BuildDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Opsi untuk langsung menjalankan aplikasi setelah instalasi selesai
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
