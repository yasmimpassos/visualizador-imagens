import streamlit as st
from PIL import Image
import io
import cv2
import numpy as np
from streamlit_image_comparison import image_comparison
from rembg import remove

st.set_page_config(page_title="Visualizador de Imagens", page_icon="📷", layout="wide")

with st.container():
    st.markdown("""
        <h1 style='text-align: center;'>🖼️ Editor de Imagens Interativo</h1>
        <p style='text-align: center; color: gray;'>Aplique filtros, ajuste cores e compare o antes e depois.</p>
    """, unsafe_allow_html=True)

st.sidebar.title("⚙️ Ajustes da Imagem")

resize = st.sidebar.checkbox("🔄 Redimensionar", value=False)
if resize:
   width = st.sidebar.number_input("Largura", min_value=1, value=800)
   height = st.sidebar.number_input("Altura", min_value=1, value=600)

rotate = st.sidebar.checkbox("↻ Rotacionar", value=False)
if rotate:
    rotate = st.sidebar.slider("Rotação (graus)", 0, 360, 90, step=1)

gray_scale = st.sidebar.checkbox("⚫ Escala de cinza")
invert_colors = st.sidebar.checkbox("🔁 Inversão de cores")

sharpen = st.sidebar.checkbox("🧪 Nitidez")
if sharpen:
    sharpen = st.sidebar.slider("Intensidade da nitidez", 1.0, 2.0, 1.0, step=0.1)

edge_detection = st.sidebar.checkbox("📐 Detecção de bordas")
if edge_detection:
    edge_detection = st.sidebar.slider("Intensidade da detecção", 50, 150, 100, step=10)

contrast = st.sidebar.checkbox("🌓 Contraste")
if contrast:
    contrast = st.sidebar.slider("Intensidade do contraste", 0.0, 3.0, 1.5, step=0.1)

brightness = st.sidebar.checkbox("🔆 Brilho")
if brightness:
    brightness = st.sidebar.slider("Intensidade do brilho", -100, 100, 0, step=1)

saturation = st.sidebar.checkbox("🌈 Saturação")
if saturation:
    saturation = st.sidebar.slider("Intensidade da saturação", 0.0, 3.0, 1.0, step=0.1)

blur = st.sidebar.checkbox("💨 Desfoque (Blur)")
if blur:
    blur = st.sidebar.slider("Intensidade do desfoque", 1, 10, 5, step=1)
    blur *= 2
    blur -= 1

flip_horizontal = st.sidebar.checkbox("↔️ Espelhar horizontalmente")
flip_vertical = st.sidebar.checkbox("↕️ Espelhar verticalmente")

text = st.sidebar.checkbox("🔤 Adicionar texto")
if text:
    text_input = st.sidebar.text_input("Texto", value="Texto de exemplo")
    font_size = st.sidebar.slider("Tamanho da fonte", 10, 100, 30, step=1)
    color = st.sidebar.color_picker("Cor do texto", "#000000")
    position_x = st.sidebar.number_input("Posição X", min_value=0, value=50)
    position_y = st.sidebar.number_input("Posição Y", min_value=0, value=50)

    font_names = [
        "FONT_HERSHEY_SIMPLEX",
        "FONT_HERSHEY_COMPLEX",
        "FONT_HERSHEY_DUPLEX",
        "FONT_HERSHEY_TRIPLEX",
        "FONT_HERSHEY_COMPLEX_SMALL",
        "FONT_HERSHEY_PLAIN",
        "FONT_HERSHEY_SCRIPT_COMPLEX",
        "FONT_ITALIC",
        "QT_FONT_BLACK",
        "QT_FONT_NORMAL"
    ]
    font = st.sidebar.selectbox("Tipo de fonte", options=font_names, index=0)

crop = st.sidebar.checkbox("✂️ Recortar imagem")
if crop:
    crop_x1 = st.sidebar.number_input("X", min_value=0, value=0)
    crop_y1 = st.sidebar.number_input("Y", min_value=0, value=0)
    crop_tipe = st.sidebar.selectbox("Tipo de recorte", options=["por tamanho", "por ponto"], index=0)
    if crop_tipe == "por ponto":
        crop_x2 = st.sidebar.number_input("X2", min_value=0, value=200)
        crop_y2 = st.sidebar.number_input("Y2", min_value=0, value=200)
    else:
        crop_altura = st.sidebar.number_input("Largura", min_value=0, value=200)
        crop_largura = st.sidebar.number_input("Altura", min_value=0, value=200)

remove_bg = st.sidebar.checkbox("🧼 Remover fundo")

