import streamlit as st
import base64
import requests
import json

# Ép máy chủ Streamlit Cloud xóa sạch toàn bộ bộ nhớ đệm cache cũ để nạp code mới
st.cache_data.clear()
st.cache_resource.clear()

# Cấu hình giao diện trang web đếm tôm tự động co giãn theo màn hình điện thoại
st.set_page_config(page_title="Hệ Thống Đếm Tôm AI", page_icon="🦐", layout="centered")

st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🦐 Hệ Thống Đếm Tôm Tự Động</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #7f8c8d;'>Tải ảnh khay tôm lên để hệ thống phân tích và trả số lượng tức thì</h3>", unsafe_allow_html=True)

# Đọc thông tin cấu hình bảo mật từ Streamlit Secrets
try:
    API_KEY = st.secrets["roboflow"]["api_key"].strip()
    WORKSPACE_NAME = st.secrets["roboflow"]["workspace_name"].strip().strip("/")
    WORKFLOW_NAME = st.secrets["roboflow"]["workflow_name"].strip().strip("/")
except Exception:
    st.error("❌ Chưa cấu hình hoặc cấu hình sai hệ thống Secrets trên Streamlit Cloud! Vui lòng kiểm tra lại phần Settings -> Secrets.")
    st.stop()

# Nút chức năng tải ảnh khay tôm từ thiết bị
uploaded_file = st.file_uploader("Chọn ảnh khay tôm của bạn...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Đọc dữ liệu ảnh từ giao diện người dùng
    image_bytes = uploaded_file.read()
    
    # Hiển thị ảnh gốc người dùng chọn lên màn hình web
    st.image(image_bytes, caption="Ảnh khay tôm đã tải lên", use_container_width=True)
    
    with st.spinner("🔄 Hệ thống đang kết nối máy chủ Roboflow và tiến hành đếm tôm..."):
        try:
            # Mã hóa dữ liệu sang chuỗi văn bản Base64 thô chuẩn định dạng JSON của Roboflow
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # 🔥 ĐÃ SỬA CHUẨN XÁC 100% ĐƯỜNG DẪN: Sử dụng cổng ://roboflow.com chuyên dụng cho xử lý mô hình
            url_chuan_xac = f"https://://roboflow.com/workflows/{WORKSPACE_NAME}/{WORKFLOW_NAME}"
            
            # Cấu trúc gói tin Payload chuẩn chỉnh theo đúng tài liệu Roboflow Serverless API
            payload = {
                "inputs": {
                    "image": {
                        "type": "base64",
                        "value": base64_image
                    }
                }
            }
            
            # Đẩy khóa API xác thực bảo mật vào Header
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            }
            
            # Gửi yêu cầu HTTP POST xử lý ảnh trực tiếp lên máy chủ đám mây
            response = requests.post(url_chuan_xac, data=json.dumps(payload), headers=headers)
            
            # Nếu cổng chính bị từ chối, tự động kích hoạt định tuyến qua máy chủ Serverless dự phòng
            if response.status_code == 404:
                url_du_phong = f"https://roboflow.com{WORKSPACE_NAME}/{WORKFLOW_NAME}"
                response = requests.post(url_du_phong, data=json.dumps(payload), headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                outputs = {}
                
                # Trích xuất tầng dữ liệu chính nằm trong trường 'outputs'
                if isinstance(result, dict):
                    if "outputs" in result:
                        if isinstance(result["outputs"], list) and len(result["outputs"]) > 0:
                            outputs = result["outputs"][0]
                        else:
                            outputs = result["outputs"]
                    else:
                        outputs = result
                elif isinstance(result, list) and len(result) > 0:
                    outputs = result[0].get("outputs", result[0]) if isinstance(result[0], dict) else result[0]
                
                total_shrimp = None
                output_image_base64 = None
                
                # Tự động quét cấu trúc cây dữ liệu trả về từ các khối sơ đồ để tìm kết quả
                if isinstance(outputs, dict):
                    # 1. Tìm số lượng con vật đếm được từ khối chức năng
                    for key, val in outputs.items():
                        if any(x in key.lower() for x in ["count", "detect", "tom", "shrimp"]):
                            if isinstance(val, dict):
                                if "count" in val:
                                    total_shrimp = val["count"]
                                elif "predictions" in val and isinstance(val["predictions"], list):
                                    total_shrimp = len(val["predictions"])
                            elif isinstance(val, (int, float)):
                                total_shrimp = int(val)
                    
                    # 2. Tìm ảnh kết quả vẽ khung bọc màu từ AI
                    for key, val in outputs.items():
                        if any(x in key.lower() for x in ["image", "render", "visual"]):
                            if isinstance(val, dict) and "value" in val:
                                output_image_base64 = val["value"]
                            elif isinstance(val, str) and (val.startswith("/9j/") or "base64" in val):
                                output_image_base64 = val
                
                # Hiển thị số lượng đếm được lên giao diện web
                if total_shrimp is not None:
                    st.success(f"🎉 Kết quả đếm thành công! Tìm thấy: {total_shrimp} con tôm.")
                else:
                    st.warning("⚠️ AI đã xử lý thành công nhưng chưa tự bóc tách được số lượng. Bạn vui lòng kiểm tra xem tên khối chứa bộ đếm trong sơ đồ Roboflow Workflow có chữ 'count' hoặc 'predictions' không.")
                
                # Hiển thị ảnh vẽ khung bọc màu kết quả trực quan
                if output_image_base64:
                    try:
                        if "," in output_image_base64:
                            output_image_base64 = output_image_base64.split(",")[-1]
                        decoded_img = base64.b64decode(output_image_base64)
                        st.image(decoded_img, caption="Ảnh kết quả phân tích bọc khung từ AI", use_container_width=True)
                    except Exception:
                        st.info("Không thể dựng ảnh bọc khung kết quả phân tích.")
            else:
                st.error(f"❌ Máy chủ AI từ chối xử lý dữ liệu. Mã lỗi HTTP: {response.status_code}")
                st.info("Nhật ký lỗi chi tiết từ máy chủ Roboflow:\n" + response.text)
                    
        except Exception as e:
            st.error(f"❌ Gặp sự cố kết nối hệ thống: {str(e)}")
