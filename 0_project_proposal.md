# Project Proposal

## Table of Contents
1. [Member Contribution Assessment](#member-contribution-assessment)
2. [Preliminary Problem Statementt](#preliminary-problem-statement)
3. [Proposed Solution](#3-proposed-solution)
4. [Development Plan](#4-development-plan)
5. [Human Resources & Costing Plan](#5-human-resources--costing-plan)
6. [Tools setup](#6-tools-setup)
7. [AI Usage Declaration](#7-ai-usage-declaration)
8. [Presentation](#8-presentation)
9. [Reflective Report](#9-reflective-report)

---

## 1. Member Contribution Assessment


## 2. Preliminary Problem Statement


## 3. Proposed Solution

### 3.1 Software

#### 3.1.1 Features

#### 3.1.2 Software Architecture

### 3.2 Hardware


## 4. Development Plan
Written by: 23120060 - Trần Kim Ngân 

### 4.1 Requirements Analysis
- **Hoạt động chính**: Khảo sát các hệ thống đặt vé hiện có (CGV, Lotte, MoMo,...), họp nhóm để chốt các tính năng chính cho dự án.

- **Yêu cầu về chức năng**: Hiện thông tin phim, đặt vé, chọn chỗ ngồi, tích hợp trợ lý đặt vé, thanh toán qua QR.

- **Yêu cầu phi chức năng**: Độ tải thấp khi load trang, thông tin trên vé và mã QR phải khớp với database, bảo mật mật khẩu người dùng.

- **Đầu ra**: Tài liệu yêu cầu phần mềm (SRS), sơ đồ Use case.

### 4.2 Software Design
- **Kiến trúc hệ thống**: sử dụng kiến trúc 3-Tier
    - **Presentation Tier (Frontend)**: Xây dựng bằng React.js, hiển thị giao diện, quản lý trạng thái chọn ghế, hiển thị tính năng trợ lý AI.
    - **Logic Tier (Backend)**: Sử dụng FastAPI để xử lý logic như: đặt vé, kiểm tra tình trạng ghế, tạo mã QR thanh toán, chuyển dữ liệu cho mô hình AI.
    - **Data Tier (Database)**: Lưu trữ Database cho web bằng PostgreSQL và Vector Database (ChromaDB) cho hệ thống RAG.

- **Thiết kế cơ sở dữ liệu**:
    - Sơ đồ thực thể mối quan hệ (ERD):
        - **Users**: Thông tin khách hàng và lịch sử đặt vé.
        - **Movies & Showtimes**: Thông tin phim, lịch chiếu và phòng chiếu.
        - **Seats**: Quản lý trạng thái ghế (Trống, Đang giữ, Đã bán) theo thời gian thực.
        - **Payments**: Lưu trữ mã giao dịch QR và trạng thái thanh toán.

    - Vector Database (ChromaDB): Lưu trữ các embeddings thông tin phim, đánh giá và mô tả để chatbot có thể thực hiện truy xuất chính xác.

- **Thiết kế giao diện: gồm các frame chính**:
    - Trang chủ (có phần trợ lý AI)
    - Trang chi tiết phim.
    - Sơ đồ ghế
    - Trang thanh toán
    - Trang thêm phim của Admin

- Công nghệ sử dụng:

| Thành phần | Công nghệ | Lý do lựa chọn / Vai trò |
| :--- | :--- | :--- |
| **Frontend** | React.js | Hiệu suất cao, dễ sử dụng và có nhiều template. |
| **Backend** | Python (FastAPI) | Tối ưu, dễ tích hợp các thư viện AI. |
| **Database** | PostgreSQL | Đảm bảo tính toàn vẹn dữ liệu cho các giao dịch đặt vé, thanh toán và phân quyền Admin. |
| **Vector DB** | ChromaDB | Lưu trữ dữ liệu phim dưới dạng Vector để Chatbot (RAG) truy vấn thông tin chính xác. |
| **AI Model** | Ollama | Chạy local giúp bảo mật dữ liệu và không tốn chi phí API. |
| **DevOps** | Docker | Đóng gói hệ thống |
| **Version Control** | Git / GitHub | Quản lý mã nguồn, chia nhánh tính năng và phối hợp làm việc nhóm hiệu quả. |

### 4.3 Implementation
- **Quy trình phát triển**: dùng mô hình Scrum để làm dự án.

- **Môi trường phát triển**: 
    - Quản lý source code: dùng Git/GitHub để lưu trữ 
    - Quy tắc đặt tên: Frontend (`varName` cho biến, `ComponentName` cho Component), Backend (`func_name` chuẩn PEP 8)
    - Đóng gói môi trường: dùng Docker, Docker Compose để đảm bảo môi trường chạy giống nhau trên mọi máy tính. 

- **Các milestone**:

| Giai đoạn | Mốc thời gian | Mục tiêu trọng tâm | Sản phẩm bàn giao |
| :--- | :--- | :--- | :--- |
| **Sprint 1** | Tuần 1-2 | Thiết lập hạ tầng: Docker, Database schema, Authentication (JWT). | Môi trường Docker hoàn chỉnh, Module Đăng nhập/Đăng ký. |
| **Sprint 2** | Tuần 3-4 | Phát triển Core Logic: CRUD phim cho Admin, Giao diện chọn ghế cho User. | Dashboard Admin, Sơ đồ ghế cập nhật thời gian thực. |
| **Sprint 3** | Tuần 5-6 | Tích hợp AI & Thanh toán: Xây dựng RAG Pipeline, tích hợp QR Payment. | Chatbot trả lời thông tin phim, Module thanh toán QR. |
| **Sprint 4** | Tuần 7-8 | Tối ưu hóa & Testing: Kiểm thử tính đồng thời (trùng ghế), fix bug và tối ưu tốc độ AI. | Bản báo cáo kiểm thử (Test Report). |
| **Sprint 5** | Tuần 9-10 | Triển khai (Deployment): Đưa hệ thống lên môi trường thật và hoàn thiện tài liệu. | Live Demo URL, Tài liệu hướng dẫn sử dụng. |

### 4.4 Testing
- **Sử dụng các loại kiểm thử**:
    - Unit test: kiểm tra từng module/hàm nhỏ.
    - Integration test: kiểm tra chức năng khi kết hợp Frontend và Backend

- **Tiêu chuẩn chất lượng**:
    - **Code Quality**: Mã nguồn đã được Review bởi Architect và tuân thủ các quy tắc đặt tên, cấu trúc của nhóm.
    - **Test Passed**: Vượt qua tất cả các bài kiểm Unit Test và Integration Test liên quan mà không có lỗi nghiêm trọng.
    - **Deployment**: Tính năng đã được đóng gói vào Docker và chạy ổn định trên môi trường thử nghiệm.
    - **Documentation**: Cập nhật hướng dẫn sử dụng hoặc mô tả API tương ứng vào tài liệu chung của dự án.
    - **User Flow**: Luồng người dùng từ lúc bắt đầu đến lúc kết thúc (từ chọn phim đến lúc nhận mã vé) không bị lỗi giữa chừng.

### 4.5 Deployment and Maintainance
- **Triển khai hệ thống**: đóng gói các phần vào Docker Containers để dễ dàng deploy lên bất kì server nào.

- **Bảo trì và hỗ trợ**:
    - Monitoring: sử dụng các công cụ quản lý log để phát hiện và cảnh báo ngay lập tức các lỗi phát sinh từ hệ thống.
    - Hỗ trợ kỹ thuật: Xây dựng Feedback form hoặc Hotline để hỗ trợ người dùng khi gặp sự cố.


## 5. Human Resources & Costing Plan


## 6. Tools setup


## 7. AI Usage Declaration

– Gemini. Gemini Fast, Google, gemini.google.com, truy cập lúc 21:55, 16/04/2026, prompt: “Về development plan ở phần Project proposal với các yêu cầu là Requirements Analysis, Software Design, Implementation, Testing, Deployment and Maintainance. Thì nội dung chính là sẽ viết những gì ở đó”, sử dụng cho phần viết report ở 4. Development Plan; AI đưa ra sườn bài viết gồm những mục cần viết sau đó sẽ thêm thông tin của dự án vào.


## 8. Presentation


## 9. Reflective Report