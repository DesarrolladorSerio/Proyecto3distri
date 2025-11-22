const paymentService = require('../services/paymentService');

const getPaymentsByPatientId = async (req, res, next) => {
  try {
    const payments = await paymentService.getPaymentsByPatientId(req.params.patientId);
    res.json(payments);
  } catch (error) {
    next(error);
  }
};

const createPayment = async (req, res, next) => {
  try {
    const payment = await paymentService.createPayment(req.body);
    res.status(201).json(payment);
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getPaymentsByPatientId,
  createPayment
};
