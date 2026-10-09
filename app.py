import streamlit as st
import requests
import base64
import json

# Cấu hình giao diện trang web đếm tôm cao cấp, tự động co giãn theo màn hình điện thoại
st.set_page_config(page_title="Hệ Thống Đếm Tôm AI", page_icon="🦐", layout="centered")

st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🦐 Hệ Thống Đếm Tôm Tự Động</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #7f8c8d;'>Tải ảnh khay tôm lên để hệ thống phân tích và trả số lượng tức thì</h3>", unsafe_allow_html=True)

# THÔNG TIN KHÓA BẢO MẬT TÀI KHOẢN CỦA BẠN
API_KEY = "rneoZ9VjCK1Zli4fX8n7"
WORKFLOW_NAME = "djem-tom-khong-hien-nhan-1791524778629"
WORKSPACE_NAME = "anh-phan-s-workspace-wf9sf"

# Nút chức năng tải ảnh khay tôm lên hệ thống
uploaded_file = st.file_uploader("Chọn ảnh khay tôm của bạn...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Đọc ảnh thô trực tiếp
    image_bytes = uploaded_file.read()
    
    # Hiển thị ảnh gốc người dùng chọn lên màn hình web
    st.image(image_bytes, caption="Ảnh khay tôm đã tải lên", use_container_width=True)
    
    with st.spinner("🔄 Hệ thống đang kết nối trực tiếp đám mây và tiến hành đếm tôm..."):
        try:
            # Mã hóa dữ liệu sang chuỗi văn bản Base64 thô chuẩn JSON
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # CẤU HÌNH ĐƯỜNG DẪN URL API NGUYÊN BẢN CHUẨN ĐÃ ĐƯỢC FIX LỖI 404
            url = f"https://roboflow.com{WORKSPACE_NAME}/workflows/{WORKFLOW_NAME}/outputs"
            
            # Đóng gói dữ liệu JSON đầu vào đúng định dạng cổng Serverless Workflows
            payload = {
                "inputs": {
                    "image": {
                        "type": "base64",
                        "value": base64_image
                    }
                }
            }
            
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Gửi yêu cầu HTTP POST trực tiếp không qua thư viện SDK trung gian
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                # Bộ lọc thông minh bóc tách dữ liệu JSON lồng nhau
                outputs = {}
                if isinstance(result, list) and len(result) > 0:
                    outputs = result[0].get("outputs", result[0]) if isinstance(result[0], dict) else result[0]
                elif isinstance(result, dict):
                    outputs = result.get("outputs", result)
                
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
            else:
                st.error(f"❌ Máy chủ AI từ chối xử lý dữ liệu. Mã lỗi: {response.status_code}")
                st.info("Hãy kiểm tra lại xem Workflow của bạn trên Roboflow đã được kích hoạt chạy ổn định chưa.")
                    
        except Exception as e:
            st.error(f"❌ Gặp sự cố kết nối hệ thống: {str(e)}")
