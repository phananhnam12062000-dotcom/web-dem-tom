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
    
    with st.spinner("🔄 Hệ thống đang kết nối trực tiếp đám mây và tiến hành đếm tôm..."):
        try:
            # Mã hóa dữ liệu sang chuỗi văn bản Base64 thô chuẩn định dạng JSON của Roboflow
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # 🔥 ĐÃ SỬA CHUẨN XÁC ĐỊNH DẠNG: URL Serverless dành riêng cho xử lý quy trình Workflows Roboflow
            url_chuan_vinh_vien = f"https://serverless.roboflow.com/infer/workflows/{WORKSPACE_NAME}/{WORKFLOW_NAME}"
            
            # Đóng gói dữ liệu JSON đầu vào đúng định dạng chuẩn của cổng Serverless Workflows
            payload = {
                "inputs": {
                    "image": {
                        "type": "base64",
                        "value": base64_image
                    }
                }
            }
            
            # Bảo mật thông tin bằng cách đẩy API Key vào Header thay vì để lộ trên thanh URL
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            }
            
            # Gửi yêu cầu HTTP POST kèm Payload JSON chuẩn hóa lên hệ thống đám mây
            response = requests.post(url_chuan_vinh_vien, data=json.dumps(payload), headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                # Khai báo biến bóc tách tầng dữ liệu từ máy chủ
                outputs = {}
                
                # Trích xuất tầng dữ liệu chính nằm trong trường 'outputs' từ cấu trúc phản hồi của Roboflow
                if isinstance(result, dict):
                    if "outputs" in result:
                        if isinstance(result["outputs"], list) and len(result["outputs"]) > 0:
                            outputs = result["outputs"][0]
                        else:
                            outputs = result["outputs"]
                    else:
                        outputs = result
                
                # Khởi tạo giá trị mặc định ban đầu để tránh lỗi đứng giao diện web
                total_shrimp = None
                output_image_base64 = None
                
                # Trích xuất dữ liệu từ các khối dựa trên cấu trúc sinh ra từ Workflow sơ đồ
                if isinstance(outputs, dict):
                    # 1. Quét tìm khối chứa kết quả đếm tôm
                    for key, val in outputs.items():
                        if "count" in key.lower() or "detect" in key.lower() or "tom" in key.lower():
                            if isinstance(val, dict):
                                if "count" in val:
                                    total_shrimp = val["count"]
                                elif "predictions" in val and isinstance(val["predictions"], list):
                                    total_shrimp = len(val["predictions"])
                            elif isinstance(val, (int, float)):
                                total_shrimp = int(val)
                    
                    # 2. Quét tìm ảnh đầu ra đã được vẽ khung bọc màu từ AI
                    for key, val in outputs.items():
                        if "image" in key.lower() or "render" in key.lower() or "visualization" in key.lower():
                            if isinstance(val, dict) and "value" in val:
                                output_image_base64 = val["value"]
                            elif isinstance(val, str) and (val.startswith("/9j/") or "base64" in val):
                                output_image_base64 = val
                
                # Hiển thị thông số kết quả đếm trực quan ra màn hình web của bạn
                if total_shrimp is not None:
                    st.success(f"🎉 Kết quả đếm thành công! Tìm thấy: {total_shrimp} con tôm.")
                else:
                    st.warning("⚠️ AI đã xử lý thành công nhưng chưa tự động trích xuất được số lượng. Bạn vui lòng kiểm tra lại chính xác tên khối đếm trong sơ đồ Roboflow Workflow.")
                
                # Giải mã chuỗi base64 trả về thành ảnh hiển thị trực tiếp lên màn hình
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
