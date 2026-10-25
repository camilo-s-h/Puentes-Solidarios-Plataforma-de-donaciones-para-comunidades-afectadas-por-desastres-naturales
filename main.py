
import flet as ft
from almacenamiento import AlmacenamientoCSV
from servicios import ServicioDonaciones


def main(page: ft.Page):
    page.title = "Puentes Solidarios"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO

    servicio = ServicioDonaciones(AlmacenamientoCSV())
    contenido = ft.Column(spacing=12)
    mensaje = ft.Text()

    def avisar(texto, error=False):
        mensaje.value = texto
        mensaje.color = "red" if error else "green"
        page.update()

    def campo(etiqueta, ancho=300):
        return ft.TextField(label=etiqueta, width=ancho)

    def boton(texto, accion):
        return ft.Button(texto, on_click=accion)

    def tabla(titulos, filas):
        if not filas:
            return ft.Text("Todavía no hay registros.")

        return ft.DataTable(
            columns=[ft.DataColumn(ft.Text(t)) for t in titulos],
            rows=[
                ft.DataRow(
                    cells=[ft.DataCell(ft.Text(str(v))) for v in fila]
                )
                for fila in filas
            ],
        )

    def mostrar(vista):
        contenido.controls.clear()
        mensaje.value = ""

        if vista == "Inicio":
            r = servicio.resumen()
            contenido.controls.extend([
                ft.Text("Panel general", size=26, weight=ft.FontWeight.BOLD),
                ft.Text(
                    f"Campañas: {r['campanas_total']} | "
                    f"Activas: {r['campanas_activas']} | "
                    f"Cerradas: {r['campanas_cerradas']}"
                ),
                ft.Text(
                    f"Donaciones: {r['donaciones_total']} | "
                    f"Registradas: {r['registradas']} | "
                    f"Recibidas: {r['recibidas']} | "
                    f"Entregadas: {r['entregadas']}"
                ),
                ft.Text("Cantidades por recurso", size=18),
                tabla(
                    ["Recurso", "Unidad", "Cantidad"],
                    [
                        [x["recurso"], x["unidad"], x["cantidad"]]
                        for x in r["cantidades_por_recurso"]
                    ],
                ),
                ft.Text(
                    "Los estados son reportados por usuarios. "
                    "La aplicación no verifica las entregas de forma "
                    "independiente.",
                    size=12,
                ),
            ])

        elif vista == "Campañas":
            nombre, ubicacion = campo("Nombre de la campaña"), campo("Ubicación")
            recurso = campo("Recurso solicitado")
            meta, unidad = campo("Meta de cantidad", 150), campo("Unidad", 150)
            descripcion = campo("Descripción", 500)

            def crear(e):
                try:
                    servicio.crear_campana(
                        nombre.value, ubicacion.value, descripcion.value or "",
                        recurso.value, meta.value, unidad.value,
                    )
                    mostrar("Campañas")
                    avisar("Campaña creada correctamente.")
                except (ValueError, RuntimeError) as ex:
                    avisar(str(ex), True)

            campanas = servicio.listar_campanas()
            selector = ft.Dropdown(
                label="Campaña",
                width=350,
                options=[
                    ft.dropdown.Option(
                        c["id"], f'{c["nombre"]} ({c["estado"]})'
                    )
                    for c in campanas
                ],
            )
            estado = ft.Dropdown(
                label="Estado",
                width=150,
                value="Cerrada",
                options=[
                    ft.dropdown.Option("Activa"),
                    ft.dropdown.Option("Cerrada"),
                ],
            )

            def cambiar(e):
                try:
                    if not selector.value:
                        raise ValueError("Selecciona una campaña.")
                    servicio.cambiar_estado_campana(
                        selector.value, estado.value
                    )
                    mostrar("Campañas")
                    avisar("Estado actualizado.")
                except (ValueError, RuntimeError) as ex:
                    avisar(str(ex), True)

            filas = []
            for c in campanas:
                total = sum(
                    float(d["cantidad"])
                    for d in servicio.listar_donaciones()
                    if d["campana_id"] == c["id"]
                    and d["recurso"].casefold() == c["recurso_solicitado"].casefold()
                    and d["unidad"].casefold() == c["unidad"].casefold()
                )
                avance = min(100, total / float(c["meta_cantidad"]) * 100)
                filas.append([
                    c["nombre"], c["ubicacion"], c["recurso_solicitado"],
                    f'{total:g}/{float(c["meta_cantidad"]):g} {c["unidad"]}',
                    f"{avance:.0f}%", c["estado"],
                ])

            contenido.controls.extend([
                ft.Text("Campañas", size=26, weight=ft.FontWeight.BOLD),
                ft.Row([nombre, ubicacion], wrap=True),
                ft.Row([recurso, meta, unidad], wrap=True),
                descripcion,
                boton("Crear campaña", crear),
                ft.Divider(),
                ft.Text("Cerrar o reabrir campañas", size=18),
                ft.Row(
                    [selector, estado, boton("Actualizar estado", cambiar)],
                    wrap=True,
                ),
                tabla(
                    ["Nombre", "Ubicación", "Recurso", "Avance", "%", "Estado"],
                    filas,
                ),
            ])

        elif vista == "Donaciones":
            campanas = [
                c for c in servicio.listar_campanas()
                if c["estado"] == "Activa"
            ]
            selector = ft.Dropdown(
                label="Campaña activa",
                width=350,
                options=[
                    ft.dropdown.Option(c["id"], c["nombre"])
                    for c in campanas
                ],
            )
            donante, recurso = campo("Donante"), campo("Recurso", 200)
            cantidad, unidad = campo("Cantidad", 130), campo("Unidad", 130)
            observacion = campo("Observación", 500)

            def crear(e):
                try:
                    servicio.crear_donacion(
                        selector.value, donante.value, recurso.value,
                        cantidad.value, unidad.value, observacion.value or "",
                    )
                    mostrar("Donaciones")
                    avisar("Donación registrada correctamente.")
                except (ValueError, RuntimeError) as ex:
                    avisar(str(ex), True)

            donaciones = servicio.listar_donaciones()
            contenido.controls.extend([
                ft.Text("Donaciones", size=26, weight=ft.FontWeight.BOLD),
                selector,
                ft.Row([donante, recurso, cantidad, unidad], wrap=True),
                observacion,
                boton("Registrar donación", crear),
                ft.Divider(),
                tabla(
                    ["ID", "Donante", "Recurso", "Cantidad", "Estado"],
                    [
                        [
                            d["id"], d["donante"], d["recurso"],
                            f'{float(d["cantidad"]):g} {d["unidad"]}',
                            d["estado"],
                        ]
                        for d in donaciones
                    ],
                ),
            ])

        elif vista == "Seguimiento":
            donaciones = servicio.listar_donaciones()
            selector = ft.Dropdown(
                label="Donación",
                width=400,
                options=[
                    ft.dropdown.Option(
                        d["id"],
                        f'{d["donante"]} — {d["recurso"]} — {d["estado"]}',
                    )
                    for d in donaciones
                ],
            )
            estado = ft.Dropdown(
                label="Estado",
                width=180,
                value="Recibida",
                options=[
                    ft.dropdown.Option(s)
                    for s in ("Registrada", "Recibida", "Entregada")
                ],
            )
            observacion = campo("Observación", 300)
            referencia = campo("Referencia de evidencia", 300)

            def actualizar(e):
                try:
                    servicio.actualizar_seguimiento(
                        selector.value, estado.value,
                        observacion.value or "", referencia.value or "",
                    )
                    mostrar("Seguimiento")
                    avisar("Seguimiento actualizado.")
                except (ValueError, RuntimeError) as ex:
                    avisar(str(ex), True)

            contenido.controls.extend([
                ft.Text("Seguimiento", size=26, weight=ft.FontWeight.BOLD),
                selector,
                ft.Row([estado, observacion, referencia], wrap=True),
                boton("Actualizar seguimiento", actualizar),
                tabla(
                    ["Donación", "Estado", "Observación", "Referencia", "Fecha"],
                    [
                        [
                            s["donacion_id"], s["estado"], s["observacion"],
                            s["referencia_evidencia"], s["fecha_creacion"],
                        ]
                        for s in servicio.listar_seguimientos()
                    ],
                ),
            ])

        page.update()

    page.add(
        ft.Text("PUENTES SOLIDARIOS", size=28, weight=ft.FontWeight.BOLD),
        ft.Text("Gestión de donaciones para comunidades afectadas por desastres"),
        ft.Row(
            [
                boton(v, lambda e, nombre=v: mostrar(nombre))
                for v in ("Inicio", "Campañas", "Donaciones", "Seguimiento")
            ],
            wrap=True,
        ),
        mensaje,
        ft.Divider(),
        contenido,
    )
    mostrar("Inicio")


if __name__ == "__main__":
    ft.run(main)
