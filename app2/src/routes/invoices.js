const express = require('express');
const router = express.Router();
const invoiceController = require('../controllers/invoiceController');
const validate = require('../middleware/validation');
const { invoiceSchema } = require('../middleware/schemas');

router.get('/:patientId', invoiceController.getInvoicesByPatientId);
router.post('/', validate(invoiceSchema), invoiceController.createInvoice);

module.exports = router;
