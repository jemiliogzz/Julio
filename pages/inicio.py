import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

if "mat" in st.session_state:
    mat = st.session_state["mat"]
else:
    st.switch_page("streamlit_app.py")

st.title("¡Práctica de Ejercicios!")
st.write("Selecciona tu tema a practicar")

cnx = st.connection("snowflake")
session = cnx.session()

# Obtener ID del estudiante
estudiante_info = session.table("primeroc.public.students") \
    .filter(col("matricula") == mat) \
    .select(col("id_estudiante")) \
    .collect()[0]
id_estudiante = estudiante_info.ID_ESTUDIANTE

# ------------------------------
# TAREA ACTIVA
# ------------------------------
st.subheader("📋 Tarea")

# Verificar si existe una tarea activa
tareas_activas = session.table("primeroc.public.tareas") \
    .filter(col("active") == True) \
    .collect()

if tareas_activas:
    tarea = tareas_activas[0]
    id_tarea = tarea.ID_TAREA
    id_tema = tarea.ID_TEMA
    premio10_id = tarea.PREMIO10
    premio20_id = tarea.PREMIO20
    premio30_id = tarea.PREMIO30
    
    # Obtener nombre del tema
    tema_info = session.table("primeroc.public.subjects") \
        .filter(col("id_tema") == id_tema) \
        .select(col("nombre_tema")) \
        .collect()[0]
    nombre_tema = tema_info.NOMBRE_TEMA
    
    # Verificar progreso del estudiante en tarea_red
    progreso_tarea = session.table("primeroc.public.tarea_red") \
        .filter((col("id_tarea") == id_tarea) & (col("id_estudiante") == id_estudiante)) \
        .collect()
    
    # Calcular puntos acumulados por el estudiante en el tema específico
    query_puntos = f"""
        SELECT COALESCE(SUM(PTS), 0) AS TOTAL_PUNTOS
        FROM PRIMEROC.PUBLIC.DONE_DONE_DONE
        WHERE ID_EST = {id_estudiante} AND ID_TEMA = {id_tema}
    """
    puntos_tema = session.sql(query_puntos).collect()[0]["TOTAL_PUNTOS"]
    
    # Inicializar flags de premios obtenidos
    premio10_obtenido = False
    premio20_obtenido = False
    premio30_obtenido = False
    
    if progreso_tarea:
        # Ya existe un registro
        premio10_obtenido = progreso_tarea[0].PREMIO10 or False
        premio20_obtenido = progreso_tarea[0].PREMIO20 or False
        premio30_obtenido = progreso_tarea[0].PREMIO30 or False
    
    # Actualizar progreso según los puntos alcanzados
    if puntos_tema >= 10 and not premio10_obtenido:
        if not progreso_tarea:
            # Crear el registro inicial
            insert_tarea_red = f"""
                INSERT INTO PRIMEROC.PUBLIC.TAREA_RED (ID_TAREA, ID_ESTUDIANTE, PREMIO10, PREMIO20, PREMIO30)
                VALUES ({id_tarea}, {id_estudiante}, TRUE, FALSE, FALSE)
            """
            session.sql(insert_tarea_red).collect()
            premio10_obtenido = True
        else:
            # Actualizar premio10
            update_tarea_red = f"""
                UPDATE PRIMEROC.PUBLIC.TAREA_RED
                SET PREMIO10 = TRUE
                WHERE ID_TAREA = {id_tarea} AND ID_ESTUDIANTE = {id_estudiante}
            """
            session.sql(update_tarea_red).collect()
            premio10_obtenido = True
        
        # Agregar premio10 a belongings automáticamente
        if premio10_id:
            insert_belongings = f"""
                INSERT INTO PRIMEROC.PUBLIC.BELONGINGS (ID_ESTUDIANTE, ID_PRODUCTO, REDIMIDO)
                VALUES ({id_estudiante}, {premio10_id}, FALSE)
            """
            session.sql(insert_belongings).collect()
    
    if puntos_tema >= 20 and not premio20_obtenido:
        update_tarea_red = f"""
            UPDATE PRIMEROC.PUBLIC.TAREA_RED
            SET PREMIO20 = TRUE
            WHERE ID_TAREA = {id_tarea} AND ID_ESTUDIANTE = {id_estudiante}
        """
        session.sql(update_tarea_red).collect()
        premio20_obtenido = True
        
        # Agregar premio20 a belongings automáticamente
        if premio20_id:
            insert_belongings = f"""
                INSERT INTO PRIMEROC.PUBLIC.BELONGINGS (ID_ESTUDIANTE, ID_PRODUCTO, REDIMIDO)
                VALUES ({id_estudiante}, {premio20_id}, FALSE)
            """
            session.sql(insert_belongings).collect()
    
    if puntos_tema >= 30 and not premio30_obtenido:
        update_tarea_red = f"""
            UPDATE PRIMEROC.PUBLIC.TAREA_RED
            SET PREMIO30 = TRUE
            WHERE ID_TAREA = {id_tarea} AND ID_ESTUDIANTE = {id_estudiante}
        """
        session.sql(update_tarea_red).collect()
        premio30_obtenido = True
        
        # Agregar premio30 a belongings automáticamente
        if premio30_id:
            insert_belongings = f"""
                INSERT INTO PRIMEROC.PUBLIC.BELONGINGS (ID_ESTUDIANTE, ID_PRODUCTO, REDIMIDO)
                VALUES ({id_estudiante}, {premio30_id}, FALSE)
            """
            session.sql(insert_belongings).collect()
    
    # Mostrar mensaje de tarea pendiente
    if puntos_tema < 30:
        st.info("¡Tarea pendiente! Alcanza 30 puntos para completarla.")
    else:
        st.success("¡Felicidades! Has completado la tarea. 🎉")
    
    # Mostrar progreso
    st.write(f"**Progreso actual:** {puntos_tema}/30 puntos en el tema **{nombre_tema}**")
    st.progress(min(puntos_tema / 30, 1.0))
    
    # Obtener información de los premios desde la tabla shop
    premios_info = {}
    for premio_id in [premio10_id, premio20_id, premio30_id]:
        if premio_id:
            producto = session.table("primeroc.public.shop") \
                .filter(col("id_producto") == premio_id) \
                .select(col("producto")) \
                .collect()
            if producto:
                premios_info[premio_id] = producto[0].PRODUCTO
    
    # Mostrar premios disponibles (solo los que no se han obtenido)
    st.write(f"**Logra puntos con el tema {nombre_tema} para conseguir los siguientes premios:**")
    
    premios_pendientes = []
    if not premio10_obtenido and premio10_id in premios_info:
        premios_pendientes.append(f"✨ 10 puntos → {premios_info[premio10_id]}")
    if not premio20_obtenido and premio20_id in premios_info:
        premios_pendientes.append(f"✨ 20 puntos → {premios_info[premio20_id]}")
    if not premio30_obtenido and premio30_id in premios_info:
        premios_pendientes.append(f"✨ 30 puntos → {premios_info[premio30_id]}")
    
    if premios_pendientes:
        for premio in premios_pendientes:
            st.write(premio)
    else:
        st.write("¡Has obtenido todos los premios! 🏆")
