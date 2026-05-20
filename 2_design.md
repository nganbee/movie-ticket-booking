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
> Written by: 23120060 - Trần Kim Ngân   
Reviewed by:

<p align="center">
  <img 
    src="data/image_template_2/2/CineBook_Conceptual_MOdel.png"
    style="width:80%; height:auto;"
  />
</p>

### 1. Mô tả chi tiết các Thực thể
* **Theater:** Đại diện cho một chi nhánh rạp phim.
* **Room:** Đại diện cho một phòng chiếu cụ thể bên trong một rạp. Mỗi phòng sẽ có một sức chứa ghế cố định.
* **Seat:** Đại diện cho từng vị trí ghế ngồi vật lý riêng biệt bên trong một phòng chiếu, có nhiều loại ghế (Ghế thường, ghế VIP) tuỳ vào từng phòng chiếu.
* **Movie:** Đại diện cho một bộ phim đã được cấp phép bản quyền để trình chiếu trong toàn bộ chuỗi rạp.
* **Showtime:** Đại diện cho một khung giờ chiếu cụ thể được lên lịch cho một bộ phim tại một phòng chiếu nhất định.
* **User (Người dùng):** Đại diện cho khách hàng đã đăng ký tài khoản và tương tác với hệ thống để thực hiện đặt vé.
* **Admin:** Đại diện cho người vận hành hệ thống, quản lý phim, suất chiếu và doanh thu của rạp.
* **Booking:** Đại diện cho một giao dịch giữ chỗ thành công của khách hàng cho các vị trí ghế cụ thể trong một suất chiếu, bao gồm cả thông tin trạng thái thanh toán.

### 2. Phân tích Mối quan hệ:
* **Theater sở hữu Room (Mối quan hệ 1:N):** Một rạp chiếu có thể có nhiều phòng chiếu phim bên trong, nhưng mỗi phòng chiếu bắt buộc chỉ thuộc về quản lý của một rạp duy nhất.
* **Room chứa Seat (Mối quan hệ 1:N):** Một phòng chiếu sẽ chứa nhiều chiếc ghế ngồi vật lý. Mỗi chiếc ghế ngồi được gắn cố định với duy nhất một phòng chiếu.
* **Room tổ chức Showtime (Mối quan hệ 1:N):** Một phòng chiếu có thể tổ chức nhiều suất chiếu nối đuôi nhau trong suốt cả ngày, nhưng một suất chiếu cụ thể chỉ được phép diễn ra tại một phòng chiếu duy nhất.
* **Movie có các Showtime (Mối quan hệ 1:N):** Một bộ phim có thể được xếp lịch vào nhiều suất chiếu khác nhau để phục vụ khán giả, nhưng mỗi suất chiếu tại một thời điểm chỉ phát duy nhất một bộ phim.
* **User thực hiện Booking (Mối quan hệ 1:N):** Một khách hàng có thể thực hiện nhiều giao dịch đặt vé khác nhau theo thời gian, nhưng mỗi đơn đặt vé chỉ thuộc sở hữu của duy nhất một tài khoản người dùng.
* **Booking bao gồm Seat (Mối quan hệ 1:N):** Một giao dịch đặt vé của khách hàng có thể bao gồm một hoặc nhiều chiếc ghế được chọn cùng lúc (Ví dụ: Đặt vé theo nhóm, đi xem phim theo cặp). Các chiếc ghế này sẽ được khóa trạng thái đi kèm với mã đơn đặt vé đó trong suốt suất chiếu diễn ra.
* **Admin (Mối quan hệ 1:N):** Quản trị viên có thể tạo và quản lý nhiều Phim (`Movie`), nhiều Suất chiếu (`Showtime`) trên hệ thống.

## 3. Architectural Design

### 3.1 Architecture Diagram
> Written by: 23120038 - Lê Hoàng Mỹ Hạ  
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
> Written by: Nguyễn Thanh Huyền - 23120049  
Reviewed by:
   