uploaded_file = st.file_uploader("📁 Selecione uma imagem", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.markdown("""
        <style>
        .stRadio > div {
            display: flex;
            justify-content: space-between;
            padding: 0.7rem 0;
        }
        .stRadio label {
            padding: 0.4rem 0.2rem;
        }
    """, unsafe_allow_html=True)

    view_mode = st.radio("🧭 Escolha como visualizar o resultado:", [ "🔀 Comparar Lado a Lado", "🧮 Comparar com Slider","📷 Imagem Original", "🖌️ Imagem Editada"], horizontal=True)

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
        kernel = np.array([[0, -1, 0],
                           [-1, 4 + sharpen, -1],
                           [0, -1, 0]], dtype=np.float32)
        filtered_image_np = cv2.filter2D(filtered_image_np, -1, kernel)

    if edge_detection:
        filtered_image_np = cv2.Canny(filtered_image_np, edge_detection, edge_detection * 2)
        filtered_image_np = cv2.cvtColor(filtered_image_np, cv2.COLOR_GRAY2BGR)

    if contrast and brightness:
        filtered_image_np = cv2.convertScaleAbs(filtered_image_np, alpha=contrast, beta=brightness)
    elif contrast:
        filtered_image_np = cv2.convertScaleAbs(filtered_image_np, alpha=contrast, beta=0)
    elif brightness:
        filtered_image_np = cv2.convertScaleAbs(filtered_image_np, alpha=1, beta=brightness)

    if saturation:
        hsv = cv2.cvtColor(filtered_image_np, cv2.COLOR_BGR2HSV).astype(np.float32)
        h, s, v = cv2.split(hsv)
        s = np.where(s > 0, s * saturation, s)
        s = np.clip(s, 0, 255)
        hsv_merged = cv2.merge((h, s, v)).astype(np.uint8)
        filtered_image_np = cv2.cvtColor(hsv_merged, cv2.COLOR_HSV2BGR)

    if blur:
        filtered_image_np = cv2.GaussianBlur(filtered_image_np, (blur, blur), 0)

    if flip_horizontal:
        filtered_image_np = cv2.flip(filtered_image_np, 1)

    if flip_vertical:
        filtered_image_np = cv2.flip(filtered_image_np, 0)

    if text:
        color_bgr = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
        cv2.putText(filtered_image_np, text_input, (position_x, position_y), getattr(cv2, font), font_size / 30, color_bgr, thickness=2)

    if crop:
        if crop_tipe == "por ponto":
            filtered_image_np = filtered_image_np[crop_y1:crop_y2, crop_x1:crop_x2]
        else:
            filtered_image_np = filtered_image_np[crop_y1:crop_y1 + crop_largura, crop_x1:crop_x1 + crop_altura]

    if remove_bg:
        filtered_image_np = remove(filtered_image_np)

    filtered_image = Image.fromarray(filtered_image_np)

    def remove_alpha(img):
        if img.mode in ("RGBA", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            return background
        return img.convert("RGB")

    image_rgb = remove_alpha(image)
    filtered_image_rgb = remove_alpha(filtered_image)

    if view_mode == "🔀 Comparar Lado a Lado":
        col1, col2 = st.columns([1, 1], gap="large")
        with col1:
            st.image(image_rgb, caption="Imagem carregada", use_container_width=True)
        with col2:
            st.image(filtered_image_rgb, caption="Imagem com filtros aplicados", use_container_width=True)

    elif view_mode == "🧮 Comparar com Slider":
        image_comparison(
            img1=image_rgb,
            img2=filtered_image_rgb,
            label1="Original",
            label2="Editada"
        )

    elif view_mode == "📷 Imagem Original":
        st.image(image_rgb, caption="Imagem original", width=700)

    elif view_mode == "🖌️ Imagem Editada":
        st.image(filtered_image_rgb, caption="Imagem editada", width=700)

    format = st.selectbox("Escolha o formato da imagem desejada", options=["PNG", "JPEG", "PDF"], index=0, key="format")
    buffer = io.BytesIO()
    if format == "JPEG" and filtered_image.mode == "RGBA":
        background = Image.new("RGB", filtered_image.size, (255, 255, 255))
        background.paste(filtered_image, mask=filtered_image.split()[3])
        background.save(buffer, format="JPEG")
    else:
        filtered_image.save(buffer, format=format)

    byte_data = buffer.getvalue()

    st.download_button(
        label="Baixar imagem editada",
        data=byte_data,
        file_name=f"imagem_editada.{format.lower()}",
        mime=f"image/{format.lower()}" if format != "PDF" else "application/pdf",
    )
