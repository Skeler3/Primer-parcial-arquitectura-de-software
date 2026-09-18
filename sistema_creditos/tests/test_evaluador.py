"""
Capa de Pruebas Unitarias Exhaustivas para la Lógica de Negocio.

Cumple con el Punto 5 de la evaluación:
'Construir una capa de pruebas unitarias con todas las pruebas necesarias
para cubrir todos los casos de la lógica de negocio.'

Principios SOLID aplicados en las pruebas:
- DIP: Usamos la abstracción ICentralRiesgo para inyectar una implementación controlada
  (un Stub/Mock de prueba) sin depender de servidores o conexiones de red externas.
- SRP: Las pruebas están organizadas por suites de responsabilidad (validación de modelos,
  cálculos financieros, reglas de negocio y casos frontera).
"""

import unittest
from typing import Optional, Dict, Tuple

from src.domain.models import SolicitudCredito, EstadoCredito
from src.business.interfaces import ICentralRiesgo
from src.business.calculadora import CalculadoraFinanciera
from src.business.evaluador_service import EvaluadorCreditoService
from src.data.memoria_repository import CentralRiesgoEnMemoria


class StubCentralRiesgo(ICentralRiesgo):
    """
    Stub de prueba para simular respuestas específicas de la central de riesgo
    sin depender de datos preexistentes. Permite configurar escenarios exactos.
    """
    def __init__(self, puntaje_a_retornar: Optional[int] = None) -> None:
        self.puntaje_a_retornar = puntaje_a_retornar
        self.fue_consultada = False
        self.ultimo_tipo_doc = None
        self.ultimo_nro_doc = None

    def consultar_puntaje(self, tipo_doc: str, nro_doc: str) -> Optional[int]:
        self.fue_consultada = True
        self.ultimo_tipo_doc = tipo_doc
        self.ultimo_nro_doc = nro_doc
        return self.puntaje_a_retornar


class TestCalculadoraFinanciera(unittest.TestCase):
    """Pruebas unitarias para la CalculadoraFinanciera (SRP)."""

    def test_calcular_balanza_positiva(self):
        """Comprueba el cálculo correcto cuando ingresos > egresos."""
        balanza = CalculadoraFinanciera.calcular_balanza(5000.0, 2000.0)
        self.assertEqual(balanza, 3000.0)

    def test_calcular_balanza_negativa(self):
        """Comprueba el cálculo cuando ingresos < egresos."""
        balanza = CalculadoraFinanciera.calcular_balanza(2000.0, 3500.0)
        self.assertEqual(balanza, -1500.0)

    def test_calcular_balanza_cero(self):
        """Comprueba cuando ingresos == egresos."""
        balanza = CalculadoraFinanciera.calcular_balanza(4000.0, 4000.0)
        self.assertEqual(balanza, 0.0)

    def test_calcular_relacion_credito_balanza_exito(self):
        """
        Comprueba fórmula: (Monto / Plazo) / Balanza.
        Monto=15000, Plazo=10 -> Cuota=1500. Balanza=3000 -> Relación = 1500/3000 = 0.5
        """
        relacion = CalculadoraFinanciera.calcular_relacion_credito_balanza(15000.0, 10, 3000.0)
        self.assertAlmostEqual(relacion, 0.5, places=4)

    def test_calcular_relacion_con_balanza_cero_o_negativa_lanza_error(self):
        """Comprueba que no se permita dividir entre balanza <= 0."""
        with self.assertRaises(ZeroDivisionError):
            CalculadoraFinanciera.calcular_relacion_credito_balanza(10000.0, 12, 0.0)
        with self.assertRaises(ZeroDivisionError):
            CalculadoraFinanciera.calcular_relacion_credito_balanza(10000.0, 12, -500.0)


class TestSolicitudCreditoModel(unittest.TestCase):
    """Pruebas unitarias para las validaciones de la entidad SolicitudCredito."""

    def test_solicitud_valida_se_crea_correctamente(self):
        solicitud = SolicitudCredito("CC", "123", 5000, 2000, 10000, 12)
        self.assertEqual(solicitud.tipo_doc, "CC")
        self.assertEqual(solicitud.plazo_solicitado, 12)

    def test_solicitud_con_tipo_doc_vacio_falla(self):
        with self.assertRaises(ValueError):
            SolicitudCredito("  ", "123", 5000, 2000, 10000, 12)

    def test_solicitud_con_nro_doc_vacio_falla(self):
        with self.assertRaises(ValueError):
            SolicitudCredito("CC", "", 5000, 2000, 10000, 12)

    def test_solicitud_con_ingresos_negativos_falla(self):
        with self.assertRaises(ValueError):
            SolicitudCredito("CC", "123", -100, 2000, 10000, 12)

    def test_solicitud_con_egresos_negativos_falla(self):
        with self.assertRaises(ValueError):
            SolicitudCredito("CC", "123", 5000, -200, 10000, 12)

    def test_solicitud_con_monto_cero_o_negativo_falla(self):
        with self.assertRaises(ValueError):
            SolicitudCredito("CC", "123", 5000, 2000, 0, 12)
        with self.assertRaises(ValueError):
            SolicitudCredito("CC", "123", 5000, 2000, -500, 12)

    def test_solicitud_con_plazo_no_entero_falla(self):
        with self.assertRaises(TypeError):
            SolicitudCredito("CC", "123", 5000, 2000, 10000, 12.5)  # type: ignore