<img width="3053" height="2957" alt="Article Manager Class Diagram (2)" src="https://github.com/user-attachments/assets/cad83c95-1a8d-4fb7-88b8-bfd2765bfe48" />  

### 3.3 Class Specifications
> Written by:   
Reviewed by:

## 4. Data Design

### 4.1 Data Diagram
> Written by: 23120060 - Trần Kim Ngân  
Reviewed by: 23120047 - Nguyễn Gia Huy


<p align="center">
  <img 
    src="data/image_template_2/2/data_diagram.jpg"
    style="width:80%; height:auto;"
  />
</p>


### 4.2 Data Specification
> Written by: 23120047 - Nguyễn Gia Huy     
Reviewed by: 23120060 - Trần Kim Ngân  


### Bảng `Theater` (Cụm rạp)
*Ý nghĩa:* Quản lý thông tin các chi nhánh rạp phim trong chuỗi hệ thống CineBook.

| Tên thuộc tính| Kiểu dữ liệu | Ràng buộc khóa | Ràng buộc giá trị | Giải thích thuộc tính|
| :--- | :--- | :--- | :--- | :--- |
| `theater_id` | SERIAL | PK | NOT NULL, UNIQUE | Mã định danh tự động tăng của cụm rạp. |
| `name` | TEXT | Không | NOT NULL | Tên hiển thị của cụm rạp (Ví dụ: CineBook Nguyễn Du). |
| `address` | TEXT | Không | NOT NULL | Địa chỉ vật lý chi tiết của rạp. |

---

### Bảng `Room` (Phòng chiếu)
*Ý nghĩa:* Quản lý các phòng chiếu phim vật lý thuộc một cụm rạp cụ thể.

| Tên thuộc tính| Kiểu dữ liệu | Ràng buộc khóa | Ràng buộc giá trị | Giải thích thuộc tính|
| :--- | :--- | :--- | :--- | :--- |
| `room_id` | SERIAL | PK | NOT NULL, UNIQUE | Mã định danh tự động tăng của phòng chiếu. |
| `theater_id` | SERIAL | FK | NOT NULL, Refs `Theater(theater_id)` | Xác định phòng chiếu này thuộc cụm rạp nào. |
| `name` | TEXT | Không | NOT NULL | Tên phòng chiếu (Ví dụ: 'Phòng 01', 'IMAX 3D'). |
| `seat_capacity` | INT | Không | NOT NULL, > 0 | Tổng số lượng ghế tối đa mà phòng chứa được. |

---

### Bảng `Seat` (Ghế ngồi cố định)
*Ý nghĩa:* Định nghĩa sơ đồ vị trí ghế vật lý tĩnh bên trong từng phòng chiếu (Sơ đồ cứng).

| Tên thuộc tính| Kiểu dữ liệu | Ràng buộc khóa | Ràng buộc giá trị | Giải thích thuộc tính|
| :--- | :--- | :--- | :--- | :--- |
| `seat_id` | SERIAL | PK | NOT NULL, UNIQUE | Mã định danh tự động tăng của chiếc ghế vật lý. |
| `room_id` | SERIAL | FK | NOT NULL, Refs `Room(room_id)` | Xác định ghế này nằm cố định ở phòng nào. |
| `seat_row` | CHAR(2) | Không | NOT NULL | Ký hiệu hàng ghế (Ví dụ: 'A', 'B', 'K'). |
| `seat_num` | INT | Không | NOT NULL, > 0 | Số thứ tự của ghế trên hàng đó (Ví dụ: 1, 2, 11). |
| `seat_type` | TEXT | Không | NOT NULL, DEFAULT 'Standard' | Phân loại phân khúc ghế ('Standard', 'VIP', 'Double'). |

---

### Bảng `Movie` (Phim)
*Ý nghĩa:* Kho dữ liệu lưu trữ thông tin các bộ phim được trình chiếu tại rạp.

