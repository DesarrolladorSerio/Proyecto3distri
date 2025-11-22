const invoiceService = require('../services/invoiceService');

const getInvoicesByPatientId = async (req, res, next) => {
  try {
    const invoices = await invoiceService.getInvoicesByPatientId(req.params.patientId);
    res.json(invoices);
  } catch (error) {
    next(error);
  }
};

const createInvoice = async (req, res, next) => {
  try {
    const invoice = await invoiceService.createInvoice(req.body);
    res.status(201).json(invoice);
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getInvoicesByPatientId,
  createInvoice
};
