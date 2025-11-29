import requests
from requests.auth import HTTPBasicAuth

def obtener_coordenadas(BASE_URL, USUARIO, PASSWORD):
    # Endpoint para obtener las posiciones (generalmente devuelve las últimas)
    url = f"{BASE_URL}/api/positions"
    
    try:
        # Hacemos la petición GET con autenticación básica
        response = requests.get(
            url, 
            auth=HTTPBasicAuth(USUARIO, PASSWORD),
            headers={"Accept": "application/json"}
        )
        
        # Si la respuesta es exitosa (Código 200)
        if response.status_code == 200:
            datos = response.json()
            
            if not datos:
                print("Not found any device.")
                return
            
            for position in datos:
                return position
                
        else:
            print(f"Error connecting: {response.status_code}")
            print(response.text)
            return None

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure Traccar is running.")
        return None