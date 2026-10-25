import csv
import os
from pathlib import Path


ESQUEMAS = {
    "campanas": [
        "id", "fecha_creacion", "nombre", "ubicacion", "descripcion",
        "recurso_solicitado", "meta_cantidad", "unidad", "estado",
    ],
    "donaciones": [
        "id", "fecha_creacion", "campana_id", "donante", "recurso",
        "cantidad", "unidad", "observacion", "estado",
    ],
    "seguimientos": [
        "id", "fecha_creacion", "donacion_id", "estado",
        "observacion", "referencia_evidencia",
    ],
}


class AlmacenamientoCSV:
    def __init__(self, carpeta="datos"):
        self.carpeta = Path(carpeta)
        self.carpeta.mkdir(parents=True, exist_ok=True)
        self.rutas = {
            nombre: self.carpeta / f"{nombre}.csv"
            for nombre in ESQUEMAS
        }

        for tabla, ruta in self.rutas.items():
            if not ruta.exists():
                self._escribir(tabla, [])

    def listar(self, tabla):
        self._validar(tabla)

        try:
            with self.rutas[tabla].open(
                "r", newline="", encoding="utf-8-sig"
            ) as archivo:
                lector = csv.DictReader(archivo)

                if lector.fieldnames != ESQUEMAS[tabla]:
                    raise ValueError(
                        f"Encabezados incorrectos en {self.rutas[tabla].name}."
                    )

                return list(lector)

        except (OSError, csv.Error) as error:
            raise RuntimeError(f"No se pudo leer el archivo: {error}") from error

    def agregar(self, tabla, registro):
        self._validar(tabla)
        filas = self.listar(tabla)
        fila = registro.a_fila()

        if list(fila) != ESQUEMAS[tabla]:
            raise ValueError("Los datos no coinciden con el esquema CSV.")

        filas.append({clave: str(valor) for clave, valor in fila.items()})
        self._escribir(tabla, filas)

    def reemplazar(self, tabla, identificador, registro):
        self._validar(tabla)
        filas = self.listar(tabla)
        nueva = {k: str(v) for k, v in registro.a_fila().items()}

        if list(nueva) != ESQUEMAS[tabla]:
            raise ValueError("Los datos no coinciden con el esquema CSV.")

        for indice, fila in enumerate(filas):
            if fila["id"] == identificador:
                filas[indice] = nueva
                self._escribir(tabla, filas)
                return

        raise ValueError("No se encontró el registro que se desea actualizar.")

    def _escribir(self, tabla, filas):
        self._validar(tabla)
        ruta = self.rutas[tabla]
        temporal = ruta.with_suffix(".tmp")

        try:
            with temporal.open(
                "w", newline="", encoding="utf-8-sig"
            ) as archivo:
                escritor = csv.DictWriter(
                    archivo, fieldnames=ESQUEMAS[tabla]
                )
                escritor.writeheader()
                escritor.writerows(filas)

            os.replace(temporal, ruta)

        except OSError as error:
            if temporal.exists():
                temporal.unlink()
            raise RuntimeError(f"No se pudo guardar el archivo: {error}") from error

    @staticmethod
    def _validar(tabla):
        if tabla not in ESQUEMAS:
            raise ValueError(f"Tabla no permitida: {tabla}")