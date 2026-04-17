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

Dự án xây dựng **hệ thống quản lý và đặt vé rạp chiếu phim trực tuyến**, nhằm giải quyết các hạn chế của phương thức đặt vé truyền thống như tốn thời gian, khó quản lý và dễ xảy ra sai sót khi lượng khách tăng cao.

Hệ thống cho phép **người dùng (User)** thực hiện các chức năng như: đăng nhập, xem lịch chiếu, xem thông tin phim, chọn ghế, đặt vé, thanh toán bằng mã QR và theo dõi lịch sử giao dịch. Ngoài ra, hệ thống tích hợp **trợ lý AI** giúp tư vấn phim và gợi ý suất chiếu phù hợp.
    
Đối với **quản trị viên (Admin)**, hệ thống hỗ trợ quản lý kho phim, tạo lịch chiếu hàng loạt, cấu hình sơ đồ rạp, đăng tin tức và theo dõi doanh thu. Điều này giúp tối ưu vận hành và nâng cao hiệu quả kinh doanh cho rạp chiếu phim.

---

**Môi trường hoạt động**

Hệ thống được xây dựng theo mô hình **web-based**:

- **Client:** Trình duyệt hỗ trợ HTML5 (Chrome, Edge, Firefox)
- **Frontend:** React.js, Tailwind CSS  
- **Backend:** FastAPI (Python), hỗ trợ Swagger API Documentation  
- **Database:** PostgreSQL (có thể tích hợp Supabase)  
- **AI Assistant:** Áp dụng mô hình RAG (Retrieval-Augmented Generation), kết hợp truy xuất dữ liệu từ hệ thống và sử dụng Ollama để triển khai mô hình AI (LLM) chạy cục bộ, giúp tăng độ chính xác và đảm bảo tính bảo mật dữ liệu  

Hệ thống giao tiếp thông qua **RESTful API** giữa frontend và backend.

---

**Ràng buộc thiết kế & triển khai**

- **Công nghệ:** Sử dụng FastAPI, React và PostgreSQL
- **Hiệu năng:** Xử lý nhiều người dùng đặt vé đồng thời, tránh trùng ghế
- **Bảo mật:** Xác thực người dùng, bảo vệ thông tin và giao dịch
- **Khả dụng:** Giao diện dễ sử dụng, trực quan (đặc biệt phần chọn ghế)
- **Tài liệu:** API phải được mô tả rõ ràng bằng Swagger
- **Mở rộng:** Thiết kế hệ thống dạng module để dễ nâng cấp (AI, thanh toán,...)

---

## 3. Proposed Solution

### 3.1 Software

#### 3.1.1 Features

#### 3.1.2 Software Architecture

### 3.2 Hardware


## 4. Development Plan

### 4.1 Requirements Analysis

### 4.2 Software Design

### 4.3 Implementation

### 4.4 Testing

### 4.5 Deployment and Maintainance


## 5. Human Resources & Costing Plan

### **5.1. Cơ cấu nhân sự**

Dự án được thực hiện bởi **nhóm 4 sinh viên (Team 3)**, với các vai trò được phân chia rõ ràng nhằm đảm bảo tiến độ và chất lượng sản phẩm:

- **Project Manager (Quản lý dự án):** Chịu trách nhiệm lập kế hoạch, phân công công việc, theo dõi tiến độ và đảm bảo dự án hoàn thành đúng thời hạn.   
  
- **Backend Developer:** Phát triển hệ thống backend FastAPI, xây dựng RESTful API, xử lý logic nghiệp vụ (đặt vé, thanh toán, quản lý dữ liệu).   
  
- **Frontend Developer:** Xây dựng giao diện người dùng bằng React.js, đảm bảo trải nghiệm người dùng (UI/UX) trực quan và dễ sử dụng.   
  
- **Database Engineer:** Thiết kế và quản lý cơ sở dữ liệu PostgreSQL, đảm bảo tính toàn vẹn, hiệu năng và bảo mật dữ liệu.   
  
- **AI/Integration Developer:** Phụ trách tích hợp trợ lý AI (RAG), xử lý truy xuất dữ liệu và xây dựng chatbot hỗ trợ người dùng.  
  
**Dự kiến vai trò của từng thành viên:**
  

| Thành viên | Vai trò |
|-----------|--------|
| Trần Kim Ngân | Project Manager, Backend Developer 1 | 
| Lê Hoàng Mỹ Hạ | AI/Integration Developer|
| Nguyễn Thanh Huyền | Frontend Developer |
| Nguyễn Gia Huy | Backend Developer 2|
---

### **5.2. Phân chia theo giai đoạn phát triển**

- **Giai đoạn 1 – Phân tích & Thiết kế:**  
  Tất cả thành viên tham gia thu thập yêu cầu, phân tích hệ thống và thiết kế kiến trúc.

- **Giai đoạn 2 – Phát triển:**  
  Backend và Frontend phát triển song song, Database hỗ trợ thiết kế dữ liệu, AI developer tích hợp chatbot.

- **Giai đoạn 3 – Kiểm thử & Triển khai:**  
  Kiểm thử toàn hệ thống, sửa lỗi và hoàn thiện sản phẩm trước khi bàn giao.

---

### **5.3. Chi phí dự kiến**

Vì đây là **dự án học tập**, chi phí chủ yếu đến từ hạ tầng và công cụ:

- **Chi phí server (cloud hosting):**  
  ~ 0 USD (chạy trên máy cá nhân, không sử dụng cloud)

- **Chi phí database (Supabase/PostgreSQL cloud):**  
  ~ 0 USD (gói miễn phí)

- **Chi phí domain (nếu có):**  
  ~ 10 – 15 USD/năm

- **Chi phí AI (API hoặc triển khai local):**  
  ~ 0 – 20 USD (tùy mức sử dụng)

- **Chi phí nhân lực:**  
  Không tính (do sinh viên thực hiện)

## 6. Tools setup


## 7. AI Usage Declaration


## 8. Presentation


## 9. Reflective Report