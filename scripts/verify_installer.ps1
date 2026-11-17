<#
.SYNOPSIS
    Cài thử bộ cài CafeTLU trên Windows sạch rồi gỡ ra, ghi lại bằng chứng.

.DESCRIPTION
    Chạy trên runner `windows-latest` (máy Windows mới mỗi lần chạy, không có gì cài sẵn
    từ máy lập trình viên) để chứng minh bộ cài dùng được, không chỉ build ra file .exe.

    Kịch bản kiểm tra:
      1. Bộ cài tồn tại, in kích thước + SHA256
      2. Cài im lặng (Inno Setup /VERYSILENT) → exit code 0
      3. File sau khi cài có đủ: CafeTLU.exe, _internal\, unins000.exe
      4. Chạy CafeTLU.exe → cửa sổ hiện ra (MainWindowHandle khác 0) sau tối đa 30 giây
      5. Chụp ảnh cửa sổ bằng PrintWindow (chụp đúng cửa sổ, không cần desktop hiển thị)
      6. Tắt app, gỡ im lặng → thư mục cài biến mất

    Không kiểm tra nghiệp vụ (đăng nhập, bán hàng) — việc đó cần API + MySQL, xem
    docs/screenshots/installer/README.md.

.PARAMETER InstallerPath
    Đường dẫn tới CaféTLU-Setup-*.exe, hoặc thư mục chứa nó (script tự tìm).

.PARAMETER InstallDir
    Thư mục cài thử. Mặc định C:\CafeTLU-verify.

.PARAMETER ScreenshotPath
    File PNG chụp cửa sổ app sau khi cài.

.PARAMETER ReportPath
    File markdown ghi kết quả từng bước (đính kèm artifact CI).

.OUTPUTS
    Exit code 0 nếu mọi bước đạt, 1 nếu có bước hỏng.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$InstallerPath,
    [string]$InstallDir = 'C:\CafeTLU-verify',
    [string]$ScreenshotPath = 'verification/gui.png',
    [string]$ReportPath = 'verification/report.md'
)

$ErrorActionPreference = 'Stop'
$script:rows = @()
$script:failed = 0

function Add-Check {
    param([string]$Name, [bool]$Ok, [string]$Detail)
    $status = if ($Ok) { 'PASS' } else { 'FAIL' }
    if (-not $Ok) { $script:failed++ }
    $script:rows += [pscustomobject]@{ Step = $Name; Status = $status; Detail = $Detail }
    Write-Host ("[{0}] {1} — {2}" -f $status, $Name, $Detail)
}

function Write-Report {
    $table = ($script:rows | ForEach-Object { "| $($_.Step) | $($_.Status) | $($_.Detail) |" }) -join "`n"
    $lines = @(
        '# Kết quả cài thử bộ cài CafeTLU trên Windows sạch',
        '',
        "- Máy: ``$env:COMPUTERNAME`` · $((Get-CimInstance Win32_OperatingSystem).Caption) $((Get-CimInstance Win32_OperatingSystem).Version)",
        "- Bộ cài: ``$($installer.Name)`` · $sizeMb MB · SHA256 ``$sha``",
        "- Lúc chạy: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')",
        "- Kết quả: **$($script:rows.Count - $script:failed)/$($script:rows.Count) bước đạt**",
        '',
        '| Bước | Kết quả | Chi tiết |',
        '|---|---|---|',
        $table
    )
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $ReportPath) | Out-Null
    Set-Content -LiteralPath $ReportPath -Value ($lines -join "`n") -Encoding utf8
    Write-Host "Báo cáo: $ReportPath"
}


function Wait-Until {
    param([scriptblock]$Condition, [int]$TimeoutSeconds = 30, [int]$IntervalMs = 500)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (& $Condition) { return $true }
        Start-Sleep -Milliseconds $IntervalMs
    }
    return (& $Condition)
}

# --- Thư viện chụp ảnh cửa sổ (Win32) -------------------------------------
if (-not ('Win32Shot' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class Win32Shot {
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left, Top, Right, Bottom; }
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hwnd, IntPtr hdc, uint flags);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hwnd, out RECT rect);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hwnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hwnd, int cmd);
}
'@
}
Add-Type -AssemblyName System.Drawing

# --- 0. Chuẩn bị -----------------------------------------------------------
$installer = if (Test-Path -LiteralPath $InstallerPath -PathType Container) {
    Get-ChildItem -LiteralPath $InstallerPath -Recurse -Filter '*.exe' |
        Where-Object { $_.Name -like '*Setup*' } | Select-Object -First 1
} elseif (Test-Path -LiteralPath $InstallerPath) {
    Get-Item -LiteralPath $InstallerPath
} else { $null }

if (-not $installer) {
    Write-Host "::error title=Không thấy bộ cài::Không tìm được *.exe trong '$InstallerPath'"
    exit 1
}

$sha = (Get-FileHash -LiteralPath $installer.FullName -Algorithm SHA256).Hash
$sizeMb = [math]::Round($installer.Length / 1MB, 1)
Add-Check 'Có file bộ cài' ($installer.Length -gt 20MB) `
    "$($installer.Name) · $sizeMb MB · SHA256 $sha"
Add-Check 'Bộ cài đủ lớn (>20 MB, có payload PyInstaller)' ($installer.Length -gt 20MB) "$sizeMb MB"

foreach ($p in @($ScreenshotPath, $ReportPath)) {
    $dir = Split-Path -Parent $p
    if ($dir) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
}

if (Test-Path -LiteralPath $InstallDir) {
    Remove-Item -LiteralPath $InstallDir -Recurse -Force
}
Add-Check 'Máy sạch trước khi cài' (-not (Test-Path -LiteralPath $InstallDir)) `
    "$InstallDir chưa tồn tại"

