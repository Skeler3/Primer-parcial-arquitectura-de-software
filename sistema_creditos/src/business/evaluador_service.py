"""
Módulo del Servicio de Evaluación de Crédito.

Principios SOLID aplicados:
- SRP (Single Responsibility Principle): Esta clase solo se encarga de orquestar
  la evaluación de preaprobación según las reglas financieras del banco.
- OCP (Open/Closed Principle): El evaluador está cerrado a modificaciones internas
  pero abierto a extensión mediante la inyección de diferentes implementaciones
  de la central de riesgo.
- LSP (Liskov Substitution Principle): Cualquier implementación de ICentralRiesgo
  puede sustituirse sin alterar el correcto funcionamiento de este servicio.
- DIP (Dependency Inversion Principle): Depende de la interfaz ICentralRiesgo,
  no de una clase concreta de base de datos o API externa.
"""

from typing import Optional
from src.domain.models import SolicitudCredito, ResultadoPreaprobacion, EstadoCredito
from src.business.interfaces import IEvaluadorCredito, ICentralRiesgo
from src.business.calculadora import CalculadoraFinanciera


class EvaluadorCreditoService(IEvaluadorCredito):
    """
    Implementación de la lógica de negocio para la preaprobación de crédito.
    Cumple con el Punto 1 de la evaluación.
    """

    def __init__(
        self,
        central_riesgo: ICentralRiesgo,
        calculadora: Optional[CalculadoraFinanciera] = None
    ) -> None:
        """
        Inyección de Dependencias a través del constructor.
        :param central_riesgo: Abstracción ICentralRiesgo (DIP).
        :param calculadora: Objeto con responsabilidad de cálculos (SRP).
        """
        self._central_riesgo = central_riesgo
        self._calculadora = calculadora or CalculadoraFinanciera()

    def evaluar_preaprobacion(self, solicitud: SolicitudCredito) -> ResultadoPreaprobacion:
        """
        Ejecuta paso a paso las reglas de negocio descritas en la evaluación:
        1. Validar que el plazo esté entre 1 y 72 meses.
        2. Calcular la balanza (Ingresos - Egresos). Si balanza <= 0 -> Negado.
        3. Calcular relacionCreditoBalanza = (Monto / Plazo) / Balanza.
        4. Si relacion >= 0.95 -> Negado.
        5. Si 0.70 <= relacion < 0.95 -> Consultar central (requiere puntaje >= 800).
        6. Si 0.40 <= relacion < 0.70 -> Consultar central (requiere puntaje >= 600).
        7. Si relacion < 0.40 -> Consultar central (requiere puntaje >= 400).
        """

        # Regla 1: El plazo solicitado debe ser entre 1 y 72 meses
        if not (1 <= solicitud.plazo_solicitado <= 72):
            return ResultadoPreaprobacion(
                estado=EstadoCredito.NEGADO,
                aprobado=False,
                mensaje="Crédito negado: El plazo solicitado debe ser entre 1 y 72 meses."
            )

        # Regla 2: Balanza = IngresosTotales - EgresosTotales
        balanza = self._calculadora.calcular_balanza(
            solicitud.ingresos_totales, solicitud.egresos_totales
        )
        if balanza <= 0:
            return ResultadoPreaprobacion(
                estado=EstadoCredito.NEGADO,
                aprobado=False,
                mensaje="Crédito negado: La balanza es cero o negativa (capacidad de pago insuficiente).",
                balanza=balanza
            )

        # Regla 3: RelacionCreditoBalanza = (MontoSolicitado / PlazoSolicitado) / Balanza
        relacion = self._calculadora.calcular_relacion_credito_balanza(
            solicitud.monto_solicitado, solicitud.plazo_solicitado, balanza
        )

        # Regla 4: Si relacionCreditoBalanza >= 0.95 -> Negado directo
        if relacion >= 0.95:
            return ResultadoPreaprobacion(
                estado=EstadoCredito.NEGADO,
                aprobado=False,
                mensaje=(
                    f"Crédito negado: La relación crédito/balanza ({relacion:.4f}) "
                    f"es igual o superior a 0.95 (nivel de endeudamiento crítico)."
                ),
                balanza=balanza,
                relacion_credito_balanza=relacion
            )

        # Determinar el umbral de puntaje exigido según el tramo de riesgo
        if relacion >= 0.70:
            puntaje_requerido = 800
            descripcion_riesgo = "alto (0.70 <= relación < 0.95)"
        elif relacion >= 0.40:
            puntaje_requerido = 600
            descripcion_riesgo = "medio (0.40 <= relación < 0.70)"
        else:
            puntaje_requerido = 400
            descripcion_riesgo = "bajo (relación < 0.40)"

        # Consultar puntaje en la central de riesgo a través de la abstracción (DIP)
        puntaje = self._central_riesgo.consultar_puntaje(
            solicitud.tipo_doc, solicitud.nro_doc
        )

        # Validación si el cliente no está en la central
        if puntaje is None:
            return ResultadoPreaprobacion(
                estado=EstadoCredito.NEGADO,
                aprobado=False,
                mensaje=(
                    "Crédito negado: El cliente no se encuentra registrado "
                    "en la central de riesgo."
                ),
                balanza=balanza,
                relacion_credito_balanza=relacion
            )

        # Comparación del puntaje obtenido contra el puntaje requerido
        if puntaje >= puntaje_requerido:
            return ResultadoPreaprobacion(
                estado=EstadoCredito.APROBADO,
                aprobado=True,
                mensaje=(
                    f"Crédito aprobado: Puntaje ({puntaje}) cumple con el mínimo "
                    f"de {puntaje_requerido} puntos requerido para un nivel de riesgo {descripcion_riesgo}."
                ),
                balanza=balanza,
                relacion_credito_balanza=relacion,
                puntaje_central=puntaje
            )
        else:
            return ResultadoPreaprobacion(
                estado=EstadoCredito.NEGADO,
                aprobado=False,
                mensaje=(
                    f"Crédito negado: Puntaje ({puntaje}) insuficiente. Se requieren "
                    f"al menos {puntaje_requerido} puntos para un nivel de riesgo {descripcion_riesgo}."
                ),
                balanza=balanza,
                relacion_credito_balanza=relacion,
                puntaje_central=puntaje
            )
