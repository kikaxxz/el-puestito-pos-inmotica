param([string]$Destination)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (-not $Destination) { $Destination = Join-Path $projectRoot 'dist' }
$buildRoot = Join-Path $projectRoot 'build/demo'
Set-Location $projectRoot
$env:APPDATA = Join-Path $buildRoot 'Profile'
$env:PUESTITO_DB_PATH = Join-Path $env:APPDATA 'demo.db'
$env:PUESTITO_DEMO = '1'
$env:TESTING = 'true'
$env:PUESTITO_BUILD_ASSETS = Join-Path $buildRoot 'Assets'
New-Item $env:APPDATA -ItemType Directory -Force | Out-Null
New-Item $env:PUESTITO_BUILD_ASSETS -ItemType Directory -Force | Out-Null
py -3.13 packaging/prepare_demo_assets.py
if ($LASTEXITCODE -ne 0) { throw 'No se prepararon los recursos.' }
py -3.13 -m PyInstaller --noconfirm --distpath $Destination --workpath (Join-Path $buildRoot 'PyInstaller') packaging/ElPuestito_POS.spec
if ($LASTEXITCODE -ne 0) { throw 'No se pudo empaquetar el POS.' }
