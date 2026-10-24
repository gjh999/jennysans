# JennySans — Windows 사용자 범위 설치 실측 (관리자 권한 불필요). 게이트 4·7 (spec 02 §8-4).
# 실행: powershell -ExecutionPolicy Bypass -File docs/qa/scripts/win-install-test.ps1 [-KeepInstalled]
#  1) dist/static/*.ttf 9 + dist/variable/JennySansVariable.ttf 를 %LOCALAPPDATA%\Microsoft\Windows\Fonts 에 복사
#  2) HKCU\Software\Microsoft\Windows NT\CurrentVersion\Fonts 에 "<Full name> (TrueType)" = 경로 등록 + AddFontResource + WM_FONTCHANGE
#  3) 열거: (a) GDI — System.Drawing InstalledFontCollection (b) DirectWrite 계열 — WPF System.Windows.Media.Fonts.SystemFontFamilies(FamilyTypefaces 굵기)
#  4) GDI 렌더 PNG: docs/qa/shots/win-gdi-<Family>.png (한·영·es·숫자·기호)
#  5) 제거: RemoveFontResource → 레지스트리 값 삭제 → 파일 삭제 → 재열거로 제거 확인(다른 프로세스가 잡고 있으면 기록)
# 결과: docs/qa/results/win-install.md
param([switch]$KeepInstalled)
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$FontDir = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
$RegKey = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
$Shots = Join-Path $Root "docs\qa\shots"
$Out = Join-Path $Root "docs\qa\results\win-install.md"
$Files = @(Get-ChildItem (Join-Path $Root "dist\static\JennySans-*.ttf")) + @(Get-Item (Join-Path $Root "dist\variable\JennySansVariable.ttf"))
$Log = New-Object System.Collections.Generic.List[string]
function L($s) { $Log.Add($s); Write-Host $s }

Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName PresentationCore
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class GdiFont {
  [DllImport("gdi32.dll", CharSet=CharSet.Unicode)] public static extern int AddFontResourceW(string lpszFilename);
  [DllImport("gdi32.dll", CharSet=CharSet.Unicode)] public static extern bool RemoveFontResourceW(string lpszFilename);
  [DllImport("user32.dll")] public static extern IntPtr SendMessageTimeout(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam, uint fuFlags, uint uTimeout, out IntPtr lpdwResult);
  public static void Broadcast() { IntPtr r; SendMessageTimeout((IntPtr)0xffff, 0x001D, IntPtr.Zero, IntPtr.Zero, 2, 1000, out r); }
}
"@

function Get-FullName($path) {
  # name ID 4 (Windows 영어) 을 fontTools 로 읽는다(PowerShell 만으로 name 테이블 파싱을 피함)
  $py = "import sys; from fontTools.ttLib import TTFont; f=TTFont(sys.argv[1], lazy=True); print(f['name'].getDebugName(4))"
  $env:PYTHONUTF8 = "1"
  return (& python -c $py $path).Trim()
}

L "# Windows 사용자 범위 설치 실측 — $(Get-Date -Format 'yyyy-MM-dd HH:mm') (PowerShell $($PSVersionTable.PSVersion), $([System.Environment]::OSVersion.VersionString))"
L ""
L "폰트 폴더: $FontDir · 레지스트리: $RegKey"
L ""

# 0) 사전 상태
$pre = @(Get-ChildItem $FontDir -Filter "JennySans*" -ErrorAction SilentlyContinue)
$preReg = @(Get-ItemProperty $RegKey -ErrorAction SilentlyContinue).PSObject.Properties | Where-Object { $_.Name -like "*JennySans*" }
L "사전 상태: 폴더 내 JennySans 파일 $($pre.Count), 레지스트리 값 $(@($preReg).Count)"
if ($pre.Count -gt 0 -or @($preReg).Count -gt 0) { L "  → 이전 잔존물 발견, 먼저 정리한다" }
foreach ($p in $preReg) { Remove-ItemProperty -Path $RegKey -Name $p.Name -ErrorAction SilentlyContinue }
foreach ($f in $pre) { [GdiFont]::RemoveFontResourceW($f.FullName) | Out-Null; Remove-Item $f.FullName -Force -ErrorAction SilentlyContinue }

# 1) 설치
New-Item -ItemType Directory -Force $FontDir | Out-Null
$installed = @()
L ""
L "## 설치"
L ""
L "| 파일 | Full name(ID 4) | 레지스트리 값 이름 | AddFontResource |"
L "|---|---|---|---|"
foreach ($f in $Files) {
  $dst = Join-Path $FontDir $f.Name
  Copy-Item $f.FullName $dst -Force
  $full = Get-FullName $f.FullName
  $valName = "$full (TrueType)"
  New-ItemProperty -Path $RegKey -Name $valName -Value $dst -PropertyType String -Force | Out-Null
  $n = [GdiFont]::AddFontResourceW($dst)
  $installed += [pscustomobject]@{ File = $f.Name; Full = $full; Val = $valName; Path = $dst }
  L "| $($f.Name) | $full | $valName | $n |"
}
[GdiFont]::Broadcast()
Start-Sleep -Milliseconds 800

