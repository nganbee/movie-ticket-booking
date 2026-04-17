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

### 4.1 Requirements Analysis

### 4.2 Software Design

### 4.3 Implementation

### 4.4 Testing

### 4.5 Deployment and Maintainance


## 5. Human Resources & Costing Plan


## 6. Tools setup
**Written by:** Nguyễn Gia Huy

Một trong những mục tiêu chính của dự án này là rèn luyện kỹ năng làm việc nhóm trong môi trường phát triển phần mềm chuyên nghiệp. Các công cụ dưới đây được nhóm sử dụng để hỗ trợ cộng tác, theo dõi công việc và quản lý mã nguồn.

---

### 6.1 Moodle

Moodle là nền tảng quản lý học tập chính thức của VNU-HCMUS. Tất cả các tài liệu mô tả bài tập, thời hạn nộp, tiêu chí chấm điểm và cổng nộp bài đều được đăng tải trên Moodle.

Mỗi thành viên trong nhóm có trách nhiệm:

Kiểm tra Moodle thường xuyên để cập nhật thông báo
Nộp bài đúng hạn thông qua các đường dẫn được chỉ định

---

### 6.2 Discord

Discord được sử dụng làm nền tảng giao tiếp thời gian thực chính của nhóm.

- Một server Discord riêng có tên **CineBook-Team** đã được tạo. Tất cả thành viên đã tham gia bằng tài khoản cá nhân và bật thông báo
- Server được tổ chức thành các kênh sau:
  - `#general` – Thông báo chung và thảo luận không mang tính kỹ thuật
  - `#dev` – Thảo luận kỹ thuật, review code và quyết định kiến trúc
  - `#design` – Đánh giá UI/UX, chia sẻ link Figma và góp ý mockup
  - `#meeting-notes` – Tổng hợp nội dung các buổi họp và các quyết định đã đưa ra
  - `#jira-updates` – Thông báo tự động từ JIRA về thay đổi trạng thái task và sprint
- Discord có thể sử dụng trên máy tính, trình duyệt và điện thoại. Tất cả thành viên cần:
  - Kiểm tra server ít nhất mỗi ngày một lần
  - Phản hồi tin nhắn trong vòng 24 giờ
---

### 6.3 JIRA

JIRA được sử dụng để lập kế hoạch sprint, theo dõi công việc và giám sát tiến độ trong suốt vòng đời dự án.

- Nhóm sử dụng một bảng dự án duy nhất có tên **CINEBOOK**.
- Công việc được chia thành các **sprint 2 tuần**. Mỗi sprint bao gồm các task được lấy từ product backlog đã được ưu tiên.
- Mỗi task (JIRA Issue) phải bao gồm
  - Tiêu đề và mô tả rõ ràng.
  - Ước lượng story point.
  - Người phụ trách .
  - Hạn hoàn thành và sprint tương ứng.
- Trạng thái của task: **To Do → In Progress → In Review → Done**.
- Lịch sử task trên JIRA (bao gồm ảnh chụp tên task, người phụ trách, trạng thái, ngày giao và ngày hoàn thành) sẽ được dùng làm minh chứng chính để đánh giá đóng góp cá nhân.

---

### 6.4 GitHub

GitHub được sử dụng để quản lý phiên bản, lưu trữ mã nguồn và review code.

- Nhóm sử dụng một repository chung: `https://github.com/nganbee/movie-ticket-booking.git`.
- Nhánh `main` được **protected**: Không cho phép push trực tiếp. Mọi thay đổi phải thông qua **Pull Request** và cần ít nhất 1 người review trước khi merge.
- Mỗi tính năng được phát triển trên **feature branch** theo quy tắc đặt tên: `feature/<jira-issue-id>-short-description` (Ví dụ, `feature/CB-12-seat-selection`).
- Commit messages phải tuân theo chuẩn **Conventional Commits** :
  - `feat:` – Thêm tính năng mới
  - `fix:` – Sửa lỗi
  - `docs:` – Cập nhật tài liệu
  - `test:` – Thêm hoặc chỉnh sửa test
- Cấu trúc repository:

```
cinebook/
├── src/               # Mã nguồn ứng dụng
│   ├── frontend/      # Ứng dụng frontend 
│   └── backend/       # API backend 
├── docs/              # Project documentation
│   ├── management/    # Kế hoạch, báo cáo tuần, báo cáo tiến độ
│   ├── requirements/  # User stories, use cases, tài liệu vision
│   ├── design/        # Kiến trúc, UML, mockup UI
│   └── test/          # Kế hoạch test, test case, báo cáo test
└── pa/                # Bài nộp theo từng giai đoạn
    ├── pa1/
    ├── pa2/
    └── pa3/
```

- Lịch sử commit và hoạt động Pull Request trên GitHub sẽ được sử dụng cùng với JIRA để đánh giá mức độ đóng góp của từng thành viên.

> **Important note:** The effective use of all four tools is a graded criterion. Every team member is expected to contribute actively and consistently to JIRA task updates, GitHub commits, and Discord communication throughout the entire project duration.

---

## 7. AI Usage Declaration


## 8. Presentation


## 9. Reflective Report
