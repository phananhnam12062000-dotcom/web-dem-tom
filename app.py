import streamlit as st
import requests
import json

# Khởi động lệnh ép máy chủ Streamlit Cloud xóa bỏ hoàn toàn mọi bộ nhớ đệm cũ để cập nhật ngay
st.cache_data.clear()
st.cache_resource.clear()

# Cấu hình giao diện trang web đếm tôm cao cấp, tự động co giãn theo màn hình điện thoại
st.set_page_config(page_title="Hệ Thống Đếm Tôm AI", page_icon="🦐", layout="centered")

st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🦐 Hệ Thống Đếm Tôm Tự Động</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #7f8c8d;'>Tải ảnh khay tôm lên để hệ thống phân tích và trả số lượng tức thì</h3>", unsafe_allow_html=True)

# Nút chức năng tải ảnh khay tôm từ thiết bị
uploaded_file = st.file_uploader("Chọn ảnh khay tôm của bạn...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Đọc dữ liệu ảnh từ giao diện người dùng dưới dạng nhị phân thô (Binary)
    image_bytes = uploaded_file.read()
    
    # Hiển thị ảnh gốc người dùng chọn lên màn hình web
    st.image(image_bytes, caption="Ảnh khay tôm đã tải lên", use_container_width=True)
    
    with st.spinner("🔄 Hệ thống đang đồng bộ sơ đồ khối và tiến hành đếm tôm..."):
        try:
            # ĐÃ ĐỔI THÀNH ĐƯỜNG DẪN CỔNG SERVERLESS WORKFLOWS CHUẨN XÁC VÀ CỐ ĐỊNH CỦA ROBOFLOW
            url_chuan_vinh_vien = "https://roboflow.com"
            
            # SỬA DỨT ĐIỂM LỖI 405: Truyền tệp nhị phân thô trực tiếp qua tham số files, loại bỏ hoàn toàn Base64 JSON
            files = {
                "image": (uploaded_file.name, image_bytes, uploaded_file.type)
            }
            
            # Đặt mã khóa bảo mật Authorization Bearer trên Header theo đúng quy chuẩn cổng Serverless Gateway
            headers = {
                "Authorization": "Bearer rneoZ9VjCK1Zli4fX8n7"
            }
            
            # Gửi yêu cầu HTTP POST nguyên bản dạng tệp tin lên hệ thống đám mây
            response = requests.post(url_chuan_vinh_vien, files=files, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                # Bộ lọc thông minh tự động bóc tách dữ liệu JSON lồng nhau từ Workflow (Mảng hoặc Đối tượng)
                outputs = {}
                if isinstance(result, list) and len(result) > 0:
                    outputs = result[0].get("outputs", result[0]) if isinstance(result[0], dict) else result[0]
                elif isinstance(result, dict):
                    outputs = result.get("outputs", result)
                
                # Khởi tạo giá trị mặc định ban đầu để tránh lỗi đứng giao diện web
                total_shrimp = None
                output_image_url = None
                
                # Trích xuất dữ liệu từ các khối (Block) dựa trên tên bạn đặt trong sơ đồ khối Roboflow
                if isinstance(outputs, dict):
                    # Quét tìm kết quả số lượng tôm đếm được từ khối chức năng
                    if "count_shrimp" in outputs:
                        shrimp_data = outputs["count_shrimp"]
                        total_shrimp = shrimp_data.get("count") if isinstance(shrimp_data, dict) else shrimp_data
                    
                    # Quét tìm đường dẫn liên kết hình ảnh bọc khung kết quả
                    if "output_image" in outputs:
                        image_data = outputs["output_image"]
                        output_image_url = image_data.get("value") if isinstance(image_data, dict) else image_data
                
                # Hiển thị thông số kết quả đếm trực quan ra màn hình web của bạn
                if total_shrimp is not None:
                    st.success(f"🎉 Kết quả đếm thành công! Tìm thấy: {total_shrimp} con tôm.")
                else:
                    st.warning("⚠️ AI đã xử lý xong nhưng không tìm thấy dữ liệu từ khối đếm 'count_shrimp'. Hãy đảm bảo tên khối trên sơ đồ trùng khớp.")
                
                # Tải dữ liệu ảnh kết quả đã được vẽ bọc khung màu từ đám mây về hiển thị
                if output_image_url:
                    img_response = requests.get(output_image_url)
                    if img_response.status_code == 200:
                        st.image(img_response.content, caption="Ảnh kết quả phân tích bọc khung từ AI", use_container_width=True)
            else:
                st.error(f"❌ Máy chủ AI từ chối xử lý dữ liệu. Mã lỗi HTTP: {response.status_code}")
                st.info("Nhật ký lỗi chi tiết từ máy chủ Roboflow:\n" + response.text)
                    
        except Exception as e:
            st.error(f"❌ Gặp sự cố kết nối hệ thống: {str(e)}")
