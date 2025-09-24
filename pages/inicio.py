import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# pages = {
#     "Your account": [
#         st.Page("create_account.py", title="Create your account"),
#         st.Page("manage_account.py", title="Manage your account"),
#     ],
#     "Resources": [
#         st.Page("learn.py", title="Learn about us"),
#         st.Page("trial.py", title="Try it out"),
#     ],
# }

# pg = st.navigation(pages)
# pg.run()

if "mat" in st.session_state:
    mat = st.session_state["mat"]
else:
    st.switch_page("streamlit_app.py")

st.title("¡Práctica de Ejercicios!")
st.write("Selecciona tu tema a practicar")

cnx = st.connection("snowflake")
session = cnx.session()

temas = session.table("primeroc.public.subjects").select(col('nombre_tema'))

option = st.selectbox(
    "¿Qué tema quisieras practicar?",
    temas,
)

tema_conf = st.button('Confirmar')

if tema_conf:
    tema_id = session.table("primeroc.public.subjects").filter(col('nombre_tema')==option).collect()[0][0]
    st.session_state['tema'] = tema_id
    ubi_quiz = "pages/quiz_" + str(tema_id) + ".py"
    st.switch_page(ubi_quiz)


    
