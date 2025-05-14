import streamlit as st
from PIL import Image
import io
import cv2
import numpy as np
from streamlit_image_comparison import image_comparison
from rembg import remove


def configurar_interface():
    st.set_page_config(page_title="Visualizador de Imagens", page_icon="📷", layout="wide")
    with st.container():
        st.markdown("""
            <h1 style='text-align: center;'>🖼️ Editor de Imagens Interativo</h1>
            <p style='text-align: center; color: gray;'>Aplique filtros, ajuste cores e compare o antes e depois.</p>
        """, unsafe_allow_html=True)


def controles_sidebar():
    st.sidebar.title("⚙️ Ajustes da Imagem")

    resize = st.sidebar.checkbox("🔄 Redimensionar", value=False)
    width = height = None
    if resize:
        width = st.sidebar.number_input("Largura", min_value=1, value=800)
        height = st.sidebar.number_input("Altura", min_value=1, value=600)

    rotate = st.sidebar.checkbox("↻ Rotacionar", value=False)
    rotate_value = st.sidebar.slider("Rotação (graus)", 0, 360, 90, step=1) if rotate else 0

    gray_scale = st.sidebar.checkbox("⚫ Escala de cinza")
    invert_colors = st.sidebar.checkbox("🔁 Inversão de cores")

    sharpen = st.sidebar.checkbox("🧪 Nitidez")
    sharpen_value = st.sidebar.slider("Intensidade da nitidez", 1.0, 2.0, 1.0, step=0.1) if sharpen else None

    edge_detection = st.sidebar.checkbox("📐 Detecção de bordas")
    edge_value = st.sidebar.slider("Intensidade da detecção", 50, 150, 100, step=10) if edge_detection else None

    contrast = st.sidebar.checkbox("🌓 Contraste")
    contrast_value = st.sidebar.slider("Intensidade do contraste", 0.0, 3.0, 1.5, step=0.1) if contrast else None

    brightness = st.sidebar.checkbox("🔆 Brilho")
    brightness_value = st.sidebar.slider("Intensidade do brilho", -100, 100, 0, step=1) if brightness else None

    saturation = st.sidebar.checkbox("🌈 Saturação")
    saturation_value = st.sidebar.slider("Intensidade da saturação", 0.0, 3.0, 1.0, step=0.1) if saturation else None

    blur = st.sidebar.checkbox("💨 Desfoque (Blur)")
    blur_value = st.sidebar.slider("Intensidade do desfoque", 1, 10, 5, step=1) if blur else None

    flip_horizontal = st.sidebar.checkbox("↔️ Espelhar horizontalmente")
    flip_vertical = st.sidebar.checkbox("↕️ Espelhar verticalmente")

    text = st.sidebar.checkbox("🔤 Adicionar texto")
    text_props = {}
    if text:
        text_props = {
            "text_input": st.sidebar.text_input("Texto", value="Texto de exemplo"),
            "font_size": st.sidebar.slider("Tamanho da fonte", 10, 100, 30, step=1),
            "color": st.sidebar.color_picker("Cor do texto", "#000000"),
            "position_x": st.sidebar.number_input("Posição X", min_value=0, value=50),
            "position_y": st.sidebar.number_input("Posição Y", min_value=0, value=50),
            "font": st.sidebar.selectbox("Tipo de fonte", options=[
                "FONT_HERSHEY_SIMPLEX", "FONT_HERSHEY_COMPLEX", "FONT_HERSHEY_DUPLEX",
                "FONT_HERSHEY_TRIPLEX", "FONT_HERSHEY_COMPLEX_SMALL", "FONT_HERSHEY_PLAIN",
                "FONT_HERSHEY_SCRIPT_COMPLEX", "FONT_ITALIC", "QT_FONT_BLACK", "QT_FONT_NORMAL"
            ], index=0)
        }

    crop = st.sidebar.checkbox("✂️ Recortar imagem")
    crop_props = {}
    if crop:
        crop_props = {
            "crop_x1": st.sidebar.number_input("X", min_value=0, value=0),
            "crop_y1": st.sidebar.number_input("Y", min_value=0, value=0),
            "crop_tipe": st.sidebar.selectbox("Tipo de recorte", options=["por tamanho", "por ponto"], index=0)
        }
        if crop_props["crop_tipe"] == "por ponto":
            crop_props["crop_x2"] = st.sidebar.number_input("X2", min_value=0, value=200)
            crop_props["crop_y2"] = st.sidebar.number_input("Y2", min_value=0, value=200)
        else:
            crop_props["crop_altura"] = st.sidebar.number_input("Largura", min_value=0, value=200)
            crop_props["crop_largura"] = st.sidebar.number_input("Altura", min_value=0, value=200)

    remove_bg = st.sidebar.checkbox("🧼 Remover fundo")

    return {
        "resize": resize, "width": width, "height": height,
        "rotate": rotate_value,
        "gray_scale": gray_scale,
        "invert_colors": invert_colors,
        "sharpen": sharpen_value,
        "edge_detection": edge_value,
        "contrast": contrast_value,
        "brightness": brightness_value,
        "saturation": saturation_value,
        "blur": blur_value,
        "flip_horizontal": flip_horizontal,
        "flip_vertical": flip_vertical,
        "text": text, "text_props": text_props,
        "crop": crop, "crop_props": crop_props,
        "remove_bg": remove_bg
    }


