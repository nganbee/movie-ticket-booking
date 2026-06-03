# Testing

## Table of Contents
1. [Member Contribution Assessment](#1-member-contribution-assessment)
2. [Test plan](#2-test-plan)
3. [Test cases](#3-test-cases)
4. [AI Usage Declaration](#4-ai-usage-declaration)
5. [Presentation](#5-presentation)
6. [Reflective Report](#6-reflective-report)

---

## 1. Member Contribution Assessment

**23120038 - Lê Hoàng Mỹ Hạ - Contribution (25%)**


**23120047 - Nguyễn Gia Huy - Contribution (25%)**


**23120049 - Nguyễn Thanh Huyền - Contribution (25%)**


**23120060 - Trần Kim Ngân - Contribution (25%)**


<p align="center">
  <img 
    src="data/image_template_2/jira.png"
    style="width:100%; height:auto;"
  />
</p>
<p align="center">
  <em>Hình 1: Bảng Jira phân công task</em>
</p>

## 2. Test plan

Hệ thống áp dụng chiến lược kiểm thử hộp đen (Black-box Testing) tập trung chủ yếu vào việc xác minh các chức năng nghiệp vụ và luồng dữ liệu của hệ thống đặt vé phim CineBook. 

* **Đối tượng kiểm thử (Testing Objects):**
  * **Về mặt Chức năng (Functions):** Kiểm thử toàn bộ 5 phân hệ tính năng cốt lõi của hệ thống bao gồm: Quản lý tài khoản (Đăng ký, đăng nhập, phân quyền); Quản lý phim và suất chiếu phía Admin; Tìm kiếm & Bộ lọc phim/suất chiếu; Đặt ghế trực quan theo thời gian thực (Real-time); Thanh toán tích hợp cổng MoMo/VNPAY và Xuất vé điện tử (ETicket) chứa mã QR.
  * **Về mặt Tài liệu (Documents):** Kiểm thử tính đúng đắn, logic của hệ thống dựa trên tài liệu Đặc tả yêu cầu phần mềm (SRS), sơ đồ thiết kế cơ sở dữ liệu (ERD), và các bản thiết kế giao diện người dùng (UI/UX) trên Figma.
* **Kỹ thuật kiểm thử áp dụng (Testing Techniques):**
  * **Kiểm thử phân vùng tương đương (Equivalence Partitioning) & Phân tích giá trị biên (Boundary Value Analysis):** Áp dụng để bắt lỗi và kiểm tra tính hợp lệ của các trường nhập liệu đầu vào (Form validation) như: định dạng Email, độ dài Số điện thoại, tính bảo mật của Mật khẩu, hoặc kiểm tra giới hạn số lượng ghế được chọn trong một giao dịch.
  * **Kiểm thử dựa trên luồng nghiệp vụ (Use Case Testing):** Thiết kế các kịch bản kiểm thử đi hết một vòng quy trình trải nghiệm của khách hàng từ lúc chọn phim, lọc suất chiếu, giữ ghế cho đến khi thực hiện giao dịch thanh toán trực tuyến thành công và nhận vé điện tử.
  * **Kiểm thử chuyển trạng thái (State Transition Testing):** Áp dụng đặc biệt cho logic đặt ghế trực quan real-time (Trạng thái ghế chuyển đổi động giữa Trống - Đang chọn - Đã bán) và trạng thái của hóa đơn đặt vé (Chờ thanh toán - Đã thanh toán - Đã hủy do quá thời gian giữ ghế).
* **Độ bao phủ kiểm thử (Test Coverage):** 
  * Nhóm cam kết thiết kế bộ kiểm thử bao phủ tất cả các kịch bản có thể xảy ra (all possible scenarios) cho từng tính năng cốt lõi được chọn. 
  * Bộ kịch bản không chỉ tập trung vào luồng vận hành thành công (Happy Path), mà còn bao phủ chặt chẽ các luồng ngoại lệ và xử lý lỗi hệ thống (Negative Scenarios) như: chặn trùng lặp tài khoản, chặn Admin xếp trùng lịch phòng chiếu, xử lý xung đột giữ ghế đồng thời giữa hai người dùng, và hoàn tác giải phóng trạng thái ghế khi người dùng chủ động hủy giao dịch hoặc hết thời gian chờ thanh toán (Timeout).

## 3. Test cases

### 3.1 List of test cases

**Danh sách feature chính được chọn để kiểm thử**
1. **Quản lý tài khoản (Account Management):** Xác thực thông tin, phân quyền Admin/Customer và bảo mật đăng nhập.
2. **Quản lý phim và suất chiếu (Movie & Showtime Admin-control):** Luồng Admin thiết lập dữ liệu phim, phòng chiếu và cấu hình khung giờ xem phim.
3. **Tìm kiếm & Bộ lọc (Search & Dynamic Filter):** Khách hàng tìm phim và lọc suất chiếu theo cụm rạp, ngày chiếu thực tế.
4. **Đặt ghế trực quan Real-time (Real-time Seat Selection):** Luồng xử lý tương tác chọn ghế, hủy chọn ghế và đồng bộ trạng thái khóa ghế theo thời gian thực.
5. **Thanh toán & Xuất vé (Payment & Ticketing):** Xử lý giao dịch qua cổng MoMo/VNPAY, cập nhật trạng thái hóa đơn, quản lý thời gian giữ ghế và xuất vé điện tử chứa mã QR.

| Seq | Test case | Feature | Description |
| :--- | :--- | :--- | :--- |
| **TC01** | Đăng ký tài khoản khách hàng thất bại khi trùng Email/SĐT | Quản lý tài khoản | Luồng lỗi: Hệ thống chặn trùng lặp dữ liệu và báo lỗi trực quan. |
| **TC02** | Đăng nhập hệ thống thất bại khi nhập sai mật khẩu | Quản lý tài khoản | Luồng lỗi: Hệ thống chặn truy cập, bảo mật thông tin tài khoản. |
| **TC03** | Đăng nhập tài khoản Admin hệ thống thành công | Quản lý tài khoản | Luồng đúng: Kiểm tra phân quyền truy cập vào trang Dashboard Admin. |
| **TC04** | Admin thêm phim mới thất bại do sai định dạng file poster | Quản lý phim và suất chiếu | Luồng lỗi: Thử tải lên file .docx/.pdf thay vì file ảnh, hệ thống phải chặn. |
| **TC05** | Admin tạo suất chiếu mới thành công cho một bộ phim | Quản lý phim và suất chiếu | Luồng đúng: Xếp lịch chiếu vào một phòng và khung giờ cụ thể hợp lệ. |
| **TC06** | Admin tạo suất chiếu thất bại do trùng lịch phòng chiếu | Quản lý phim và suất chiếu | Luồng lỗi: Xếp lịch mới đè lên khung giờ của phim khác đang chiếu cùng phòng. |
| **TC07** | Tìm kiếm phim hiển thị giao diện trống khi nhập từ khóa vô nghĩa | Tìm kiếm & Bộ lọc | Luồng biên: Nhập chuỗi ký tự lạ, hệ thống báo "Không tìm thấy phim phù hợp". |
| **TC08** | Lọc suất chiếu theo Cụm rạp và Ngày chiếu thành công | Tìm kiếm & Bộ lọc | Luồng đúng: Hiển thị chính xác các khung giờ chiếu hiển thị theo bộ lọc. |
| **TC09** | Chọn ghế trống thành công trên sơ đồ phòng chiếu | Đặt ghế trực quan Real-time | Luồng đúng: Ghế đổi sang màu "Đang chọn" và tính đúng giá tiền tương ứng. |
| **TC10** | Khóa ghế real-time khi có user khác đang nhanh tay giữ trước | Đặt ghế trực quan Real-time | Luồng xung đột: Ngăn chặn tài khoản thứ hai click chọn trùng ghế đang xử lý. |
| **TC11** | Hủy chọn ghế đã chọn (Deselect) thành công | Đặt ghế trực quan Real-time | Luồng đúng: Khách hàng click lại ghế đang chọn, ghế trả về màu trắng, trừ tiền. |
| **TC12** | Khách hàng thanh toán đặt vé thành công qua cổng MoMo/VNPAY | Thanh toán & Xuất vé | Luồng đúng: Trừ tiền chính xác, chuyển trạng thái đơn hàng sang "Đã thanh toán". |
| **TC13** | Khách hàng chủ động hủy giao dịch tại trang thanh toán của bên thứ ba | Thanh toán & Xuất vé | Luồng ngoại lệ: User bấm "Quay lại" tại trang MoMo/VNPAY, hệ thống hoàn tác ghế trống. |
| **TC14** | Tự động hủy giữ ghế khi hết thời gian chờ thanh toán (Timeout) | Thanh toán & Xuất vé | Luồng lỗi hệ thống: Hết thời gian giữ ghế (5-10p) mà chưa thanh toán, ghế tự nhả ra. |
| **TC15** | Kiểm tra xuất vé điện tử (ETicket) thành công kèm mã QR hợp lệ | Thanh toán & Xuất vé | Luồng đúng: Sau khi thanh toán, hệ thống sinh mã QR chứa thông tin ID vé chính xác. |

### 3.2 Test case specifications

Dựa trên ảnh bạn gửi thì **TC01, TC02, TC03 đã có Actual Output cụ thể**, nên mình sẽ cập nhật lại cho đúng với kết quả thực tế thay vì để chung chung.

---

### 3.2.1 TC01 – Đăng ký tài khoản khách hàng thất bại khi trùng Email/SĐT

**Written by:** 23120038 - Lê Hoàng Mỹ Hạ  
**Edited by:**  
**Reviewed by:**  

| Test case           | Content                                                                                                                           |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **Related feature** | Quản lý tài khoản (Account Management)                                                                                            |
| **Context**         | Người dùng đăng ký tài khoản mới bằng Email đã tồn tại trong hệ thống.                                                            |
| **Input Data**      | Họ tên: Nguyễn Văn A <br> Email: [miha@gmail.com](mailto:miha@gmail.com) <br> Mật khẩu: miha1234 <br> Xác nhận mật khẩu: miha1234 |
| **Expected Output** | Hệ thống từ chối tạo tài khoản và hiển thị thông báo lỗi: "Email này đã được sử dụng".                                            |
| **Test steps**      | 1. Mở form Đăng ký. <br> 2. Nhập thông tin hợp lệ nhưng Email đã tồn tại. <br> 3. Nhấn nút "Tạo Tài Khoản".                       |
| **Actual Output**   | Hệ thống hiển thị thông báo lỗi màu đỏ: **"Email này đã được sử dụng"** và không tạo tài khoản mới.                               |
| **Result**          | Passed                                                                                                                            |  

![TC01](data/image_template_3/3.1.1.png)
---

### 3.2.2 TC02 – Đăng nhập hệ thống thất bại khi nhập sai mật khẩu

**Written by:** 23120038 - Lê Hoàng Mỹ Hạ  
**Edited by:**  
**Reviewed by:**  

| Test case           | Content                                                                                                                |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **Related feature** | Quản lý tài khoản (Account Management)                                                                                 |
| **Context**         | Người dùng đã có tài khoản hợp lệ nhưng nhập sai mật khẩu khi đăng nhập.                                               |
| **Input Data**      | Email: [miha@gmail.com](mailto:miha@gmail.com) <br> Mật khẩu: admin123                                                 |
| **Expected Output** | Hệ thống từ chối đăng nhập và hiển thị thông báo lỗi: "Email hoặc mật khẩu không chính xác".                           |
| **Test steps**      | 1. Mở form Đăng nhập. <br> 2. Nhập Email hợp lệ. <br> 3. Nhập mật khẩu không đúng. <br> 4. Nhấn nút "Đăng Nhập".       |
| **Actual Output**   | Hệ thống hiển thị thông báo lỗi màu đỏ: **"Email hoặc mật khẩu không chính xác"** và không cho phép truy cập hệ thống. |
| **Result**          | Passed                                                                                                                 |  
  
![TC01](data/image_template_3/3.1.2.png)
---

### 3.2.3 TC03 – Đăng nhập tài khoản Admin hệ thống thành công

**Written by:** 23120038 - Lê Hoàng Mỹ Hạ  
**Edited by:**  
**Reviewed by:**  

| Test case           | Content                                                                                                                                                                         |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Related feature** | Quản lý tài khoản (Account Management)                                                                                                                                          |
| **Context**         | Quản trị viên đăng nhập bằng tài khoản Admin hợp lệ để truy cập khu vực quản trị.                                                                                               |
| **Input Data**      | Username: [admin@gmail.com](mailto:admin@gmail.com) <br> Password: admin123                                                                                                     |
| **Expected Output** | Hệ thống xác thực thành công và chuyển hướng đến Dashboard Admin.                                                                                                               |
| **Test steps**      | 1. Truy cập trang Admin Login. <br> 2. Nhập Username: [admin@gmail.com](mailto:admin@gmail.com). <br> 3. Nhập Password: admin123. <br> 4. Nhấn nút "Đăng nhập vào Admin Panel". |
| **Actual Output**   | Hệ thống xác thực thành công và điều hướng đến giao diện Dashboard Admin.                                                                                                       |
| **Result**          | Passed                                                                                                                                                                          | 
   
![TC01](data/image_template_3/3.1.3a.png)
![TC01](data/image_template_3/3.1.3b.png)
---

### 3.2.4 TC04 – Admin thêm phim mới thất bại do sai định dạng file poster

**Written by:** 23120038 - Lê Hoàng Mỹ Hạ  
**Edited by:**  
**Reviewed by:**  

| Test case           | Content                                                                                                                                                         |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Related feature** | Quản lý phim và suất chiếu (Movie & Showtime Admin-control)                                                                                                     |
| **Context**         | Quản trị viên thực hiện thêm phim mới nhưng tải lên file poster không phải định dạng hình ảnh hợp lệ.                                                           |
| **Input Data**      | Tên phim: Avengers Endgame <br> Poster: poster.docx hoặc poster.pdf                                                                                             |
| **Expected Output** | Hệ thống từ chối upload file và hiển thị thông báo lỗi định dạng.                                                                                               |
| **Test steps**      | 1. Đăng nhập Admin. <br> 2. Mở chức năng Thêm phim mới. <br> 3. Nhập đầy đủ thông tin phim. <br> 4. Chọn file .pdf hoặc .docx làm poster. <br> 5. Nhấn nút Lưu. |
| **Actual Output**   | Hệ thống chặn thao tác lưu phim và hiển thị thông báo: **"Chỉ chấp nhận file JPG, PNG hoặc JPEG"**.                                                             |
| **Result**          | Passed                                                                                                                                                          |

#### 3.2.5 TC05

#### 3.2.6 TC06

#### 3.2.7 TC07

#### 3.2.8 TC08

#### 3.2.9 TC09

#### 3.2.10 TC10

#### 3.2.11 TC11

#### 3.2.12 TC12

#### 3.2.13 TC13

#### 3.2.14 TC14

#### 3.2.15 TC15

## 4. AI Usage Declaration

## 5. Presentation

## 6. Reflective Report