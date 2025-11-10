# 📋 Guía de Refactorización de Quizzes

## Objetivo

Modificar todos los archivos `quiz_##.py` para que:
1. Usen una variable `cantidad_preguntas` en lugar de hardcode `5`
2. La validación use `for i in range(cantidad_preguntas)` en lugar de hardcode
3. Soporten modo examen (3 preguntas) y modo práctica normal (5 preguntas)
4. Naveguen automáticamente entre temas en modo examen

## Cambios Necesarios en Cada Quiz

### Paso 1: Agregar Imports

**Buscar:**
```python
#Reutilizable
import streamlit as st
import random
import time 
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
```

**Reemplazar con:**
```python
#Reutilizable
import streamlit as st
import random
import time 
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import sys
sys.path.append('..')
from quiz_utils import obtener_cantidad_preguntas, esta_en_modo_examen, obtener_siguiente_tema_examen, avanzar_siguiente_tema_examen, registrar_resultado_examen
```

### Paso 2: Agregar Variable cantidad_preguntas

**Buscar:**
```python
preguntas = []
respuestas = []

for i in range (5):
```

**Reemplazar con:**
```python
preguntas = []
respuestas = []

# Obtener cantidad de preguntas (5 por defecto, 3 si es examen)
cantidad_preguntas = obtener_cantidad_preguntas()

for i in range(cantidad_preguntas):
```

### Paso 3: Actualizar Loop de Formulario

**Buscar:**
```python
    respuestas_estudiante = []
    
    for i in range(5):
```

**Reemplazar con:**
```python
    respuestas_estudiante = []
    
    for i in range(cantidad_preguntas):
```

### Paso 4: Actualizar Loop de Validación

**Buscar:**
```python
#Reutilizable
if logrado:
    pts = 0
    
    for i in range(5):
```

**Reemplazar con:**
```python
#Reutilizable
if logrado:
    pts = 0
    
    for i in range(cantidad_preguntas):
```

### Paso 5: Actualizar Condición de Puntos Extra

**Buscar:**
```python
    pts_extra = 0
    if pts == 5:
```

**Reemplazar con:**
```python
    pts_extra = 0
    if pts == cantidad_preguntas:
```

### Paso 6: Reemplazar Lógica de Guardado y Navegación

**Buscar TODO el bloque desde `pts_extra = 0` hasta el final del archivo (antes de `#Fin`):**

```python
    pts_extra = 0
    if pts == 5:
        st.write(f"Felicidades por contestar todo bien. Obtienes", info[2], "punto(s) adicional.")
        pts_extra += info[2]
    
    pts = int((pts * 0.7) + (pts * 0.3 * info[2]) + 0.1) + pts_extra
    std_ac = std_info[3] + pts 
    std_tot = std_info[4] + pts
    std_id = std_info[0]
    
    st.write("En esta práctica, obtuviste: **" + str(pts) + "pts.**")
    st.write("Puntos Actuales: " + str(std_ac) + "pts.")
    st.write("Puntos Totales: " + str(std_tot) + "pts.")
    
    my_insert_stmt = """update students
    set puntos_act = """ + str(std_ac) + """, puntos_tot = """ + str(std_tot) + """
    WHERE matricula = """ + mat
    session.sql(my_insert_stmt).collect()
    
    my_insert_stmt = insert_stmt = f"""
    INSERT INTO PRIMEROC.PUBLIC.DONE_DONE_DONE VALUES
    ({std_id}, '{st.session_state.tema}', {pts}, CURRENT_TIMESTAMP)
    """
    session.sql(my_insert_stmt).collect()

regresar = st.button("Volver a inicio")
if regresar:
    st.session_state.s_seed = new_seed
    st.session_state.button_disabled = False
    st.switch_page("pages/inicio.py")
```

