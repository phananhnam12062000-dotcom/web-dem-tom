import streamlit as st
import base64
import os
from roboflow import Roboflow

# Cấu hình giao diện trang web đếm tôm tự động co giãn theo màn hình điện thoại
st.set_page_config(page_title="Hệ Thống Đếm Tôm AI", page_icon="🦐", layout="centered")

st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🦐 Hệ Thống Đếm Tôm Tự Động</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #7f8c8d;'>Tải ảnh khay tôm lên để hệ thống phân tích và trả số lượng tức thì</h3>", unsafe_allow_html=True)

# Đọc thông tin cấu hình bảo mật từ Streamlit Secrets
try:
    API_KEY = st.secrets["roboflow"]["api_key"].strip()
    WORKSPACE_NAME = st.secrets["roboflow"]["workspace_name"].strip()
    WORKFLOW_NAME = st.secrets["roboflow"]["workflow_name"].strip()
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
    
    with st.spinner("🔄 Hệ thống đang kết nối trực tiếp Roboflow và tiến hành đếm tôm..."):
        try:
            # Lưu ảnh tạm thời để thư viện Roboflow đọc dữ liệu gửi lên máy chủ
            temp_filename = "temp_shrimp_image.jpg"
            with open(temp_filename, "wb") as f:
                f.write(image_bytes)
            
            # 🔥 SỬA ĐÚNG HÀM GỌI WORKFLOW THEO THƯ VIỆN ROBOFLOW CHUẨN
            rf = Roboflow(api_key=API_KEY)
            
            # Truy cập vào phân vùng workspace của bạn
            workspace = rf.workspace(WORKSPACE_NAME)
            
            # Gọi lệnh thực thi Workflow bằng hàm predict_workflow
            response = workspace.predict_workflow(
                image_path=temp_filename,
                workflow_id=WORKFLOW_NAME
            )
            
            # Xóa file ảnh tạm sau khi gửi xong để sạch bộ nhớ máy chủ
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                
            # Đọc kết quả JSON trả về từ Roboflow Workflows
            if response:
                # Cấu trúc của predict_workflow thường trả về trực tiếp kết quả hoặc bọc trong 'outputs'
                outputs = response.get("outputs", response)
                
                # Nếu kết quả trả về dạng danh sách (List), lấy phần tử đầu tiên
                if isinstance(outputs, list) and len(outputs) > 0:
                    outputs = outputs[0]
                
                total_shrimp = None
                output_image_base64 = None
                
                # Tự động quét cấu trúc cây dữ liệu trả về từ các khối sơ đồ để tìm kết quả
                if isinstance(outputs, dict):
                    # 1. Tìm số lượng con vật đếm được
                    for key, val in outputs.items():
                        if any(x in key.lower() for x in ["count", "detect", "tom", "shrimp"]):
                            if isinstance(val, dict):
                                if "count" in val:
                                    total_shrimp = val["count"]
                                elif "predictions" in val and isinstance(val["predictions"], list):
                                    total_shrimp = len(val["predictions"])
                            elif isinstance(val, (int, float)):
                                total_shrimp = int(val)
                    
                    # 2. Tìm ảnh kết quả vẽ khung bọc màu từ AI
                    for key, val in outputs.items():
                        if any(x in key.lower() for x in ["image", "render", "visual"]):
                            if isinstance(val, dict) and "value" in val:
                                output_image_base64 = val["value"]
                            elif isinstance(val, str) and (val.startswith("/9j/") or "base64" in val):
                                output_image_base64 = val
                
                # Hiển thị số lượng đếm được lên giao diện
                if total_shrimp is not None:
                    st.success(f"🎉 Kết quả đếm thành công! Tìm thấy: {total_shrimp} con tôm.")
                else:
                    st.warning("⚠️ AI đã xử lý thành công nhưng chưa tự bóc tách được số lượng. Vui lòng kiểm tra lại tên khối đếm trên sơ đồ Roboflow Workflow.")
                
                # Hiển thị ảnh vẽ khung bọc màu kết quả
                if output_image_base64:
                    try:
                        if "," in output_image_base64:
                            output_image_base64 = output_image_base64.split(",")[-1]
                        decoded_img = base64.b64decode(output_image_base64)
                        st.image(decoded_img, caption="Ảnh kết quả phân tích bọc khung từ AI", use_container_width=True)
                    except Exception:
                        st.info("Không thể dựng ảnh bọc khung kết quả phân tích.")
            else:
                st.error("❌ Máy chủ AI trả về dữ liệu rỗng hoặc không đúng cấu trúc.")
                st.info("Dữ liệu phản hồi thực tế: " + str(response))
                    
        except Exception as e:
            st.error(f"❌ Gặp sự cố kết nối hệ thống: {str(e)}")
