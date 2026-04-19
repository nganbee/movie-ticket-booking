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
> Written by: 23120049 - Nguyễn Thanh Huyền  
Edited by: [StudentID - Fullname]    
Reviewed by: [StudentID - Fullname]   

| Nhu cầu | Yêu cầu | 
| :--- | :--- |   
| Là khách hàng, tôi muốn xem lịch chiếu và thông tin phim để chọn suất chiếu phù hợp | Tra cứu phim & Lịch chiếu |   
| Là khách hàng, tôi muốn tự chọn ghế và đặt vé trực tuyến để không phải xếp hàng | Đặt vé & Sơ đồ chọn ghế trực quan |  
| Là khách hàng, tôi muốn thanh toán nhanh qua mã QR và xem lại lịch sử giao dịch | Thanh toán QR & Lịch sử giao dịch  |
| Là khách hàng, tôi muốn xem lại lịch sử giao dịch |  Lịch sử giao dịch  |
| Là khách hàng, tôi muốn được trợ lý AI tư vấn phim dựa trên sở thích cá nhân | Trợ lý AI tư vấn |  
| Là quản trị viên, tôi muốn quản lý kho phim và tạo lịch chiếu hàng loạt để tối ưu vận hành | Quản lý Phim & Lịch chiếu |  
| Là quản trị viên, tôi muốn cấu hình rạp | Cấu hình hệ thống |  
| Là quản trị viên, tôi muốn theo dõi doanh thu để quản lý kinh doanh | Thống kê doanh thu |  
| Là người dùng, tôi muốn thông tin giao  của tôi được bảo mật | Bảo mật giao dịch |      
---
#### 3.1.2 Software Architecture  
> Written by: 23120049 - Nguyễn Thanh Huyền  
Edited by: [StudentID - Fullname]    
Reviewed by: [StudentID - Fullname]    

Hệ thống được thiết kế theo kiến trúc Client-Server hiện đại, tách biệt giữa giao diện và xử lý nghiệp vụ: 
Hệ thống được thiết kế theo kiến trúc Client-Server hiện đại, tách biệt hoàn toàn giữa giao diện và nghiệp vụ thông qua RESTful API:

- **Frontend (Client):** Xây dựng bằng React.js kết hợp với Tailwind CSS để tạo giao diện phản hồi nhanh (Responsive) và tối ưu trải nghiệm người dùng trên các trình duyệt hỗ trợ HTML5.

- **Backend (Server):** Sử dụng FastAPI (Python) để xử lý logic nghiệp vụ. FastAPI cung cấp hiệu năng cao và tự động tạo tài liệu Swagger API giúp việc phát triển và tích hợp dễ dàng hơn.

- **Database:** Sử dụng PostgreSQL để lưu trữ dữ liệu có cấu trúc (thông tin phim, người dùng, giao dịch vé).

- **AI Component:** Triển khai theo mô hình RAG (Retrieval-Augmented Generation). Sử dụng Ollama để chạy các mô hình LLM cục bộ, kết hợp với dữ liệu truy xuất từ PostgreSQL để phản hồi các yêu cầu tư vấn của người dùng một cách chính xác và bảo mật.
### 3.2 Hardware  
> Written by: 23120049 - Nguyễn Thanh Huyền  
Edited by: [StudentID - Fullname]   
Reviewed by: [StudentID - Fullname]  

Để hệ thống hoạt động ổn định, đặc biệt là khi triển khai mô hình AI cục bộ, các yêu cầu phần cứng bao gồm:  

**Server Side:**  
- CPU: Tối thiểu 4 Cores  
- RAM: Tối thiểu 16GB (Để chạy mô hình LLM qua Ollama ổn định).  
- Lưu trữ: SSD với dung lượng trống tối thiểu 20GB.   

**Client Side:** 
- Máy tính hoặc thiết bị di động có kết nối Internet.  
- Trình duyệt web hiện đại (Chrome, Edge, Firefox) hỗ trợ HTML5.


## 4. Development Plan

### 4.1 Requirements Analysis

### 4.2 Software Design

### 4.3 Implementation

### 4.4 Testing

### 4.5 Deployment and Maintainance


## 5. Human Resources & Costing Plan


## 6. Tools setup


## 7. AI Usage Declaration


## 8. Presentation


## 9. Reflective Report