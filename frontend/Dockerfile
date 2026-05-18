FROM node:20-alpine

# Cài đặt thư mục làm việc trong container
WORKDIR /app

# Copy các file quản lý thư viện vào trước để tận dụng cache của Docker
COPY package*.json ./

# Cài đặt các thư viện Node.js
RUN npm install

# Copy toàn bộ mã nguồn vào container
COPY . .

# Biên dịch Tailwind CSS để tạo ra file style.css tĩnh
RUN npm run build:css

# Mở cổng 3000 để giao tiếp với bên ngoài
EXPOSE 3000

# Lệnh khởi chạy server khi container bắt đầu
CMD ["npm", "start"]
