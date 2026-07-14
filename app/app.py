import os
from datetime import datetime, timezone

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template_string,
    request,
    url_for,
)

app = Flask(__name__)

APP_ENV = os.getenv("APP_ENV", "dev")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0-dev")

ZONES = [
    {
        "name": "Oficinas",
        "occupancy": "Ocupada",
        "lighting": 80,
        "status": "Operativa"
    },
    {
        "name": "Sala de juntas",
        "occupancy": "Desocupada",
        "lighting": 20,
        "status": "Operativa"
    },
    {
        "name": "Almacén",
        "occupancy": "Ocupada",
        "lighting": 100,
        "status": "Operativa"
    },
    {
        "name": "Estacionamiento",
        "occupancy": "Desocupado",
        "lighting": 40,
        "status": "Mantenimiento"
    }
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DCS Simulator</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            margin: 0;
            padding: 30px;
        }

        .container {
            max-width: 950px;
            margin: auto;
        }

        .header {
            background: #1f2937;
            color: white;
            padding: 25px;
            border-radius: 8px;
        }

        .cards {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 20px;
        }

        .card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            min-width: 180px;
            flex: 1;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.10);
        }

        table {
            width: 100%;
            margin-top: 20px;
            border-collapse: collapse;
            background: white;
        }

        th, td {
            padding: 12px;
            border-bottom: 1px solid #dddddd;
            text-align: left;
        }

        th {
            background: #e5e7eb;
        }

        .online {
            color: green;
            font-weight: bold;
        }

        .environment {
            text-transform: uppercase;
            font-weight: bold;
        }

        .lighting-form {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .lighting-input {
            width: 65px;
            padding: 7px;
        }

        .update-button {
            border: none;
            border-radius: 5px;
            padding: 8px 12px;
            background: #2563eb;
            color: white;
            cursor: pointer;
        }

        .update-button:hover {
            background: #1d4ed8;
        }

        .footer {
            margin-top: 20px;
            color: #555555;
        }
    </style>
</head>

<body>
    <div class="container">

        <div class="header">
            <h1>DCS Building Monitoring Simulator</h1>

            <p>
                Ambiente:
                <span class="environment">{{ environment }}</span>
            </p>

            <p>Versión: {{ version }}</p>
        </div>

        <div class="cards">
            <div class="card">
                <h3>Estado general</h3>
                <p class="online">Operativo</p>
            </div>

            <div class="card">
                <h3>Controladores</h3>
                <p>4 conectados</p>
            </div>

            <div class="card">
                <h3>Dispositivos</h3>
                <p>125 registrados</p>
            </div>

            <div class="card">
                <h3>Dispositivos offline</h3>
                <p>3 dispositivos</p>
            </div>
        </div>

        <h2>Zonas de iluminación</h2>

        <table>
            <thead>
                <tr>
                    <th>Zona</th>
                    <th>Ocupación</th>
                    <th>Iluminación</th>
                    <th>Estado</th>
                </tr>
            </thead>

            <tbody>
                {% for zone in zones %}
                <tr>
                    <td>{{ zone.name }}</td>
                    <td>{{ zone.occupancy }}</td>

                    <td>
                        <form
                            class="lighting-form"
                            action="{{ url_for(
                                'update_lighting',
                                zone_name=zone.name
                            ) }}"
                            method="post"
                        >
                            <input
                                class="lighting-input"
                                type="number"
                                name="lighting"
                                min="0"
                                max="100"
                                value="{{ zone.lighting }}"
                                required
                            >

                            <span>%</span>

                            <button
                                class="update-button"
                                type="submit"
                            >
                                Actualizar
                            </button>
                        </form>
                    </td>

                    <td>{{ zone.status }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <div class="footer">
            <p>Aplicación de demostración para despliegues DevOps.</p>
            <p>Health check: <strong>/health</strong></p>
            <p>API de estado: <strong>/api/status</strong></p>
        </div>

    </div>
</body>
</html>
"""


def find_zone(zone_name):
    return next(
        (
            zone
            for zone in ZONES
            if zone["name"].lower() == zone_name.lower()
        ),
        None
    )


def is_valid_lighting(lighting):
    return isinstance(lighting, int) and 0 <= lighting <= 100


@app.route("/")
def index():
    return render_template_string(
        HTML_TEMPLATE,
        environment=APP_ENV,
        version=APP_VERSION,
        zones=ZONES
    )


@app.route("/zones/<zone_name>/lighting", methods=["POST"])
def update_lighting(zone_name):
    zone = find_zone(zone_name)

    if zone is None:
        return jsonify({
            "error": "Zone not found",
            "zone": zone_name
        }), 404

    try:
        lighting = int(request.form.get("lighting", ""))
    except ValueError:
        return jsonify({
            "error": "Lighting must be an integer"
        }), 400

    if not is_valid_lighting(lighting):
        return jsonify({
            "error": "Lighting must be between 0 and 100"
        }), 400

    zone["lighting"] = lighting

    return redirect(url_for("index"))


@app.route("/api/zones/<zone_name>/lighting", methods=["PUT"])
def api_update_lighting(zone_name):
    zone = find_zone(zone_name)

    if zone is None:
        return jsonify({
            "error": "Zone not found",
            "zone": zone_name
        }), 404

    request_data = request.get_json(silent=True) or {}
    lighting = request_data.get("lighting")

    if not is_valid_lighting(lighting):
        return jsonify({
            "error": "Lighting must be an integer between 0 and 100"
        }), 400

    zone["lighting"] = lighting

    return jsonify({
        "message": "Lighting updated successfully",
        "zone": zone["name"],
        "lighting": zone["lighting"],
        "environment": APP_ENV
    }), 200


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "environment": APP_ENV,
        "version": APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200


@app.route("/api/status")
def api_status():
    return jsonify({
        "application": "DCS Building Monitoring Simulator",
        "environment": APP_ENV,
        "version": APP_VERSION,
        "system_status": "operational",
        "controllers_online": 4,
        "devices_total": 125,
        "devices_offline": 3,
        "zones": ZONES
    }), 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
