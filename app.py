import streamlit as st
import requests
import base64
import json

# LỆNH TỐI CAO: Ép buộc máy chủ Streamlit xóa bỏ toàn bộ cache cũ ngay khi khởi chạy
st.cache_data.clear()
st.cache_resource.clear()

# Cấu hình giao diện trang web đếm tôm cao cấp, tự động co giãn theo màn hình điện thoại
st.set_page_config(page_title="Hệ Thống Đếm Tôm AI", page_icon="🦐", layout="centered")

st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🦐 Hệ Thống Đếm Tôm Tự Động</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #7f8c8d;'>Tải ảnh khay tôm lên để hệ thống phân tích và trả số lượng tức thì</h3>", unsafe_allow_html=True)

# Nút chức năng tải ảnh khay tôm từ thiết bị
anh_tai_len = st.file_uploader("Chọn ảnh khay tôm của bạn...", type=["jpg", "jpeg", "png"])

if anh_tai_len is not None:
    # Đọc dữ liệu ảnh từ giao diện người dùng
    du_lieu_anh_tho = anh_tai_len.read()
    
    # Hiển thị ảnh gốc người dùng chọn lên màn hình web
    st.image(du_lieu_anh_tho, caption="Ảnh khay tôm đã tải lên", use_container_width=True)
    
    with st.spinner("🔄 Hệ thống đang kết nối trực tiếp đám mây và tiến hành đếm tôm..."):
        try:
            # Mã hóa dữ liệu sang chuỗi văn bản Base64 thô chuẩn định dạng JSON của Roboflow
            chuoi_anh_base64 = base64.b64encode(du_lieu_anh_tho).decode('utf-8')
            
            # ĐÃ THAY ĐỔI TÊN BIẾN VÀ ĐIỀN ĐƯỜNG DẪN TĨNH TUYỆT ĐỐI - KHÔNG GHÉP CHUỖI - KHÔNG THỂ BỊ LỖI DÍNH CHỮ
            duong_dan_api_chuan = "https://roboflow.com"
            
            # Đóng gói dữ liệu JSON đầu vào đúng định dạng chuẩn của cổng Serverless Workflows
            goi_tin_payload = {
                "inputs": {
                    "image": {
                        "type": "base64",
                        "value": chuoi_anh_base64
                    }
                }
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            # Gửi yêu cầu HTTP POST trực tiếp lên hệ thống đám mây không qua nối chuỗi
            phan_hoi_he_thong = requests.post(duong_dan_api_chuan, data=json.dumps(goi_tin_payload), headers=headers)
            
            if phan_hoi_he_thong.status_code == 200:
                ket_qua_json = phan_hoi_he_thong.json()
                
                # Bộ lọc thông minh tự động bóc tách dữ liệu JSON lồng nhau từ Workflow
                du_lieu_dau_ra = {}
                if isinstance(ket_qua_json, list) and len(ket_qua_json) > 0:
                    du_lieu_dau_ra = ket_qua_json.get("outputs", ket_qua_json) if isinstance(ket_qua_json, dict) else ket_qua_json
                elif isinstance(ket_qua_json, dict):
                    if "outputs" in ket_qua_json:
                        du_lieu_dau_ra = ket_qua_json["outputs"]
                        if isinstance(du_lieu_dau_ra, list) and len(du_lieu_dau_ra) > 0:
                            du_lieu_dau_ra = du_lieu_dau_ra
                    else:
                        du_lieu_dau_ra = ket_qua_json
                
                # Khởi tạo giá trị mặc định ban đầu để tránh lỗi đứng giao diện web
                so_luong_tom = None
                url_anh_ket_qua = None
                
                # Trích xuất dữ liệu từ các khối (Block) dựa trên tên bạn đặt trong sơ đồ khối Roboflow
                if isinstance(du_lieu_dau_ra, dict):
                    # Quét tìm kết quả số lượng tôm đếm được từ khối chức năng 'count_shrimp'
                    if "count_shrimp" in du_lieu_dau_ra:
                        khoi_dem = du_lieu_dau_ra["count_shrimp"]
                        so_luong_tom = khoi_dem.get("count") if isinstance(khoi_dem, dict) else khoi_dem
                    
                    # Quét tìm đường dẫn liên kết hình ảnh bọc khung kết quả từ khối 'output_image'
                    if "output_image" in du_lieu_dau_ra:
                        khoi_anh = du_lieu_dau_ra["output_image"]
                        url_anh_ket_qua = khoi_anh.get("value") if isinstance(khoi_anh, dict) else khoi_anh
                
                # Hiển thị thông số kết quả đếm trực quan ra màn hình web của bạn
                if so_luong_tom is not None:
                    st.success(f"🎉 Kết quả đếm thành công! Tìm thấy: {so_luong_tom} con tôm.")
                else:
                    st.warning("⚠️ AI đã xử lý xong nhưng không tìm thấy dữ liệu từ khối đếm 'count_shrimp'. Hãy đảm bảo tên khối trên sơ đồ trùng khớp.")
                
                # Tải dữ liệu ảnh kết quả đã được vẽ bọc khung màu từ đám mây về hiển thị
                if url_anh_ket_qua:
                    phan_hoi_anh = requests.get(url_anh_ket_qua)
                    if phan_hoi_anh.status_code == 200:
                        st.image(phan_hoi_anh.content, caption="Ảnh kết quả phân tích bọc khung từ AI", use_container_width=True)
            else:
                st.error(f"❌ Máy chủ AI từ chối xử lý dữ liệu. Mã lỗi HTTP: {phan_hoi_he_thong.status_code}")
                st.info("Nhật ký hệ thống: " + phan_hoi_he_thong.text)
                    
        except Exception as e:
            st.error(f"❌ Gặp sự cố kết nối hệ thống: {str(e)}")