# 2) 열거 (GDI)
L ""
L "## 열거 (a) GDI — System.Drawing.Text.InstalledFontCollection"
L ""
$coll = New-Object System.Drawing.Text.InstalledFontCollection
$fams = $coll.Families | Where-Object { $_.Name -like "*JennySans*" -or $_.Name -like "*제니산스*" }
L "| 패밀리 | Regular | Bold | Italic | BoldItalic |"
L "|---|---|---|---|---|"
foreach ($fam in $fams) {
  L "| $($fam.Name) | $($fam.IsStyleAvailable([System.Drawing.FontStyle]::Regular)) | $($fam.IsStyleAvailable([System.Drawing.FontStyle]::Bold)) | $($fam.IsStyleAvailable([System.Drawing.FontStyle]::Italic)) | $($fam.IsStyleAvailable([System.Drawing.FontStyle]::Bold -bor [System.Drawing.FontStyle]::Italic)) |"
}
L ""
L "GDI 패밀리 수: $(@($fams).Count) (기대 16 = 정적 8: JennySans(Regular+Bold 링크) + Thin/ExtraLight/Light/Medium/SemiBold/ExtraBold/Black 7 — ko-KR 로캘에서는 '제니산스 <W>' 로 표시될 수 있음 + 변수 8: 'JennySans Variable' + Windows 10+ 가 명명 인스턴스를 GDI 패밀리로 노출한 7)"

