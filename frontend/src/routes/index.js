const express = require('express');
const router = express.Router();

const API_BASE_URL = 'http://localhost:8000';

const mapMovie = (m) => ({
    id: m.movie_id,
    title: m.title,
    genre: m.genre,
    rating: m.imdb_rating ? m.imdb_rating.toFixed(1) : 'N/A', // Lấy rating thực tế từ Backend
    poster: m.poster_url || 'https://via.placeholder.com/500x750?text=No+Poster',
    duration: `${m.duration} phút`,
    director: m.director,
    cast: 'Đang cập nhật...',
    description: m.description,
    releaseDate: m.release_date ? new Date(m.release_date).toLocaleDateString('vi-VN') : 'Đang cập nhật'
});

// Home page
router.get('/', async (req, res) => {
    let nowShowing = [];
    let comingSoon = [];
    try {
        const [nowShowingRes, comingSoonRes] = await Promise.all([
            fetch(`${API_BASE_URL}/movies/?status=now_showing`),
            fetch(`${API_BASE_URL}/movies/?status=coming_soon`)
        ]);
        if (nowShowingRes.ok) {
            const data = await nowShowingRes.json();
            nowShowing = data.map(mapMovie);
        }
        if (comingSoonRes.ok) {
            const data = await comingSoonRes.json();
            comingSoon = data.map(mapMovie);
        }
    } catch (error) {
        console.error("Error fetching movies from backend:", error);
    }

    res.render('user/home', { 
        title: 'CineBook - Trang chủ',
        nowShowing,
        comingSoon,
        hideNavbar: false
    });
});

// Movie Detail
router.get('/movie/:id', async (req, res) => {
    const movieId = req.params.id;
    try {
        const response = await fetch(`${API_BASE_URL}/movies/${movieId}`);
        if (response.ok) {
            const data = await response.json();
            const movie = mapMovie(data);
            return res.render('user/movie-detail', {
                title: `${movie.title} - CineBook`,
                movie,
                hideNavbar: false
            });
        } else {
            return res.status(404).send('Phim không tồn tại');
        }
    } catch (error) {
        console.error("Error fetching movie detail:", error);
        return res.status(500).send('Lỗi kết nối tới máy chủ Backend');
    }
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
