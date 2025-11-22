const { Payment } = require('../models');

const getPaymentsByPatientId = async (patientId) => {
  return await Payment.findAll({ where: { patient_id: patientId } });
};

const createPayment = async (data) => {
  return await Payment.create(data);
};

module.exports = {
  getPaymentsByPatientId,
  createPayment
};