**Reemplazar con:**
```python
    pts_extra = 0
    if pts == cantidad_preguntas:
        st.write(f"Felicidades por contestar todo bien. Obtienes", info[2], "punto(s) adicional.")
        pts_extra += info[2]
    
    # Si está en modo examen, registrar resultado pero NO guardar puntos en BD
    if esta_en_modo_examen():
        registrar_resultado_examen(st.session_state.tema, pts, cantidad_preguntas)
        st.write(f"**Aciertos en este tema: {pts}/{cantidad_preguntas}**")
        
        # Botón para continuar al siguiente tema
        siguiente_tema = obtener_siguiente_tema_examen()
        if siguiente_tema is not None:
            if st.button("➡️ Continuar al siguiente tema", type="primary"):
                if avanzar_siguiente_tema_examen():
                    st.session_state.tema = siguiente_tema
                    st.session_state.s_seed = random.randint(1, 10000)
                    st.session_state.button_disabled = False
                    st.rerun()
        else:
            # Terminó el examen, mostrar resumen
            st.success("✅ Has completado todos los temas del examen!")
            if st.button("📊 Ver Resumen del Examen", type="primary"):
                st.switch_page("pages/simulacion_examen.py")
    else:
        # Modo práctica normal: guardar puntos en BD
        pts = int((pts * 0.7) + (pts * 0.3 * info[2]) + 0.1) + pts_extra
        std_ac = std_info[3] + pts 
        std_tot = std_info[4] + pts
        std_id = std_info[0]
        
        st.write("En esta práctica, obtuviste: **" + str(pts) + "pts.**")
        st.write("Puntos Actuales: " + str(std_ac) + "pts.")
        st.write("Puntos Totales: " + str(std_tot) + "pts.")
        
        my_insert_stmt = """update students
        set puntos_act = """ + str(std_ac) + """, puntos_tot = """ + str(std_tot) + """
        WHERE matricula = """ + mat
        session.sql(my_insert_stmt).collect()
        
        my_insert_stmt = insert_stmt = f"""
        INSERT INTO PRIMEROC.PUBLIC.DONE_DONE_DONE VALUES
        ({std_id}, '{st.session_state.tema}', {pts}, CURRENT_TIMESTAMP)
        """
        session.sql(my_insert_stmt).collect()
        
        regresar = st.button("Volver a inicio")
        if regresar:
            st.session_state.s_seed = new_seed
            st.session_state.button_disabled = False
            st.switch_page("pages/inicio.py")
```

## Archivos Ya Modificados (Ejemplos)

✅ `pages/quiz_1.py` - Completado  
✅ `pages/quiz_5.py` - Completado

## Archivos Pendientes

Necesitan ser modificados siguiendo los pasos anteriores:
- `pages/quiz_2.py`
- `pages/quiz_3.py`
- `pages/quiz_4.py`
- `pages/quiz_6.py`
- `pages/quiz_7.py`
- `pages/quiz_8.py`
- `pages/quiz_9.py`
- `pages/quiz_10.py`
- `pages/quiz_11.py`
- `pages/quiz_12.py`
- `pages/quiz_13.py`
- `pages/quiz_14.py`
- `pages/quiz_15.py`
- `pages/quiz_16.py`
- `pages/quiz_17.py`
- `pages/quiz_18.py`
- `pages/quiz_19.py`
- `pages/quiz_20.py`
- `pages/quiz_21.py`
- `pages/quiz_22.py`
- `pages/quiz_23.py` (si aplica)

## Notas Importantes

### Variaciones en Algunos Quizzes

Algunos quizzes pueden tener pequeñas variaciones:

1. **Quiz con `std_id` ya definido**: Algunos ya tienen `std_id = std_info[0]` antes del bloque de guardado
2. **Quiz con fórmulas diferentes**: Algunos pueden tener fórmulas ligeramente diferentes para calcular puntos
3. **Quiz con validación diferente**: Algunos pueden tener validaciones especiales (ej: quiz_23 con gráficas)

### Verificación

Después de modificar cada quiz, verificar:
- ✅ El quiz funciona en modo normal (5 preguntas)
- ✅ El quiz funciona en modo examen (3 preguntas)
- ✅ La navegación entre temas funciona
- ✅ Los resultados se registran correctamente

## Script de Verificación Rápida

Para verificar que un quiz está correctamente modificado, buscar:

1. ✅ `from quiz_utils import`
2. ✅ `cantidad_preguntas = obtener_cantidad_preguntas()`
3. ✅ `for i in range(cantidad_preguntas):` (al menos 3 veces)
4. ✅ `if pts == cantidad_preguntas:`
5. ✅ `if esta_en_modo_examen():`

## Flujo del Sistema

### Modo Práctica Normal
1. Estudiante selecciona tema desde inicio.py
2. Se carga quiz_##.py
3. `cantidad_preguntas = 5` (default)
4. Genera 5 preguntas
5. Valida con `for i in range(5)`
6. Guarda puntos en BD
7. Muestra botón "Volver a inicio"

### Modo Examen
1. Estudiante selecciona temas desde simulacion_examen.py
2. Se configura `exam_mode = True`
3. Se carga primer quiz_##.py
4. `cantidad_preguntas = 3` (modo examen)
5. Genera 3 preguntas
6. Valida con `for i in range(3)`
7. NO guarda puntos en BD
8. Registra resultado en `exam_resultados`
9. Muestra botón "Continuar al siguiente tema"
10. Al terminar todos los temas, muestra resumen en simulacion_examen.py

## Estado Actual

- ✅ Sistema base creado (`quiz_utils.py`)
- ✅ Nuevo sistema de simulación (`simulacion_examen.py`)
- ✅ 2 quizzes modificados como ejemplo (`quiz_1.py`, `quiz_5.py`)
- ⏳ Pendiente: Modificar los 20 quizzes restantes

