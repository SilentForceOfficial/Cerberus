param (
    [string]$inputFile,
    [string]$outputFile,
    [switch]$resolvedOnly = $false
)


# Función para mostrar la ayuda
function Show-Help {
    Write-Host ""
    Write-Host "Resolve IP addresses of host names in a file."
    Write-Host ""
    Write-Host "Arguments: "
    Write-Host "    -inputFile      Path to the input file containing host names."
    Write-Host "    -outputFile     Path to the output file where results will be saved."
    Write-Host "    -resolvedOnly   Output only the resolved hosts."
    Write-Host "    -h, --help      Show help."
    Write-Host ""
    Write-Host "Example: ./script.ps1 -inputFile <archivo1> -outputFile <archivo2> -resolvedOnly"
    Write-Host ""
    exit 1
}

function Resolve-IP {
    param (
        [string]$hostName
    )

    try {
        $ipAddress = [System.Net.Dns]::GetHostAddresses($hostName)[0].IPAddressToString
        return $ipAddress
    } catch {
        return "not resolved"
    }
}

function Resolve-IP-Concurrent {
    param (
        [string]$hostName
    )

    $result = @{
        Host = $hostName
        IP = (Resolve-IP -hostName $hostName)
    }
    return $result
}

# Verificar si se proporciona el parámetro -h o --help
if ($args -contains "-h" -or $args -contains "--help") {
    Show-Help
}

# Borra el archivo de salida si ya existe
if (Test-Path $outputFile) {
    Remove-Item $outputFile -Force
}

# Lee todas las líneas del archivo de entrada
$lines = Get-Content $inputFile

# Inicializa arrays para datos resueltos y no resueltos
$resolvedDataArray = @()
$unresolvedDataArray = @()

# Resuelve IP para cada línea y muestra por pantalla
foreach ($line in $lines) {
    $resolvedData = Resolve-IP-Concurrent -hostName $line

    if ($resolvedData.IP -ne "not resolved") {
        $resolvedDataArray += $resolvedData
    } else {
        $unresolvedDataArray += $resolvedData
    }

}

if ($resolvedOnly) {
    foreach ($resolved in $resolvedDataArray){
        Add-Content -Path $outputFile -Value "$($resolved.Host)-$($resolved.IP)"
    }
} else {
    foreach ($resolved in $resolvedDataArray){
        Add-Content -Path $outputFile -Value "$($resolved.Host)-$($resolved.IP)"
    }
    foreach ($resolved in $unresolvedDataArray){
        Add-Content -Path $outputFile -Value "$($resolved.Host)-$($resolved.IP)"
    }
}

# Imprime la cantidad de hosts detectados, resueltos y no resueltos
Write-Host "$($lines.Count) hosts detected."
Write-Host "|-$($resolvedDataArray.Count) hosts resolved."
Write-Host "|-$($unresolvedDataArray.Count) hosts not resolved."
Write-Host "Results output: '$outputFile'."


