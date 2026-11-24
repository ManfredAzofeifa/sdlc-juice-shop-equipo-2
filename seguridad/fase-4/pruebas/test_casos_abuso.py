"""Pruebas escritas desde los casos de abuso (fase 4).

Reglas:
* Cada prueba lleva @pytest.mark.caso_abuso(N), donde N es el número del issue
  del caso de abuso del que sale.
* La prueba afirma el comportamiento seguro, el «Entonces» del requerimiento.
  Por eso falla mientras la app siga vulnerable: rojo esperado en la fase 4.
* Cuando el equipo corrige la debilidad (fase 5), la prueba suma
  @pytest.mark.corregida y el gate del release exige que pase.

Ejecución local, con la app levantada (bash lab/app.sh levantar):
    pytest seguridad/fase-4/pruebas -v
"""
from uuid import uuid4

import pytest
import requests


def crear_usuario(app_url: str):
    """Registra una cuenta temporal y devuelve correo, contraseña y canasta."""
    correo = f"fase4-{uuid4().hex}@example.test"
    contrasena = "Fase4-prueba-segura"
    registro = requests.post(
        f"{app_url}/api/Users",
        json={
            "email": correo,
            "password": contrasena,
            "passwordRepeat": contrasena,
            "securityQuestion": {"id": 1},
            "securityAnswer": "respuesta de prueba",
        },
        timeout=10,
    )
    assert registro.status_code == 201, registro.text

    inicio = requests.post(
        f"{app_url}/rest/user/login",
        json={"email": correo, "password": contrasena},
        timeout=10,
    )
    assert inicio.status_code == 200, inicio.text
    autenticacion = inicio.json()["authentication"]
    return correo, contrasena, autenticacion["bid"]


def iniciar_sesion(app_url: str, correo: str, contrasena: str):
    respuesta = requests.post(
        f"{app_url}/rest/user/login",
        json={"email": correo, "password": contrasena},
        timeout=10,
    )
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()["authentication"]["token"]


@pytest.mark.caso_abuso(3)
def test_cambio_de_contrasena_exige_contrasena_actual(app_url, sesion):
    """Dado un cliente autenticado con una contraseña vigente
    Cuando el servidor no puede verificar la contraseña actual en una solicitud de cambio
    Entonces rechaza el cambio y conserva la contraseña vigente."""
    correo, contrasena_actual, _ = crear_usuario(app_url)
    token = iniciar_sesion(app_url, correo, contrasena_actual)
    contrasena_nueva = "Nueva-clave-segura"

    cambio = sesion.get(
        f"{app_url}/rest/user/change-password",
        params={
            "new": contrasena_nueva,
            "repeat": contrasena_nueva,
        },
        headers={"Authorization": f"Bearer={token}"},
        timeout=10,
    )

    ingreso_con_actual = sesion.post(
        f"{app_url}/rest/user/login",
        json={
            "email": correo,
            "password": contrasena_actual,
        },
        timeout=10,
    )

    ingreso_con_nueva = sesion.post(
        f"{app_url}/rest/user/login",
        json={
            "email": correo,
            "password": contrasena_nueva,
        },
        timeout=10,
    )

    assert cambio.status_code in {401, 403}, (f"La API no devolvió el rechazo esperado (401 o 403) al omitir la contraseña actual: HTTP {cambio.status_code}")
    assert ingreso_con_actual.status_code == 200, ("La contraseña anterior dejó de funcionar tras el intento sin contraseña actual.")
    assert ingreso_con_nueva.status_code in {401, 403}, ("La contraseña nueva funciona aunque nunca se presentó la contraseña actual.")


@pytest.mark.caso_abuso(5)
def test_usuario_no_puede_leer_canasta_de_otra_persona(app_url, sesion):
    """Dado un cliente autenticado y una canasta que pertenece a otra persona
    Cuando el cliente solicita consultar esa canasta
    Entonces el servidor deniega el acceso y no devuelve los datos de la canasta."""
    correo_a, contrasena_a, canasta_a = crear_usuario(app_url)
    correo_b, contrasena_b, canasta_b = crear_usuario(app_url)
    token_a = iniciar_sesion(app_url, correo_a, contrasena_a)
    token_b = iniciar_sesion(app_url, correo_b, contrasena_b)

    encabezados_a = {"Authorization": f"Bearer {token_a}"}
    encabezados_b = {"Authorization": f"Bearer {token_b}"}

    propia = sesion.get(
        f"{app_url}/rest/basket/{canasta_a}",
        headers=encabezados_a,
        timeout=10,
    )
    assert propia.status_code == 200, (
        "La solicitud de control sobre la canasta propia falló, "
        "no se puede evaluar correctamente el permiso sobre la canasta ajena. "
        f"HTTP {propia.status_code}: {propia.text}"
    )

    existencia_objetivo = sesion.get(
        f"{app_url}/rest/basket/{canasta_b}",
        headers=encabezados_b,
        timeout=10,
    )
    assert existencia_objetivo.status_code == 200, (
        "No se pudo verificar la existencia de la canasta objetivo con su propietario. "
        f"HTTP {existencia_objetivo.status_code}"
    )

    ajena = sesion.get(
        f"{app_url}/rest/basket/{canasta_b}",
        headers=encabezados_a,
        timeout=10,
    )

    assert ajena.status_code in {403, 404}, (
        "La API permitió consultar una canasta ajena. "
        f"HTTP {ajena.status_code}: {ajena.text}"
    )

    if "application/json" in ajena.headers.get("Content-Type", "").lower():
        cuerpo = ajena.json()
        if isinstance(cuerpo, dict):
            for campo in ("data", "basket"):
                assert not cuerpo.get(campo), (f"La respuesta denegada contiene datos en '{campo}': {cuerpo}")
        else:
            assert not cuerpo, f"La respuesta denegada contiene datos: {cuerpo}"
    else:
        assert not ajena.text.strip(), (f"La respuesta denegada no JSON devolvió contenido: {ajena.text}")


@pytest.mark.caso_abuso(7)
def test_respuesta_no_expone_hash_de_contrasena(app_url, sesion):
    """Dado un usuario autenticado
    Cuando solicita sus datos indicando campos adicionales
    Entonces la API no entrega su contraseña ni su hash
    """
    correo, contrasena, _ = crear_usuario(app_url)
    token = iniciar_sesion(app_url, correo, contrasena)

    respuesta = sesion.get(
        f"{app_url}/rest/user/whoami",
        params={"fields": "id,email,password"},
        cookies={"token": token},
        timeout=10,
    )

    assert respuesta.status_code == 200, (f"No fue posible consultar los datos del usuario autenticado. HTTP {respuesta.status_code}")

    cuerpo = respuesta.json()
    usuario = cuerpo.get("user") if isinstance(cuerpo, dict) else None
    assert isinstance(usuario, dict) and usuario, ("La respuesta no incluyó un objeto de usuario válido para validar la cuenta.")
    assert usuario.get("email") == correo, ("La respuesta no corresponde al correo de la cuenta autenticada.")

    campos_sensibles = {"password", "passwordhash", "hash"}
    claves_encontradas = {k.lower() for k in usuario.keys()} & campos_sensibles
    assert not claves_encontradas, (f"La respuesta expuso campos sensibles de credenciales: {sorted(claves_encontradas)}")