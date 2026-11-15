param([string]$EngineRoot=$env:UE_ROOT)
$ErrorActionPreference = 'Stop'
$projectDir = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$project = Join-Path $projectDir 'ElPuestitoPiloto.uproject'
if (-not $EngineRoot) { throw 'Define UE_ROOT con la ruta de Unreal Engine 5.8.' }
$engineDir = (Resolve-Path $EngineRoot).Path
$build = Join-Path $engineDir 'Build/BatchFiles/Build.bat'
$uat = Join-Path $engineDir 'Build/BatchFiles/RunUAT.bat'
if (-not (Test-Path $build) -or -not (Test-Path $uat)) { throw 'Unreal Engine no se encontro en la ruta indicada.' }
& $build ElPuestitoPilotoEditor Win64 Development `"-Project=$project`" -WaitMutex
if ($LASTEXITCODE -ne 0) { throw 'Fallo la compilacion C++ del editor.' }
$archive = Join-Path $projectDir 'Build/Package'
& $uat BuildCookRun `"-project=$project`" -noP4 -platform=Win64 -clientconfig=Development -build -cook '-map=/Game/RestauranteCompleto/RestauranteNoche' -stage -pak -package -archive `"-archivedirectory=$archive`" -utf8output
if ($LASTEXITCODE -ne 0) { throw 'Fallo el empaquetado de Unreal.' }
Write-Host `"Paquete listo en $archive`"
