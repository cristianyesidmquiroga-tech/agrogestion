<#
.SYNOPSIS
    Ejecuta la misma verificacion que la integracion continua, en local.

.DESCRIPTION
    Los cuatro pasos, en el mismo orden y con los mismos comandos. Correrlo
    antes de subir evita el ciclo de "subir, esperar, ver el fallo, corregir".

.PARAMETER Pruebas
    Ruta de pytest a correr (ej. tests/modulos/test_siembras.py, tests/roles/agricultor,
    tests/vistas/mis_siembras). Sin ella corre todo con cobertura.
#>
param([string]$Pruebas = 'tests')
$ErrorActionPreference = 'Stop'

$cobertura = '--cov=app --cov-report=term-missing'
if ($Pruebas -ne 'tests') { $cobertura = '--no-cov' }

Write-Host ""
Write-Host "  AgroGestion - verificacion local" -ForegroundColor Cyan
Write-Host "  --------------------------------" -ForegroundColor DarkGray

$pasos = @(
    @{ nombre = 'Estilo (ruff)';      comando = { ruff check . } },
    @{ nombre = 'Tipado (mypy)';      comando = { mypy --strict app/ } },
    @{ nombre = 'Seguridad (bandit)'; comando = { bandit -r app/ -ll } },
    @{ nombre = 'Pruebas (pytest)';   comando = { pytest $Pruebas $cobertura.Split(" ") } }
)

$fallos = 0
foreach ($paso in $pasos) {
    Write-Host ""
    Write-Host "  > $($paso.nombre)" -ForegroundColor Yellow
    try {
        & $paso.comando
        Write-Host "    OK" -ForegroundColor Green
    } catch {
        Write-Host "    FALLA: $_" -ForegroundColor Red
        $fallos++
    }
}

Write-Host ""
if ($fallos -eq 0) {
    Write-Host "  Los cuatro pasos pasan." -ForegroundColor Green
    exit 0
}
Write-Host "  $fallos paso(s) con hallazgos." -ForegroundColor Red
exit 1
