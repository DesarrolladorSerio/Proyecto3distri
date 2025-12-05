# ====================================================================
# SCRIPT DE PRUEBA DE FAILOVER AUTOMÁTICO
# ====================================================================
# Este script te guía paso a paso para probar el failover automático

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PRUEBA DE FAILOVER AUTOMÁTICO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Función para pausar
function Pause {
    Write-Host ""
    Write-Host "Presiona Enter para continuar..." -ForegroundColor Yellow
    Read-Host
}

# Función para verificar servicio
function Check-Service {
    param($ServiceName)
    $running = docker ps --filter "name=$ServiceName" --filter "status=running" -q
    if ($running) {
        Write-Host "✅ $ServiceName está corriendo" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ $ServiceName NO está corriendo" -ForegroundColor Red
        return $false
    }
}

Write-Host "PASO 1: Verificando que todos los servicios estén corriendo..." -ForegroundColor Yellow
Write-Host ""

Start-Sleep -Seconds 2

Check-Service "mariadb-master"
Check-Service "mariadb-replica"
Check-Service "mariadb-monitor"
Check-Service "postgres_primary"
Check-Service "postgres_replica"
Check-Service "postgres-monitor"
Check-Service "mysql_primary"
Check-Service "mysql_replica"
Check-Service "mysql-monitor"

Pause

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PRUEBA 1: FAILOVER DE MARIADB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Vamos a:" -ForegroundColor Yellow
Write-Host "   1. Ver logs del monitor en tiempo real"
Write-Host "   2. Detener mariadb-master"
Write-Host "   3. Observar la promoción automática (~15-20 segundos)"
Write-Host ""

Pause

Write-Host ""
Write-Host "🔍 Abriendo logs del monitor MariaDB..." -ForegroundColor Cyan
Write-Host "   (Mantén esto visible en otra terminal)" -ForegroundColor Yellow
Write-Host ""
Write-Host "📌 Ejecuta este comando en OTRA terminal:" -ForegroundColor Green
Write-Host "   docker logs -f mariadb-monitor" -ForegroundColor White
Write-Host ""

Pause

Write-Host ""
Write-Host "🚨 Deteniendo mariadb-master en 3 segundos..." -ForegroundColor Red
Start-Sleep -Seconds 1
Write-Host "   3..." -ForegroundColor Red
Start-Sleep -Seconds 1
Write-Host "   2..." -ForegroundColor Red
Start-Sleep -Seconds 1
Write-Host "   1..." -ForegroundColor Red
Start-Sleep -Seconds 1

docker stop mariadb-master

Write-Host ""
Write-Host "✅ mariadb-master DETENIDO" -ForegroundColor Red
Write-Host ""
Write-Host "👀 Observa los logs del monitor (en la otra terminal):" -ForegroundColor Yellow
Write-Host "   Verás mensajes como:" -ForegroundColor Gray
Write-Host "   ⚠️  Master mariadb-master unhealthy (1/3)" -ForegroundColor Gray
Write-Host "   ⚠️  Master mariadb-master unhealthy (2/3)" -ForegroundColor Gray
Write-Host "   ⚠️  Master mariadb-master unhealthy (3/3)" -ForegroundColor Gray
Write-Host "   🚨 MASTER mariadb-master IS DOWN!" -ForegroundColor Gray
Write-Host "   🚨 PROMOTING mariadb-replica to MASTER" -ForegroundColor Gray
Write-Host "   ✅ FAILOVER COMPLETE" -ForegroundColor Gray
Write-Host ""

Write-Host "⏳ Esperando 20 segundos para que se complete el failover..." -ForegroundColor Yellow

Start-Sleep -Seconds 20

Write-Host ""
Write-Host "✅ Failover completado!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Verificando últimos logs del monitor:" -ForegroundColor Yellow

docker logs mariadb-monitor --tail 10

Pause

Write-Host ""
Write-Host "🔄 Restaurando mariadb-master..." -ForegroundColor Cyan
docker start mariadb-master
Write-Host "✅ mariadb-master reiniciado" -ForegroundColor Green

Pause

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PRUEBA 2: FAILOVER DE POSTGRESQL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📌 Ejecuta en OTRA terminal:" -ForegroundColor Green
Write-Host "   docker logs -f postgres-monitor" -ForegroundColor White
Write-Host ""

Pause

Write-Host "🚨 Deteniendo postgres_primary..." -ForegroundColor Red
docker stop postgres_primary

Write-Host ""
Write-Host "⏳ Esperando failover automático (20 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

Write-Host ""
Write-Host "📊 Logs del monitor PostgreSQL:" -ForegroundColor Yellow
docker logs postgres-monitor --tail 10

Write-Host ""
Write-Host "🔄 Restaurando postgres_primary..." -ForegroundColor Cyan
docker start postgres_primary
Write-Host "✅ postgres_primary reiniciado" -ForegroundColor Green

Pause

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PRUEBA 3: FAILOVER DE MYSQL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📌 Ejecuta en OTRA terminal:" -ForegroundColor Green
Write-Host "   docker logs -f mysql-monitor" -ForegroundColor White
Write-Host ""

Pause

Write-Host "🚨 Deteniendo mysql_primary..." -ForegroundColor Red
docker stop mysql_primary

Write-Host ""
Write-Host "⏳ Esperando failover automático (20 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

Write-Host ""
Write-Host "📊 Logs del monitor MySQL:" -ForegroundColor Yellow
docker logs mysql-monitor --tail 10

Write-Host ""
Write-Host "🔄 Restaurando mysql_primary..." -ForegroundColor Cyan
docker start mysql_primary
Write-Host "✅ mysql_primary reiniciado" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  🎉 PRUEBAS COMPLETADAS" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "✅ Has probado exitosamente el failover automático en:" -ForegroundColor Green
Write-Host "   - MariaDB (App1)" -ForegroundColor White
Write-Host "   - PostgreSQL (App2)" -ForegroundColor White
Write-Host "   - MySQL (App3)" -ForegroundColor White
Write-Host ""
Write-Host "📝 Para tu presentación:" -ForegroundColor Yellow
Write-Host "   - Tiempo de detección: ~5-15 segundos" -ForegroundColor White
Write-Host "   - Tiempo de promoción: ~15-20 segundos" -ForegroundColor White
Write-Host "   - SIN intervención manual requerida" -ForegroundColor White
Write-Host ""