# 3) 열거 (DirectWrite 계열 — WPF)
L ""
L "## 열거 (b) DirectWrite 계열 — System.Windows.Media.Fonts.SystemFontFamilies (typographic family + FamilyTypefaces)"
L ""
$wpf = [System.Windows.Media.Fonts]::SystemFontFamilies | Where-Object { $_.Source -like "*JennySans*" -or $_.Source -like "*제니산스*" }
L "| 패밀리(Source) | FamilyNames(언어별) | Typeface 수 | Weight/Style 목록 |"
L "|---|---|---|---|"
foreach ($w in $wpf) {
  $names = ($w.FamilyNames.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join "; "
  $tfs = @($w.FamilyTypefaces | ForEach-Object { "$($_.Weight)/$($_.Style)" })
  L "| $($w.Source) | $names | $($tfs.Count) | $($tfs -join ', ') |"
}
L ""
L "DirectWrite 계열 패밀리 수: $(@($wpf).Count) (기대 2: 'JennySans' 9 typefaces + 'JennySans Variable')"
# 폰트 폴더에서 직접 읽기(설치 여부와 무관한 파일 자체의 패밀리 묶임)
L ""
L "폴더 직접 열거 GetFontFamilies('$FontDir'):"
$dir = [System.Windows.Media.Fonts]::GetFontFamilies((New-Object System.Uri ($FontDir + "\"))) | Where-Object { $_.Source -like "*JennySans*" -or $_.Source -like "*제니산스*" }
foreach ($w in $dir) {
  $tfs = @($w.FamilyTypefaces | ForEach-Object { "$($_.Weight)/$($_.Style)" })
  L "- $($w.Source): $($tfs.Count) typefaces — $($tfs -join ', ')"
}

# 4) GDI 렌더 PNG
L ""
L "## GDI 렌더 (System.Drawing Graphics.DrawString, ClearType)"
L ""
$sample = @("제니산스 다람쥐 헌 쳇바퀴에 타고파 똠방각하 뷁 힣", "¿Qué tal, señor? ¡Año nuevo! Ñandú, pingüino, 1ª 2º, 12,50 €", "The quick brown fox jumps over the lazy dog 0123456789", "※ ①②③ ㉠㉡㉢ ㈜ ㎏ ← → ★ ○ ◎ ■ ◇ ┌─┬─┐│└┴┘ ∠∴ ± × ÷ ≠ ⅔ ∼ ≒ ◈ 간 ㅥ")
$bmp = New-Object System.Drawing.Bitmap 1800, (60 + 9 * 150 + 150)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.Clear([System.Drawing.Color]::White)
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
$label = New-Object System.Drawing.Font("Segoe UI", 10)
$g.DrawString("JennySans 1.000 — Windows GDI (System.Drawing) user-scope install test $(Get-Date -Format 'yyyy-MM-dd HH:mm')", $label, [System.Drawing.Brushes]::Gray, 20, 16)
$y = 50
$gdiRows = @()
foreach ($spec in @(@("JennySans Thin", "Regular"), @("JennySans ExtraLight", "Regular"), @("JennySans Light", "Regular"), @("JennySans", "Regular"), @("JennySans Medium", "Regular"), @("JennySans SemiBold", "Regular"), @("JennySans", "Bold"), @("JennySans ExtraBold", "Regular"), @("JennySans Black", "Regular"), @("JennySans Variable", "Regular"))) {
  $famName = $spec[0]; $style = [System.Drawing.FontStyle]::($spec[1])
  try {
    $fnt = New-Object System.Drawing.Font($famName, 22, $style, [System.Drawing.GraphicsUnit]::Pixel)
    $actual = $fnt.FontFamily.Name
    # GDI 는 시스템 로캘(ko-KR)의 name ID 1(제니산스 …)로 패밀리를 부를 수 있다 → 영문/한국어 현지화명 모두 같은 패밀리로 인정
    $koName = $famName -replace "^JennySans", "제니산스"
    $ok = ($actual -eq $famName) -or ($actual -eq $koName)
    $g.DrawString("$famName / $($spec[1]) → $actual", $label, [System.Drawing.Brushes]::Gray, 20, $y)
    $yy = $y + 18
    foreach ($s in $sample) { $g.DrawString($s, $fnt, [System.Drawing.Brushes]::Black, 20, $yy); $yy += 30 }
    $gdiRows += "| $famName | $($spec[1]) | $actual | $(if ($ok) {'OK'} else {'폴백!'}) |"
    $fnt.Dispose()
  } catch { $gdiRows += "| $famName | $($spec[1]) | 오류 $($_.Exception.Message) | FAIL |" }
  $y += 150
}
$png = Join-Path $Shots "win-gdi-all-weights.png"
$bmp.Save($png, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
L "| 요청 패밀리 | 스타일 | 실제 패밀리(Font.FontFamily.Name) | 판정 |"
L "|---|---|---|---|"
$gdiRows | ForEach-Object { L $_ }
L ""
L "렌더 PNG: docs/qa/shots/win-gdi-all-weights.png"

if ($KeepInstalled) { L ""; L "-KeepInstalled: 제거 생략"; $Log | Set-Content -Path $Out -Encoding UTF8; exit 0 }

# 5) 제거
L ""
L "## 제거"
L ""
$coll.Dispose()
[GC]::Collect(); [GC]::WaitForPendingFinalizers()
$removeRows = @()
foreach ($i in $installed) {
  $r = [GdiFont]::RemoveFontResourceW($i.Path)
  Remove-ItemProperty -Path $RegKey -Name $i.Val -ErrorAction SilentlyContinue
  $delOk = $true
  try { Remove-Item $i.Path -Force -ErrorAction Stop } catch { $delOk = $false; $err = $_.Exception.Message }
  if (-not $delOk) {
    # 다른 프로세스가 잡고 있을 수 있음 — 잠시 후 재시도
    Start-Sleep -Seconds 2
    try { Remove-Item $i.Path -Force -ErrorAction Stop; $delOk = $true } catch { $err = $_.Exception.Message }
  }
  $removeRows += "| $($i.File) | $r | $(if ($delOk) {'삭제됨'} else {"삭제 실패: $err (다른 앱이 폰트를 잡고 있음 — 로그아웃 후 삭제 필요)"}) |"
}
[GdiFont]::Broadcast()
L "| 파일 | RemoveFontResource | 파일 삭제 |"
L "|---|---|---|"
$removeRows | ForEach-Object { L $_ }
Start-Sleep -Milliseconds 500
$post = @(Get-ChildItem $FontDir -Filter "JennySans*" -ErrorAction SilentlyContinue)
$postReg = @((Get-ItemProperty $RegKey -ErrorAction SilentlyContinue).PSObject.Properties | Where-Object { $_.Name -like "*JennySans*" })
$coll2 = New-Object System.Drawing.Text.InstalledFontCollection
$fams2 = @($coll2.Families | Where-Object { $_.Name -like "*JennySans*" })
$wpf2 = @([System.Windows.Media.Fonts]::SystemFontFamilies | Where-Object { $_.Source -like "*JennySans*" })
L ""
L "제거 후: 폴더 잔존 $($post.Count), 레지스트리 잔존 $($postReg.Count), GDI 열거 잔존 $($fams2.Count), WPF 열거 잔존 $($wpf2.Count) (WPF 는 프로세스 캐시로 남을 수 있음 — 폴더·레지스트리 0 이면 제거 완료)"
$verdict = if ($post.Count -eq 0 -and $postReg.Count -eq 0) { "PASS" } else { "FAIL" }
L ""
L "제거 판정: **$verdict**"
$Log | Set-Content -Path $Out -Encoding UTF8
Write-Host "→ $Out"
