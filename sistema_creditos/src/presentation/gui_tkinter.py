"""
Módulo de la Capa de Presentación (Interfaz Gráfica de Usuario con Tkinter).

Principios SOLID aplicados:
- SRP (Single Responsibility Principle): Esta clase solo se encarga de la vista
  (renderizar widgets, capturar entradas del usuario, validar formato y mostrar alerts).
  NO contiene reglas de negocio ni cálculos de riesgo.
- DIP (Dependency Inversion Principle): Depende de la abstracción IEvaluadorCredito,
  la cual se recibe por inyección de dependencias.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from src.business.interfaces import IEvaluadorCredito
from src.domain.models import SolicitudCredito, EstadoCredito


class VentanaCreditoTkinter:
    """
    Ventana principal de la aplicación para consultar preaprobación de crédito.
    """

    def __init__(self, evaluador: IEvaluadorCredito, root: Optional[tk.Tk] = None) -> None:
        """
        Inicializa la interfaz gráfica inyectando el servicio de negocio evaluador.
        :param evaluador: Abstracción IEvaluadorCredito (DIP).
        :param root: Instancia opcional de tk.Tk.
        """
        self._evaluador = evaluador
        self.root = root or tk.Tk()
        self._configurar_ventana()
        self._crear_widgets()

    def _configurar_ventana(self) -> None:
        self.root.title("Consultar Preaprobación Crédito - Sistema Bancario")
        self.root.geometry("520x620")
        self.root.resizable(False, False)
        
        # Aplicar estilo ttk moderno
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")

    def _crear_widgets(self) -> None:
        # Contenedor principal con margen
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título y encabezado
        lbl_titulo = ttk.Label(
            main_frame,
            text="Solicitud de Preaprobación de Crédito",
            font=("Helvetica", 14, "bold")
        )
        lbl_titulo.pack(pady=(0, 15))

        lbl_subtitulo = ttk.Label(
            main_frame,
            text="Ingrese la información financiera para evaluar la viabilidad del crédito.",
            font=("Helvetica", 9),
            foreground="#555555"
        )
        lbl_subtitulo.pack(pady=(0, 20))

        # Marco del formulario
        form_frame = ttk.LabelFrame(main_frame, text=" Datos del Solicitante ", padding="15 15 15 15")
        form_frame.pack(fill=tk.X, pady=(0, 15))

        # 1. Tipo de Documento
        ttk.Label(form_frame, text="Tipo de Documento:").grid(row=0, column=0, sticky=tk.W, pady=6)
        self.combo_tipo_doc = ttk.Combobox(
            form_frame,
            values=["CC", "CE", "PAS"],
            state="readonly",
            width=22
        )
        self.combo_tipo_doc.set("CC")
        self.combo_tipo_doc.grid(row=0, column=1, sticky=tk.E, pady=6)

        # 2. Número de Documento
        ttk.Label(form_frame, text="Número de Documento:").grid(row=1, column=0, sticky=tk.W, pady=6)
        self.txt_nro_doc = ttk.Entry(form_frame, width=25)
        self.txt_nro_doc.grid(row=1, column=1, sticky=tk.E, pady=6)

        # 3. Ingresos Totales
        ttk.Label(form_frame, text="Ingresos Totales ($/mes):").grid(row=2, column=0, sticky=tk.W, pady=6)
        self.txt_ingresos = ttk.Entry(form_frame, width=25)
        self.txt_ingresos.grid(row=2, column=1, sticky=tk.E, pady=6)

        # 4. Egresos Totales
        ttk.Label(form_frame, text="Egresos Totales ($/mes):").grid(row=3, column=0, sticky=tk.W, pady=6)
        self.txt_egresos = ttk.Entry(form_frame, width=25)
        self.txt_egresos.grid(row=3, column=1, sticky=tk.E, pady=6)

        # 5. Monto Solicitado
        ttk.Label(form_frame, text="Monto Solicitado ($):").grid(row=4, column=0, sticky=tk.W, pady=6)
        self.txt_monto = ttk.Entry(form_frame, width=25)
        self.txt_monto.grid(row=4, column=1, sticky=tk.E, pady=6)

        # 6. Plazo Solicitado (Meses)
        ttk.Label(form_frame, text="Plazo Solicitado (1 a 72 meses):").grid(row=5, column=0, sticky=tk.W, pady=6)
        self.txt_plazo = ttk.Entry(form_frame, width=25)
        self.txt_plazo.grid(row=5, column=1, sticky=tk.E, pady=6)

        # Botones de acción
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        self.btn_evaluar = tk.Button(
            btn_frame,
            text="Evaluar Preaprobación",
            command=self._on_evaluar_click,
            bg="#0066cc",
            fg="white",
            font=("Helvetica", 10, "bold"),
            relief="flat",
            padx=10,
            pady=8,
            cursor="hand2"
        )
        self.btn_evaluar.pack(fill=tk.X, pady=(0, 6))

        self.btn_limpiar = ttk.Button(
            btn_frame,
            text="Limpiar Formulario",
            command=self._limpiar_campos
        )
        self.btn_limpiar.pack(fill=tk.X, pady=(0, 6))

        # Botón pedagógico para cargar datos de prueba rápidos
        self.btn_ejemplo = ttk.Button(
            btn_frame,
            text="Cargar Ejemplo del Examen (CC 12234587)",
            command=self._cargar_ejemplo_examen
        )
        self.btn_ejemplo.pack(fill=tk.X)

    def _on_evaluar_click(self) -> None:
        """
        Manejador del evento de clic.
        Valida entradas, crea la Solicitud y delega la evaluación al servicio de negocio.
        Muestra el resultado en un Alert (messagebox).
        """
        tipo_doc = self.combo_tipo_doc.get().strip()
        nro_doc = self.txt_nro_doc.get().strip()
        ingresos_str = self.txt_ingresos.get().strip()
        egresos_str = self.txt_egresos.get().strip()
        monto_str = self.txt_monto.get().strip()
        plazo_str = self.txt_plazo.get().strip()

        # Validación de campos no vacíos
        if not nro_doc or not ingresos_str or not egresos_str or not monto_str or not plazo_str:
            messagebox.showwarning(
                "Campos Incompletos",
                "Por favor complete todos los campos del formulario antes de continuar."
            )
            return

        # Validación de formatos numéricos
        try:
            ingresos = float(ingresos_str)
            egresos = float(egresos_str)
            monto = float(monto_str)
            plazo = int(plazo_str)
        except ValueError:
            messagebox.showerror(
                "Formato Inválido",
                "Los ingresos, egresos y monto deben ser números válidos.\n"
                "El plazo debe ser un número entero de meses."
            )
            return

        # Creación de la entidad de dominio
        try:
            solicitud = SolicitudCredito(
                tipo_doc=tipo_doc,
                nro_doc=nro_doc,
                ingresos_totales=ingresos,
                egresos_totales=egresos,
                monto_solicitado=monto,
                plazo_solicitado=plazo
            )
        except ValueError as ex:
            messagebox.showwarning("Datos Inválidos", str(ex))
            return

        # Delegación exclusiva a la capa de negocio (Cero lógica de decisión en la UI)
        resultado = self._evaluador.evaluar_preaprobacion(solicitud)

        # Mostrar veredicto en Alert según la evaluación
        self._mostrar_alert_resultado(resultado)

    def _mostrar_alert_resultado(self, resultado) -> None:
        """
        Construye y muestra la ventana de alerta requerida por la evaluación.
        """
        detalles = []
        if resultado.balanza is not None:
            detalles.append(f"• Balanza: ${resultado.balanza:,.2f}")
        if resultado.relacion_credito_balanza is not None:
            detalles.append(f"• Relación Crédito/Balanza: {resultado.relacion_credito_balanza:.4f}")
        if resultado.puntaje_central is not None:
            detalles.append(f"• Puntaje Central de Riesgo: {resultado.puntaje_central} pts")

        texto_detalles = "\n".join(detalles)

        if resultado.estado == EstadoCredito.APROBADO:
            mensaje_completo = (
                "¡FELICITACIONES! SU CRÉDITO HA SIDO PREAPROBADO.\n\n"
                f"{resultado.mensaje}\n\n"
                "Detalles Financieros:\n"
                f"{texto_detalles}"
            )
            messagebox.showinfo("Crédito Aprobado", mensaje_completo)
        else:
            mensaje_completo = (
                "SU SOLICITUD DE CRÉDITO HA SIDO NEGADA.\n\n"
                f"{resultado.mensaje}\n"
            )
            if texto_detalles:
                mensaje_completo += f"\nDetalles Financieros:\n{texto_detalles}"
            messagebox.showwarning("Crédito Negado", mensaje_completo)

    def _limpiar_campos(self) -> None:
        self.txt_nro_doc.delete(0, tk.END)
        self.txt_ingresos.delete(0, tk.END)
        self.txt_egresos.delete(0, tk.END)
        self.txt_monto.delete(0, tk.END)
        self.txt_plazo.delete(0, tk.END)
        self.combo_tipo_doc.set("CC")

    def _cargar_ejemplo_examen(self) -> None:
        """Carga automáticamente el cliente que aparece en el PDF del examen."""
        self._limpiar_campos()
        self.combo_tipo_doc.set("CC")
        self.txt_nro_doc.insert(0, "12234587")
        self.txt_ingresos.insert(0, "4000000")
        self.txt_egresos.insert(0, "1000000")
        self.txt_monto.insert(0, "15000000")
        self.txt_plazo.insert(0, "10")

    def iniciar(self) -> None:
        """Arranca el bucle principal de eventos de Tkinter."""
        self.root.mainloop()
