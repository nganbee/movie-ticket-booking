# CineBook - Hệ Thống Đặt Vé Xem Phim Tích Hợp AI Chatbot

## Tổng quan dự án
CineBook là một hệ thống đặt vé xem phim trực tuyến hiện đại, mang đến trải nghiệm tiện lợi cho người dùng và cung cấp công cụ quản lý toàn diện cho quản trị viên (Admin). Điểm nổi bật của CineBook là việc tích hợp **Trợ lý ảo AI (CineBot)**, giúp người dùng dễ dàng tìm kiếm phim, tra cứu suất chiếu và thực hiện đặt vé thông qua ngôn ngữ tự nhiên.

## Kiến trúc hệ thống
Hệ thống được chia làm hai phần chính:
- **Frontend:** Xây dựng bằng `Node.js` + `Express.js`, sử dụng View Engine `EJS` để render giao diện Server-side. Giao diện được thiết kế bằng `TailwindCSS` mang lại phong cách hiện đại (Modern UI) và đáp ứng tốt trên các thiết bị di động.
- **Backend:** Xây dựng bằng `Python` với Framework `FastAPI`, cung cấp các RESTful APIs tốc độ cao. Giao tiếp với cơ sở dữ liệu `PostgreSQL` thông qua ORM `SQLAlchemy` (Async mode). Tích hợp các AI Model (HuggingFace) để xử lý ngôn ngữ tự nhiên cho Chatbot.

## Các nhóm chức năng ở Backend (FastAPI)
1. **Quản lý Phim & Rạp (Movies & Theaters):** API thêm, sửa, xóa thông tin phim, rạp chiếu, phòng chiếu và sơ đồ ghế.
2. **Quản lý Suất chiếu (Showtimes):** API tạo lịch chiếu, hỗ trợ tính năng tạo lịch chiếu hàng loạt (Bulk Insert) có kiểm tra trùng lặp thời gian thực.
3. **Quản lý Đặt vé (Bookings):** API đặt chỗ (giữ ghế), thanh toán qua VNPAY, xuất vé điện tử (E-Ticket) với mã QR, và tự động hủy vé (Background Sweeper) nếu quá hạn thanh toán 10 phút.
4. **AI & Chatbot Service:** Phân tích câu hỏi của người dùng, truy vấn cơ sở dữ liệu để đưa ra gợi ý phim, suất chiếu tối ưu và lưu lịch sử phiên chat.
5. **Xác thực & Phân quyền (Auth):** Quản lý người dùng, đăng nhập/đăng ký bằng JWT (JSON Web Tokens), và phân quyền Admin.

## Các trang ở Frontend (Express.js + EJS)
### Dành cho Người dùng (User)
- **Trang chủ:** Hiển thị phim đang chiếu, phim sắp chiếu, các banner quảng cáo.
- **Trang chi tiết phim:** Thông tin chi tiết, trailer, đánh giá và lịch chiếu của bộ phim.
- **Trang Đặt vé & Chọn ghế:** Giao diện chọn ghế ngồi trực quan (ghế thường, ghế VIP, ghế đôi) theo sơ đồ phòng chiếu thực tế.
- **Trang Lịch sử & E-Ticket:** Nơi người dùng xem lại vé đã đặt và mã QR để quét khi vào rạp.
- **Widget Chatbot AI:** Biểu tượng nổi ở góc màn hình, giúp người dùng chat trực tiếp để tìm phim, hỏi suất chiếu hoặc nhờ gợi ý.

### Dành cho Quản trị viên (Admin Dashboard)
- **Quản lý Giao dịch:** Xem danh sách đơn hàng, doanh thu, được phân trang (Server-side Pagination) để tối ưu hiệu suất, có tìm kiếm và lọc trạng thái.
- **Quản lý Lịch chiếu:** Thêm, sửa lịch chiếu phim vào các phòng, hỗ trợ thêm hàng loạt.
- **Quản lý Phòng & Rạp:** Theo dõi sức chứa, thiết lập sơ đồ ghế cho từng phòng chiếu.
- **Quản lý Phim:** Cập nhật thông tin, poster, thể loại và ngày khởi chiếu.

## Cách cài đặt môi trường

### 1. Yêu cầu hệ thống
- **Python:** Phiên bản 3.9 trở lên (dành cho Backend).
- **Node.js:** Phiên bản 18.x trở lên (dành cho Frontend).
- **Cơ sở dữ liệu:** PostgreSQL (Host trên Supabase)

### 2. Thiết lập Backend (FastAPI)
```bash
# Di chuyển vào thư mục backend
cd backend

# Tạo môi trường ảo (Virtual Environment)
python -m venv venv
# Kích hoạt môi trường (Windows)
venv\Scripts\activate

# Cài đặt thư viện
pip install -r requirements.txt

# Cấu hình biến môi trường
# Tạo file .env và điền thông tin (DATABASE_URL, JWT_SECRET, VNPAY_KEYS...)
```

### 3. Thiết lập Frontend (Node.js)
```bash
# Di chuyển vào thư mục frontend
cd frontend

# Cài đặt gói thư viện NPM
npm install
```

## Cách chạy web

1. **Khởi động Backend:**
Mở terminal, đảm bảo đã kích hoạt `venv` và đang ở thư mục `backend`:
```bash
uvicorn main:app --reload --port 8000
# Backend sẽ chạy tại: http://localhost:8000
```

2. **Khởi động Frontend:**
Mở một terminal khác, di chuyển vào thư mục `frontend`:
```bash
npm run dev
# Frontend sẽ chạy tại: http://localhost:3000
```

3. Truy cập vào trình duyệt tại `http://localhost:3000` để trải nghiệm hệ thống.

## Hướng phát triển trong tương lai
- **Hệ thống Recommendation System:** Ứng dụng Machine Learning để cá nhân hóa đề xuất phim cho từng người dùng dựa trên lịch sử xem và đánh giá.
- **Nâng cấp Chatbot:** Cho phép Chatbot có khả năng trực tiếp "giữ ghế" và tạo lệnh thanh toán ngay trong giao diện chat.
- **Microservices hoàn chỉnh:** Tách hẳn AI Service và Payment Service thành các Container độc lập (Docker/Kubernetes) để dễ dàng scale-up khi hệ thống chịu tải lớn.
- **Mobile App:** Xây dựng ứng dụng di động bằng React Native hoặc Flutter sử dụng lại toàn bộ API từ Backend hiện tại.
