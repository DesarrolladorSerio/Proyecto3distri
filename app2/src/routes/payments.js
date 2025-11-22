const express = require('express');
const router = express.Router();
const paymentController = require('../controllers/paymentController');
const validate = require('../middleware/validation');
const { paymentSchema } = require('../middleware/schemas');

router.get('/:patientId', paymentController.getPaymentsByPatientId);
router.post('/', validate(paymentSchema), paymentController.createPayment);

module.exports = router;
