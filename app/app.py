import os
from datetime import datetime, timezone

import requests

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

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_LATITUDE = float(os.getenv("WEATHER_LATITUDE", "25.6866"))
WEATHER_LONGITUDE = float(os.getenv("WEATHER_LONGITUDE", "-100.3161"))
WEATHER_TIMEZONE = os.getenv("WEATHER_TIMEZONE", "America/Monterrey")

DAYLIGHTING_STATE = {
    "available": False,
    "is_day": None,
    "cloud_cover": None,
    "recommendation": "Ajuste automático no ejecutado",
    "last_update": None,
    "error": None,
}

DEVICES_OFFLINE = 3

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
        "occupancy": "Desocupada",
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
            max-width: 1050px;
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

        .alert-bar {
            margin-top: 20px;
            padding: 16px 20px;
            border-radius: 8px;
            background: #fef3c7;
            border-left: 6px solid #f59e0b;
            color: #92400e;
        }

        .alert-bar.no-alerts {
            background: #dcfce7;
            border-left-color: #16a34a;
            color: #166534;
        }

        .alert-bar h3 {
            margin-top: 0;
            margin-bottom: 8px;
        }

        .alert-bar ul {
            margin: 0;
            padding-left: 20px;
        }

        table {
            width: 100%;
            margin-top: 20px;
            border-collapse: collapse;
            background: white;
        }

        th,
        td {
            padding: 12px;
            border-bottom: 1px solid #dddddd;
            text-align: left;
            vertical-align: middle;
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

        .lighting-form,
        .occupancy-form {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .lighting-input {
            width: 65px;
            padding: 7px;
        }

        .occupancy-select {
            padding: 7px;
            border: 1px solid #cccccc;
            border-radius: 5px;
        }

        .update-button,
        .occupancy-button {
            border: none;
            border-radius: 5px;
            padding: 8px 12px;
            color: white;
            cursor: pointer;
        }

        .update-button {
            background: #2563eb;
        }

        .update-button:hover {
            background: #1d4ed8;
        }

        .occupancy-button {
            background: #4b5563;
        }

        .occupancy-button:hover {
            background: #374151;
        }

        .status-warning {
            color: #b45309;
            font-weight: bold;
        }

        .status-ok {
            color: #15803d;
            font-weight: bold;
        }

        .daylighting-panel {
            margin-top: 20px;
            padding: 20px;
            border-radius: 8px;
            background: white;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.10);
        }

        .daylighting-panel h2 {
            margin-top: 0;
        }

        .daylighting-button {
            border: none;
            border-radius: 5px;
            padding: 10px 16px;
            background: #059669;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }

        .daylighting-button:hover {
            background: #047857;
        }

        .weather-error {
            color: #b91c1c;
            font-weight: bold;
        }

        .weather-result {
            color: #374151;
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

                {% if alerts %}
                <p class="status-warning">Con alertas</p>
                {% else %}
                <p class="online">Operativo</p>
                {% endif %}
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
                <p>{{ devices_offline }} dispositivos</p>
            </div>
        </div>

        {% if alerts %}
        <div class="alert-bar">
            <h3>Alertas activas: {{ alerts|length }}</h3>

            <ul>
                {% for alert in alerts %}
                <li>{{ alert }}</li>
                {% endfor %}
            </ul>
        </div>
        {% else %}
        <div class="alert-bar no-alerts">
            <h3>Sin alertas activas</h3>
            <p>Todos los sistemas se encuentran operando normalmente.</p>
        </div>
        {% endif %}

        <div class="daylighting-panel">
            <h2>Ajuste automático de daylighting</h2>

            <p>
                Consulta Open-Meteo para detectar si es de día o de noche
                y revisar la nubosidad antes de ajustar la iluminación.
            </p>

            <form
                action="{{ url_for('adjust_daylighting') }}"
                method="post"
            >
                <button
                    class="daylighting-button"
                    type="submit"
                >
                    Aplicar ajuste automático
                </button>
            </form>

            {% if daylighting.error %}
            <p class="weather-error">
                Error: {{ daylighting.error }}
            </p>
            {% elif daylighting.available %}
            <div class="weather-result">
                <p>
                    Momento:
                    <strong>
                        {% if daylighting.is_day %}
                        Día
                        {% else %}
                        Noche
                        {% endif %}
                    </strong>
                </p>

                <p>
                    Nubosidad:
                    <strong>{{ daylighting.cloud_cover }}%</strong>
                </p>

                <p>
                    Resultado:
                    {{ daylighting.recommendation }}
                </p>

                <p>
                    Última actualización:
                    {{ daylighting.last_update }}
                </p>
            </div>
            {% else %}
            <p>El ajuste automático todavía no se ha ejecutado.</p>
            {% endif %}
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

                    <td>
                        <form
                            class="occupancy-form"
                            action="{{ url_for(
                                'update_occupancy',
                                zone_name=zone.name
                            ) }}"
                            method="post"
                        >
                            <select
                                class="occupancy-select"
                                name="occupancy"
                            >
                                <option
                                    value="Ocupada"
                                    {% if zone.occupancy == "Ocupada" %}
                                    selected
                                    {% endif %}
                                >
                                    Ocupada
                                </option>

                                <option
                                    value="Desocupada"
                                    {% if zone.occupancy == "Desocupada" %}
                                    selected
                                    {% endif %}
                                >
                                    Desocupada
                                </option>
                            </select>

                            <button
                                class="occupancy-button"
                                type="submit"
                            >
                                Cambiar
                            </button>
                        </form>
                    </td>

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

                    <td>
                        {% if zone.status == "Operativa" %}
                        <span class="status-ok">{{ zone.status }}</span>
                        {% else %}
                        <span class="status-warning">{{ zone.status }}</span>
                        {% endif %}
                    </td>
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


