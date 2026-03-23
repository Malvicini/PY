<#
install_msedgedriver.ps1

Detects the local Microsoft Edge version and downloads the matching msedgedriver
(zip) into the project folder (default) or a specified destination.

Usage (PowerShell):
  # run in project folder (recommended)
  .\install_msedgedriver.ps1

  # or pass a destination folder
  .\install_msedgedriver.ps1 -Destination 'H:\96-GESTIONE_STUDI\PY'

This script uses Invoke-WebRequest and Expand-Archive which are available on
Windows PowerShell 5.1+. It will not change your system PATH; it places the
extracted driver in the destination folder.

Security notes:
- The script performs HTTPS downloads from msedgedriver.azureedge.net
- It does not modify system settings or install packages globally
- Run only on a trusted network and machine
#>
param(
    [string]$Destination = (Get-Location).Path,
    [switch]$Force
)

function Write-ErrExit($msg, $code=1){
    Write-Host "ERROR: $msg" -ForegroundColor Red
    exit $code
}

Write-Host "Destination: $Destination"

if(-not (Test-Path $Destination)){
    try{ New-Item -ItemType Directory -Path $Destination -Force | Out-Null } catch { Write-ErrExit "Cannot create destination directory: $_" }
}

# Try to detect Edge executable path
$edgePaths = @(
    'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
)
$edgeExe = $null
foreach($p in $edgePaths){ if(Test-Path $p){ $edgeExe = $p; break } }

# If not found, try registry/where
if(-not $edgeExe){
    $possible = (Get-Command msedge -ErrorAction SilentlyContinue).Source
    if($possible){ $edgeExe = $possible }
}

# Get version
$version = $null
if($edgeExe){
    try{
        $vi = (Get-Item $edgeExe).VersionInfo.ProductVersion
        if($vi){ $version = $vi }
    } catch {}
}

if(-not $version){
    Write-Host "Could not auto-detect Edge version."
    $version = Read-Host "Enter Edge version (example: 142.0.3595.80) or press Enter to abort"
    if([string]::IsNullOrWhiteSpace($version)){
        Write-ErrExit "Edge version not provided. Aborting."
    }
}

Write-Host "Detected Edge version: $version"

# Build download URL - use full version
$base = "https://msedgedriver.azureedge.net"
$zipName = "edgedriver_win64.zip"
$url = "$base/$version/$zipName"

$tmpZip = Join-Path $env:TEMP "msedgedriver_$([System.Guid]::NewGuid().ToString()).zip"

Write-Host "Downloading msedgedriver from: $url"
try{
    Invoke-WebRequest -Uri $url -OutFile $tmpZip -UseBasicParsing -ErrorAction Stop
} catch {
    Write-ErrExit "Download failed: $($_.Exception.Message). If your machine is offline or the version is not available, try a different version or download manually from https://developer.microsoft.com/microsoft-edge/tools/webdriver/"
}

Write-Host "Extracting to $Destination"
try{
    Expand-Archive -Path $tmpZip -DestinationPath $Destination -Force
} catch {
    Remove-Item $tmpZip -ErrorAction SilentlyContinue
    Write-ErrExit "Failed to extract archive: $($_.Exception.Message)"
}

# The zip usually contains msedgedriver.exe in a folder (e.g., msedgedriver.exe)
# Move driver to destination root if necessary
$found = Get-ChildItem -Path $Destination -Filter msedgedriver.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
if($found){
    $target = Join-Path $Destination 'msedgedriver.exe'
    if($found.FullName -ne $target){
        try{ Copy-Item -Path $found.FullName -Destination $target -Force }
        catch { Write-ErrExit "Failed to copy msedgedriver.exe: $_" }
    }
    Write-Host "msedgedriver.exe is at: $target"
} else {
    Write-Host "Warning: msedgedriver.exe not found under $Destination after extraction. Listing files:"
    Get-ChildItem -Path $Destination | Select-Object Name,Mode,Length | Format-Table
}

# cleanup
Remove-Item $tmpZip -ErrorAction SilentlyContinue

Write-Host "Done. You can now pass the driver path to the app modal or place it in the project root."
Write-Host "Example driver path: $(Join-Path $Destination 'msedgedriver.exe')" -ForegroundColor Green
