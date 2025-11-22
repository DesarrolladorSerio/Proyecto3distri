const express = require('express');
const router = express.Router();
const patientController = require('../controllers/patientController');
const validate = require('../middleware/validation');
const { patientSchema } = require('../middleware/schemas');

router.get('/', patientController.getAllPatients);
router.get('/:id', patientController.getPatientById);
router.post('/', validate(patientSchema), patientController.createPatient);
router.put('/:id', validate(patientSchema), patientController.updatePatient);
router.delete('/:id', patientController.deletePatient);

module.exports = router;