else:
    st.info("No hay tareas activas en este momento.")

st.divider()

# ------------------------------
# SIMULACIÓN DE EXAMEN (Solo para matrícula 112233)
# ------------------------------

st.subheader("🎯 Simulación de Examen")
st.write("Prepárate para tus exámenes con ejercicios personalizados de los temas que elijas.")

if st.button("Iniciar Simulación de Examen", type="primary", use_container_width=True):
    st.switch_page("pages/simulacion_examen.py")

st.divider()

# ------------------------------
# TEMAS
# ------------------------------
temas = session.table("primeroc.public.subjects").select(col('nombre_tema'))

option = st.selectbox(
    "¿Qué tema quisieras practicar?",
    temas,
)

tema_conf = st.button('Confirmar')

if tema_conf:
    tema_id = session.table("primeroc.public.subjects") \
        .filter(col('nombre_tema') == option) \
        .collect()[0][0]
    st.session_state['tema'] = tema_id
    ubi_quiz = "pages/quiz_" + str(tema_id) + ".py"
    st.switch_page(ubi_quiz)

# ------------------------------
# TIENDA
# ------------------------------
st.subheader("Tienda 🛒")

# Buscar puntos actuales del estudiante
puntos_act = session.table("primeroc.public.students") \
    .filter(col("matricula") == mat) \
    .select(col("puntos_act")) \
    .collect()[0].PUNTOS_ACT

