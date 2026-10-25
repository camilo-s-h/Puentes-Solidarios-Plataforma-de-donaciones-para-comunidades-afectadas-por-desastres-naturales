from abc import ABC, abstractmethod
from datetime import datetime
from uuid import uuid4


def nuevo_id():
    return uuid4().hex[:10].upper()


def fecha_actual():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class RegistroBase(ABC):
    def __init__(self, identificador=None, fecha_creacion=None):
        self.id = identificador or nuevo_id()
        self.fecha_creacion = fecha_creacion or fecha_actual()

    @abstractmethod
    def a_fila(self):
        pass


class Campana(RegistroBase):
    def __init__(
        self, nombre, ubicacion, descripcion, recurso_solicitado,
        meta_cantidad, unidad, estado="Activa",
        identificador=None, fecha_creacion=None,
    ):
        super().__init__(identificador, fecha_creacion)
        self.nombre = nombre.strip()
        self.ubicacion = ubicacion.strip()
        self.descripcion = (descripcion or "").strip()
        self.recurso_solicitado = recurso_solicitado.strip()
        self.meta_cantidad = float(meta_cantidad)
        self.unidad = unidad.strip()
        self.estado = estado

    def a_fila(self):
        return {
            "id": self.id,
            "fecha_creacion": self.fecha_creacion,
            "nombre": self.nombre,
            "ubicacion": self.ubicacion,
            "descripcion": self.descripcion,
            "recurso_solicitado": self.recurso_solicitado,
            "meta_cantidad": self.meta_cantidad,
            "unidad": self.unidad,
            "estado": self.estado,
        }


class Donacion(RegistroBase):
    def __init__(
        self, campana_id, donante, recurso, cantidad, unidad,
        observacion="", estado="Registrada",
        identificador=None, fecha_creacion=None,
    ):
        super().__init__(identificador, fecha_creacion)
        self.campana_id = campana_id.strip()
        self.donante = donante.strip()
        self.recurso = recurso.strip()
        self.cantidad = float(cantidad)
        self.unidad = unidad.strip()
        self.observacion = (observacion or "").strip()
        self.estado = estado

    def a_fila(self):
        return {
            "id": self.id,
            "fecha_creacion": self.fecha_creacion,
            "campana_id": self.campana_id,
            "donante": self.donante,
            "recurso": self.recurso,
            "cantidad": self.cantidad,
            "unidad": self.unidad,
            "observacion": self.observacion,
            "estado": self.estado,
        }


class Seguimiento(RegistroBase):
    ESTADOS = ("Registrada", "Recibida", "Entregada")

    def __init__(
        self, donacion_id, estado, observacion="",
        referencia_evidencia="", identificador=None,
        fecha_creacion=None,
    ):
        super().__init__(identificador, fecha_creacion)

        if estado not in self.ESTADOS:
            raise ValueError("El estado del seguimiento no es válido.")

        self.donacion_id = donacion_id.strip()
        self.estado = estado
        self.observacion = (observacion or "").strip()
        self.referencia_evidencia = (referencia_evidencia or "").strip()

    def a_fila(self):
        return {
            "id": self.id,
            "fecha_creacion": self.fecha_creacion,
            "donacion_id": self.donacion_id,
            "estado": self.estado,
            "observacion": self.observacion,
            "referencia_evidencia": self.referencia_evidencia,
        }