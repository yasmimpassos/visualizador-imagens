import streamlit as st
from PIL import Image
import io
import cv2
import numpy as np

st.set_page_config(page_title="Visualizador de Imagens", page_icon="📷", layout="wide")

st.title("Editor de Imagens")
st.write("Escolha uma imagem para poder editar")

st.sidebar.title("Ajustes da imagem")

resize = st.sidebar.checkbox("Redimensionar", value=False)
if resize:
   width = st.sidebar.number_input("Largura", min_value=1, value=800)
   height = st.sidebar.number_input("Altura", min_value=1, value=600)

rotate = st.sidebar.slider("Rotação", 0, 360, 0, step=1)

gray_scale = st.sidebar.checkbox("Escala de cinza")
invert_colors = st.sidebar.checkbox("Inversão de cores")
sharpen = st.sidebar.checkbox("Nitidez")
edge_detection = st.sidebar.checkbox("Detecção de bordas")
contrast = st.sidebar.checkbox("Aumento de contraste")
blur = st.sidebar.checkbox("Desfoque (Blur)")

uploaded_file = st.file_uploader("Selecione uma imagem", type=["jpg", "jpeg", "png"])

if uploaded_file:

    image = Image.open(uploaded_file)
    filtered_image_np = np.array(image)

    if resize:
       filtered_image_np = cv2.resize(filtered_image_np, (width, height))

    if rotate != 0:
       center = (filtered_image_np.shape[1] // 2, filtered_image_np.shape[0] // 2)
       rotation_matrix = cv2.getRotationMatrix2D(center, rotate, 1.0) 
       filtered_image_np = cv2.warpAffine(filtered_image_np, rotation_matrix, (filtered_image_np.shape[1], filtered_image_np.shape[0]))

    if gray_scale:
        filtered_image_np = cv2.cvtColor(filtered_image_np, cv2.COLOR_BGR2GRAY)
        filtered_image_np = cv2.cvtColor(filtered_image_np, cv2.COLOR_GRAY2BGR)

    if invert_colors:
        filtered_image_np = cv2.bitwise_not(filtered_image_np)

    if sharpen:
        kernel = np.array([[-1, -1, -1],
                            [-1, 9, -1],
                            [-1, -1, -1]])
        
        filtered_image_np = cv2.filter2D(filtered_image_np, -1, kernel)
    
    if edge_detection:
        filtered_image_np = cv2.Canny(filtered_image_np, 100, 200)
        filtered_image_np = cv2.cvtColor(filtered_image_np, cv2.COLOR_GRAY2BGR)

    if contrast:
        alpha = 1.5
        beta = 0
        filtered_image_np = cv2.convertScaleAbs(filtered_image_np, alpha=alpha, beta=beta)

    if blur:
        kernel_size = (5, 5)
        filtered_image_np = cv2.GaussianBlur(filtered_image_np, kernel_size, 0)

    filtered_image = Image.fromarray(filtered_image_np)

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