"""
Módulo de Modelos y Entidades del Dominio.
Define las estructuras de datos fundamentales para el sistema de créditos.
Principio SOLID:
- SRP (Single Responsibility Principle): Estas clases solo representan datos
  y su estado; no contienen lógica de base de datos ni interfaz gráfica.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class EstadoCredito(Enum):
    """Representa el estado final de una solicitud de crédito."""
    APROBADO = "APROBADO"
    NEGADO = "NEGADO"


@dataclass(frozen=True)
class SolicitudCredito:
    """
    Entidad inmutable que transporta los datos de entrada para la evaluación.
    
    Campos según el documento:
    - tipo_doc: Tipo de documento (ej. 'CC', 'CE', 'PAS')
    - nro_doc: Número de documento (ej. '12234587')
    - ingresos_totales: Ingresos mensuales totales
    - egresos_totales: Gastos o egresos mensuales totales
    - monto_solicitado: Monto total del crédito solicitado
    - plazo_solicitado: Plazo del crédito en meses
    """
    tipo_doc: str
    nro_doc: str
    ingresos_totales: float
    egresos_totales: float
    monto_solicitado: float
    plazo_solicitado: int

    def __post_init__(self) -> None:
        """Validaciones básicas de integridad de tipos y valores positivos."""
        if not self.tipo_doc or not self.tipo_doc.strip():
            raise ValueError("El tipo de documento no puede estar vacío.")
        if not self.nro_doc or not self.nro_doc.strip():
            raise ValueError("El número de documento no puede estar vacío.")
        if self.ingresos_totales < 0:
            raise ValueError("Los ingresos totales no pueden ser negativos.")
        if self.egresos_totales < 0:
            raise ValueError("Los egresos totales no pueden ser negativos.")
        if self.monto_solicitado <= 0:
            raise ValueError("El monto solicitado debe ser mayor a cero.")
        if not isinstance(self.plazo_solicitado, int):
            raise TypeError("El plazo solicitado debe ser un número entero de meses.")


@dataclass(frozen=True)
class ResultadoPreaprobacion:
    """
    Entidad inmutable que encapsula el veredicto final de la evaluación crediticia.
    """
    estado: EstadoCredito
    aprobado: bool
    mensaje: str
    balanza: Optional[float] = None
    relacion_credito_balanza: Optional[float] = None
    puntaje_central: Optional[int] = None
