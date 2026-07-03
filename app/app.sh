#!/bin/bash

set -e

mkdir -p app/output

cat > app/output/index.html <<EOF
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Proyecto DevOps</title>
</head>
<body>
    <h1>Proyecto final DevOps</h1>
    <p>Aplicación desplegada mediante Docker y Kubernetes.</p>
    <p>Ambiente: ${APP_ENV:-local}</p>
    <p>Versión: ${APP_VERSION:-1.0.0}</p>
</body>
</html>
EOF

echo "Aplicación generada correctamente."
