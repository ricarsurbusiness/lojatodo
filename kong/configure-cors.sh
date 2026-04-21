#!/bin/bash
# Script para configurar CORS en Kong Gateway
# Ejecutar: bash kong/configure-cors.sh

echo "Configurando CORS en Kong..."

# Añadir plugin CORS globalmente
curl -X POST http://localhost:9001/plugins \
  -H "Content-Type: application/json" \
  -d '{
    "name": "cors",
    "config": {
      "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
      "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
      "headers": ["Accept", "Accept-Language", "Content-Type", "Authorization", "X-Requested-With"],
      "exposed_headers": ["X-Total-Count", "X-Page-Count"],
      "credentials": true,
      "max_age": 3600
    }
  }'

echo ""
echo "CORS configurado. Verificando..."
curl -s http://localhost:9001/plugins | jq '.data[] | select(.name == "cors")'