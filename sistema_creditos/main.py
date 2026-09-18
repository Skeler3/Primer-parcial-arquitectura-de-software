"""
Punto de entrada principal de la aplicación (Composition Root).

Aquí se realiza el ensamblaje de las dependencias respetando el principio DIP:
1. Se instancia la fuente de datos (CentralRiesgoEnMemoria).
2. Se inyecta la fuente de datos al servicio de negocio (EvaluadorCreditoService).
3. Se inyecta el servicio de negocio a la interfaz gráfica (VentanaCreditoTkinter).
4. Se inicia la aplicación.
"""

import sys
import os

# Asegurar que el directorio raíz del proyecto esté en el sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data.memoria_repository import CentralRiesgoEnMemoria
from src.business.evaluador_service import EvaluadorCreditoService
from src.presentation.gui_tkinter import VentanaCreditoTkinter


def main() -> None:
    # 1. Capa de Datos (Implementa ICentralRiesgo)
    central_riesgo = CentralRiesgoEnMemoria()

    # 2. Capa de Negocio (Recibe ICentralRiesgo por Inversión de Dependencias)
    evaluador_servicio = EvaluadorCreditoService(central_riesgo=central_riesgo)

    # 3. Capa de Presentación (Recibe IEvaluadorCredito por Inversión de Dependencias)
    app = VentanaCreditoTkinter(evaluador=evaluador_servicio)

    # 4. Iniciar la aplicación de escritorio
    print("Iniciando Sistema de Preaprobación de Créditos...")
    app.iniciar()


if __name__ == "__main__":
    main()
