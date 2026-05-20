const express = require('express');
const router = express.Router();

// Mock data
const nowShowing = [
    { id: 1, title: 'Godzilla x Kong: Đế Chế Mới', genre: 'Hành Động, Phiêu Lưu, Giả Tưởng', rating: '6.7', poster: 'https://image.tmdb.org/t/p/w500/tMefBSflR6PGQLvLuPEoBiY14Z.jpg', duration: '115 phút', director: 'Adam Wingard', cast: 'Rebecca Hall, Brian Tyree Henry, Dan Stevens, Kaylee Hottle, Trần Pháp Lai', description: 'Kong và người bảo vệ của anh ta tìm kiếm một hành trình mới để khám phá ra nguồn gốc của anh ta trong Trái Đất Rỗng, trong khi Godzilla phải đối mặt với mối đe dọa mới từ Skar King — kẻ cai trị lực lượng Titan băng giá Shimo đang âm mưu hủy diệt bề mặt Trái Đất.' },
    { id: 2, title: 'Kung Fu Panda 4', genre: 'Hoạt Hình, Hài Hước', rating: '7.5', poster: 'https://image.tmdb.org/t/p/w500/kDp1vUBnMpe8ak4rjgl3cLELqjU.jpg', duration: '94 phút', director: 'Mike Mitchell', cast: 'Jack Black, Awkwafina, Viola Davis', description: 'Po phải huấn luyện một chiến binh mới đảm nhận vai trò Thần Long Đại Hiệp, trong khi một phù thủy độc ác tên là Tắc Kè Hoa nhắm đến việc đánh cắp những kỹ năng kung fu của tất cả các bậc thầy độc ác trước đây.' },
    { id: 3, title: 'Dune: Hành Tinh Cát 2', genre: 'Viễn Tưởng, Phiêu Lưu', rating: '9.0', poster: 'https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2JGjjc9CW.jpg', duration: '166 phút', director: 'Denis Villeneuve', cast: 'Timothée Chalamet, Zendaya, Rebecca Ferguson', description: 'Paul Atreides hợp nhất với Chani và người Fremen trên hành trình báo thù những kẻ đã tiêu diệt gia tộc anh.' },
    { id: 4, title: 'Mai', genre: 'Tâm Lý, Tình Cảm', rating: '8.5', poster: 'https://image.tmdb.org/t/p/w500/yRbD3Dhn0fA1L7A2D3wY1g9qY6I.jpg', duration: '131 phút', director: 'Trấn Thành', cast: 'Phương Anh Đào, Tuấn Trần, Trấn Thành', description: 'Một câu chuyện tình lãng mạn nhưng cũng đầy bi kịch giữa Mai và Dương.' }
];

const comingSoon = [
    { id: 5, title: 'Deadpool & Wolverine', genre: 'Hành Động, Hài Hước', releaseDate: '26/07/2024', poster: 'https://image.tmdb.org/t/p/w500/8cdWjvZQUExUUTzyp4t6EDMubfO.jpg' },
    { id: 6, title: 'Furiosa: Câu Chuyện TỪ Mad Max', genre: 'Hành Động, Phiêu Lưu', releaseDate: '24/05/2024', poster: 'https://image.tmdb.org/t/p/w500/iADOJ8Zymht2JPMoy3R7xceZprc.jpg' },
    { id: 7, title: 'Inside Out 2', genre: 'Hoạt Hình, Gia Đình', releaseDate: '14/06/2024', poster: 'https://image.tmdb.org/t/p/w500/vpnVM9B6NMmQpWeZvzLvDESb2QY.jpg' },
    { id: 8, title: 'Hành Tinh Khỉ: Vương Quốc Mới', genre: 'Viễn Tưởng, Hành Động', releaseDate: '10/05/2024', poster: 'https://image.tmdb.org/t/p/w500/gKkl37BQuKTanygYQG1pyYgLVgf.jpg' }
];

// Home page
router.get('/', (req, res) => {
    res.render('user/home', { 
        title: 'CineBook - Trang chủ',
        nowShowing,
        comingSoon,
        hideNavbar: false
    });
});

// Movie Detail
router.get('/movie/:id', (req, res) => {
    const movieId = parseInt(req.params.id);
    const movie = nowShowing.find(m => m.id === movieId) || comingSoon.find(m => m.id === movieId);
    
    if (!movie) {
        return res.status(404).send('Movie not found');
    }

    res.render('user/movie-detail', {
        title: `${movie.title} - CineBook`,
        movie,
        hideNavbar: false
    });
});

// Auth Routes (Mock API for modal)
router.post('/login', (req, res) => {
    // Return mock success/failure if needed, but since we do client-side validation
    // and navigation, we don't strict require this anymore.
    // For demo purposes, we can just redirect to Home.
    res.redirect('/');
});

// Find your existing path rule inside src/routes/index.js and swap it:
router.get('/booking/:showtimeId', (req, res) => {
  // Pulling the showtimeId placeholder argument from URL safely
  const showtimeId = req.params.showtimeId;
  
  // Render your newly created seat-selection template mockup file
  res.render('user/seat-selection', { 
    title: 'Select Your Seats',
    showtimeId: showtimeId 
  });
});

// Inside src/routes/index.js
router.get('/checkout/:bookingId', (req, res) => {
  const bookingId = req.params.bookingId;
  
  // Renders the views/user/checkout.ejs template file
  res.render('user/checkout', {
    title: 'Payment Checkout',
    bookingId: bookingId
  });
});

// Receipt Page
router.get('/receipt/:bookingId', (req, res) => {
  const bookingId = req.params.bookingId;
  
  // Renders the views/user/receipt.ejs template file
  res.render('user/receipt', {
    title: 'Booking Confirmed - CineBook',
    bookingId: bookingId
  });
});

// Profile Page
router.get('/profile', (req, res) => {
  res.render('user/profile', {
    title: 'Thông tin cá nhân & Lịch sử đặt vé - CineBook',
    hideNavbar: false
  });
});

module.exports = router;
