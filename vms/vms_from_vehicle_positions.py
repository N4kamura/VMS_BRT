import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

PATH_JSON = "./GTFS/rt/vehiclePositions.json"
TZ_LIMA = ZoneInfo("America/Lima")

# Mapeo de ocupación GTFS-RT -> texto corto para PMV
OCCUPANCY_MAP = {
    "EMPTY": "Vacío",
    "MANY_SEATS_AVAILABLE": "Vacío",
    "FEW_SEATS_AVAILABLE": "Medio",
    "STANDING_ROOM_ONLY": "Lleno",
    "CRUSHED_STANDING_ROOM_ONLY": "Lleno",
    "FULL": "Lleno",
    "NOT_ACCEPTING_PASSENGERS": "No aborda",
    None: "s/d",  # sin dato
}

def fmt_hora_local(unix_ts: int) -> str:
    """Convierte timestamp UNIX a hora local Lima (HH:MM:SS)."""
    dt = datetime.fromtimestamp(unix_ts, tz=timezone.utc).astimezone(TZ_LIMA)
    return dt.strftime("%H:%M:%S")

def map_occupancy(status: str) -> str:
    """Mapea el estado de ocupación GTFS-RT a texto corto para PMV."""
    return OCCUPANCY_MAP.get(status, "s/d")

def build_vms_lines(entity: dict) -> tuple[str, str]:
    """
    Construye 2 líneas típicas de un PMV.
    Línea 1: Ruta / Trip
    Línea 2: (ETA placeholder) + Aforo
    Nota: ETA real se calculará luego con paraderos/TripUpdates.
    """
    veh = entity.get("vehicle", {})
    trip = veh.get("trip", {})
    route_id = trip.get("routeId", "-")
    trip_id = trip.get("tripId", "-")
    occ = map_occupancy(veh.get("occupancyStatus"))
    ts = veh.get("timestamp") or 0

    eta_txt = "ETA: -"


    line1 = f"Ruta {route_id} · Trip {trip_id}"
    line2 = f"{eta_txt} · Aforo: {occ} · {fmt_hora_local(ts)}"

    return line1, line2

def main():
    with open(PATH_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    entities = data.get("entity", [])
    for entity in entities:
        if "vehicle" in entity:
            line1, line2 = build_vms_lines(entity)
            print(line1)
            print(line2)
            print("-" * 40)  # Separador entre vehículos

if __name__ == "__main__":
    main()