import streamlit as st
from Home import home
from Model import model
from Results import results

# Default route
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Nav bar
st.markdown("## Tariff Impact Interface")
with st.container():
    st.markdown(
        """
        <div style='text-align: center; max-width: 600px; margin: auto;'>
        """,
        unsafe_allow_html=True
    )
    nav = st.columns(3, gap="medium")
    with nav[0]:
        if st.button("🏠 Home"):
            st.session_state.page = "Home"
    with nav[1]:
        if st.button("🧮 Model"):
            st.session_state.page = "Model"
    with nav[2]:
        if st.button("📊 Results"):
            st.session_state.page = "Results"
    st.markdown("</div>", unsafe_allow_html=True)


st.markdown("---")

# Render active page
if st.session_state.page == "Home":
    home()
elif st.session_state.page == "Model":
    model()
elif st.session_state.page == "Results":
    results()
