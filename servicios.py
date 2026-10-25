from modelos import Campana, Donacion, Seguimiento


class ServicioDonaciones:
    ESTADOS_CAMPANA = ("Activa", "Cerrada")

    def __init__(self, almacenamiento):
        self.almacenamiento = almacenamiento

    def listar_campanas(self):
        return self.almacenamiento.listar("campanas")

    def listar_donaciones(self):
        return self.almacenamiento.listar("donaciones")

    def listar_seguimientos(self):
        return self.almacenamiento.listar("seguimientos")

    @staticmethod
    def _texto(valor, campo):
        if valor is None or not str(valor).strip():
            raise ValueError(f"{campo} es obligatorio.")
        return str(valor).strip()

    @staticmethod
    def _cantidad(valor, campo):
        try:
            numero = float(valor)
        except (TypeError, ValueError) as error:
            raise ValueError(f"{campo} debe ser un número válido.") from error

        if numero <= 0:
            raise ValueError(f"{campo} debe ser mayor que cero.")
        return numero

    def crear_campana(
        self, nombre, ubicacion, descripcion, recurso, meta, unidad
    ):
        nombre = self._texto(nombre, "El nombre")
        ubicacion = self._texto(ubicacion, "La ubicación")
        recurso = self._texto(recurso, "El recurso")
        unidad = self._texto(unidad, "La unidad")
        meta = self._cantidad(meta, "La meta")

        campana = Campana(
            nombre, ubicacion, descripcion or "",
            recurso, meta, unidad,
        )
        self.almacenamiento.agregar("campanas", campana)
        return campana

    def cambiar_estado_campana(self, campana_id, estado):
        if estado not in self.ESTADOS_CAMPANA:
            raise ValueError("El estado de la campaña no es válido.")

        fila = next(
            (c for c in self.listar_campanas() if c["id"] == campana_id),
            None,
        )
        if not fila:
            raise ValueError("No se encontró la campaña.")

        campana = Campana(
            fila["nombre"], fila["ubicacion"], fila["descripcion"],
            fila["recurso_solicitado"], fila["meta_cantidad"],
            fila["unidad"], estado, fila["id"], fila["fecha_creacion"],
        )
        self.almacenamiento.reemplazar("campanas", campana_id, campana)
        return campana

    def crear_donacion(
        self, campana_id, donante, recurso, cantidad, unidad, observacion=""
    ):
        campana = next(
            (c for c in self.listar_campanas() if c["id"] == campana_id),
            None,
        )
        if not campana:
            raise ValueError("Selecciona una campaña existente.")
        if campana["estado"] != "Activa":
            raise ValueError("No se puede donar a una campaña cerrada.")

        donante = self._texto(donante, "El donante")
        recurso = self._texto(recurso, "El recurso")
        unidad = self._texto(unidad, "La unidad")
        cantidad = self._cantidad(cantidad, "La cantidad")

        donacion = Donacion(
            campana_id, donante, recurso, cantidad, unidad, observacion or ""
        )
        self.almacenamiento.agregar("donaciones", donacion)

        seguimiento = Seguimiento(
            donacion.id, "Registrada", "Donación registrada"
        )
        self.almacenamiento.agregar("seguimientos", seguimiento)
        return donacion

    def actualizar_seguimiento(
        self, donacion_id, estado, observacion="", referencia_evidencia=""
    ):
        if estado not in Seguimiento.ESTADOS:
            raise ValueError("Selecciona un estado válido.")

        donacion = next(
            (d for d in self.listar_donaciones() if d["id"] == donacion_id),
            None,
        )
        if not donacion:
            raise ValueError("No se encontró la donación.")

        orden = {estado: i for i, estado in enumerate(Seguimiento.ESTADOS)}
        if orden[estado] < orden[donacion["estado"]]:
            raise ValueError("El seguimiento no puede retroceder.")

        observacion = observacion or ""
        referencia_evidencia = referencia_evidencia or ""

        if estado in ("Recibida", "Entregada") and not (
            observacion.strip() or referencia_evidencia.strip()
        ):
            raise ValueError(
                "Agrega una observación o referencia para registrar "
                "la recepción o entrega."
            )

        actualizada = Donacion(
            donacion["campana_id"], donacion["donante"],
            donacion["recurso"], donacion["cantidad"], donacion["unidad"],
            donacion["observacion"], estado, donacion["id"],
            donacion["fecha_creacion"],
        )
        self.almacenamiento.reemplazar(
            "donaciones", donacion_id, actualizada
        )

        evento = Seguimiento(
            donacion_id, estado, observacion, referencia_evidencia
        )
        self.almacenamiento.agregar("seguimientos", evento)
        return evento

    def resumen(self):
        campanas = self.listar_campanas()
        donaciones = self.listar_donaciones()
        cantidades = {}

        for donacion in donaciones:
            clave = (
                donacion["recurso"].casefold().strip(),
                donacion["unidad"].casefold().strip(),
            )
            if clave not in cantidades:
                cantidades[clave] = {
                    "recurso": donacion["recurso"],
                    "unidad": donacion["unidad"],
                    "cantidad": 0.0,
                }
            cantidades[clave]["cantidad"] += float(donacion["cantidad"])

        return {
            "campanas_total": len(campanas),
            "campanas_activas": sum(
                c["estado"] == "Activa" for c in campanas
            ),
            "campanas_cerradas": sum(
                c["estado"] == "Cerrada" for c in campanas
            ),
            "donaciones_total": len(donaciones),
            "registradas": sum(
                d["estado"] == "Registrada" for d in donaciones
            ),
            "recibidas": sum(
                d["estado"] == "Recibida" for d in donaciones
            ),
            "entregadas": sum(
                d["estado"] == "Entregada" for d in donaciones
            ),
            "cantidades_por_recurso": list(cantidades.values()),
        }
    