const { Patient } = require('../models');

const getAllPatients = async () => {
  return await Patient.findAll();
};

const getPatientById = async (id) => {
  return await Patient.findByPk(id);
};

const createPatient = async (data) => {
  return await Patient.create(data);
};

const updatePatient = async (id, data) => {
  const patient = await Patient.findByPk(id);
  if (!patient) return null;
  return await patient.update(data);
};

const deletePatient = async (id) => {
  const patient = await Patient.findByPk(id);
  if (!patient) return null;
  return await patient.destroy();
};

module.exports = {
  getAllPatients,
  getPatientById,
  createPatient,
  updatePatient,
  deletePatient
};
