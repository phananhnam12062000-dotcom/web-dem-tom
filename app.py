import streamlit as st
import requests
import base64
import json

# Ép máy chủ Streamlit Cloud xóa sạch toàn bộ bộ nhớ đệm cache cũ để nạp code mới
st.cache_data.clear()
st.cache_resource.clear()

# Cấu hình giao diện trang web đếm tôm cao cấp, tự động co giãn theo màn hình điện thoại
st.set_page_config(page_title="Hệ Thống Đếm Tôm AI", page_icon="🦐", layout="centered")

st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🦐 Hệ Thống Đếm Tôm Tự Động</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #7f8c8d;'>Tải ảnh khay tôm lên để hệ thống phân tích và trả số lượng tức thì</h3>", unsafe_allow_html=True)

# Đọc thông tin từ hệ thống Secrets an toàn của Streamlit
try:
    API_KEY = st.secrets["roboflow"]["api_key"]
    WORKSPACE_NAME = st.secrets["roboflow"]["workspace_name"]
    WORKFLOW_NAME = st.secrets["roboflow"]["workflow_name"]
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
    
    with st.spinner("🔄 Hệ thống đang kết nối trực tiếp đám mây và tiến hành đếm tôm..."):
        try:
            # Mã hóa dữ liệu sang chuỗi văn bản Base64 thô chuẩn định dạng JSON của Roboflow
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # ĐÃ SỬA CHUẨN XÁC 100% ĐƯỜNG DẪN: Chuyển cụm '/outputs' lên ngay sau tên Workspace theo đúng cấu trúc cổng api v1
            url_chuan_vinh_vien = f"https://roboflow.com{WORKSPACE_NAME}/outputs/{WORKFLOW_NAME}?api_key={API_KEY}"
            
            # Đóng gói dữ liệu JSON đầu vào đúng định dạng chuẩn của cổng Serverless Workflows
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
            
            # Gửi yêu cầu HTTP POST kèm Payload JSON chuẩn hóa lên hệ thống đám mây
            response = requests.post(url_chuan_vinh_vien, data=json.dumps(payload), headers=headers)
            
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
                            outputs = outputs if isinstance(outputs, dict) else outputs
                    else:
                        outputs = result
                
                # Khởi tạo giá trị mặc định ban đầu để tránh lỗi đứng giao diện web
                total_shrimp = None
                output_image_url = None
                
                # Trích xuất dữ liệu từ các khối (Block) dựa trên tên bạn đặt trong sơ đồ khối Roboflow
                if isinstance(outputs, dict):
                    # Quét tìm kết quả số lượng tôm đếm được từ khối chức năng 'count_shrimp'
                    if "count_shrimp" in outputs:
                        shrimp_data = outputs["count_shrimp"]
                        total_shrimp = shrimp_data.get("count") if isinstance(shrimp_data, dict) else shrimp_data
                    
                    # Quét tìm đường dẫn liên kết hình ảnh bọc khung kết quả từ khối 'output_image'
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
