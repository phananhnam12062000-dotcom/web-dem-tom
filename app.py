import streamlit as st
import requests
import base64
import json

# Ép máy chủ Streamlit xóa bỏ hoàn toàn cache cũ ngay lập tức
st.cache_data.clear()
st.cache_resource.clear()

st.set_page_config(page_title="Hệ Thống Đếm Tôm AI", page_icon="🦐", layout="centered")

st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🦐 Hệ Thống Đếm Tôm Tự Động</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #7f8c8d;'>Tải ảnh khay tôm lên để hệ thống phân tích và trả số lượng tức thì</h3>", unsafe_allow_html=True)

# TỰ ĐỘNG NÂNG CẤP THÔNG MINH: Lấy thông tin bảo mật từ hệ thống Streamlit Secrets
try:
    API_KEY = st.secrets["roboflow"]["api_key"]
    WORKSPACE_NAME = st.secrets["roboflow"]["workspace_name"]
    WORKFLOW_NAME = st.secrets["roboflow"]["workflow_name"]
except Exception:
    st.error("❌ Chưa cấu hình hệ thống Secrets trên Streamlit Cloud! Vui lòng kiểm tra lại phần Settings.")
    st.stop()

uploaded_file = st.file_uploader("Chọn ảnh khay tôm của bạn...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image_bytes = uploaded_file.read()
    st.image(image_bytes, caption="Ảnh khay tôm đã tải lên", use_container_width=True)
    
    with st.spinner("🔄 Hệ thống đang kết nối đám mây và tiến hành đếm tôm..."):
        try:
            # Mã hóa dữ liệu sang chuỗi văn bản Base64 thô không chứa tiêu đề mở rộng
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # CẤU TRÚC ĐƯỜNG DẪN POST WORKFLOW CHUẨN XÁC THEO TÀI LIỆU HÃNG ĐỂ SỬA LỖI 405
            url = f"https://api.roboflow.com/workflows/{WORKSPACE_NAME}/{WORKFLOW_NAME}/outputs?api_key={API_KEY}"
            
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
            
            # Thực hiện lệnh gửi gói tin JSON Payload an toàn
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                # Trích xuất bóc tách mảng lồng dữ liệu tự động
                outputs = result.get("outputs", result) if isinstance(result, dict) else result
                if isinstance(outputs, list) and len(outputs) > 0:
                    outputs = outputs[0]
                
                total_shrimp = None
                output_image_url = None
                
                if isinstance(outputs, dict):
                    if "count_shrimp" in outputs:
                        total_shrimp = outputs["count_shrimp"].get("count") if isinstance(outputs["count_shrimp"], dict) else outputs["count_shrimp"]
                    if "output_image" in outputs:
                        output_image_url = outputs["output_image"].get("value") if isinstance(outputs["output_image"], dict) else outputs["output_image"]
                
                if total_shrimp is not None:
                    st.success(f"🎉 Kết quả đếm thành công! Tìm thấy: {total_shrimp} con tôm.")
                else:
                    st.warning("⚠️ AI đã xử lý xong nhưng không trích xuất được số lượng từ khối đếm 'count_shrimp'.")
                
                if output_image_url:
                    img_response = requests.get(output_image_url)
                    if img_response.status_code == 200:
                        st.image(img_response.content, caption="Ảnh kết quả phân tích bọc khung từ AI", use_container_width=True)
            else:
                st.error(f"❌ Máy chủ AI từ chối xử lý dữ liệu. Mã lỗi HTTP: {response.status_code}")
                st.info("Chi tiết từ hệ thống: " + response.text)
                    
        except Exception as e:
            st.error(f"❌ Gặp sự cố kết nối hệ thống: {str(e)}")
