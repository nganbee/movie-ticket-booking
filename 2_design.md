# Design

## Table of Contents
1. [Member Contribution Assessment](#1-member-contribution-assessment)
2. [Conceptual Model](#2-conceptual-model)
3. [Architectural Design](#3-architectural-design)
4. [Data Design](#4-data-design)
5. [UI/UX](#5-uiux)
6. [AI Usage Declaration](#6-ai-usage-declaration)
7. [Presentation](#7-presentation)
8. [Reflective Report](#8-reflective-report)

---

## 1. Member Contribution Assessment

**23120038 - Lê Hoàng Mỹ Hạ - Contribution (25%)**

**23120047 - Nguyễn Gia Huy - Contribution (25%)**

**23120049 - Nguyễn Thanh Huyền - Contribution (25%)**

**23120060 - Trần Kim Ngân - Contribution (25%)**

## 2. Conceptual Model
> Written by:   
Reviewed by:


## 3. Architectural Design

### 3.1 Architecture Diagram
> Written by: Lê Hoàng Mỹ Hạ  
Reviewed by:

#### 3.1.1 System Decomposition Tree Diagram

Hình dưới đây mô tả sơ đồ phân rã hệ thống (System Decomposition Tree Diagram) của CineBook. Hệ thống được chia thành nhiều tầng và module chức năng nhằm đảm bảo tính tổ chức, khả năng mở rộng và dễ bảo trì trong quá trình phát triển.

CineBook được phân rã thành bốn thành phần chính:

- **Presentation Tier**: Bao gồm toàn bộ giao diện tương tác với người dùng như trang chủ, đăng nhập/đăng ký, chi tiết phim, chọn ghế, thanh toán, chatbot và dashboard quản trị.
- **Logic Tier**: Chứa các module xử lý nghiệp vụ như xác thực người dùng, quản lý phim và suất chiếu, đặt vé, thanh toán VietQR, recommendation AI, báo cáo doanh thu và tài liệu API.
- **Data Tier**: Bao gồm các thành phần lưu trữ dữ liệu như PostgreSQL Database, ChromaDB vector store và media storage.
- **External / Runtime Services**: Bao gồm các dịch vụ ngoài hệ thống như Ollama Local LLM, VietQR Banking App và môi trường trình duyệt web.

Việc phân rã theo module giúp hệ thống giảm coupling giữa các thành phần, đồng thời hỗ trợ phát triển độc lập và dễ dàng mở rộng chức năng trong tương lai.

<p align="center">
  <img 
    src="data/image_template_2/3_1/decomposition.svg"
    style="width:100%; height:auto;"
  />
</p>

<p align="center">
  <em>Hình 3.1.1: System Decomposition Tree Diagram của hệ thống CineBook</em>
</p>

---

#### 3.1.2 Overall System Architecture Diagram
Hình dưới đây mô tả kiến trúc tổng thể (Overall System Architecture Diagram) của hệ thống CineBook theo mô hình Client–Server đa tầng.

Trong kiến trúc này:

- Người dùng và quản trị viên truy cập hệ thống thông qua trình duyệt web.
- Frontend được xây dựng bằng React.js và Tailwind CSS, chịu trách nhiệm hiển thị giao diện và gửi request đến backend thông qua REST API.
- Backend được phát triển bằng FastAPI, xử lý toàn bộ nghiệp vụ hệ thống như authentication, booking flow, payment processing, admin operations và AI recommendation.
- PostgreSQL được sử dụng để lưu trữ dữ liệu quan hệ và dữ liệu giao dịch.
- ChromaDB đóng vai trò vector database phục vụ semantic retrieval cho chatbot recommendation.
- Ollama Local LLM được tích hợp để sinh phản hồi hội thoại và recommendation bằng ngôn ngữ tự nhiên.
- VietQR được sử dụng để xử lý thanh toán QR-code và callback giao dịch.

Kiến trúc này cho phép tách biệt rõ ràng giữa giao diện, xử lý nghiệp vụ và lưu trữ dữ liệu, từ đó giúp hệ thống dễ mở rộng và dễ triển khai hơn.

<p align="center">
  <img src="data/image_template_2/3_1/architecture.svg" width="100%"/>
</p>
<p align="center"><em>Hình 3.1.2: Overall System Architecture Diagram của hệ thống CineBook</em></p>

---

#### 3.1.3 Architectural Characteristics & Design Approach
> Written by: 23120038 - Lê Hoàng Mỹ Hạ  
Reviewed by:   

Hệ thống CineBook áp dụng nhiều đặc điểm kiến trúc và nguyên tắc thiết kế nhằm đảm bảo hiệu năng, khả năng mở rộng và bảo trì lâu dài.

##### Client–Server Architecture
Hệ thống được xây dựng theo mô hình Client–Server, trong đó frontend đóng vai trò client và backend FastAPI đóng vai trò server xử lý nghiệp vụ.

##### Multi-Tier Architecture
Kiến trúc hệ thống được chia thành nhiều tầng gồm:
- Presentation Tier
- Logic Tier
- Data Tier
- External Services

Việc phân tầng giúp giảm sự phụ thuộc giữa các thành phần và tăng khả năng mở rộng hệ thống.

##### Modular Architecture
Các chức năng như authentication, booking, payment, AI recommendation, reporting và admin management được xây dựng thành các module độc lập. Điều này giúp việc phát triển, kiểm thử và bảo trì trở nên dễ dàng hơn.

##### RESTful API Communication
Frontend và backend giao tiếp với nhau thông qua REST API sử dụng dữ liệu JSON. Swagger/OpenAPI được tích hợp để hỗ trợ tài liệu hóa và kiểm thử API.

##### AI-Enhanced Recommendation System
Hệ thống recommendation sử dụng kiến trúc RAG (Retrieval-Augmented Generation), kết hợp:
- PostgreSQL để truy xuất dữ liệu phim
- ChromaDB để semantic retrieval
- Ollama Local LLM để sinh phản hồi hội thoại

Kiến trúc này giúp chatbot có khả năng hỗ trợ recommendation theo ngữ cảnh và tương tác tự nhiên với người dùng.

##### Security Considerations
Hệ thống áp dụng nhiều cơ chế bảo mật:
- JWT Authentication
- bcrypt password hashing
- HTTPS communication
- Token expiration
- Role-based access control cho admin dashboard

Những đặc điểm kiến trúc trên giúp CineBook có nền tảng phù hợp cho việc mở rộng tính năng và triển khai thực tế trong tương lai.

### 3.2 Class Diagram
> Written by:   
Reviewed by:

### 3.3 Class Specifications
> Written by:   
Reviewed by:

## 4. Data Design

### 4.1 Data Diagram
> Written by:   
Reviewed by:

### 4.2 Data Specification
> Written by:   
Reviewed by:

## 5. UI/UX

### 5.1 Screen Diagram
> Written by:   
Reviewed by:

### 5.2 Screen Specifications
> Written by:   
Reviewed by:

## 6. AI Usage Declaration

## 7. Presentation
Video thuyết trình: [LINK]()

## 8. Reflective Report