| Tên thuộc tính| Kiểu dữ liệu | Ràng buộc khóa | Ràng buộc giá trị | Giải thích thuộc tính|
| :--- | :--- | :--- | :--- | :--- |
| `movie_id` | SERIAL | PK | NOT NULL, UNIQUE | Mã định danh tự động tăng của bộ phim. |
| `title` | TEXT | Không | NOT NULL | Tên của bộ phim. |
| `duration` | INT | Không | NOT NULL, > 0 | Thời lượng của phim (Tính bằng phút). |
| `genre` | TEXT | Không | Cho phép NULL | Thể loại phim (Hành động, Hài, Kinh dị...). |
| `language` | TEXT | Không | NOT NULL | Ngôn ngữ phim (Phụ đề tiếng Việt, Lồng tiếng...). |
| `release_date` | DATE | Không | Cho phép NULL | Ngày bộ phim chính thức khởi chiếu. |
| `poster_url` | TEXT | Không | Cho phép NULL | Đường dẫn URL đến hình ảnh poster của phim. |
| `director` | TEXT | Không | Cho phép NULL | Tên đạo diễn bộ phim. |

---

### Bảng `Showtime` (Suất chiếu)
*Ý nghĩa:* Lịch chiếu cụ thể của một bộ phim tại một phòng chiếu vào một khung giờ nhất định.

| Tên thuộc tính| Kiểu dữ liệu | Ràng buộc khóa | Ràng buộc giá trị | Giải thích thuộc tính |
| :--- | :--- | :--- | :--- | :--- |
| `showtime_id` | SERIAL | PK | NOT NULL, UNIQUE | Mã định danh tự động tăng của suất chiếu. |
| `movie_id` | SERIAL | FK | NOT NULL, Refs `Movie(movie_id)` | Xác định suất chiếu này phát bộ phim nào. |
| `room_id` | SERIAL | FK | NOT NULL, Refs `Room(room_id)` | Xác định suất chiếu diễn ra tại phòng nào. |
| `start_time` | TIMESTAMPTZ | Không | NOT NULL | Thời gian bắt đầu suất chiếu (Bao gồm múi giờ). |
| `end_time` | TIMESTAMPTZ | Không | NOT NULL | Thời gian dự kiến kết thúc suất chiếu. |

---

### Bảng `ShowSeat` (Trạng thái ghế theo suất)
*Ý nghĩa:* Quản lý trạng thái động (Trống/Đang giữ/Đã bán) của từng chiếc ghế trong từng suất chiếu cụ thể.

| Tên thuộc tính| Kiểu dữ liệu | Ràng buộc khóa | Ràng buộc giá trị | Giải thích thuộc tính|
| :--- | :--- | :--- | :--- | :--- |
| `show_seat_id`| SERIAL | PK | NOT NULL, UNIQUE | Mã định danh tự động tăng trạng thái ghế theo suất. |
| `showtime_id` | SERIAL | FK | NOT NULL, Refs `Showtime(showtime_id)`| Thuộc về suất chiếu cụ thể nào. |
| `seat_id` | SERIAL | FK | NOT NULL, Refs `Seat(seat_id)` | Gắn với chiếc ghế vật lý cố định nào. |
| `booking_id` | SERIAL | FK | Cho phép NULL | Mã đơn hàng liên kết sau khi đặt thành công (Nối sang bảng Booking). |
| `status` | TEXT | Không | NOT NULL, DEFAULT 'Available' | Trạng thái ghế hiện tại ('Available', 'Holding', 'Sold'). |

## 5. UI/UX

### 5.1 Screen Diagram
> Written by: Nguyễn Thanh Huyền  
Reviewed by:  
  
<img width="1572" height="1120" alt="flow (1)" src="https://github.com/user-attachments/assets/365e0280-6860-4df7-bb72-57319eae1f09" />  
    
### 5.2 Screen Specifications
> Written by:   
Reviewed by:

## 6. AI Usage Declaration

## 7. Presentation
Video thuyết trình: [LINK]()

## 8. Reflective Report
