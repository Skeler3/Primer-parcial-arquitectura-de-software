"""
Módulo de Interfaces y Abstracciones de la Capa de Negocio.

Principios SOLID aplicados:
- DIP (Dependency Inversion Principle): Los módulos de alto nivel (la lógica de negocio)
  no dependen de implementaciones concretas, sino de estas abstracciones.
- ISP (Interface Segregation Principle): Cada interfaz es concisa, con métodos
  específicos para su propósito, evitando métodos innecesarios.
"""

from abc import ABC, abstractmethod
from typing import Optional
from src.domain.models import SolicitudCredito, ResultadoPreaprobacion


class ICentralRiesgo(ABC):
    """
    Abstracción para la consulta de puntaje en la central de riesgo.
    Cumple con el Punto 2 de la evaluación:
    'Construir una capa de acceso a datos que permita realizar la consulta
    de puntaje en la central de riesgo. Utilizar inversión de dependencias.'
    """

    @abstractmethod
    def consultar_puntaje(self, tipo_doc: str, nro_doc: str) -> Optional[int]:
        """
        Consulta el puntaje crediticio a partir del tipo y número de documento.
        
        :param tipo_doc: Tipo de documento (ej. 'CC')
        :param nro_doc: Número de documento (ej. '12234587')
        :return: Puntaje numérico (ej. 563) o None si el cliente no está registrado.
        """
        pass


class IEvaluadorCredito(ABC):
    """
    Abstracción para el servicio evaluador de preaprobación de créditos.
    Cumple con el Punto 1 de la evaluación:
    'Construir una capa de negocio abstracta e independiente...'
    """

    @abstractmethod
    def evaluar_preaprobacion(self, solicitud: SolicitudCredito) -> ResultadoPreaprobacion:
        """
        Evalúa una solicitud de crédito aplicando las reglas de negocio descritas.
        
        :param solicitud: Objeto SolicitudCredito con los datos del usuario.
        :return: ResultadoPreaprobacion con el veredicto y métricas calculadas.
        """
        pass
