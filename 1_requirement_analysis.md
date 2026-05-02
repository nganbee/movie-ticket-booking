# Project Proposal

## Table of Contents
1. [Member Contribution Assessment](#member-contribution-assessment)
2. [Problem Statementt](#problem-statement)
3. [Requirements Overview](#3-proposed-solution)
4. [Requirements Analysis](#4-requirements-analysis)
5. [AI Usage Declaration](#5-ai-usage-declaration)
6. [Presentation](#6-presentation)
7. [Reflective Report](#7-reflective-report)

---

## 1. Member Contribution Assessment

**23120038 - Lê Hoàng Mỹ Hạ - Contribution (100%)**

**23120047 - Nguyễn Gia Huy - Contribution (100%)**

**23120049 - Nguyễn Thanh Huyền - Contribution (100%)**

**23120060 - Trần Kim Ngân - Contribution (100%)**


## 2. Problem Statement
> Written by:  Lê Hoàng Mỹ Hạ   
Reviewed by:


### 2.1 Mô tả nghiệp vụ

Các rạp chiếu phim hiện nay đang đối mặt với áp lực ngày càng tăng khi nhu cầu đặt vé tăng cao và kỳ vọng của khách hàng ngày càng hướng đến sự tiện lợi số. Các phương thức đặt vé truyền thống — tại quầy hoặc qua điện thoại — ngày càng bộc lộ nhiều hạn chế: tạo ra hàng đợi dài vào giờ cao điểm, dễ xảy ra sai sót trong phân công ghế, không cung cấp thông tin tình trạng ghế theo thời gian thực, và thiếu hạ tầng dữ liệu cần thiết để theo dõi doanh thu cũng như hành vi khách hàng một cách hiệu quả.

**CineBook** là hệ thống đặt vé và quản lý rạp chiếu phim trực tuyến dựa trên nền tảng web, được xây dựng nhằm giải quyết toàn diện các hạn chế trên. Hệ thống phục vụ hai nhóm người dùng chính:

**Khách hàng (User)** có thể đăng ký và đăng nhập vào tài khoản cá nhân, xem danh sách phim đang chiếu và sắp chiếu với thông tin chi tiết (nội dung, thể loại, diễn viên, đánh giá), tra cứu lịch chiếu theo ngày và phòng chiếu, và chọn ghế trực quan qua sơ đồ ghế theo thời gian thực. Sau khi xác nhận đặt chỗ, khách hàng tiến hành thanh toán qua mã QR và nhận vé điện tử. Mô-đun lịch sử giao dịch cho phép khách hàng xem lại toàn bộ các lần đặt vé trước đó. Ngoài ra, hệ thống tích hợp **trợ lý AI** được xây dựng trên kiến trúc RAG (Retrieval-Augmented Generation), cho phép chatbot đưa ra gợi ý phim và suất chiếu phù hợp dựa trên sở thích cá nhân và dữ liệu hiện có của hệ thống.

**Quản trị viên (Admin)** có quyền truy cập vào bảng điều khiển quản lý để thực hiện các nghiệp vụ back-office: quản lý kho phim (thêm, sửa, xóa), tạo lịch chiếu hàng loạt trên nhiều phòng chiếu, cấu hình sơ đồ rạp và sắp xếp ghế ngồi, đăng tin tức và nội dung khuyến mãi, theo dõi doanh thu qua mô-đun báo cáo. Các chức năng này giúp giảm thiểu công sức phối hợp thủ công và hỗ trợ ra quyết định kinh doanh dựa trên dữ liệu.

---

### 2.2 Môi trường hoạt động

CineBook được thiết kế dưới dạng **ứng dụng web**, có thể truy cập từ bất kỳ trình duyệt hiện đại nào mà không cần cài đặt phần mềm phía client. Hệ thống vận hành trên các tầng môi trường sau:

| Tầng | Công nghệ |
|---|---|
| **Client** | Trình duyệt hỗ trợ HTML5 (Google Chrome, Microsoft Edge, Mozilla Firefox) |
| **Frontend** | React.js, Tailwind CSS   |
| **Backend / Server** | FastAPI (Python, tương thích ASGI), cung cấp các RESTful API endpoint |
| **Giao tiếp API** | RESTful API qua HTTPS; định dạng trao đổi dữ liệu JSON |
| **Cơ sở dữ liệu** | PostgreSQL (lưu trữ quan hệ cho người dùng, phim, lịch chiếu, giao dịch) |
| **Vector Database** | ChromaDB (phục vụ truy xuất ngữ nghĩa trong pipeline RAG của AI) |
| **AI Runtime** | Ollama (engine chạy LLM cục bộ, triển khai mô hình ngôn ngữ lớn on-premises) |
| **Tài liệu API** | Swagger UI (tự động sinh bởi FastAPI, dùng để đặc tả và kiểm thử API) |

**Yêu cầu phần cứng phía server:**
- CPU: Tối thiểu 4 cores (đáp ứng xử lý đồng thời API và LLM inference)
- RAM: Tối thiểu 16 GB (cần thiết để chạy Ollama/LLM ổn định)
- Lưu trữ: Tối thiểu 20 GB SSD trống (cho model weights, database và tài nguyên media)

**Yêu cầu phía client:**
- Bất kỳ thiết bị nào (máy tính, laptop, điện thoại) có trình duyệt web hiện đại và kết nối internet.

---

### 2.3 Ràng buộc thiết kế & triển khai

Các ràng buộc sau đây chi phối các quyết định thiết kế và lựa chọn triển khai trong suốt dự án:

**Ngôn ngữ lập trình & Framework**
Backend phải được triển khai bằng **Python** sử dụng framework **FastAPI**. Frontend phải được xây dựng bằng **React.js** kết hợp **Tailwind CSS**. Không sử dụng ngôn ngữ hay framework chủ đạo nào khác cho hệ thống core nhằm đảm bảo tính nhất quán trong nhóm phát triển.

**Cơ sở dữ liệu**
Cơ sở dữ liệu quan hệ chính phải là **PostgreSQL**. Toàn bộ dữ liệu ứng dụng — tài khoản người dùng, thông tin phim, lịch chiếu, trạng thái ghế và bản ghi thanh toán — phải được lưu trữ trong schema có cấu trúc, được chuẩn hóa. **ChromaDB** được sử dụng như vector store thứ cấp, phục vụ riêng cho tầng retrieval của trợ lý AI.

**Xử lý đồng thời & Tính toàn vẹn ghế**
Hệ thống phải xử lý các yêu cầu đặt ghế đồng thời mà không cho phép đặt trùng hoặc xung đột. Cơ chế khóa ghế (ví dụ: optimistic locking hoặc database-level transaction) phải được triển khai ở tầng backend để ngăn race condition trong thời điểm lưu lượng cao.

**Bảo mật**
Xác thực người dùng phải được triển khai theo cơ chế chuẩn (ví dụ: xác thực token JWT). Mật khẩu phải được lưu trữ bằng thuật toán băm một chiều (ví dụ: bcrypt). Toàn bộ dữ liệu liên quan đến thanh toán và bản ghi giao dịch phải được bảo vệ khỏi truy cập trái phép.

**Tiêu chuẩn tài liệu API**
Tất cả endpoint backend phải được mô tả đầy đủ và có thể kiểm thử qua **Swagger UI**, được tự động sinh bởi FastAPI. Đặc tả endpoint phải bao gồm schema request/response, yêu cầu xác thực và mã lỗi.

**Thành phần AI**
Trợ lý AI phải được triển khai bằng **Ollama** để chạy LLM cục bộ, theo kiến trúc **RAG**: câu hỏi của người dùng được xử lý bằng cách truy xuất ngữ cảnh liên quan từ dữ liệu nội bộ của hệ thống (qua ChromaDB) trước khi đưa vào mô hình ngôn ngữ. Thiết kế này đảm bảo độ chính xác của phản hồi và ngăn dữ liệu nghiệp vụ nhạy cảm bị gửi ra các dịch vụ AI bên ngoài.

**Kiến trúc module hóa**
Hệ thống phải được thiết kế theo kiến trúc phân tầng, module hóa (3-Tier: Presentation → Logic → Data) để cho phép thay thế hoặc mở rộng độc lập từng thành phần (ví dụ: đổi module thanh toán, nâng cấp mô hình AI, hoặc chuyển sang cloud database) mà không cần viết lại toàn bộ hệ thống.

**Tài liệu dự án**
Toàn bộ tài liệu dự án — bao gồm yêu cầu (SRS), tài liệu thiết kế (ERD, UML, sơ đồ kiến trúc) và kế hoạch kiểm thử — phải tuân theo tiêu chuẩn tài liệu được quy định bởi môn học và lưu trữ trong thư mục `/docs` của repository dự án.

## 3. Requirements Overview

### 3.1 Stakeholders
> Written by:  
Reviewed by:

### 3.2 Requirements
#### 3.2.1 Functional Requirements Specification
> Written by:  
Reviewed by:

#### 3.2.2 Non-Functional Requirements Specification
> Written by:  
Reviewed by:

## 4. Requirements Analysis
### 4.1 Use Case Model
> Written by:  
Reviewed by:

### 4.2 Use Case Specification

#### 4.2.1 User Authentication
> Written by:  
Reviewed by:

#### 4.2.2 Movie Browsing and Search
> Written by:  
Reviewed by:

#### 4.2.3 Seat Selection and Booking
> Written by:  
Reviewed by:

#### 4.2.4 Online Payment Processing
> Written by:  
Reviewed by:

#### 4.2.5 Profile and Booking History Management
> Written by: Lê Hoàng Mỹ Hạ  
Reviewed by:  

---

**1. Đặc tả Use Case**

| Mục                            | Nội dung                                                                                                                                                                                                                                                                                                                                                                                    |
| :----------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Use case ID**                | UC005                                                                                                                                                                                                                                                                                                                                                                                       |
| **Use Case**                   | Quản lý thông tin cá nhân và lịch sử đặt vé                                                                                                                                                                                                                                                                                                                                                 |
| **Brief Description**          | Cho phép người dùng xem, chỉnh sửa thông tin cá nhân, tra cứu lịch sử đặt vé/bắp nước và thực hiện thanh toán các giao dịch chưa hoàn tất.                                                                                                                                                                                                                                                  |
| **Actor**                      | Người dùng (User)                                                                                                                                                                                                                                                                                                                                                                           |
| **Pre-Condition**              | Người dùng đã đăng nhập thành công vào hệ thống.                                                                                                                                                                                                                                                                                                                                            |
| **Result**                     | Thông tin cá nhân được cập nhật hoặc thông tin chi tiết vé/mã thanh toán được hiển thị.                                                                                                                                                                                                                                                                                                     |
| **Main Scenario**              | 1. Người dùng chọn mục **"Tài khoản của tôi"**.<br>2. Hệ thống hiển thị hồ sơ cá nhân và danh sách lịch sử giao dịch (phim, suất chiếu, ghế, bắp nước).<br>3. Vé đã thanh toán: nhấn **"Xem mã QR"** để nhận diện tại rạp.<br>4. Vé chưa thanh toán: nhấn **"Thanh toán ngay (QR)"** để hiển thị mã VietQR.<br>5. Người dùng chỉnh sửa thông tin bằng biểu tượng **bút** và nhấn **"Lưu"**. |
| **Alternative Scenarios**      | **A1. Thông tin không hợp lệ:** Nếu email/số điện thoại sai định dạng, hệ thống hiển thị viền đỏ và thông báo lỗi.<br>**A2. Lịch sử trống:** Nếu chưa có giao dịch, hệ thống hiển thị màn hình trống và nút **"Đặt vé ngay"**.                                                                                                                                                              |
| **Non-Functional Constraints** | - Thời gian truy xuất dữ liệu < 2 giây.<br>- Tích hợp thanh toán VietQR.<br>- Mật khẩu được mã hóa bằng bcrypt trước khi lưu trữ.                                                                                                                                                                                                                                                           |

---

**2. Prototype & Mockups**  
- Link figma: [Profile and Booking History Management](https://www.figma.com/make/TyfblB8AsyicccnM4SzNDb/SE_4.2.5-6?t=zCgvVZksUYXShR4e-20&fullscreen=1)

**2.1 Giao diện chính (Interface)**

Màn hình tổng quan hiển thị thông tin cá nhân và danh sách các vé đã đặt. Vé chưa thanh toán được làm nổi bật với nút hành động.

<p align="center">
  <img src="data/image_template_1/4_2_5/interface_not_payment.png" width="100%"/>
</p>
<p align="center"><em>Hình 4.2.5.1: Giao diện quản lý thông tin cá nhân và lịch sử đặt vé</em></p>

---

**2.2 Thông tin mã QR vé (QR Ticket Information)**

Hiển thị khi người dùng chọn **"Xem mã QR"** đối với vé đã thanh toán thành công. Mã QR được sử dụng để nhận vé và bắp nước tại rạp.

<p align="center">
  <img src="data/image_template_1/4_2_5/qr_information.png" width="100%"/>
</p>
<p align="center"><em>Hình 4.2.5.2: Mã QR vé hiển thị thông tin sau khi thanh toán</em></p>

---

**2.3 Thanh toán QR (QR Payment)**

Hiển thị khi người dùng chọn **"Thanh toán ngay"**. Hệ thống tạo mã VietQR với thông tin thanh toán được điền sẵn.

<p align="center">
  <img src="data/image_template_1/4_2_5/qr_payment.png" width="100%"/>
</p>
<p align="center"><em>Hình 4.2.5.3: Thanh toán vé bằng mã VietQR</em></p>

Kết quả sau khi thanh toán:
  

<p align="center">
  <img src="data/image_template_1/4_2_5/interface_payment.png" width="100%"/>
</p>
<p align="center"><em>Hình 4.2.5.3: Thanh toán vé bằng mã VietQR</em></p>

---

**2.4 Kịch bản A1: Thông tin không hợp lệ (Invalid Information)**

Minh họa trường hợp người dùng nhập sai định dạng thông tin cá nhân. Các trường lỗi được highlight để cảnh báo.

<p align="center">
  <img src="data/image_template_1/4_2_5/invalid_information.png" width="100%"/>
</p>
<p align="center"><em>Hình 4.2.5.4: Hiển thị lỗi khi nhập thông tin không hợp lệ</em></p>

---

**2.5 Kịch bản A2: Lịch sử trống (Empty History)**

Giao diện thân thiện dành cho người dùng chưa có giao dịch, kèm nút điều hướng để bắt đầu đặt vé.

<p align="center">
  <img src="data/image_template_1/4_2_5/empty.png" width="100%"/>
</p>
<p align="center"><em>Hình 4.2.5.5: Giao diện khi chưa có lịch sử giao dịch</em></p>

#### 4.2.6 AI-Powered Movie Recommendation (Chatbot)
> Written by: Lê Hoàng Mỹ Hạ  
Reviewed by:

**1. Đặc tả Use Case**  
| Mục                            | Nội dung                                                                                                                                                                                                                                                                                                                                                                                          |
| :----------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Use case ID**                | UC006                                                                                                                                                                                                                                                                                                                                                                                             |
| **Use Case**                   | Trợ lý AI tư vấn phim và suất chiếu                                                                                                                                                                                                                                                                                                                                                               |
| **Brief Description**          | Người dùng tương tác với chatbot để nhận gợi ý phim dựa trên sở thích cá nhân và dữ liệu thực tế của rạp.                                                                                                                                                                                                                                                                                         |
| **Actor**                      | Người dùng (User / Guest)                                                                                                                                                                                                                                                                                                                                                                         |
| **Pre-Condition**              | Người dùng truy cập vào hệ thống (không bắt buộc đăng nhập).                                                                                                                                                                                                                                                                                                                                      |
| **Result**                     | Chatbot trả lời bằng ngôn ngữ tự nhiên kèm theo các gợi ý phim/suất chiếu phù hợp.                                                                                                                                                                                                                                                                                                                |
| **Main Scenario**              | 1. Người dùng nhập nội dung cần tư vấn *(ví dụ: "Tìm phim hành động chiếu tối nay")*.<br>2. Backend (FastAPI) nhận request và kích hoạt pipeline **RAG**.<br>3. Hệ thống truy vấn **Vector DB (ChromaDB)** để lấy dữ liệu phim và lịch chiếu.<br>4. **Ollama (LLM)** tổng hợp thông tin và sinh câu trả lời.<br>5. Hệ thống hiển thị phản hồi kèm các **movie cards** để người dùng đặt vé nhanh. |
| **Alternative Scenarios**      | **A1. Không tìm thấy phim phù hợp:** AI xin lỗi và gợi ý phim đang hot.<br>**A2. Lỗi hệ thống AI:** Nếu Ollama không phản hồi, hệ thống chuyển sang fallback hoặc hiển thị thông báo *"Chatbot đang bảo trì"*.                                                                                                                                                                                    |
| **Non-Functional Constraints** | - Đảm bảo tính chính xác (không hallucinate dữ liệu lịch chiếu).<br>- Thời gian phản hồi < 3 giây.<br>- Giao diện chat thân thiện, hỗ trợ tiếng Việt tốt.                                                                                                                                                                                                                                         |

---

**2. Prototype & Mockups**
- Link figma: [AI-Powered Movie Recommendation (Chatbot)](https://www.figma.com/make/TyfblB8AsyicccnM4SzNDb/SE_4.2.5-6?t=zCgvVZksUYXShR4e-20&fullscreen=1)  

**2.1 Giao diện chatbot mặc định (Default Chat Interface)**

Giao diện ban đầu khi người dùng mở chatbot, hiển thị các gợi ý truy vấn nhanh giúp tăng trải nghiệm.

<p align="center">
  <img src="data/image_template_1/4_2_6/default_chatbot.png" width="100%"/>
</p>
<p align="center"><em>Hình 4.2.6.1: Giao diện chatbot mặc định với các gợi ý nhanh</em></p>

---

**2.2 Biểu tượng chatbot (Chatbot Icon)**

Biểu tượng nổi (floating button) giúp người dùng truy cập nhanh vào chức năng tư vấn AI từ bất kỳ trang nào.

<p align="center">
  <img src="data/image_template_1/4_2_6/icon_chatbot.png" width="100%"/>
</p>
<p align="center"><em>Hình 4.2.6.2: Biểu tượng chatbot trên giao diện hệ thống</em></p>

---

**2.3 Kịch bản A1: Không tìm thấy phim phù hợp**

Trường hợp người dùng nhập yêu cầu không phù hợp với dữ liệu hiện có, hệ thống sẽ phản hồi thân thiện và đề xuất nội dung thay thế.

<p align="center">
  <img src="data/image_template_1/4_2_6/invalid_information.png" width="100%"/>
</p>
<p align="center"><em>Hình 4.2.6.3: Chatbot phản hồi khi không tìm thấy kết quả phù hợp</em></p>

---

**2.4 Kịch bản A2: Lỗi hệ thống AI**

Khi hệ thống AI (Ollama) không phản hồi, chatbot chuyển sang chế độ fallback và thông báo cho người dùng.

<p align="center">
  <img src="data/image_template_1/4_2_6/error_system.png" width="100%"/>
</p>
<p align="center"><em>Hình 4.2.6.4: Thông báo lỗi khi hệ thống AI không khả dụng</em></p>

---

#### 4.2.7 Movie and Showtime Management (Admin)
> Written by:  
Reviewed by:

#### 4.2.8 Sales Statistics and Reporting (Admin)
> Written by:  
Reviewed by:

## 5. AI Usage Declaration

## 6. Presentation

## 7. Reflective Report