# Mostrar puntos disponibles
st.markdown(f"### 💰 Tus puntos actuales: **{puntos_act}**")

# Cargar productos ordenados por precio ascendente
productos = (
    session.table("primeroc.public.shop")
           .sort(col("PRECIO"))
           .collect()
)

# Mostrar productos como tabla con botón de compra
for prod in productos:
    col1, col2, col3 = st.columns([3,1,1])
    with col1:
        st.write(f"**{prod.PRODUCTO}**")
    with col2:
        st.write(f"${prod.PRECIO}")
    with col3:
        # Verificar si tiene puntos suficientes
        if puntos_act >= prod.PRECIO:
            if st.button("Comprar", key=f"comprar_{prod.ID_PRODUCTO}"):
                # Insertar la compra
                insert_stmt = f"""
                    INSERT INTO PRIMEROC.PUBLIC.BELONGINGS (ID_ESTUDIANTE, ID_PRODUCTO, REDIMIDO)
                    VALUES ({id_estudiante}, {prod.ID_PRODUCTO}, FALSE)
                """
                session.sql(insert_stmt).collect()

                # Descontar puntos y aumentar compras totales
                update_stmt = f"""
                    UPDATE PRIMEROC.PUBLIC.STUDENTS
                    SET PUNTOS_ACT = PUNTOS_ACT - {prod.PRECIO},
                        COMPRAS_TOTALES = COMPRAS_TOTALES + 1
                    WHERE ID_ESTUDIANTE = {id_estudiante}
                """
                session.sql(update_stmt).collect()

                st.success(f"Compraste {prod.PRODUCTO} 🎉")
                st.rerun()
        else:
            st.button("Sin puntos", key=f"nop_{prod.ID_PRODUCTO}", disabled=True)


# ------------------------------
# INVENTARIO DEL ESTUDIANTE
# ------------------------------
st.subheader("Tus pertenencias 🎁")

bel = session.table("primeroc.public.belongings").alias("b")
shop = session.table("primeroc.public.shop").alias("s")

# Productos NO redimidos
no_redimidos = (
    bel.join(shop, bel["ID_PRODUCTO"] == shop["ID_PRODUCTO"])
       .filter((bel["ID_ESTUDIANTE"] == id_estudiante) & (bel["REDIMIDO"] == False))
       .select(
           shop["PRODUCTO"].alias("producto"),
           shop["PRECIO"].alias("precio")
       )
       .collect()
)

# Productos redimidos
redimidos = (
    bel.join(shop, bel["ID_PRODUCTO"] == shop["ID_PRODUCTO"])
       .filter((bel["ID_ESTUDIANTE"] == id_estudiante) & (bel["REDIMIDO"] == True))
       .select(
           shop["PRODUCTO"].alias("producto"),
           shop["PRECIO"].alias("precio")
       )
       .collect()
)

# Mostrar
st.markdown("#### 🟢 Productos disponibles (no redimidos)")
if no_redimidos:
    for item in no_redimidos:
        st.write(f"- {item.PRODUCTO}")
else:
    st.write("No tienes productos disponibles.")

st.markdown("#### ⚪ Productos ya canjeados")
if redimidos:
    for item in redimidos:
        st.write(f"- {item.PRODUCTO}")
else:
    st.write("Aún no has canjeado nada.")
