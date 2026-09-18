"""
Módulo de Cálculos Financieros.

Principios SOLID aplicados:
- SRP (Single Responsibility Principle): Esta clase tiene una única responsabilidad:
  realizar los cálculos matemáticos de balanza y relación crédito/balanza,
  aislando la aritmética de la lógica de decisión de crédito.
"""

class CalculadoraFinanciera:
    """
    Encargada de computar métricas financieras a partir de los datos solicitados.
    """

    @staticmethod
    def calcular_balanza(ingresos_totales: float, egresos_totales: float) -> float:
        """
        Calcula la balanza financiera:
        Balanza = IngresosTotales - EgresosTotales
        """
        return round(ingresos_totales - egresos_totales, 2)

    @staticmethod
    def calcular_relacion_credito_balanza(
        monto_solicitado: float, plazo_solicitado: int, balanza: float
    ) -> float:
        """
        Calcula la relación crédito/balanza:
        relacionCreditoBalanza = (MontoSolicitado / PlazoSolicitado) / Balanza

        Lanza ZeroDivisionError si la balanza es 0.
        """
        if balanza <= 0:
            raise ZeroDivisionError("No se puede calcular la relación con una balanza menor o igual a cero.")
        
        cuota_estimada = monto_solicitado / plazo_solicitado
        return round(cuota_estimada / balanza, 4)
