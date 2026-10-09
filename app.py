import streamlit as st
import requests
import base64
import json

# LỆNH TỐI CAO: Ép buộc máy chủ Streamlit xóa bỏ hoàn toàn bộ nhớ đệm cũ ngay lập tức
st.cache_data.clear()
st.cache_resource.clear()

st.set_page_config(page_title="Hệ Thống Đếm Tôm AI", page_icon="🦐", layout="centered")

st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🦐 Hệ Thống Đếm Tôm Tự Động</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #7f8c8d;'>Tải ảnh khay tôm lên để hệ thống phân tích và trả số lượng tức thì</h3>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Chọn ảnh khay tôm của bạn...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image_bytes = uploaded_file.read()
    st.image(image_bytes, caption="Ảnh khay tôm đã tải lên", use_container_width=True)
    
    with st.spinner("🔄 Hệ thống đang kết nối trực tiếp đám mây và tiến hành đếm tôm..."):
        try:
            # Mã hóa ảnh sang chuỗi văn bản Base64 chuẩn
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # ĐÃ ĐỔI THÀNH ĐƯỜNG LINK TĨNH VIẾT TAY 100% - TUYỆT ĐỐI KHÔNG GHÉP CHUỖI, KHÔNG THỂ SAI TÊN MIỀN
            url_vinh_vien = "https://roboflow.com"
            
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
            
            # Gửi yêu cầu dữ liệu
            response = requests.post(url_vinh_vien, data=json.dumps(payload), headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                # Tự động bóc tách mảng lồng dữ liệu từ quy trình Workflow
                outputs = result.get("outputs", result)
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
                    st.warning("⚠️ AI đã xử lý xong nhưng không tìm thấy dữ liệu từ khối đếm 'count_shrimp'.")
                
                if output_image_url:
                    img_response = requests.get(output_image_url)
                    if img_response.status_code == 200:
                        st.image(img_response.content, caption="Ảnh kết quả phân tích bọc khung từ AI", use_container_width=True)
            else:
                st.error(f"❌ Máy chủ AI từ chối xử lý dữ liệu. Mã lỗi HTTP: {response.status_code}")
                st.info("Chi tiết: " + response.text)
                    
        except Exception as e:
            st.error(f"❌ Gặp sự cố kết nối hệ thống: {str(e)}")
