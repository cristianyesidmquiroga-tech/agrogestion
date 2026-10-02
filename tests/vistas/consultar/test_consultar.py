"""Vista 38: Consultar."""

URL = "/consultas"
ENTRAN = {"admin", "agricultor"}


async def consulta(siembra, texto="Las hojas tienen manchas amarillas"):
    return {"siembra_id": str(siembra.id), "texto": texto}


async def test_acceso_segun_el_rol(cliente, entrar_como, f, clave):
    yo = await entrar_como(clave)
    siembra = await f.siembra(*await f.escenario(yo))
    r = await cliente.post(URL, json=await consulta(siembra))
    assert r.status_code == (201 if clave in ENTRAN else 403)


async def test_sin_sesion_pide_iniciar_sesion(cliente, f):
    yo = await f.usuario()
    siembra = await f.siembra(*await f.escenario(yo))
    assert (await cliente.post(URL, json=await consulta(siembra))).status_code == 401


async def test_la_respuesta_trae_todas_sus_partes(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    finca, lote, cultivo = await f.escenario(yo)
    siembra = await f.siembra(finca, lote, cultivo)
    await f.ficha(
        "Mancha amarilla",
        cultivo=cultivo,
        quimico=("Aplicar según la etiqueta", "Producto Registrado X"),
    )
    r = (await cliente.post(URL, json=await consulta(siembra))).json()["respuesta"]
    assert set(r) == {
        "lo_que_entendi",
        "causas_probables",
        "que_hacer",
        "tratamientos",
        "mensaje_tratamiento",
        "cuando_llamar_al_tecnico",
        "aviso",
        "hay_informacion",
    }
    assert r["causas_probables"][0]["fuentes"]
    assert r["tratamientos"][0]["producto_ica"]


async def test_sin_informacion_pide_asistencia_tecnica(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    siembra = await f.siembra(*await f.escenario(yo))
    r = (await cliente.post(URL, json=await consulta(siembra))).json()["respuesta"]
    assert r["hay_informacion"] is False
    assert "asistencia técnica" in r["cuando_llamar_al_tecnico"]


async def test_valora_la_respuesta_y_puede_corregirla(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    siembra = await f.siembra(*await f.escenario(yo))
    c = (await cliente.post(URL, json=await consulta(siembra))).json()["id"]
    await cliente.post(f"{URL}/{c}/retroalimentacion", json={"valor": "sirvio"})
    r = await cliente.post(
        f"{URL}/{c}/retroalimentacion", json={"valor": "equivocado", "comentario": "Era otra cosa"}
    )
    assert r.json()["valor"] == "equivocado"
    assert (await cliente.get(f"{URL}/{c}")).json()["valoracion"] == "equivocado"


async def test_valida_lo_que_se_escribe(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    siembra = await f.siembra(*await f.escenario(yo))
    assert (await cliente.post(URL, json=await consulta(siembra, "hoy"))).status_code == 422
    assert (
        await cliente.post(
            f"{URL}/00000000-0000-0000-0000-000000000000/retroalimentacion",
            json={"valor": "sirvio"},
        )
    ).status_code == 404
    assert (
        await cliente.post(URL, json={**await consulta(siembra), "foto": "x"})
    ).status_code == 422
