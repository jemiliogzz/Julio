# Simulación de Examen - Documentación

## Descripción General

Se ha implementado una nueva funcionalidad llamada **Simulación de Examen** que permite a los estudiantes crear exámenes personalizados seleccionando los temas que desean practicar.

## ✨ Mejores Prácticas Aplicadas

El sistema sigue principios de **código limpio y modular**:

- **Módulo Compartido**: Los generadores de preguntas están en `quiz_generators.py`, permitiendo su reutilización
- **Separación de Responsabilidades**: Lógica de generación separada de la interfaz de usuario
- **Sin Hardcoding**: Fácil agregar nuevos temas sin modificar múltiples archivos
- **Mantenibilidad**: Un solo lugar para actualizar la lógica de generación de preguntas

## Archivos del Sistema

### Archivos Nuevos:

1. **`quiz_generators.py`** (Raíz del proyecto)
   - Módulo compartido con todos los generadores de preguntas
   - 19 generadores específicos por tema
   - Generador genérico para temas no implementados
   - Funciones utilitarias para gestión de temas
   - ~650 líneas, bien documentado

2. **`pages/simulacion_examen.py`**
   - Interfaz de usuario para la simulación de examen
   - Lógica de navegación y evaluación
   - Importa generadores desde `quiz_generators.py`
   - ~300 líneas (reducido de ~900 líneas)

### Archivos Modificados:

3. **`pages/inicio.py`**
   - Se agregó botón de acceso a la simulación (+9 líneas)

## Arquitectura del Sistema

```
Julio/
├── quiz_generators.py          ← Módulo compartido (NUEVO)
│   ├── generar_pregunta_tema_X()  # Funciones específicas por tema
│   ├── generar_pregunta()         # Función principal
│   └── obtener_temas_disponibles()
│
├── pages/
│   ├── simulacion_examen.py    ← UI y lógica de examen (NUEVO)
│   ├── inicio.py               ← Agregado botón de acceso (MODIFICADO)
│   └── quiz_X.py               ← Sin cambios (potencial para refactorizar)
│
└── SIMULACION_EXAMEN_README.md ← Documentación
```

## Funcionalidades Implementadas

### 1. Selección de Temas ✅
- Muestra todos los temas disponibles (excepto el tema 23)
- Permite seleccionar uno o varios temas mediante checkboxes
- Muestra el total de preguntas que se generarán (3 por tema)
- Validación para evitar generar examen vacío

### 2. Generación del Examen ✅
- Por cada tema seleccionado se generan exactamente 3 ejercicios
- Los ejercicios se mezclan en orden aleatorio
- **Importa generadores desde módulo compartido** (no hay código duplicado)

### 3. Flujo del Examen ✅
- **Navegación:** Los ejercicios se presentan uno por uno
- **Progreso:** Barra de progreso visual que muestra el avance
- **Respuestas:** Sistema de captura según el tipo de pregunta:
  - Texto libre
  - Opción múltiple (radio buttons)
  - Slider (para gráficas en recta numérica)
- **Navegación flexible:** Botones para ir a pregunta anterior, guardar respuesta, o avanzar
- **Finalización:** Botón especial al llegar a la última pregunta

### 4. Resultados Finales ✅
Al finalizar el examen se muestra:
- **Métricas principales:**
  - Total de preguntas
  - Número de aciertos
  - Número de errores
  - Porcentaje de calificación
- **Retroalimentación visual:** Mensajes personalizados según el desempeño
- **Detalles expandibles:** Lista de todas las preguntas con respuestas correctas/incorrectas
- **Opciones:** Generar nuevo examen o volver a inicio

## Módulo `quiz_generators.py`

### Estructura de Pregunta Estándar

```python
{
    'pregunta': str,              # LaTeX o texto de la pregunta
    'respuesta_correcta': str,    # Respuesta correcta
    'tipo': str,                  # 'texto', 'radio', o 'slider'
    'opciones': list,             # Solo para tipo 'radio' (opcional)
    'rango': tuple,               # Solo para tipo 'slider' (min, max) (opcional)
    'tema_id': int,               # ID del tema
    'instruccion': str            # Instrucciones adicionales (opcional)
}
```

### Funciones Principales

#### `generar_pregunta(tema_id, seed, dificultad)`
Función principal que genera una pregunta para cualquier tema.