def get_active_alerts():
    alerts = []

    if DEVICES_OFFLINE > 0:
        alerts.append(
            f"{DEVICES_OFFLINE} dispositivos se encuentran offline."
        )

    for zone in ZONES:
        if zone["status"] != "Operativa":
            alerts.append(
                f'{zone["name"]} requiere atención: {zone["status"]}.'
            )

        if (
            zone["occupancy"] == "Desocupada"
            and zone["lighting"] > 30
        ):
            alerts.append(
                f'{zone["name"]} está desocupada con iluminación '
                f'al {zone["lighting"]}%.'
            )

    return alerts


def get_weather_data():
    parameters = {
        "latitude": WEATHER_LATITUDE,
        "longitude": WEATHER_LONGITUDE,
        "current": "is_day,cloud_cover",
        "timezone": WEATHER_TIMEZONE,
    }

    response = requests.get(
        WEATHER_API_URL,
        params=parameters,
        timeout=5,
    )
    response.raise_for_status()

    data = response.json()
    current = data.get("current", {})

    is_day = current.get("is_day")
    cloud_cover = current.get("cloud_cover")

    if is_day not in (0, 1):
        raise ValueError(
            "Open-Meteo no devolvió un valor válido para is_day"
        )

    if not isinstance(cloud_cover, (int, float)):
        raise ValueError(
            "Open-Meteo no devolvió un valor válido para cloud_cover"
        )

    return {
        "is_day": is_day == 1,
        "cloud_cover": float(cloud_cover),
    }


def calculate_daylighting_level(is_day, cloud_cover, occupancy):
    if occupancy == "Desocupada":
        return 10

    if not is_day:
        return 80

    if cloud_cover <= 30:
        return 30

    if cloud_cover <= 70:
        return 50

    return 70


