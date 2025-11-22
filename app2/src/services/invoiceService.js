const { Invoice } = require('../models');

const getInvoicesByPatientId = async (patientId) => {
  return await Invoice.findAll({ where: { patient_id: patientId } });
};

const createInvoice = async (data) => {
  return await Invoice.create(data);
};

module.exports = {
  getInvoicesByPatientId,
  createInvoice
};
