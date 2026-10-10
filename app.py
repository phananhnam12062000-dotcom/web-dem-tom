import streamlit as st
import base64
import json
from PIL import Image
from io import BytesIO
from inference_sdk import InferenceHTTPClient, InferenceConfiguration

# 1. CẤU HÌNH GIAO DIỆN CHUẨN TEMPLATE ROBOFLOW COOKBOOKS
st.set_page_config(
    page_title="Roboflow Object Detection Playground",
    page_icon="🦐",
    layout="wide" # Sử dụng giao diện hai cột (Cột ảnh gốc và Cột kết quả AI)
)

st.title("🦐 Máy Đếm Tôm Tự Động - Roboflow Playground")
st.write("Mẫu thiết kế chuẩn hóa từ thư viện mã nguồn mở Roboflow Utilities")

# Cấu hình cứng bộ mã khóa xác thực của riêng bạn để bảo mật hệ thống Backend
API_KEY = "rneoZ9VjCK1Zli4fX8n7"
WORKSPACE_NAME = "anh-phan-s-workspace-wf9sf"
WORKFLOW_NAME = "djem-tom-khong-hien-nhan-1791524778629"

# 2. XÂY DỰNG SIDEBAR (THANH ĐIỀU KHIỂN BÊN TRÁI)
st.sidebar.header("Cấu Hình Bộ Lọc AI")
# Thanh trượt cho phép người dùng tự chỉnh độ nhạy phân tích trực tiếp trên Web
confidence_threshold = st.sidebar.slider(
    "Độ tự tin tối thiểu (Confidence)", 
    min_value=0.0, max_value=1.0, value=0.4, step=0.05
)

# 3. CHUẨN BỊ VÙNG CHỨA DỮ LIỆU GIAO DIỆN
input_column, output_column = st.columns(2)

with input_column:
    st.header("Khay Ảnh Đầu Vào")
    uploaded_file = st.file_uploader("Tải lên hoặc chụp ảnh khay tôm của bạn", type=["png", "jpeg", "jpg"])
    
    if uploaded_file:
        image_bytes = uploaded_file.read()
        st.image(image_bytes, caption="Ảnh khay tôm gốc", use_container_width=True)

# 4. TIẾN HÀNH XỬ LÝ INFERENCE QUA CỔNG SERVERLESS WORKFLOW
if uploaded_file:
    with output_column:
        st.header("Kết Quả Phân Tích")
        
        with st.spinner("🔄 Thư viện SDK đang gửi dữ liệu an toàn lên máy chủ AI..."):
            try:
                # Mã hóa dữ liệu tệp hình ảnh
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
                
                # Khởi tạo Inference HTTP Client theo đúng tài liệu chính hãng
                client = InferenceHTTPClient(
                    api_url="https://serverless.roboflow.com",
                    api_key=API_KEY
                ).configure(InferenceConfiguration(api_key_transport="header"))
                
                # Đóng gói biến đầu vào bao gồm cả thanh trượt cấu hình
                payload = {
                    "image": base64_image,
                    "confidence": confidence_threshold
                }
                
                # Gọi lệnh thực thi quy trình từ SDK
                result = client.run_workflow(
                    workspace_name=WORKSPACE_NAME,
                    workflow_id=WORKFLOW_NAME,
                    images=payload
                )
                
                if result:
                    outputs = result.get("outputs", result)
                    if isinstance(outputs, list) and len(outputs) > 0:
                        outputs = outputs
                    
                    total_shrimp = None
                    output_image_base64 = None
                    
                    # Bộ bóc tách cây thư mục JSON tự động từ Roboflow Workflow
                    if isinstance(outputs, dict):
                        for key, val in outputs.items():
                            if any(x in key.lower() for x in ["count", "detect", "tom", "shrimp"]):
                                if isinstance(val, dict):
                                    if "count" in val:
                                        total_shrimp = val["count"]
                                    elif "predictions" in val and isinstance(val["predictions"], list):
                                        total_shrimp = len(val["predictions"])
                                elif isinstance(val, (int, float)):
                                    total_shrimp = int(val)
                        
                        for key, val in outputs.items():
                            if any(x in key.lower() for x in ["image", "render", "visual"]):
                                if isinstance(val, dict) and "value" in val:
                                    output_image_base64 = val["value"]
                                elif isinstance(val, str) and (val.startswith("/9j/") or "base64" in val):
                                    output_image_base64 = val

                    # Hiển thị số lượng đếm được lên màn hình bằng Success Banner
                    if total_shrimp is not None:
                        st.success(f"🎉 Kết quả đếm thành công! Tìm thấy: {total_shrimp} con tôm.")
                    else:
                        st.warning("⚠️ AI đã xử lý thành công nhưng không tìm thấy trường số lượng 'count'.")

                    # Dựng hình ảnh đã vẽ khung màu đa sắc trả về giao diện
                    if output_image_base64:
                        if "," in output_image_base64:
                            output_image_base64 = output_image_base64.split(",")[-1]
                        decoded_img = base64.b64decode(output_image_base64)
                        st.image(decoded_img, caption="Ảnh kết quả vẽ khung bọc màu từ AI", use_container_width=True)
                else:
                    st.error("❌ Máy chủ đám mây trả về dữ liệu rỗng.")
            except Exception as e:
                st.error(f"❌ Sự cố kết nối: {str(e)}")