def apply_daylighting_adjustment():
    weather = get_weather_data()
    is_day = weather["is_day"]
    cloud_cover = weather["cloud_cover"]

    for zone in ZONES:
        zone["lighting"] = calculate_daylighting_level(
            is_day=is_day,
            cloud_cover=cloud_cover,
            occupancy=zone["occupancy"],
        )

    if not is_day:
        recommendation = (
            "Es de noche. Se aumentó la iluminación de las zonas ocupadas."
        )
    elif cloud_cover <= 30:
        recommendation = (
            "Día despejado. Se redujo la iluminación artificial."
        )
    elif cloud_cover <= 70:
        recommendation = (
            "Día parcialmente nublado. Se aplicó iluminación media."
        )
    else:
        recommendation = (
            "Día nublado. Se incrementó la iluminación artificial."
        )

    DAYLIGHTING_STATE.update({
        "available": True,
        "is_day": is_day,
        "cloud_cover": cloud_cover,
        "recommendation": recommendation,
        "last_update": datetime.now(timezone.utc).isoformat(),
        "error": None,
    })

    return DAYLIGHTING_STATE


@app.route("/")
def index():
    return render_template_string(
        HTML_TEMPLATE,
        environment=APP_ENV,
        version=APP_VERSION,
        zones=ZONES,
        alerts=get_active_alerts(),
        devices_offline=DEVICES_OFFLINE,
        daylighting=DAYLIGHTING_STATE,
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


@app.route("/zones/<zone_name>/occupancy", methods=["POST"])
def update_occupancy(zone_name):
    zone = find_zone(zone_name)

    if zone is None:
        return jsonify({
            "error": "Zone not found",
            "zone": zone_name
        }), 404

    occupancy = request.form.get("occupancy", "")

    valid_occupancy_values = {
        "Ocupada",
        "Desocupada"
    }

    if occupancy not in valid_occupancy_values:
        return jsonify({
            "error": "Occupancy must be Ocupada or Desocupada"
        }), 400

    zone["occupancy"] = occupancy

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


@app.route("/api/zones/<zone_name>/occupancy", methods=["PUT"])
def api_update_occupancy(zone_name):
    zone = find_zone(zone_name)

    if zone is None:
        return jsonify({
            "error": "Zone not found",
            "zone": zone_name
        }), 404

    request_data = request.get_json(silent=True) or {}
    occupancy = request_data.get("occupancy")

    valid_occupancy_values = {
        "Ocupada",
        "Desocupada"
    }

    if occupancy not in valid_occupancy_values:
        return jsonify({
            "error": "Occupancy must be Ocupada or Desocupada"
        }), 400

    zone["occupancy"] = occupancy

    return jsonify({
        "message": "Occupancy updated successfully",
        "zone": zone["name"],
        "occupancy": zone["occupancy"],
        "environment": APP_ENV
    }), 200


@app.route("/daylighting/adjust", methods=["POST"])
def adjust_daylighting():
    try:
        apply_daylighting_adjustment()
    except (requests.RequestException, ValueError) as error:
        DAYLIGHTING_STATE.update({
            "available": False,
            "error": str(error),
            "last_update": datetime.now(timezone.utc).isoformat(),
        })

    return redirect(url_for("index"))


@app.route("/api/daylighting/adjust", methods=["POST"])
def api_adjust_daylighting():
    try:
        result = apply_daylighting_adjustment()

        return jsonify({
            "message": "Daylighting adjustment applied",
            "environment": APP_ENV,
            "daylighting": result,
            "zones": ZONES,
        }), 200

    except requests.RequestException as error:
        return jsonify({
            "error": "Weather service unavailable",
            "details": str(error),
        }), 503

    except ValueError as error:
        return jsonify({
            "error": "Invalid weather response",
            "details": str(error),
        }), 502


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
    alerts = get_active_alerts()

    return jsonify({
        "application": "DCS Building Monitoring Simulator",
        "environment": APP_ENV,
        "version": APP_VERSION,
        "system_status": (
            "warning"
            if alerts
            else "operational"
        ),
        "controllers_online": 4,
        "devices_total": 125,
        "devices_offline": DEVICES_OFFLINE,
        "active_alerts": len(alerts),
        "alerts": alerts,
        "daylighting": DAYLIGHTING_STATE,
        "zones": ZONES
    }), 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )