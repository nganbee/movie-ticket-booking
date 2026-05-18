const express = require('express');
const path = require('path');
const expressLayouts = require('express-ejs-layouts');
const routes = require('./src/routes');

const app = express();
const PORT = process.env.PORT || 3000;

// Setup static folder
app.use(express.static(path.join(__dirname, 'public')));

// Setup view engine
app.use(expressLayouts);
app.set('layout', 'layouts/user-layout');
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

// Parse JSON and URL-encoded bodies
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/', routes);

// Start server
app.listen(PORT, () => {
    console.log(`Frontend server is running on http://localhost:${PORT}`);
});
