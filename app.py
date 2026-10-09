import streamlit as st
import requests
import base64
import json

# Ép máy chủ Streamlit xóa bỏ hoàn toàn bộ nhớ đệm cũ ngay khi khởi động để nạp code mới
st.cache_data.clear()
st.cache_resource.clear()

# Cấu hình giao diện trang web đếm tôm cao cấp, tự động co giãn theo màn hình điện thoại
st.set_page_config(page_title="Hệ Thống Đếm Tôm AI", page_icon="🦐", layout="centered")

st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🦐 Hệ Thống Đếm Tôm Tự Động</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #7f8c8d;'>Tải ảnh khay tôm lên để hệ thống phân tích và trả số lượng tức thì</h3>", unsafe_allow_html=True)

# THÔNG TIN KHÓA BẢO MẬT TÀI KHOẢN CỦA BẠN (ĐÃ XÁC THỰC CHUẨN XÁC)
API_KEY = "rneoZ9VjCK1Zli4fX8n7"

# Nút chức năng tải ảnh khay tôm từ thiết bị
uploaded_file = st.file_uploader("Chọn ảnh khay tôm của bạn...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Đọc dữ liệu ảnh từ giao diện người dùng
    image_bytes = uploaded_file.read()
    
    # Hiển thị ảnh gốc người dùng chọn lên màn hình web
    st.image(image_bytes, caption="Ảnh khay tôm đã tải lên", use_container_width=True)
    
    with st.spinner("🔄 Hệ thống đang kết nối trực tiếp đám mây và tiến hành đếm tôm..."):
        try:
            # Mã hóa dữ liệu sang chuỗi văn bản Base64 thô không chứa ký tự xuống dòng
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # SỬA LỖI 404 & 405: Sử dụng cổng API Workflow chuẩn của Roboflow
            url = f"https://roboflow.com{API_KEY}"
            
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
                "Content-Type": "application/json"
            }
            
            # Gửi yêu cầu HTTP POST trực tiếp lên hệ thống đám mây
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                # Bộ lọc thông minh tự động bóc tách dữ liệu JSON lồng nhau từ Workflow
                outputs = {}
                if isinstance(result, list) and len(result) > 0:
                    outputs = result[0].get("outputs", result[0]) if isinstance(result[0], dict) else result[0]
                elif isinstance(result, dict):
                    if "outputs" in result:
                        outputs = result["outputs"]
                        if isinstance(outputs, list) and len(outputs) > 0:
                            outputs = outputs[0]
                    else:
                        outputs = result
                
                # Khởi tạo giá trị mặc định để tránh lỗi đứng giao diện
                total_shrimp = None
                output_image_url = None
                
                # Trích xuất dữ liệu từ khối 'count_shrimp' và 'output_image' trên sơ đồ của bạn
                if isinstance(outputs, dict):
                    # Quét tìm kết quả đếm tôm từ khối chức năng
                    if "count_shrimp" in outputs:
                        shrimp_data = outputs["count_shrimp"]
                        total_shrimp = shrimp_data.get("count") if isinstance(shrimp_data, dict) else shrimp_data
                    
                    # Quét tìm liên kết hình ảnh bọc khung kết quả
                    if "output_image" in outputs:
                        image_data = outputs["output_image"]
                        output_image_url = image_data.get("value") if isinstance(image_data, dict) else image_data
                
                # Hiển thị thông số kết quả đếm trực quan ra màn hình web
                if total_shrimp is not None:
                    st.success(f"🎉 Kết quả đếm thành công! Tìm thấy: {total_shrimp} con tôm.")
                else:
                    st.warning("⚠️ AI đã xử lý xong nhưng không trích xuất được số lượng từ khối đếm 'count_shrimp'.")
                
                # Tải ảnh kết quả đã bọc khung từ máy chủ về hiển thị
                if output_image_url:
                    img_response = requests.get(output_image_url)
                    if img_response.status_code == 200:
                        st.image(img_response.content, caption="Ảnh kết quả phân tích bọc khung từ AI", use_container_width=True)
            else:
                st.error(f"❌ Máy chủ AI từ chối xử lý dữ liệu. Mã lỗi HTTP: {response.status_code}")
                st.info("Nhật ký hệ thống: " + response.text)
                    
        except Exception as e:
            st.error(f"❌ Gặp sự cố kết nối hệ thống: {str(e)}")
