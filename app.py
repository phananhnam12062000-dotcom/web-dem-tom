import streamlit as st
from inference_sdk import InferenceHTTPClient
import requests
import base64

# Cấu hình giao diện trang web đếm tôm cao cấp, tự động co giãn theo màn hình điện thoại
st.set_page_config(page_title="Hệ Thống Đếm Tôm AI", page_icon="🦐", layout="centered")

st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🦐 Hệ Thống Đếm Tôm Tự Động</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #7f8c8d;'>Tải ảnh khay tôm lên để hệ thống phân tích và trả số lượng tức thì</h3>", unsafe_allow_html=True)

# THÔNG TIN KHÓA BẢO MẬT VÀ WORKFLOW CHUẨN XÁC CỦA BẠN
API_KEY = "rneoZ9VjCK1Zli4fX8n7"
WORKFLOW_NAME = "djem-tom-khong-hien-nhan-1791524778629"
WORKSPACE_NAME = "anh-phan-s-workspace-wf9sf"

# ĐÃ SỬA DỨT ĐIỂM LỖI 405: Khởi tạo Client kết nối chính thống qua SDK đám mây của Roboflow
@st.cache_resource
def get_inference_client():
    return InferenceHTTPClient(
        api_url="https://roboflow.com", 
        api_key=API_KEY
    )

client = get_inference_client()

# Nút chức năng tải ảnh khay tôm lên hệ thống
uploaded_file = st.file_uploader("Chọn ảnh khay tôm của bạn...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Đọc ảnh thô trực tiếp từ giao diện người dùng
    image_bytes = uploaded_file.read()
    
    # Hiển thị ảnh gốc người dùng chọn lên màn hình web
    st.image(image_bytes, caption="Ảnh khay tôm đã tải lên", use_container_width=True)
    
    with st.spinner("🔄 Hệ thống đang kết nối SDK và tiến hành đếm tôm..."):
        try:
            # ĐÃ SỬA LỖI BYTES: Mã hóa dữ liệu nhị phân thành chuỗi văn bản Base64 thô chuẩn JSON
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # ĐÃ SỬA TOÀN BỘ THAM SỐ CHUẨN: Sử dụng đúng các tên tham số mới nhất của SDK
            result = client.infer_from_workflow(
                workspace_name=WORKSPACE_NAME,
                workflow_name=WORKFLOW_NAME,
                parameters={"image": base64_image} # Truyền ảnh chuỗi base64 đã sửa lỗi
            )
            
            # Bộ lọc thông minh tự động quét cấu trúc phản hồi từ Workflow (Mảng hoặc Đối tượng)
            outputs = {}
            if isinstance(result, list) and len(result) > 0:
                outputs = result.get("outputs", result) if isinstance(result, dict) else result
            elif isinstance(result, dict):
                if "outputs" in result:
                    outputs = result["outputs"]
                    if isinstance(outputs, list) and len(outputs) > 0:
                        outputs = outputs
                else:
                    outputs = result
            
            # Trích xuất dữ liệu từ các khối (Block) bạn đã đặt tên trên sơ đồ khối Roboflow
            total_shrimp = None
            output_image_url = None
            
            if isinstance(outputs, dict):
                total_shrimp = outputs.get("count_shrimp", {}).get("count") if isinstance(outputs.get("count_shrimp"), dict) else outputs.get("count_shrimp")
                output_image_url = outputs.get("output_image", {}).get("value") if isinstance(outputs.get("output_image"), dict) else outputs.get("output_image")
            
            # Hiển thị thông số kết quả đếm trực quan ra màn hình web của bạn
            if total_shrimp is not None:
                st.success(f"🎉 Kết quả đếm thành công! Tìm thấy: {total_shrimp} con tôm.")
            else:
                st.warning("⚠️ AI đã xử lý xong nhưng không tìm thấy dữ liệu từ khối đếm 'count_shrimp'.")
            
            # Tải ảnh kết quả đã bọc khung màu từ đám mây về hiển thị
            if output_image_url:
                img_response = requests.get(output_image_url)
                if img_response.status_code == 200:
                    st.image(img_response.content, caption="Ảnh kết quả phân tích bọc khung từ AI", use_container_width=True)
                    
        except Exception as e:
            st.error(f"❌ Gặp sự cố xử lý hệ thống AI: {str(e)}")
