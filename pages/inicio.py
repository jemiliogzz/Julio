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

# Buscar el id_estudiante con la matrícula
id_estudiante = session.table("primeroc.public.students") \
    .filter(col("matricula") == mat) \
    .select(col("id_estudiante")) \
    .collect()[0][0]

# Cargar productos disponibles
productos = session.table("primeroc.public.shop").collect()

# Mostrar productos como tabla
for prod in productos:
    col1, col2, col3 = st.columns([3,1,1])
    with col1:
        st.write(f"**{prod.PRODUCTO}**")
    with col2:
        st.write(f"${prod.PRECIO}")
    with col3:
        if st.button("Comprar", key=f"comprar_{prod.ID_PRODCUTO}"):
            insert_stmt = f"""
                INSERT INTO PRIMEROC.PUBLIC.BELONGINGS (ID_ESTUDIANTE, ID_PRODUCTO, REDIMIDO)
                VALUES ({id_estudiante}, {prod.ID_PRODCUTO}, FALSE)
            """
            session.sql(insert_stmt).collect()
            st.success(f"Compraste {prod.PRODUCTO} 🎉")
            st.rerun()

# ------------------------------
# INVENTARIO DEL ESTUDIANTE
# ------------------------------
st.subheader("Tus pertenencias 🎁")

bel = session.table("primeroc.public.belongings").alias("b")
shop = session.table("primeroc.public.shop").alias("s")

inventario = (
    bel.join(shop, bel["ID_PRODUCTO"] == shop["ID_PRODUCTO"])
       .filter(bel["ID_ESTUDIANTE"] == id_estudiante)
       .select(
           shop["PRODUCTO"].alias("producto"),
           shop["PRECIO"].alias("precio"),
           bel["REDIMIDO"].alias("redimido")
       )
       .collect()
)

if inventario:
    for item in inventario:
        st.write(f"- {item.PRODUCTO} (Redimido: {item.REDIMIDO})")
else:
    st.write("Todavía no tienes productos.")

