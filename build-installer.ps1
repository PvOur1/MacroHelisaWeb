$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

& .\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean MacroHelisa.spec

$iscc = Get-Command iscc.exe -ErrorAction SilentlyContinue
if ($iscc) {
    & $iscc.Source installer.iss
    exit $LASTEXITCODE
}

$outputDirectory = Join-Path $projectRoot "installer-output"
$sedPath = Join-Path $projectRoot "installer-build\iexpress.sed"
New-Item -ItemType Directory -Force -Path $outputDirectory, (Split-Path $sedPath) | Out-Null

$sed = @"
[Version]
Class=IEXPRESS
SEDVersion=3
[Options]
PackagePurpose=InstallApp
ShowInstallProgramWindow=0
HideExtractAnimation=0
UseLongFileName=1
InsideCompressed=0
CAB_FixedSize=0
CAB_ResvCodeSigning=0
RebootMode=N
InstallPrompt=
DisplayLicense=
FinishMessage=
TargetName=$outputDirectory\Instalar-CargueFacturas.exe
FriendlyName=Instalador de CargueFacturas
AppLaunched=install.cmd
PostInstallCmd=<None>
AdminQuietInstCmd=
UserQuietInstCmd=
SourceFiles=SourceFiles
[Strings]
FILE0="CargueFacturas.exe"
FILE1="install.cmd"
[SourceFiles]
SourceFiles0=$projectRoot\dist\
SourceFiles1=$projectRoot\installer-files\
[SourceFiles0]
%FILE0%=
[SourceFiles1]
%FILE1%=
"@

Set-Content -LiteralPath $sedPath -Value $sed -Encoding ASCII
& "$env:WINDIR\System32\iexpress.exe" /N /Q $sedPath
if ($LASTEXITCODE -ne 0) { throw "IExpress no pudo crear el instalador." }

Get-ChildItem -LiteralPath $outputDirectory -Filter "~Instalar-CargueFacturas.*" -ErrorAction SilentlyContinue |
    Remove-Item -Force