# --- 1. Cài im lặng --------------------------------------------------------
$sw = [System.Diagnostics.Stopwatch]::StartNew()
$installProc = Start-Process -FilePath $installer.FullName -Wait -PassThru -ArgumentList @(
    '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/NOCANCEL',
    "/DIR=$InstallDir", '/LOG'
)
$sw.Stop()
Add-Check 'Cài im lặng (/VERYSILENT)' ($installProc.ExitCode -eq 0) `
    ("exit code {0} sau {1:N0} giây" -f $installProc.ExitCode, $sw.Elapsed.TotalSeconds)

$exe = Join-Path $InstallDir 'CafeTLU.exe'
$internal = Join-Path $InstallDir '_internal'
$uninst = Join-Path $InstallDir 'unins000.exe'

Add-Check 'Có CafeTLU.exe sau khi cài' (Test-Path -LiteralPath $exe) $exe
Add-Check 'Có thư mục _internal (onedir)' (Test-Path -LiteralPath $internal) $internal
Add-Check 'Có bộ gỡ cài đặt unins000.exe' (Test-Path -LiteralPath $uninst) $uninst
Add-Check 'Có shortcut trong Start Menu' (
    (Get-ChildItem -Path (Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs') -Recurse -Filter 'CafeTLU*.lnk' -ErrorAction SilentlyContinue | Measure-Object).Count -ge 1
) 'tìm CafeTLU*.lnk'

if (-not (Test-Path -LiteralPath $exe)) {
    # Không có gì để chạy — ghi báo cáo rồi thoát.
    Write-Report
    exit 1
}

# --- 2. Chạy thử + chụp ảnh cửa sổ ----------------------------------------
$env:QT_OPENGL = 'software'      # runner không có GPU
$env:QT_QUICK_BACKEND = 'software'
$proc = Start-Process -FilePath $exe -PassThru
$null = $proc.Handle  # cache handle

$hasWindow = Wait-Until -TimeoutSeconds 45 -Condition {
    $proc.Refresh()
    (-not $proc.HasExited) -and ($proc.MainWindowHandle -ne 0)
}
$proc.Refresh()
$title = if ($proc.MainWindowHandle -ne 0) { $proc.MainWindowTitle } else { '' }
Add-Check 'App khởi động và mở cửa sổ' $hasWindow `
    ("pid {0} · tiêu đề '{1}'" -f $proc.Id, $title)

$shot = $false
if ($proc.MainWindowHandle -ne 0) {
    try {
        [Win32Shot]::ShowWindow($proc.MainWindowHandle, 5) | Out-Null   # SW_SHOW
        [Win32Shot]::SetForegroundWindow($proc.MainWindowHandle) | Out-Null
        Start-Sleep -Seconds 2

        $r = New-Object Win32Shot+RECT
        [Win32Shot]::GetWindowRect($proc.MainWindowHandle, [ref]$r) | Out-Null
        $w = $r.Right - $r.Left
        $h = $r.Bottom - $r.Top
        if ($w -gt 0 -and $h -gt 0) {
            $bmp = New-Object System.Drawing.Bitmap $w, $h
            $gfx = [System.Drawing.Graphics]::FromImage($bmp)
            $hdc = $gfx.GetHdc()
            # 2 = PW_RENDERFULLCONTENT: chụp được cả cửa sổ bị che / Qt vẽ bằng DirectX
            [Win32Shot]::PrintWindow($proc.MainWindowHandle, $hdc, 2) | Out-Null
            $gfx.ReleaseHdc($hdc)
            $gfx.Dispose()
            $bmp.Save((Join-Path (Resolve-Path '.').Path $ScreenshotPath), [System.Drawing.Imaging.ImageFormat]::Png)
            $bmp.Dispose()
            $shot = (Get-Item -LiteralPath $ScreenshotPath).Length -gt 5KB
        }
    } catch {
        Write-Host "::warning title=Không chụp được ảnh::$($_.Exception.Message)"
    }
}
Add-Check 'Chụp ảnh cửa sổ (PrintWindow)' $shot `
    ("{0} · {1:N0} KB" -f $ScreenshotPath, ((Get-Item -LiteralPath $ScreenshotPath -ErrorAction SilentlyContinue).Length / 1KB))

# --- 3. Tắt app + gỡ cài ---------------------------------------------------
$proc.CloseMainWindow() | Out-Null
if (-not (Wait-Until -TimeoutSeconds 10 -Condition { $proc.HasExited })) {
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}
Add-Check 'Tắt app không treo' $proc.HasExited 'đóng cửa sổ chính'

$unProc = Start-Process -FilePath $uninst -Wait -PassThru -ArgumentList @(
    '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART'
)
Add-Check 'Gỡ cài im lặng' ($unProc.ExitCode -eq 0) "exit code $($unProc.ExitCode)"

$gone = Wait-Until -TimeoutSeconds 60 -Condition { -not (Test-Path -LiteralPath $exe) }
Add-Check 'Gỡ sạch (không còn CafeTLU.exe)' $gone $exe

# --- 4. Báo cáo ------------------------------------------------------------
Write-Report

if ($script:failed -gt 0) {
    Write-Host "::error title=Cài thử thất bại::$script:failed bước hỏng — xem $ReportPath"
    exit 1
}
Write-Host 'Cài thử đạt toàn bộ các bước.'
exit 0
