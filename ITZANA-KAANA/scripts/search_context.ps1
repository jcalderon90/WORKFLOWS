# search_context.ps1 - Navegacion rapida del proyecto Itz'ana / Kaan
# Uso: .\scripts\search_context.ps1 -topic <tema> [-name <nombre>]
# Temas: status | architecture | credentials | kb | workflow | node

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("status","architecture","credentials","kb","workflow","node")]
    [string]$topic,
    [string]$name = ""
)

$root = Split-Path $PSScriptRoot -Parent
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

if ($topic -eq "status") {
    Write-Host "=== ESTADO DEL PROYECTO ===" -ForegroundColor Cyan
    $lines = Get-Content "$root\BUILD.md" -Encoding UTF8
    $lines[8..43] | ForEach-Object { Write-Host $_ }
}

if ($topic -eq "architecture") {
    Write-Host "=== ARQUITECTURA / FLUJO ===" -ForegroundColor Cyan
    $lines = Get-Content "$root\CLAUDE.md" -Encoding UTF8
    $lines[12..35] | ForEach-Object { Write-Host $_ }
}

if ($topic -eq "credentials") {
    Write-Host "=== CREDENCIALES N8N ===" -ForegroundColor Cyan
    $lines = Get-Content "$root\CLAUDE.md" -Encoding UTF8
    $lines[54..66] | ForEach-Object { Write-Host $_ }
}

if ($topic -eq "kb") {
    Write-Host "=== KB ITZANA - CHUNKS POR CATEGORIA ===" -ForegroundColor Cyan
    $kb = Get-Content "$root\KBs\KB_ITZANA.json" -Raw -Encoding UTF8 | ConvertFrom-Json
    $categorias = $kb | Group-Object categoria
    foreach ($cat in $categorias) {
        Write-Host ""
        Write-Host "[$($cat.Name)] - $($cat.Count) chunks" -ForegroundColor Yellow
        foreach ($chunk in $cat.Group) {
            $pregunta = $chunk.pregunta -replace "`n", " "
            if ($pregunta.Length -gt 90) { $pregunta = $pregunta.Substring(0,90) + "..." }
            Write-Host "  $($chunk.id)" -ForegroundColor White
            Write-Host "    $pregunta" -ForegroundColor Gray
        }
    }
    Write-Host ""
    Write-Host "Total: $($kb.Count) chunks" -ForegroundColor Green
}

if ($topic -eq "workflow") {
    if ($name -eq "") {
        Write-Host "Workflows disponibles:" -ForegroundColor Cyan
        Get-ChildItem "$root\workflows\*.json" | ForEach-Object { Write-Host "  $($_.BaseName)" }
        Write-Host ""
        Write-Host "Uso: -topic workflow -name <nombre>" -ForegroundColor Gray
    } else {
        $file = Get-ChildItem "$root\workflows\*.json" | Where-Object { $_.BaseName -like "*$name*" } | Select-Object -First 1
        if (-not $file) {
            Write-Host "Workflow no encontrado: $name" -ForegroundColor Red
        } else {
            Write-Host "=== NODOS: $($file.BaseName) ===" -ForegroundColor Cyan
            $wf = Get-Content $file.FullName -Raw | ConvertFrom-Json
            foreach ($node in $wf.nodes) {
                $type = $node.type -replace "^.*\.", ""
                Write-Host "  [$type] $($node.name)" -ForegroundColor White
            }
            Write-Host ""
            Write-Host "Conexiones:" -ForegroundColor Yellow
            $wf.connections.PSObject.Properties | ForEach-Object {
                $targets = @()
                if ($_.Value.main) {
                    foreach ($arr in $_.Value.main) {
                        if ($arr) { foreach ($conn in $arr) { $targets += $conn.node } }
                    }
                }
                if ($targets.Count -gt 0) {
                    Write-Host "  $($_.Name) -> $($targets -join ', ')" -ForegroundColor Gray
                }
            }
        }
    }
}

if ($topic -eq "node") {
    if ($name -eq "") {
        Write-Host "Uso: -topic node -name <nombre_nodo>" -ForegroundColor Gray
    } else {
        Write-Host "=== BUSCANDO NODO: $name ===" -ForegroundColor Cyan
        foreach ($file in Get-ChildItem "$root\workflows\*.json") {
            $wf = Get-Content $file.FullName -Raw | ConvertFrom-Json
            $found = $wf.nodes | Where-Object { $_.name -like "*$name*" }
            if ($found) {
                Write-Host ""
                Write-Host "Workflow: $($file.BaseName)" -ForegroundColor Yellow
                foreach ($node in $found) {
                    Write-Host "  Nodo: $($node.name)" -ForegroundColor White
                    Write-Host "  Tipo: $($node.type) v$($node.typeVersion)" -ForegroundColor Gray
                    $params = $node.parameters | ConvertTo-Json -Depth 2 -Compress
                    if ($params.Length -gt 400) { $params = $params.Substring(0,400) + "..." }
                    Write-Host "  Params: $params" -ForegroundColor Gray
                }
            }
        }
    }
}