```python
pregunta = generar_pregunta(tema_id=5, seed=12345, dificultad=2)
# Retorna un diccionario con la estructura estándar
```

#### `obtener_temas_disponibles()`
Retorna la lista de IDs de temas con generadores específicos.

```python
temas = obtener_temas_disponibles()
# Retorna: [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 21, 22]
```

### Generadores Implementados

| Tema | Función | Tipo | Descripción |
|------|---------|------|-------------|
| 1 | `generar_pregunta_tema_1` | texto | Sumas |
| 2 | `generar_pregunta_tema_2` | texto | Multiplicación/División |
| 3 | `generar_pregunta_tema_3` | slider | Recta Numérica |
| 4 | `generar_pregunta_tema_4` | radio | Desigualdades |
| 5 | `generar_pregunta_tema_5` | radio | Fracciones |
| 6 | `generar_pregunta_tema_6` | texto | Op. con Fracciones (×/÷) |
| 7 | `generar_pregunta_tema_7` | texto | Op. con Fracciones (+/−) |
| 9 | `generar_pregunta_tema_9` | texto | Conjuntos Numéricos |
| 10 | `generar_pregunta_tema_10` | radio | Propiedades |
| 11 | `generar_pregunta_tema_11` | texto | Valor Absoluto |
| 12 | `generar_pregunta_tema_12` | texto | Expresiones Algebraicas |
| 13 | `generar_pregunta_tema_13` | texto | Ecuaciones Simples |
| 14 | `generar_pregunta_tema_14` | texto | Ecuaciones con Paréntesis |
| 15 | `generar_pregunta_tema_15` | texto | Ecuaciones Lineales Complejas |
| 16 | `generar_pregunta_tema_16` | texto | Pendiente |
| 17 | `generar_pregunta_tema_17` | texto | Ecuación de la Recta |
| 19 | `generar_pregunta_tema_19` | texto | Sistemas de Ecuaciones |
| 21 | `generar_pregunta_tema_21` | texto | Factorización |
| 22 | `generar_pregunta_tema_22` | texto | Ecuaciones Cuadráticas |

**Temas con generador genérico:** 8, 18, 20  
**Tema excluido:** 23

## Gestión de Estado (Session State)

```python
st.session_state.exam_state       # 'selection', 'taking_exam', 'results'
st.session_state.exam_questions   # Lista de preguntas generadas
st.session_state.exam_answers     # Lista de respuestas del estudiante
st.session_state.current_question_idx  # Índice de pregunta actual
st.session_state.exam_seed        # Semilla para generación aleatoria
```

## Flujo de Usuario

1. **Inicio**: Clic en "Iniciar Simulación de Examen" desde `inicio.py`
2. **Selección**: Usuario marca los temas que desea practicar
3. **Generación**: Sistema genera 3 preguntas por tema (importadas desde módulo)
4. **Examen**: Usuario responde pregunta por pregunta con navegación flexible
5. **Resultados**: Sistema evalúa y muestra resultados detallados
6. **Cierre**: Usuario puede generar nuevo examen o volver al inicio

## Ventajas de la Arquitectura Modular

### ✅ Reutilización de Código
- Los generadores pueden ser usados por otros componentes
- Potencial para refactorizar `quiz_X.py` en el futuro

### ✅ Mantenibilidad
- Un solo lugar para corregir bugs en la generación
- Cambios en la lógica no afectan la UI

### ✅ Escalabilidad
- Fácil agregar nuevos temas
- Fácil agregar nuevos tipos de preguntas

### ✅ Testabilidad
- Los generadores pueden probarse independientemente
- No requieren interfaz de usuario para testing

## Cómo Agregar un Nuevo Tema

### Paso 1: Agregar Generador en `quiz_generators.py`

```python
def generar_pregunta_tema_25(seed, dificultad):
    """Tema 25: Descripción del tema"""
    random.seed(seed)
    
    # Tu lógica de generación aquí
    pregunta = "..."
    respuesta = "..."
    
    return {
        'pregunta': pregunta,
        'respuesta_correcta': respuesta,
        'tipo': 'texto',  # o 'radio' o 'slider'
        'tema_id': 25
    }
```

### Paso 2: Registrar en el Diccionario

