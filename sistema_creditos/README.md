# Sistema de Preaprobación de Créditos

Aplicación desarrollada en **Python 3** con interfaz gráfica en **Tkinter**, diseñada con una **Arquitectura en Capas Limpia** y aplicando rigurosamente los principios de diseño de software **SOLID**.

---

## 1. Cumplimiento de los Criterios de Evaluación

| Punto en el Enunciado | Ponderación | Componente en el Proyecto | Cumplimiento Técnico |
| :--- | :---: | :--- | :--- |
| **1. Capa de negocio abstracta e independiente** | **1.0** | `src/domain/models.py`<br>`src/business/interfaces.py`<br>`src/business/calculadora.py`<br>`src/business/evaluador_service.py` | Lógica pura sin acoplamiento a frameworks. Aplica las 5 reglas financieras del enunciado, separando responsabilidades matemáticas y de decisión. |
| **2. Capa de acceso a datos con inversión de dependencias** | **1.0** | `src/business/interfaces.py` (`ICentralRiesgo`)<br>`src/data/memoria_repository.py` | La lógica de negocio depende de la abstracción `ICentralRiesgo`. La consulta de puntaje crediticio se desacopla mediante Inyección de Dependencias. |
| **3. Capa de presentación con GUI y Alert** | **1.0** | `src/presentation/gui_tkinter.py` | Formulario en Tkinter con validación de entradas numéricas, botón para cargar el ejemplo del examen (`CC 12234587`) y presentación del veredicto en una alerta emergente modal (`messagebox`). |
| **4. Capa de datos simulados en memoria con DIP** | **1.0** | `src/data/memoria_repository.py` (`CentralRiesgoEnMemoria`) | Repositorio en memoria que implementa `ICentralRiesgo`, precargado con el registro del PDF (`563` pts), puntajes altos ($\ge 800$), medios ($\ge 600$), bajos ($\ge 400$) e inexistentes. |
| **5. Capa de pruebas unitarias exhaustivas** | **1.0** | `tests/test_evaluador.py` | **28 pruebas automatizadas con unittest** que cubren el 100% de las ramas de decisión, valores frontera, clientes no registrados y modelos de datos. |

---

## 2. Auditoría de Principios SOLID

| Principio | Dónde se aplica | Cómo se aplica |
| :--- | :--- | :--- |
| **SRP** (*Single Responsibility*) | `SolicitudCredito`, `CalculadoraFinanciera`, `EvaluadorCreditoService`, `CentralRiesgoEnMemoria`, `VentanaCreditoTkinter` | Cada clase tiene una sola razón para cambiar: los modelos transportan datos; la calculadora realiza cálculos aritméticos; el evaluador aplica políticas bancarias; el repositorio almacena puntajes; y la interfaz solo interactúa con el usuario. |
| **OCP** (*Open/Closed*) | `EvaluadorCreditoService` e `ICentralRiesgo` | El sistema está abierto a la extensión (se puede conectar una API HTTP real de Datacrédito/TransUnion creando una nueva clase `CentralRiesgoApiRest`) y cerrado a la modificación (no se requiere modificar el evaluador de negocio). |
| **LSP** (*Liskov Substitution*) | `ICentralRiesgo`, `CentralRiesgoEnMemoria`, `StubCentralRiesgo` | Cualquier implementación del contrato `ICentralRiesgo` puede sustituir a otra en el evaluador sin alterar el comportamiento esperado ni requerir comprobaciones de tipo (`isinstance`). |
| **ISP** (*Interface Segregation*) | `ICentralRiesgo` e `IEvaluadorCredito` | Interfaces pequeñas, cohesivas y específicas. `ICentralRiesgo` solo expone `consultar_puntaje`, evitando forzar métodos innecesarios a sus implementaciones. |
| **DIP** (*Dependency Inversion*) | `EvaluadorCreditoService` $\rightarrow$ `ICentralRiesgo` | El módulo de alto nivel (negocio) no depende de módulos de bajo nivel (acceso a datos o memoria). Ambos dependen de la abstracción `ICentralRiesgo`, inyectada a través del constructor (`__init__`). |

---

## 3. Estructura del Proyecto

```text
sistema_creditos/
├── src/
│   ├── __init__.py
│   ├── domain/                         # Entidades y Modelos Inmutables
│   │   ├── __init__.py
│   │   └── models.py                   # SolicitudCredito, ResultadoPreaprobacion, EstadoCredito
│   ├── business/                       # Capa de Negocio (Punto 1)
│   │   ├── __init__.py
│   │   ├── interfaces.py               # Contratos ICentralRiesgo, IEvaluadorCredito
│   │   ├── calculadora.py              # CalculadoraFinanciera (SRP)
│   │   └── evaluador_service.py        # EvaluadorCreditoService (Reglas de Decisión)
│   ├── data/                           # Capa de Acceso a Datos / En Memoria (Puntos 2 y 4)
│   │   ├── __init__.py
│   │   └── memoria_repository.py       # CentralRiesgoEnMemoria (implementa ICentralRiesgo)
│   └── presentation/                   # Capa de Presentación (Punto 3)
│       ├── __init__.py
│       └── gui_tkinter.py              # Formulario gráfico y alertas emergentes (Tkinter)
├── tests/                              # Capa de Pruebas Unitarias (Punto 5)
│   ├── __init__.py
│   └── test_evaluador.py               # Suite de 28 pruebas unitarias
├── main.py                             # Punto de entrada / Composition Root
└── README.md                           # Documentación técnica
```

---

## 4. Requisitos e Instalación

* **Python:** Versión 3.10 o superior (compatible con Python 3.13).
* **Librerías externas:** Ninguna. Se construyó utilizando exclusivamente la **Biblioteca Estándar de Python** (`tkinter`, `dataclasses`, `enum`, `abc`, `typing`, `unittest`).

---

## 5. Instrucciones de Ejecución

### A. Ejecutar la Aplicación Gráfica (GUI)
Abre una terminal en la raíz del proyecto y ejecuta:

```powershell
py main.py
```
*(o `python main.py` según tu entorno).*

1. Usa el botón **"Cargar Ejemplo del Examen (CC 12234587)"** para ver los datos del enunciado.
2. Haz clic en **"Evaluar Preaprobación"** para ver el `alert` con el resultado.

### B. Ejecutar las Pruebas Unitarias
Abre una terminal en la raíz del proyecto y ejecuta:

```powershell
py -m unittest discover -s tests -v
```

Deberías poder observar la ejecución de los **28 tests con veredicto OK**.
