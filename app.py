import streamlit as st
import requests
import base64
import json

# Ép hệ thống xóa sạch mọi bộ nhớ đệm cache cũ để nạp tài nguyên mới
st.cache_data.clear()
st.cache_resource.clear()

# Cấu hình giao diện ứng dụng co giãn thông minh, tương thích tuyệt đối giao diện điện thoại
st.set_page_config(page_title="Hệ Thống Đếm Tôm AI", page_icon="🦐", layout="centered")

st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🦐 Hệ Thống Đếm Tôm Tự Động</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #7f8c8d;'>Chụp ảnh hoặc tải ảnh khay tôm lên để AI phân tích số lượng tức thì</h3>", unsafe_allow_html=True)

# Khai báo thông số tài khoản và sơ đồ khối Roboflow Workflow của riêng bạn
API_KEY = "rneoZ9VjCK1Zli4fX8n7"
WORKSPACE_NAME = "anh-phan-s-workspace-wf9sf"
WORKFLOW_NAME = "djem-tom-khong-hien-nhan-1791524778629"

# Nút chức năng tải ảnh khay tôm từ thiết bị
uploaded_file = st.file_uploader("Chọn ảnh khay tôm của bạn...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Đọc và hiển thị hình ảnh gốc của người dùng lên giao diện trang web
    image_bytes = uploaded_file.read()
    st.image(image_bytes, caption="Ảnh khay tôm đã tải lên", use_container_width=True)
    
    with st.spinner("🔄 Hệ thống đang gửi dữ liệu an toàn lên đám mây và tiến hành đếm tôm..."):
        try:
            # Mã hóa dữ liệu hình ảnh sang chuỗi văn bản Base64 thô sạch tinh khiết
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # 🔥 ĐỊA CHỈ API CỔNG MỞ CHUẨN XÁC TUYỆT ĐỐI: Gửi request trực tiếp không qua thư viện SDK
            url = f"https://roboflow.com{WORKSPACE_NAME}/{WORKFLOW_NAME}?api_key={API_KEY}"
            
            # Đóng gói dữ liệu tin đầu vào chuẩn cấu trúc sơ đồ khối Workflow
            payload = {
                "inputs": {
                    "image": {
                        "type": "base64",
                        "value": base64_image
                    }
                }
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            # Gửi yêu cầu dữ liệu mạng HTTP POST từ máy chủ lên hệ thống đám mây Roboflow
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                # Trích xuất tầng dữ liệu chính nằm trong trường 'outputs'
                outputs = result.get("outputs", result)
                if isinstance(outputs, list) and len(outputs) > 0:
                    outputs = outputs[0]
                
                total_shrimp = None
                output_image_base64 = None
                
                if isinstance(outputs, dict):
                    # 1. Tự động bóc tách số lượng đếm tôm từ khối chức năng trên sơ đồ của bạn
                    for key, val in outputs.items():
                        if any(x in key.lower() for x in ["count", "detect", "tom", "shrimp"]):
                            if isinstance(val, dict):
                                if "count" in val:
                                    total_shrimp = val["count"]
                                elif "predictions" in val and isinstance(val["predictions"], list):
                                    total_shrimp = len(val["predictions"])
                            elif isinstance(val, (int, float)):
                                total_shrimp = int(val)
                    
                    # 2. Tự động tìm chuỗi ảnh kết quả bọc khung màu đa sắc từ AI
                    for key, val in outputs.items():
                        if any(x in key.lower() for x in ["image", "render", "visual"]):
                            if isinstance(val, dict) and "value" in val:
                                output_image_base64 = val["value"]
                            elif isinstance(val, str) and (val.startswith("/9j/") or "base64" in val):
                                output_image_base64 = val
                
                # Xuất kết quả hiển thị thông tin số lượng ra màn hình web của bạn
                if total_shrimp is not None:
                    st.success(f"🎉 Kết quả đếm thành công! Tìm thấy: {total_shrimp} con tôm.")
                else:
                    st.warning("⚠️ AI đã xử lý xong nhưng không tìm thấy khối dữ liệu đếm tên là count hoặc predictions.")
                
                # Giải mã chuỗi văn bản ngược về dạng hình ảnh bọc khung kết quả để hiển thị trực quan
                if output_image_base64:
                    try:
                        if "," in output_image_base64:
                            output_image_base64 = output_image_base64.split(",")[-1]
                        decoded_img = base64.b64decode(output_image_base64)
                        st.image(decoded_img, caption="Ảnh kết quả phân tích bọc khung từ AI", use_container_width=True)
                    except Exception:
                        st.info("Không thể hiển thị ảnh bọc khung màu kết quả.")
            else:
                st.error(f"❌ Máy chủ AI từ chối xử lý dữ liệu. Mã lỗi: {response.status_code}")
                st.info("Chi tiết nhật ký phản hồi: " + response.text)
                    
        except Exception as e:
            st.error(f"❌ Gặp sự cố mạng kết nối hệ thống: {str(e)}")
