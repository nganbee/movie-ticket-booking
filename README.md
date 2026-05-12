# movie-ticket-booking

## Directory Tree
```bash
Cinema-hub/
├── backend/                # API Service
│   ├── src/
│   │   ├── controllers/    # Điều hướng logic (nhận request, trả response)
│   │   ├── models/         # Định nghĩa Schema MongoDB (User, Movie, Ticket...)
│   │   ├── routes/         # Khai báo các endpoint API
│   │   ├── services/       # Xử lý nghiệp vụ (Bulk Insert, tính tiền, Payment)
│   │   ├── middlewares/    # Kiểm tra Token, phân quyền Admin/User
│   │   ├── config/         # Kết nối Database, Redis, Cloudinary
│   │   └── utils/          # Các hàm tiện ích (Format date, Logger)
│   ├── tests/              # Các kịch bản kiểm thử (Unit test)
│   ├── .env                # Biến môi trường (DB_URI, JWT_SECRET)
│   ├── Dockerfile
│   └── package.json
│
├── frontend/               # Web Interface (Node.js + Tailwind)
│   ├── public/             # Tài nguyên tĩnh
│   │   ├── css/            # File style.css (đã compile từ Tailwind)
│   │   ├── js/             # Scripts chạy ở trình duyệt (DOM, Fetch API)
│   │   └── images/         # Logo, Poster, Banner
│   ├── src/
│   │   ├── styles/         # Chứa tailwind.css gốc
│   │   ├── middlewares/    # Chặn truy cập trang Admin nếu không đủ quyền
│   │   ├── routes/         # Quản lý các tuyến đường render giao diện
│   │   ├── services/       # Các hàm gọi API từ Backend sang
│   │   └── utils/          # Format tiền tệ, định dạng ngày tháng
│   ├── views/              # Thư mục chứa template EJS
│   │   ├── layouts/        # Khung giao diện (admin-layout, user-layout)
│   │   ├── user/           # Trang chủ, Chi tiết phim, Đặt vé
│   │   ├── admin/          # Dashboard, Quản lý phim, Xếp lịch
│   │   └── partials/       # Các khối dùng lại (Navbar, Footer, Modal)
│   ├── tailwind.config.js
│   ├── server.js           # Server khởi chạy Frontend
│   ├── Dockerfile
│   └── package.json
│
├── ai-chatbot/             # Module RAG Pipeline (Python)
│   ├── data/               # File dữ liệu text/json để AI học
│   ├── vector_db/          # Lưu trữ chỉ mục Vector (ChromaDB/FAISS)
│   ├── src/
│   │   ├── engine.py       # Logic xử lý LangChain / LlamaIndex
│   │   ├── retriever.py    # Tìm kiếm thông tin từ Database/Vector
│   │   └── main.py         # API phục vụ khung chat (FastAPI)
│   ├── requirements.txt
│   └── Dockerfile
│
├── docs/                   # Tài liệu SRS, API Spec, Database Design
├── docker-compose.yml      # File điều phối chạy tất cả các container
└── README.md
```
