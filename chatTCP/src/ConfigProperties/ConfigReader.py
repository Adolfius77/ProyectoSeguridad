import os
from typing import Any, Optional


class ConfigReader:
    """
    Clase para leer archivos .properties de configuración.
    Soporta comentarios (#) y pares clave=valor.
    """

    def __init__(self, archivo_config: str):
        """
        Inicializa el lector de configuración.

        Args:
            archivo_config: Ruta al archivo .properties

        Raises:
            FileNotFoundError: Si el archivo no existe
        """
        if not os.path.exists(archivo_config):
            raise FileNotFoundError(f"Archivo de configuración no encontrado: {archivo_config}")

        self.archivo_config = archivo_config
        self.propiedades = {}
        self._cargar_propiedades()

    def _cargar_propiedades(self) -> None:
        """
        Carga las propiedades desde el archivo.
        Ignora líneas vacías y comentarios (#).
        """
        with open(self.archivo_config, 'r', encoding='utf-8') as archivo:
            for linea in archivo:
                linea = linea.strip()

                # Ignorar líneas vacías y comentarios
                if not linea or linea.startswith('#'):
                    continue

                # Buscar separador = o :
                if '=' in linea:
                    clave, valor = linea.split('=', 1)
                elif ':' in linea:
                    clave, valor = linea.split(':', 1)
                else:
                    continue

                # Limpiar espacios
                clave = clave.strip()
                valor = valor.strip()

                self.propiedades[clave] = valor

    def obtener(self, clave: str, valor_defecto: Optional[Any] = None) -> Any:
        """
        Obtiene el valor de una propiedad.

        Args:
            clave: Nombre de la propiedad (ej: "host" o "puerto.entrada")
            valor_defecto: Valor a retornar si la clave no existe

        Returns:
            El valor de la propiedad o valor_defecto si no existe
        """
        return self.propiedades.get(clave, valor_defecto)

    def obtener_str(self, clave: str, valor_defecto: str = "") -> str:
        """
        Obtiene una propiedad como string.

        Args:
            clave: Nombre de la propiedad
            valor_defecto: Valor por defecto si no existe

        Returns:
            El valor como string
        """
        return str(self.obtener(clave, valor_defecto))

    def obtener_int(self, clave: str, valor_defecto: int = 0) -> int:
        """
        Obtiene una propiedad como entero.

        Args:
            clave: Nombre de la propiedad
            valor_defecto: Valor por defecto si no existe o no es convertible

        Returns:
            El valor como entero
        """
        valor = self.obtener(clave)
        if valor is None:
            return valor_defecto

        try:
            return int(valor)
        except ValueError:
            return valor_defecto

    def obtener_bool(self, clave: str, valor_defecto: bool = False) -> bool:
        """
        Obtiene una propiedad como booleano.
        Valores true: "true", "yes", "1", "on"
        Valores false: "false", "no", "0", "off"

        Args:
            clave: Nombre de la propiedad
            valor_defecto: Valor por defecto si no existe

        Returns:
            El valor como booleano
        """
        valor = self.obtener(clave)
        if valor is None:
            return valor_defecto

        valor_lower = str(valor).lower()
        if valor_lower in ("true", "yes", "1", "on"):
            return True
        elif valor_lower in ("false", "no", "0", "off"):
            return False
        else:
            return valor_defecto

    def obtener_todas(self) -> dict:
        """
        Retorna todas las propiedades como diccionario.

        Returns:
            Diccionario con todas las propiedades
        """
        return self.propiedades.copy()

    def existe(self, clave: str) -> bool:
        """
        Verifica si una clave existe en las propiedades.

        Args:
            clave: Nombre de la propiedad

        Returns:
            True si existe, False si no
        """
        return clave in self.propiedades

    def __repr__(self) -> str:
        return f"ConfigReader(archivo='{self.archivo_config}', propiedades={len(self.propiedades)})"
