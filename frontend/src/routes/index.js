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
            fetch(`${API_BASE_URL}/movies/?status=now_showing&limit=100`),
            fetch(`${API_BASE_URL}/movies/?status=coming_soon&limit=100`)
        ]);
        if (nowShowingRes.ok) {
            const data = await nowShowingRes.json();
            // Backend trả về { items: [...], total, ... } sau khi thêm phân trang
            nowShowing = (data.items ?? data).map(mapMovie);
        }
        if (comingSoonRes.ok) {
            const data = await comingSoonRes.json();
            comingSoon = (data.items ?? data).map(mapMovie);
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

// Movie Filter / Browse page
router.get('/movies', async (req, res) => {
    res.render('user/movies', {
        title: 'Tất Cả Phim - CineBook',
        hideNavbar: false
    });
});

// API Proxy: Trả về danh sách phim từ backend cho client-side fetch
router.get('/api/movies', async (req, res) => {
    try {
        // Chuyển tiếp các query params (status, genre, page, limit) sang backend
        const params = new URLSearchParams();
        if (req.query.status) params.append('status', req.query.status);
        if (req.query.genre)  params.append('genre',  req.query.genre);
        if (req.query.page)   params.append('page',   req.query.page);
        if (req.query.limit)  params.append('limit',  req.query.limit);

        const url = `${API_BASE_URL}/movies/${params.toString() ? '?' + params.toString() : ''}`;
        const response = await fetch(url);

        if (!response.ok) {
            return res.status(response.status).json({ error: 'Backend error' });
        }

        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error('Error proxying /api/movies:', error);
        res.status(500).json({ error: 'Không thể kết nối tới backend' });
    }
});

// ── Admin Routes ──────────────────────────────────────────────────────────────
// Admin Login
router.get('/admin/login', (req, res) => {
    res.render('admin/login', { layout: false, error: null, username: '' });
});

router.post('/admin/login', (req, res) => {
    const { username, password } = req.body;
    if (username === 'admin@gmail.com' && password === 'admin123') {
        res.redirect('/admin/dashboard');
    } else {
        res.render('admin/login', { layout: false, error: 'Tên đăng nhập hoặc mật khẩu không chính xác.', username });
    }
});

// Admin Dashboard
router.get('/admin/dashboard', (req, res) => {
    res.render('admin/dashboard', {
        layout: 'layouts/admin-layout',
        title: 'Admin Dashboard - CineBook',
        pageTitle: 'Dashboard',
        currentPage: 'dashboard'
    });
});

// API Proxy: Analytics Dashboard (chuyển tiếp token admin từ client)
router.get('/api/admin/dashboard', async (req, res) => {
    try {
        const authHeader = req.headers['authorization'] || '';
        const response = await fetch(`${API_BASE_URL}/analytics/dashboard`, {
            headers: { 'Authorization': authHeader }
        });
        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            return res.status(response.status).json(err);
        }
        res.json(await response.json());
    } catch (error) {
        console.error('Error proxying /api/admin/dashboard:', error);
        res.status(500).json({ error: 'Không thể kết nối tới backend' });
    }
});

// API Proxy: News Management
router.all('/api/admin/news*', async (req, res) => {
    try {
        const authHeader = req.headers['authorization'] || '';
        const path = req.originalUrl.replace('/api/admin/news', ''); // vd: /1?type=Tin Phim
        
        const options = {
            method: req.method,
            headers: { 
                'Authorization': authHeader,
                'Content-Type': 'application/json'
            }
        };
        
        if (req.method !== 'GET' && req.method !== 'HEAD' && Object.keys(req.body || {}).length > 0) {
            options.body = JSON.stringify(req.body);
        }

        const response = await fetch(`${API_BASE_URL}/news${path}`, options);
        if (response.status === 204) {
             return res.status(204).send();
        }
        
        const data = await response.json().catch(() => ({}));
        res.status(response.status).json(data);
    } catch (error) {
        console.error('Error proxying /api/admin/news:', error);
        res.status(500).json({ error: 'Không thể kết nối tới backend' });
    }
});

// Admin News Management
router.get('/admin/news', (req, res) => {
    res.render('admin/news-management', {
        layout: 'layouts/admin-layout',
        title: 'Quản lý Tin Tức - CineBook',
        pageTitle: 'Tin Tức & Khuyến Mãi',
        currentPage: 'news'
    });
});

// Admin Bulk Showtime Tool
router.get('/admin/bulk-showtime', (req, res) => {
    res.render('admin/bulk-showtime', {
        layout: 'layouts/admin-layout',
        title: 'Tạo Lịch Chiếu Hàng Loạt - CineBook',
        pageTitle: 'Tạo Lịch Chiếu Hàng Loạt',
        currentPage: 'bulk-showtime'
    });
});

// Redirect /admin to login
router.get('/admin', (req, res) => {
    res.redirect('/admin/login');
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
