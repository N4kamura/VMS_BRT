from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

# ---- Función de distancia Haversine (en metros) ----
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # radio de la tierra en m
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))

# ---- Datos de ejemplo: dos posiciones del mismo bus ----
pos1 = {"lat": -12.0530, "lon": -77.0300, "ts": 1735579200}       # t=0
pos2 = {"lat": -12.0521, "lon": -77.0290, "ts": 1735579205}       # t=+5s (100 m más adelante)

# 1. Calcular distancia recorrida
distancia_recorrida = haversine(pos1["lat"], pos1["lon"], pos2["lat"], pos2["lon"])
delta_t = pos2["ts"] - pos1["ts"]  # segundos

# 2. Calcular velocidad promedio (m/s)
velocidad = distancia_recorrida / delta_t

# 3. Calcular ETA hasta un paradero a 1000 m de distancia
distancia_restante = 1000  # metros
eta_segundos = distancia_restante / velocidad
eta_minutos = eta_segundos / 60

print(f"Distancia recorrida: {distancia_recorrida:.1f} m en {delta_t} s")
print(f"Velocidad promedio: {velocidad:.2f} m/s ({velocidad*3.6:.1f} km/h)")
print(f"ETA al paradero (1 km): {eta_segundos:.1f} s ≈ {eta_minutos:.1f} min")