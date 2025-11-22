const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const errorHandler = require('./src/middleware/errorHandler');
const patientRoutes = require('./src/routes/patients');
const paymentRoutes = require('./src/routes/payments');
const invoiceRoutes = require('./src/routes/invoices');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3002;

// Middleware
app.use(cors());
app.use(morgan('dev'));
app.use(express.json());
app.use(express.static('public')); // Serve static files

// Routes
app.use('/patients', patientRoutes);
app.use('/payments', paymentRoutes);
app.use('/invoices', invoiceRoutes);

// Error Handler
app.use(errorHandler);

// Start server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

module.exports = app;
