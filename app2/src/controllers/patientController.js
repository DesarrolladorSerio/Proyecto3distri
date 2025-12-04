const patientService = require('../services/patientService');

const getAllPatients = async (req, res, next) => {
  try {
    // Si hay query parameter rut, buscar por RUT específico
    if (req.query.rut) {
      const patient = await patientService.getPatientByRut(req.query.rut);
      if (!patient) {
        return res.status(404).json({ error: { message: 'Patient not found', status: 404 } });
      }
      return res.json(patient);
    }
    
    // Si no, retornar todos los pacientes
    const patients = await patientService.getAllPatients();
    res.json(patients);
  } catch (error) {
    next(error);
  }
};

const getPatientById = async (req, res, next) => {
  try {
    const patient = await patientService.getPatientById(req.params.id);
    if (!patient) {
      return res.status(404).json({ error: { message: 'Patient not found', status: 404 } });
    }
    res.json(patient);
  } catch (error) {
    next(error);
  }
};

const createPatient = async (req, res, next) => {
  try {
    const patient = await patientService.createPatient(req.body);
    res.status(201).json(patient);
  } catch (error) {
    next(error);
  }
};

const updatePatient = async (req, res, next) => {
  try {
    const patient = await patientService.updatePatient(req.params.id, req.body);
    if (!patient) {
      return res.status(404).json({ error: { message: 'Patient not found', status: 404 } });
    }
    res.json(patient);
  } catch (error) {
    next(error);
  }
};

const deletePatient = async (req, res, next) => {
  try {
    const result = await patientService.deletePatient(req.params.id);
    if (!result) {
      return res.status(404).json({ error: { message: 'Patient not found', status: 404 } });
    }
    res.status(204).send();
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getAllPatients,
  getPatientById,
  createPatient,
  updatePatient,
  deletePatient
};
