"""
Módulo de Acceso a Datos Simulados en Memoria.

Principios SOLID aplicados:
- DIP (Dependency Inversion Principle): Esta clase concreta depende de la
  abstracción ICentralRiesgo y la implementa.
- LSP (Liskov Substitution Principle): Puede sustituir cualquier otra implementación
  de ICentralRiesgo (como un futuro cliente HTTP de API REST) sin afectar el negocio.
- SRP (Single Responsibility Principle): Su única responsabilidad es gestionar
  y consultar el almacenamiento en memoria de puntajes crediticios.
"""

from typing import Dict, Tuple, Optional
from src.business.interfaces import ICentralRiesgo


class CentralRiesgoEnMemoria(ICentralRiesgo):
    """
    Implementación en memoria de la Central de Riesgo.
    Almacena los puntajes en una estructura de diccionario indexada por (tipo_doc, nro_doc).
    """

    def __init__(self, datos_iniciales: Optional[Dict[Tuple[str, str], int]] = None) -> None:
        """
        Inicializa la base de datos simulada en memoria.
        Si no se proveen datos iniciales, se precarga con casos representativos para pruebas.
        """
        if datos_iniciales is not None:
            self._registros: Dict[Tuple[str, str], int] = dict(datos_iniciales)
        else:
            self._registros = self._obtener_datos_semilla()

    def _obtener_datos_semilla(self) -> Dict[Tuple[str, str], int]:
        """
        Genera el conjunto inicial de datos de prueba cubriendo todos los escenarios exigidos:
        - Registro exacto del diagrama del examen: (CC, 12234587) -> 563
        - Cliente con puntaje excelente / alto: >= 800
        - Cliente con puntaje medio: entre 600 y 799
        - Cliente con puntaje regular: entre 400 y 599
        - Cliente con puntaje deficiente: < 400
        """
        return {
            ("CC", "12234587"): 563,
            
            # Cliente con puntaje sobresaliente (apto para riesgo alto >= 800)
            ("CC", "10000001"): 850,
            
            # Cliente con puntaje alto en el límite exacto (800)
            ("CC", "10000002"): 800,
            
            # Cliente con puntaje medio (apto para riesgo medio >= 600, pero < 800)
            ("CC", "20000001"): 650,
            ("CC", "20000002"): 600,
            
            # Cliente con puntaje moderado (apto solo para riesgo bajo >= 400, pero < 600)
            ("CC", "30000001"): 480,
            ("CC", "30000002"): 400,
            
            # Cliente con puntaje muy bajo (rechazado en todos los tramos < 400)
            ("CC", "40000001"): 250,
            
            # Cliente con documento de extranjería (CE)
            ("CE", "90000001"): 920,
        }

    def consultar_puntaje(self, tipo_doc: str, nro_doc: str) -> Optional[int]:
        """
        Consulta el puntaje del cliente normalizando las cadenas (mayúsculas y sin espacios).
        Retorna el puntaje entero o None si el documento no existe.
        """
        clave = (tipo_doc.strip().upper(), nro_doc.strip())
        return self._registros.get(clave, None)

    def registrar_o_actualizar_cliente(
        self, tipo_doc: str, nro_doc: str, puntaje: int
    ) -> None:
        """
        Permite agregar o actualizar dinámicamente un cliente.
        Muy útil para tests unitarios específicos.
        """
        if not (0 <= puntaje <= 1000):
            raise ValueError("El puntaje debe estar entre 0 y 1000.")
        clave = (tipo_doc.strip().upper(), nro_doc.strip())
        self._registros[clave] = puntaje

    def total_registros(self) -> int:
        """Retorna la cantidad de registros en memoria."""
        return len(self._registros)
