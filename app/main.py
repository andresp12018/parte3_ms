"""
Microservicio proxy en Python usando FastAPI.

Provee 3 endpoints:
- /health : comprobación de salud
- /get    : obtiene todos los empleados desde parte1_ms
- /post   : inserta un empleado en parte1_ms

Este servicio actúa como proxy/cliente de parte1_ms, sin conexión directa a BD.
Comentado en español como pidió el usuario.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import httpx

# --------------------------------------------------
# Configuración: URL del servicio parte1_ms
# --------------------------------------------------
PARTE1_URL = os.getenv("PARTE1_URL", "http://localhost:8000")



app = FastAPI()


@app.on_event("startup")
def startup():
    """Evento de arranque: verifica que parte1_ms esté disponible.

    Intenta conectar 5 veces con 2 segundos de espera entre intentos.
    """
    max_retries = 5
    for attempt in range(max_retries):
        try:
            print(f"Intento {attempt + 1}/{max_retries} de conectar a parte1_ms...")
            with httpx.Client() as client:
                response = client.get(f"{PARTE1_URL}/health")
                if response.status_code == 200:
                    print("✓ Conexión a parte1_ms exitosa")
                    return  # Éxito, salir
        except Exception as e:
            print(f"Error en intento {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print(f"Reintentando en 2 segundos...")
                import time
                time.sleep(2)
            else:
                print("⚠ No se pudo conectar a parte1_ms después de todos los intentos, continuando...")




# Modelo Pydantic para la entrada de /post
class EmpleadoIn(BaseModel):
    nombres: str
    telefono: str


# Modelo de salida
class EmpleadoOut(BaseModel):
    id: int
    nombres: str
    telefono: str




@app.get("/health")
def health():
    """Endpoint de salud simple.

    Retorna un JSON sencillo indicando que la app está viva.
    """
    return {"status": "ok"}


@app.get("/get", response_model=list[EmpleadoOut])
def get_empleados():
    """Obtiene la lista de empleados desde parte1_ms.

    Realiza una llamada GET a parte1_ms/get y devuelve los resultados.
    """
    try:
        with httpx.Client() as client:
            response = client.get(f"{PARTE1_URL}/get")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error llamando a parte1_ms: {e}")


@app.post("/post", response_model=EmpleadoOut)
def create_empleado(payload: EmpleadoIn):
    """Inserta un nuevo empleado en parte1_ms.

    Realiza una llamada POST a parte1_ms/post con los datos del empleado.
    """
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{PARTE1_URL}/post",
                json={"nombres": payload.nombres, "telefono": payload.telefono}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error llamando a parte1_ms: {e}")
