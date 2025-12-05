#!/bin/bash
# Script de verificación de failover automático

echo "======================================"
echo "  VERIFICACIÓN FAILOVER AUTOMÁTICO"
echo "======================================"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_service() {
    local service=$1
    if docker ps | grep -q "$service"; then
        echo -e "${GREEN}✅ $service running${NC}"
        return 0
    else
        echo -e "${RED}❌ $service not running${NC}"
        return 1
    fi
}

echo "1. Verificando monitores en ejecución..."
check_service "mariadb-monitor"
check_service "postgres-monitor"
check_service "mysql-monitor"
echo ""

echo "2. Verificando bases de datos..."
check_service "mariadb-master"
check_service "mariadb-replica"
check_service "postgres_primary"
check_service "postgres_replica"
check_service "mysql_primary"
check_service "mysql_replica"
echo ""

echo "3. Últimos logs de monitores:"
echo ""
echo -e "${YELLOW}=== MariaDB Monitor ===${NC}"
docker logs mariadb-monitor --tail 3 2>/dev/null || echo "Monitor no disponible"
echo ""
echo -e "${YELLOW}=== PostgreSQL Monitor ===${NC}"
docker logs postgres-monitor --tail 3 2>/dev/null || echo "Monitor no disponible"
echo ""
echo -e "${YELLOW}=== MySQL Monitor ===${NC}"
docker logs mysql-monitor --tail 3 2>/dev/null || echo "Monitor no disponible"
echo ""

echo "======================================"
echo "  VERIFICACIÓN COMPLETA"
echo "======================================"
echo ""
echo "Para probar failover:"
echo "  1. docker stop mariadb-master"
echo "  2. docker logs -f mariadb-monitor"
echo ""