class TestEvaluadorCreditoService(unittest.TestCase):
    """
    Pruebas unitarias de las 5 Reglas de Negocio del Sistema de Crédito.
    """

    # --- 1. REGLA DE PLAZO: Debe ser entre 1 y 72 meses ---
    def test_plazo_menor_a_1_mes_es_negado(self):
        stub = StubCentralRiesgo(850)
        evaluador = EvaluadorCreditoService(stub)
        solicitud = SolicitudCredito("CC", "123", 5000, 2000, 10000, 0)
        res = evaluador.evaluar_preaprobacion(solicitud)
        
        self.assertEqual(res.estado, EstadoCredito.NEGADO)
        self.assertFalse(res.aprobado)
        self.assertIn("entre 1 y 72 meses", res.mensaje)
        self.assertFalse(stub.fue_consultada, "No debió consultar la central si el plazo es inválido")

    def test_plazo_mayor_a_72_meses_es_negado(self):
        stub = StubCentralRiesgo(850)
        evaluador = EvaluadorCreditoService(stub)
        solicitud = SolicitudCredito("CC", "123", 5000, 2000, 10000, 73)
        res = evaluador.evaluar_preaprobacion(solicitud)
        
        self.assertEqual(res.estado, EstadoCredito.NEGADO)
        self.assertFalse(res.aprobado)
        self.assertIn("entre 1 y 72 meses", res.mensaje)
        self.assertFalse(stub.fue_consultada)

    def test_plazos_limite_1_y_72_son_validos(self):
        """Valida que los extremos exactos 1 y 72 meses sí se procesen."""
        stub = StubCentralRiesgo(900)
        evaluador = EvaluadorCreditoService(stub)
        
        # Plazo 1 mes con baja relación: Monto 200, Plazo 1, Balanza 2000 -> Relación = 0.1 (<0.40)
        sol_1 = SolicitudCredito("CC", "123", 3000, 1000, 200, 1)
        res_1 = evaluador.evaluar_preaprobacion(sol_1)
        self.assertTrue(res_1.aprobado)

        # Plazo 72 meses con baja relación: Monto 7200, Plazo 72, Balanza 2000 -> Relación = 0.05 (<0.40)
        sol_72 = SolicitudCredito("CC", "123", 3000, 1000, 7200, 72)
        res_72 = evaluador.evaluar_preaprobacion(sol_72)
        self.assertTrue(res_72.aprobado)

    # --- 2. REGLA DE BALANZA: Si es cero o negativa -> Negado ---
    def test_balanza_negativa_es_negado_sin_consultar_central(self):
        stub = StubCentralRiesgo(950)
        evaluador = EvaluadorCreditoService(stub)
        # Ingresos 2000, Egresos 3000 -> Balanza = -1000
        solicitud = SolicitudCredito("CC", "123", 2000, 3000, 10000, 12)
        res = evaluador.evaluar_preaprobacion(solicitud)
        
        self.assertEqual(res.estado, EstadoCredito.NEGADO)
        self.assertFalse(res.aprobado)
        self.assertIn("cero o negativa", res.mensaje)
        self.assertFalse(stub.fue_consultada, "No debió consultar central con balanza negativa")

    def test_balanza_cero_es_negado_sin_consultar_central(self):
        stub = StubCentralRiesgo(950)
        evaluador = EvaluadorCreditoService(stub)
        # Ingresos 2500, Egresos 2500 -> Balanza = 0
        solicitud = SolicitudCredito("CC", "123", 2500, 2500, 5000, 10)
        res = evaluador.evaluar_preaprobacion(solicitud)
        
        self.assertEqual(res.estado, EstadoCredito.NEGADO)
        self.assertFalse(res.aprobado)
        self.assertIn("cero o negativa", res.mensaje)
        self.assertFalse(stub.fue_consultada)

    # --- 3. REGLA: relacionCreditoBalanza >= 0.95 -> Negado directo ---
    def test_relacion_igual_o_mayor_a_0_95_es_negado_sin_consultar_central(self):
        stub = StubCentralRiesgo(999)
        evaluador = EvaluadorCreditoService(stub)
        # Balanza = 4000 - 2000 = 2000. Cuota = 1900 / 1 = 1900. Relación = 1900/2000 = 0.95
        solicitud_exacta = SolicitudCredito("CC", "123", 4000, 2000, 1900, 1)
        res_exacta = evaluador.evaluar_preaprobacion(solicitud_exacta)
        
        self.assertEqual(res_exacta.estado, EstadoCredito.NEGADO)
        self.assertFalse(res_exacta.aprobado)
        self.assertIn("igual o superior a 0.95", res_exacta.mensaje)
        self.assertFalse(stub.fue_consultada)

        # Relación muy superior: 1.25
        solicitud_alta = SolicitudCredito("CC", "123", 4000, 2000, 2500, 1)
        res_alta = evaluador.evaluar_preaprobacion(solicitud_alta)
        self.assertEqual(res_alta.estado, EstadoCredito.NEGADO)
        self.assertFalse(stub.fue_consultada)

    # --- 4. TRAMO ALTO: 0.70 <= Relación < 0.95 (Exige Puntaje >= 800) ---
    def test_tramo_alto_con_puntaje_mayor_o_igual_a_800_es_aprobado(self):
        """Balanza = 2000. Monto = 1600, Plazo = 1 -> Relación = 0.80. Puntaje = 800 -> Aprobado"""
        stub = StubCentralRiesgo(800)
        evaluador = EvaluadorCreditoService(stub)
        solicitud = SolicitudCredito("CC", "123", 3000, 1000, 1600, 1)
        res = evaluador.evaluar_preaprobacion(solicitud)
        
        self.assertTrue(stub.fue_consultada)
        self.assertEqual(res.estado, EstadoCredito.APROBADO)
        self.assertTrue(res.aprobado)
        self.assertIn("Crédito aprobado", res.mensaje)

    def test_tramo_alto_con_puntaje_menor_a_800_es_negado(self):
        """Relación = 0.80. Puntaje = 799 -> Negado"""
        stub = StubCentralRiesgo(799)
        evaluador = EvaluadorCreditoService(stub)
        solicitud = SolicitudCredito("CC", "123", 3000, 1000, 1600, 1)
        res = evaluador.evaluar_preaprobacion(solicitud)
        
        self.assertTrue(stub.fue_consultada)
        self.assertEqual(res.estado, EstadoCredito.NEGADO)
        self.assertFalse(res.aprobado)
        self.assertIn("insuficiente", res.mensaje)

    def test_tramo_alto_limite_inferior_0_70(self):
        """Balanza = 2000. Monto = 1400, Plazo = 1 -> Relación = 1400/2000 = 0.70 exactamente"""
        # Puntaje 800 -> Aprobado
        evaluador_ok = EvaluadorCreditoService(StubCentralRiesgo(800))
        solicitud = SolicitudCredito("CC", "123", 3000, 1000, 1400, 1)
        self.assertTrue(evaluador_ok.evaluar_preaprobacion(solicitud).aprobado)

        # Puntaje 799 -> Negado
        evaluador_fail = EvaluadorCreditoService(StubCentralRiesgo(799))
        self.assertFalse(evaluador_fail.evaluar_preaprobacion(solicitud).aprobado)

    # --- 5. TRAMO MEDIO: 0.40 <= Relación < 0.70 (Exige Puntaje >= 600) ---
    def test_tramo_medio_con_puntaje_mayor_o_igual_a_600_es_aprobado(self):
        """Balanza = 3000. Monto = 15000, Plazo = 10 -> Cuota = 1500 -> Relación = 0.50. Puntaje = 600 -> Aprobado"""
        stub = StubCentralRiesgo(600)
        evaluador = EvaluadorCreditoService(stub)
        solicitud = SolicitudCredito("CC", "123", 4000, 1000, 15000, 10)
        res = evaluador.evaluar_preaprobacion(solicitud)
        
        self.assertTrue(stub.fue_consultada)
        self.assertEqual(res.estado, EstadoCredito.APROBADO)
        self.assertTrue(res.aprobado)

    def test_tramo_medio_con_puntaje_menor_a_600_es_negado(self):
        """Caso del examen del PDF: CC 12234587 tiene puntaje 563 (<600) en relación 0.50 -> Negado"""
        stub = StubCentralRiesgo(563)
        evaluador = EvaluadorCreditoService(stub)
        solicitud = SolicitudCredito("CC", "12234587", 4000, 1000, 15000, 10)
        res = evaluador.evaluar_preaprobacion(solicitud)
        
        self.assertTrue(stub.fue_consultada)
        self.assertEqual(res.estado, EstadoCredito.NEGADO)
        self.assertFalse(res.aprobado)
        self.assertIn("insuficiente", res.mensaje)

    def test_tramo_medio_limite_inferior_0_40(self):
        """Balanza = 2000. Monto = 800, Plazo = 1 -> Relación = 800/2000 = 0.40 exactamente"""
        # Puntaje 600 -> Aprobado
        evaluador_ok = EvaluadorCreditoService(StubCentralRiesgo(600))
        solicitud = SolicitudCredito("CC", "123", 3000, 1000, 800, 1)
        self.assertTrue(evaluador_ok.evaluar_preaprobacion(solicitud).aprobado)

        # Puntaje 599 -> Negado
        evaluador_fail = EvaluadorCreditoService(StubCentralRiesgo(599))
        self.assertFalse(evaluador_fail.evaluar_preaprobacion(solicitud).aprobado)

    # --- 6. TRAMO BAJO: Relación < 0.40 (Exige Puntaje >= 400) ---
    def test_tramo_bajo_con_puntaje_mayor_o_igual_a_400_es_aprobado(self):
        """Balanza = 2000. Monto = 600, Plazo = 1 -> Relación = 0.30 (< 0.40). Puntaje = 400 -> Aprobado"""
        stub = StubCentralRiesgo(400)
        evaluador = EvaluadorCreditoService(stub)
        solicitud = SolicitudCredito("CC", "123", 3000, 1000, 600, 1)
        res = evaluador.evaluar_preaprobacion(solicitud)
        
        self.assertTrue(stub.fue_consultada)
        self.assertEqual(res.estado, EstadoCredito.APROBADO)
        self.assertTrue(res.aprobado)

    def test_tramo_bajo_con_puntaje_menor_a_400_es_negado(self):
        """Relación = 0.30. Puntaje = 399 (< 400) -> Negado"""
        stub = StubCentralRiesgo(399)
        evaluador = EvaluadorCreditoService(stub)
        solicitud = SolicitudCredito("CC", "123", 3000, 1000, 600, 1)
        res = evaluador.evaluar_preaprobacion(solicitud)
        
        self.assertTrue(stub.fue_consultada)
        self.assertEqual(res.estado, EstadoCredito.NEGADO)
        self.assertFalse(res.aprobado)
        self.assertIn("insuficiente", res.mensaje)

    # --- 7. CLIENTE INEXISTENTE EN CENTRAL DE RIESGO ---
    def test_cliente_no_encontrado_en_central_es_negado(self):
        """Cuando la central retorna None para el documento, se niega el crédito."""
        stub = StubCentralRiesgo(None)
        evaluador = EvaluadorCreditoService(stub)
        solicitud = SolicitudCredito("CC", "99999999", 3000, 1000, 600, 1)
        res = evaluador.evaluar_preaprobacion(solicitud)
        
        self.assertTrue(stub.fue_consultada)
        self.assertEqual(res.estado, EstadoCredito.NEGADO)
        self.assertFalse(res.aprobado)
        self.assertIn("no se encuentra registrado", res.mensaje)

    # --- 8. PRUEBA DE INTEGRACIÓN CON REPOSITORIO REAL EN MEMORIA ---
    def test_integracion_con_central_en_memoria(self):
        """Verifica que Evaluador funcione impecablemente con CentralRiesgoEnMemoria (LSP y DIP)."""
        repo_memoria = CentralRiesgoEnMemoria()
        evaluador = EvaluadorCreditoService(central_riesgo=repo_memoria)

        # Cliente del examen CC 12234587 tiene 563 puntos.
        # Caso 1: En tramo medio (relación 0.50), requiere 600 -> NEGADO
        sol_pdf_medio = SolicitudCredito("CC", "12234587", 4000, 1000, 15000, 10)
        self.assertFalse(evaluador.evaluar_preaprobacion(sol_pdf_medio).aprobado)

        # Caso 2: Mismo cliente pero con un crédito más pequeño (tramo bajo, relación 0.20), requiere 400 -> APROBADO (563 >= 400)
        sol_pdf_bajo = SolicitudCredito("CC", "12234587", 4000, 1000, 6000, 10)
        res_bajo = evaluador.evaluar_preaprobacion(sol_pdf_bajo)
        self.assertTrue(res_bajo.aprobado)
        self.assertEqual(res_bajo.puntaje_central, 563)


if __name__ == "__main__":
    unittest.main()