```python
GENERADORES_POR_TEMA = {
    ...
    25: generar_pregunta_tema_25,  # ← Agregar aquí
}
```

### Paso 3: ¡Listo!

El sistema automáticamente:
- ✅ Detectará el nuevo tema
- ✅ Lo mostrará en la selección
- ✅ Generará preguntas cuando sea seleccionado

## Uso del Sistema

### Para Estudiantes

1. Ingresar con matrícula
2. Clic en "Iniciar Simulación de Examen"
3. Seleccionar temas deseados
4. Responder las preguntas
5. Ver resultados y decidir siguiente acción

### Para Desarrolladores

#### Importar y Usar Generadores

```python
from quiz_generators import generar_pregunta, obtener_temas_disponibles

# Generar una pregunta
pregunta = generar_pregunta(tema_id=5, seed=123, dificultad=2)

# Obtener temas disponibles
temas = obtener_temas_disponibles()
```

#### Estructura de Código

```python
# BUENO: Importar desde módulo compartido
from quiz_generators import generar_pregunta

# MALO: Duplicar código de generación
def mi_propia_version_de_generador():
    # código duplicado...
```

## Integración con el Sistema Existente

### No Modifica Archivos Existentes
- ✅ Los archivos `quiz_1.py` a `quiz_23.py` permanecen sin cambios
- ✅ Solo se agregó un botón en `inicio.py`
- ✅ Toda la nueva funcionalidad está encapsulada

### Base de Datos
- Lee información de temas desde `primeroc.public.subjects`
- Filtra tema 23 automáticamente
- Obtiene dificultad y nombre de cada tema

### Sin Persistencia de Resultados
- Los resultados del examen **no se guardan** en la base de datos
- Diferente a los quizzes regulares (intencional para práctica)
- Puede agregarse en el futuro si se requiere

## Mejoras Futuras Sugeridas

### Funcionalidad
1. **Guardar Historial**: Almacenar resultados en base de datos
2. **Reportes de Progreso**: Análisis de desempeño por tema
3. **Modo Timed**: Opción de tiempo límite
4. **Modo Estricto**: Desactivar navegación hacia atrás

### Código
5. **Refactorizar Quizzes**: Migrar `quiz_X.py` para usar `quiz_generators.py`
6. **Tests Unitarios**: Agregar pruebas para cada generador
7. **Validación Flexible**: Aceptar múltiples formatos de respuesta
8. **Temas Complejos**: Implementar temas 8, 18, 20 completamente

### UX
9. **Exportar Resultados**: Descargar en PDF
10. **Hints**: Sistema de pistas durante el examen
11. **Revisión**: Permitir revisar respuestas antes de finalizar
12. **Estadísticas**: Dashboard con análisis detallado

## Requerimientos Cumplidos

| Requerimiento | Estado | Notas |
|---------------|--------|-------|
| Selección múltiple de temas | ✅ | Con validación |
| Exclusión del tema 23 | ✅ | Automático |
| 3 ejercicios por tema | ✅ | Configurable |
| Orden aleatorio | ✅ | Usando shuffle |
| Navegación uno por uno | ✅ | Con back/forward |
| Registro de respuestas | ✅ | En session state |
| Resumen con estadísticas | ✅ | Completo |
| Sin modificar quizzes | ✅ | Solo agregado botón |
| Integración limpia | ✅ | Módulo separado |
| Código modular | ✅ | **Mejora aplicada** |
| Sin hardcoding | ✅ | **Mejora aplicada** |

## Conclusión

La funcionalidad de **Simulación de Examen** está completamente implementada siguiendo **mejores prácticas de desarrollo**:

### ✅ Completitud
- Todos los requerimientos funcionales cumplidos
- 19 temas con generadores específicos
- Sistema robusto y funcional

### ✅ Calidad de Código
- **Arquitectura modular** con separación de responsabilidades
- **Código reutilizable** mediante módulo compartido
- **Sin duplicación** de lógica de generación
- **Fácil mantenimiento** y extensibilidad

### ✅ Documentación
- Código bien comentado
- README completo
- Ejemplos de uso
- Guías para desarrolladores

### 🚀 Listo para Producción
El sistema está preparado para ser usado por estudiantes y puede ser fácilmente extendido por desarrolladores en el futuro.
