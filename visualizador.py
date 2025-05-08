import streamlit as st
from PIL import Image
import io

st.set_page_config(page_title="Visualizador de Imagens", page_icon="📷", layout="wide")

st.title("Editor de Imagens")
st.write("Escolha uma imagem para poder editar")

st.sidebar.title("Ajustes da imagem")

uploaded_file = st.file_uploader("Selecione uma imagem", type=["jpg", "jpeg", "png"])

if uploaded_file:

    image = Image.open(uploaded_file)
    filtered_image = image.copy()

    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        st.image(image, caption="Imagem carregada", use_container_width=True)
    with col2:
        st.image(filtered_image, caption="Imagem com filtros aplicados", use_container_width=True)

    buffer = io.BytesIO()
    filtered_image.save(buffer, format="PNG")
    byte_data = buffer.getvalue()

    st.download_button(
        label="Baixar imagem editada",
        data=byte_data,
        file_name="imagem_editada.png",
        mime="image/png",
    )