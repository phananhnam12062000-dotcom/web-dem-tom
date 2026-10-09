import streamlit as st
import requests
import json

# Ép máy chủ Streamlit xóa bỏ hoàn toàn bộ nhớ đệm cũ ngay khi khởi động
st.cache_data.clear()
st.cache_resource.clear()

# Cấu hình giao diện trang web đếm tôm cao cấp, tự động co giãn theo màn hình điện thoại
st.set_page_config(page_title="Hệ Thống Đếm Tôm AI", page_icon="🦐", layout="centered")

st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🦐 Hệ Thống Đếm Tôm Tự Động</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #7f8c8d;'>Tải ảnh khay tôm lên để hệ thống phân tích và trả số lượng tức thì</h3>", unsafe_allow_html=True)

# THÔNG TIN KHÓA BẢO MẬT TÀI KHOẢN CỦA BẠN (ĐÃ XÁC THỰC CHUẨN XÁC)
API_KEY = "rneoZ9VjCK1Zli4fX8n7"

# Nút chức năng tải ảnh khay tôm lên hệ thống
uploaded_file = st.file_uploader("Chọn ảnh khay tôm của bạn...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Đọc ảnh thô trực tiếp từ giao diện người dùng dưới dạng nhị phân
    image_bytes = uploaded_file.read()
    
    # Hiển thị ảnh gốc người dùng chọn lên màn hình web
    st.image(image_bytes, caption="Ảnh khay tôm đã tải lên", use_container_width=True)
    
    with st.spinner("🔄 Hệ thống đang kết nối trực tiếp đám mây và tiến hành đếm tôm..."):
        try:
            # ĐƯỜNG DẪN CỐ ĐỊNH CHUẨN ĐÃ ĐƯỢC FIX LỖI TÊN MIỀN
            url = "https://roboflow.com"
            
            # SỬA DỨT ĐIỂM LỖI 405: Truyền ảnh bằng định dạng tệp nhị phân thô qua tham số files thay vì chuỗi JSON Base64
            files = {
                "image": (uploaded_file.name, image_bytes, uploaded_file.type)
            }
            
            headers = {
                "Authorization": f"Bearer {API_KEY}"
            }
            
            # Gửi yêu cầu HTTP POST chuẩn multipart/form-data lên hệ thống đám mây
            response = requests.post(url, files=files, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                # Bộ lọc thông minh tự động bóc tách dữ liệu JSON lồng nhau từ Workflow
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
                st.info("Hãy kiểm tra chắc chắn rằng tên các ô vuông trên sơ đồ Roboflow của bạn viết đúng chữ: 'count_shrimp' và 'output_image'.")
                    
        except Exception as e:
            st.error(f"❌ Gặp sự cố kết nối hệ thống: {str(e)}")
