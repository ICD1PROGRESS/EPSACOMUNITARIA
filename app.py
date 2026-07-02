import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()
os.makedirs("data", exist_ok=True)
os.makedirs("data/logos", exist_ok=True)
os.makedirs("recibos", exist_ok=True)

from src.database.connection import init_db, get_session
from src.database.crud import get_all_epsas, create_epsa

def main():
    st.set_page_config(page_title="EPSACOL - Gestión de Agua", layout="wide")
    init_db()

    if "epsa_id" not in st.session_state:
        st.session_state.epsa_id = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"

    with st.sidebar:
        st.image("https://via.placeholder.com/150x80?text=EPSACOL", width=150)
        st.header("EPSA Activa")
        
        with get_session() as session:
            epsas = get_all_epsas(session)
        
        epsa_options = {e.nombre: e.id for e in epsas}
        selected_epsa_name = st.selectbox(
            "Seleccionar EPSA",
            list(epsa_options.keys()) if epsas else ["-- Crear nueva --"]
        )
        
        if selected_epsa_name == "-- Crear nueva --":
            new_name = st.text_input("Nombre de la nueva EPSA")
            new_city = st.text_input("Ciudad")
            if st.button("Crear EPSA", width='stretch'):
                if new_name and new_city:
                    with get_session() as sess:
                        epsa = create_epsa(sess, new_name, new_city)
                        st.session_state.epsa_id = epsa.id
                        st.rerun()
                else:
                    st.error("Complete nombre y ciudad")
        else:
            st.session_state.epsa_id = epsa_options[selected_epsa_name]
            st.success(f"EPSA activa: {selected_epsa_name}")
        
        st.divider()
        st.subheader("Menú")
        
        if st.button("📊 Dashboard", width='stretch'):
            st.session_state.current_page = "dashboard"
            st.rerun()
        if st.button("⚙️ Configuración EPSA", width='stretch'):
            st.session_state.current_page = "configuracion_epsa"
            st.rerun()
        if st.button("👥 Gestión de Usuarios", width='stretch'):
            st.session_state.current_page = "gestion_usuarios"
            st.rerun()
        if st.button("💰 Tarifas", width='stretch'):
            st.session_state.current_page = "configuracion_tarifas"
            st.rerun()
        if st.button("📝 Toma de Lecturas", width='stretch'):
            st.session_state.current_page = "toma_lecturas"
            st.rerun()
        if st.button("💵 Caja / Pagos", width='stretch'):
            st.session_state.current_page = "caja_pagos"
            st.rerun()
        if st.button("🔄 Cierre de Periodo", width='stretch'):
            st.session_state.current_page = "cierre_periodo"
            st.rerun()
        if st.button("📄 Reportes", width='stretch'):
            st.session_state.current_page = "reportes"
            st.rerun()

    # Cargar la página seleccionada
    try:
        if st.session_state.current_page == "dashboard":
            from src.ui.pages import dashboard
            dashboard.show()
        elif st.session_state.current_page == "configuracion_epsa":
            from src.ui.pages import configuracion_epsa
            configuracion_epsa.show()
        elif st.session_state.current_page == "gestion_usuarios":
            from src.ui.pages import gestion_usuarios
            gestion_usuarios.show()
        elif st.session_state.current_page == "configuracion_tarifas":
            from src.ui.pages import configuracion_tarifas
            configuracion_tarifas.show()
        elif st.session_state.current_page == "toma_lecturas":
            from src.ui.pages import toma_lecturas
            toma_lecturas.show()
        elif st.session_state.current_page == "caja_pagos":
            from src.ui.pages import caja_pagos
            caja_pagos.show()
        elif st.session_state.current_page == "cierre_periodo":
            from src.ui.pages import cierre_periodo
            cierre_periodo.show()
        elif st.session_state.current_page == "reportes":
            from src.ui.pages import reportes
            reportes.show()
        else:
            from src.ui.pages import dashboard
            dashboard.show()
    except ImportError as e:
        import traceback
        st.error(f"ImportError: {e}")
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
