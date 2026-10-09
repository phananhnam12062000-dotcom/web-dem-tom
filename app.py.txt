import streamlit as st
import requests
import json

# Cấu hình giao diện trang web đếm tôm cao cấp
st.set_page_config(page_title="Hệ Thống Đếm Tôm AI", page_icon="🦐", layout="centered")

st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🦐 Hệ Thống Đếm Tôm Tự Động</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #7f8c8d;'>Tải ảnh khay tôm lên để hệ thống phân tích và trả số lượng tức thì</p>", unsafe_allow_html=True)

# Thông tin cổng kết nối bảo mật từ tài khoản của bạn
WORKFLOW_URL = "https://roboflow.com"
API_KEY = "rneoZ9VjCK1Zli4fX8n7"

# Nút chức năng tải ảnh khay tôm từ điện thoại hoặc máy tính
uploaded_file = st.file_uploader("Chọn ảnh khay tôm của bạn...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Hiển thị ảnh gốc người dùng chọn
    st.image(uploaded_file, caption="Ảnh khay tôm đã tải lên", use_container_width=True)
    
    with st.spinner("🔄 AI đang bẻ khóa bảo mật và tiến hành đếm tôm..."):
        try:
            # Đọc tệp tin nhị phân truyền thẳng dữ liệu thô chống lỗi mã hóa hình ảnh
            file_bytes = uploaded_file.read()
            files = {"image": (uploaded_file.name, file_bytes, uploaded_file.type)}
            headers = {"Authorization": f"Bearer {API_KEY}"}
            
            # Gửi gói tin lên máy chủ trung tâm xử lý dữ liệu
            response = requests.post(WORKFLOW_URL, files=files, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                # THUẬT TOÁN TỰ NÂNG CẤP: Tự quét mọi cấu trúc phản hồi mảng/đối tượng từ Workflow của bạn
                outputs = {}
                if isinstance(result, list) and len(result) > 0:
                    outputs = result[0].get("outputs", result[0])
                elif isinstance(result, dict):
                    outputs = result.get("outputs", result)
                
                # Trích xuất dữ liệu từ các khối (Block) bạn đã đặt tên trên sơ đồ
                total_shrimp = outputs.get("count_shrimp", {}).get("count") if isinstance(outputs.get("count_shrimp"), dict) else outputs.get("count_shrimp")
                output_image_url = outputs.get("output_image", {}).get("value") if isinstance(outputs.get("output_image"), dict) else outputs.get("output_image")
                
                # Hiển thị thông số đếm trực quan ra màn hình web
                if total_shrimp is not None:
                    st.success(f"🎉 Kết quả đếm thành công! Tìm thấy: {total_shrimp} con tôm.")
                else:
                    st.warning("⚠️ AI đã xử lý xong nhưng không bóc tách được số lượng từ khối chức năng.")
                
                # Tải ảnh kết quả đã bọc khung màu từ máy chủ về hiển thị
                if output_image_url:
                    img_response = requests.get(output_image_url)
                    if img_response.status_code == 200:
                        st.image(img_response.content, caption="Ảnh kết quả phân tích từ AI", use_container_width=True)
            else:
                st.error(f"❌ Máy chủ AI từ chối xử lý dữ liệu. Mã lỗi: {response.status_code}")
                st.info(response.text)
                
        except Exception as e:
            st.error(f"⚠️ Gặp sự cố kết nối đường truyền: {str(e)}")