def aplicar_filtros(image, ajustes):
    image_np = np.array(image)

    if ajustes["resize"]:
        image_np = cv2.resize(image_np, (ajustes["width"], ajustes["height"]))

    if ajustes["rotate"] != 0:
        center = (image_np.shape[1] // 2, image_np.shape[0] // 2)
        matrix = cv2.getRotationMatrix2D(center, ajustes["rotate"], 1.0)
        image_np = cv2.warpAffine(image_np, matrix, (image_np.shape[1], image_np.shape[0]))

    if ajustes["gray_scale"]:
        image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
        image_np = cv2.cvtColor(image_np, cv2.COLOR_GRAY2BGR)

    if ajustes["invert_colors"]:
        image_np = cv2.bitwise_not(image_np)

    if ajustes["sharpen"]:
        kernel = np.array([[0, -1, 0], [-1, 4 + ajustes["sharpen"], -1], [0, -1, 0]], dtype=np.float32)
        image_np = cv2.filter2D(image_np, -1, kernel)

    if ajustes["edge_detection"]:
        image_np = cv2.Canny(image_np, ajustes["edge_detection"], ajustes["edge_detection"] * 2)
        image_np = cv2.cvtColor(image_np, cv2.COLOR_GRAY2BGR)

    if ajustes["contrast"] is not None or ajustes["brightness"] is not None:
        alpha = ajustes["contrast"] if ajustes["contrast"] is not None else 1
        beta = ajustes["brightness"] if ajustes["brightness"] is not None else 0
        image_np = cv2.convertScaleAbs(image_np, alpha=alpha, beta=beta)

    if ajustes["saturation"]:
        hsv = cv2.cvtColor(image_np, cv2.COLOR_BGR2HSV).astype(np.float32)
        h, s, v = cv2.split(hsv)
        s = np.clip(s * ajustes["saturation"], 0, 255)
        image_np = cv2.cvtColor(cv2.merge((h, s, v)).astype(np.uint8), cv2.COLOR_HSV2BGR)

    if ajustes["blur"]:
        blur_val = ajustes["blur"] * 2 - 1
        image_np = cv2.GaussianBlur(image_np, (blur_val, blur_val), 0)

    if ajustes["flip_horizontal"]:
        image_np = cv2.flip(image_np, 1)

    if ajustes["flip_vertical"]:
        image_np = cv2.flip(image_np, 0)

    if ajustes["text"]:
        props = ajustes["text_props"]
        bgr = tuple(int(props["color"][i:i + 2], 16) for i in (1, 3, 5))
        cv2.putText(image_np, props["text_input"], (props["position_x"], props["position_y"]),
                    getattr(cv2, props["font"]), props["font_size"] / 30, bgr, thickness=2)

    if ajustes["crop"]:
        c = ajustes["crop_props"]
        if c["crop_tipe"] == "por ponto":
            image_np = image_np[c["crop_y1"]:c["crop_y2"], c["crop_x1"]:c["crop_x2"]]
        else:
            image_np = image_np[c["crop_y1"]:c["crop_y1"] + c["crop_largura"], c["crop_x1"]:c["crop_x1"] + c["crop_altura"]]

    if ajustes["remove_bg"]:
        image_np = remove(image_np)

    return Image.fromarray(image_np)


def visualizar_resultado(image, filtered_image):
    view_mode = st.radio("🧭 Escolha como visualizar o resultado:",
                         ["🔀 Comparar Lado a Lado", "🧮 Comparar com Slider", "📷 Imagem Original", "🖌️ Imagem Editada"],
                         horizontal=True)

    def remove_alpha(img):
        if img.mode in ("RGBA", "LA"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[-1])
            return bg
        return img.convert("RGB")

    original = remove_alpha(image)
    editada = remove_alpha(filtered_image)

    if view_mode == "🔀 Comparar Lado a Lado":
        col1, col2 = st.columns(2)
        with col1:
            st.image(original, caption="Imagem carregada", use_container_width=True)
        with col2:
            st.image(editada, caption="Imagem com filtros aplicados", use_container_width=True)
    elif view_mode == "🧮 Comparar com Slider":
        image_comparison(img1=original, img2=editada, label1="Original", label2="Editada")
    elif view_mode == "📷 Imagem Original":
        st.image(original, caption="Imagem original", width=700)
    elif view_mode == "🖌️ Imagem Editada":
        st.image(editada, caption="Imagem editada", width=700)


def botao_download(filtered_image):
    format = st.selectbox("Escolha o formato da imagem desejada", options=["PNG", "JPEG", "PDF"], index=0)
    buffer = io.BytesIO()
    if format == "JPEG" and filtered_image.mode == "RGBA":
        bg = Image.new("RGB", filtered_image.size, (255, 255, 255))
        bg.paste(filtered_image, mask=filtered_image.split()[3])
        bg.save(buffer, format="JPEG")
    else:
        filtered_image.save(buffer, format=format)

    st.download_button(
        label="Baixar imagem editada",
        data=buffer.getvalue(),
        file_name=f"imagem_editada.{format.lower()}",
        mime=f"image/{format.lower()}" if format != "PDF" else "application/pdf",
    )


configurar_interface()
ajustes = controles_sidebar()
uploaded_file = st.file_uploader("📁 Selecione uma imagem", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    filtered_image = aplicar_filtros(image, ajustes)
    visualizar_resultado(image, filtered_image)
    botao_download(filtered_image)
