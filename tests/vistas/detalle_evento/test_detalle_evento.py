"""Vista 26: Detalle de evento."""

from datetime import date

from app.models import EventoAdverso

URL = "/eventos-adversos"
ENTRAN = {"admin", "agricultor"}


async def crear(cliente, finca, riesgo):
    cuerpo = {
        "finca_id": str(finca.id),
        "riesgo_id": str(riesgo.id),
        "inicio": date.today().isoformat(),
        "severidad": "severa",
        "perdida_pct": 40,
    }
    return (await cliente.post(URL, json=cuerpo)).json()["id"]


async def test_acceso_segun_el_rol(cliente, entrar_como, f, clave):
    yo = await entrar_como(clave)
    finca = await f.finca(yo)
    riesgo = await f.riesgo()
    if clave in ENTRAN:
        evento = await crear(cliente, finca, riesgo)
        assert (await cliente.get(f"{URL}/{evento}")).status_code == 200
    else:
        assert (await cliente.get(f"{URL}/00000000-0000-0000-0000-000000000000")).status_code == 403


async def test_actualiza_severidad_y_conserva_la_perdida(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    evento = await crear(cliente, await f.finca(yo), await f.riesgo())
    r = await cliente.patch(
        f"{URL}/{evento}", json={"severidad": "moderada", "notas": "Menos daño"}
    )
    assert r.json()["severidad"] == "moderada"
    assert r.json()["perdida_pct"] == 40.0


async def test_el_evento_de_otro_no_se_abre(cliente, entrar_como, f):
    await entrar_como("agricultor")
    otro = await f.usuario()
    finca = await f.finca(otro)
    riesgo = await f.riesgo()
    ajeno = EventoAdverso(
        finca_id=finca.id, riesgo_id=riesgo.id, inicio=date.today(), severidad="leve"
    )
    f.s.add(ajeno)
    await f.s.commit()
    assert (await cliente.get(f"{URL}/{ajeno.id}")).status_code == 404
    assert (await cliente.patch(f"{URL}/{ajeno.id}", json={"notas": "x"})).status_code == 404


async def test_la_fecha_final_no_puede_ser_anterior(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    evento = await crear(cliente, await f.finca(yo), await f.riesgo())
    r = await cliente.patch(f"{URL}/{evento}", json={"fin": "2000-01-01"})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "EVENTO_FECHAS_INVALIDAS"
