# 🔒 Restricción de Acceso - Simulación de Examen

## Cambios Implementados

Se ha restringido el acceso a la funcionalidad de **Simulación de Examen** únicamente para la matrícula **112233**.

## Implementación de Seguridad (Doble Capa)

### Capa 1: Ocultación en UI (`inicio.py`)
**Líneas 179-186**

```python
if mat == '112233':
    st.subheader("🎯 Simulación de Examen")
    st.write("Prepárate para tus exámenes con ejercicios personalizados de los temas que elijas.")
    
    if st.button("Iniciar Simulación de Examen", type="primary", use_container_width=True):
        st.switch_page("pages/simulacion_examen.py")
    
    st.divider()
```

**Comportamiento:**
- ✅ Si matrícula = `112233` → Botón visible
- ❌ Si matrícula ≠ `112233` → Botón oculto (no aparece en la página)

### Capa 2: Validación de Acceso (`simulacion_examen.py`)
**Líneas 18-27**

```python
# Restricción de acceso: Solo matrícula 112233
if mat != '112233':
    st.title("🔒 Acceso Restringido")
    st.error("⚠️ Esta funcionalidad está en fase de prueba.")
    st.info("La Simulación de Examen estará disponible próximamente para todos los estudiantes.")
    
    if st.button("🏠 Volver a Inicio"):
        st.switch_page("pages/inicio.py")
    
    st.stop()  # Detener ejecución del resto del código
```

**Comportamiento:**
- ✅ Si matrícula = `112233` → Acceso permitido, continúa a la simulación
- ❌ Si matrícula ≠ `112233` → Muestra mensaje amigable y detiene ejecución

## Pantalla de Acceso Restringido

Cuando un estudiante sin autorización intenta acceder, verá:

```
🔒 Acceso Restringido

⚠️ Esta funcionalidad está en fase de prueba.

💡 La Simulación de Examen estará disponible 
   próximamente para todos los estudiantes.

[🏠 Volver a Inicio]
```

## Razones para la Doble Capa

### 1. **Mejor Experiencia de Usuario**
- Los estudiantes no autorizados no ven el botón → No se frustran intentando acceder
- Mensaje claro si intentan acceder directamente

### 2. **Seguridad Real**
- No se puede acceder modificando la URL
- No se puede acceder mediante bookmarks antiguos
- No se puede acceder mediante scripts externos

### 3. **Buenas Prácticas**
- **Never Trust the Client**: La validación debe estar en el servidor/backend
- **Defense in Depth**: Múltiples capas de seguridad
- **Graceful Degradation**: Mensaje amigable en caso de error

## Casos de Uso

### Caso 1: Estudiante Autorizado (112233)
```
1. Login con matrícula 112233
2. Ve la página de inicio
3. ✅ Ve el botón "Iniciar Simulación de Examen"
4. Click en el botón
5. ✅ Accede a la simulación sin problemas
6. Usa la funcionalidad normalmente
```

### Caso 2: Estudiante No Autorizado (cualquier otra matrícula)
```
1. Login con otra matrícula (ej: 123456)
2. Ve la página de inicio
3. ❌ NO ve el botón "Iniciar Simulación de Examen"
4. Continúa usando otras funcionalidades (quizzes, tienda, etc.)
```

### Caso 3: Intento de Acceso Directo
```
1. Estudiante con matrícula 123456
2. Intenta acceder directamente a la URL de simulación
3. ❌ Ve pantalla de "Acceso Restringido"
4. Mensaje amigable explicando la situación
5. Botón para volver a inicio
```

## Cómo Modificar la Restricción

### Para Autorizar Otra Matrícula

**Opción 1: Matrícula Individual**
```python
# En inicio.py y simulacion_examen.py
if mat == '999999':  # ← Cambiar aquí
```

**Opción 2: Múltiples Matrículas**
```python
# Lista de matrículas autorizadas
MATRICULAS_AUTORIZADAS = ['112233', '999999', '888888']

# En inicio.py y simulacion_examen.py
if mat in MATRICULAS_AUTORIZADAS:
```

**Opción 3: Autorizar a Todos (Quitar Restricción)**
```python
# En inicio.py: Eliminar el if y desindentar el contenido
st.subheader("🎯 Simulación de Examen")
st.write("Prepárate para tus exámenes con ejercicios personalizados de los temas que elijas.")

if st.button("Iniciar Simulación de Examen", type="primary", use_container_width=True):
    st.switch_page("pages/simulacion_examen.py")

st.divider()

# En simulacion_examen.py: Eliminar líneas 18-27 completas
```

### Para Usar Base de Datos (Método Recomendado)

Si en el futuro quieres gestionar accesos desde base de datos:

```python
# En simulacion_examen.py
# Verificar si tiene acceso desde base de datos
tiene_acceso = session.table("primeroc.public.accesos_especiales") \
    .filter((col('matricula') == mat) & (col('funcionalidad') == 'simulacion_examen')) \
    .count() > 0

if not tiene_acceso:
    st.title("🔒 Acceso Restringido")
    # ... mensaje ...
    st.stop()
```

## Archivos Modificados

| Archivo | Líneas | Cambio |
|---------|--------|--------|
| `pages/inicio.py` | 179-186 | Botón condicionado a matrícula 112233 |
| `pages/simulacion_examen.py` | 18-27 | Validación de acceso con mensaje |

## Testing

### Probar con Matrícula Autorizada (112233)
```
1. Login con 112233
2. ✅ Verificar que aparece el botón en inicio
3. ✅ Click en el botón
4. ✅ Verificar acceso a la simulación
5. ✅ Verificar que funciona normalmente
```

### Probar con Matrícula No Autorizada
```
1. Login con otra matrícula
2. ✅ Verificar que NO aparece el botón
3. (Opcional) Intentar acceso directo por URL
4. ✅ Verificar mensaje de acceso restringido
5. ✅ Verificar botón de volver a inicio funciona
```

## Notas Importantes

### ⚠️ Consideraciones de Seguridad

1. **Validación en Backend**: La validación real está en `simulacion_examen.py`, no solo en la UI
2. **Session State**: Se usa `st.session_state["mat"]` que se establece en el login
3. **No Modificar Directamente**: Los estudiantes no pueden modificar su matrícula en session state sin re-autenticarse

### 💡 Recomendaciones

1. **Monitorear**: Si necesitas saber quién intenta acceder, agrega logging
2. **Comunicar**: Avisa a los estudiantes cuándo estará disponible para todos
3. **Documentar**: Mantén registro de quiénes tienen acceso especial

### 🔄 Rollback (Reversar Cambios)

Si necesitas reversar estos cambios:

1. En `inicio.py`: Eliminar el `if mat == '112233':` y desindentar
2. En `simulacion_examen.py`: Eliminar líneas 18-27
3. Commit y push

## Resumen

✅ **Implementado**: Restricción de acceso a matrícula 112233  
✅ **Seguridad**: Doble capa (UI + Backend)  
✅ **UX**: Mensaje amigable para usuarios no autorizados  
✅ **Mantenible**: Fácil modificar o quitar restricción  
✅ **Documentado**: Este archivo explica todo  

---

**Fecha de implementación**: Noviembre 2025  
**Matrícula autorizada**: 112233  
**Estado**: Activo ✅

