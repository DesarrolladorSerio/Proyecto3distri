const Joi = require('joi');

const patientSchema = Joi.object({
  rut: Joi.string().required(),
  nombre: Joi.string().required(),
  email: Joi.string().email().required(),
  telefono: Joi.string().allow(null, ''),
  direccion: Joi.string().allow(null, '')
});

const paymentSchema = Joi.object({
  patient_id: Joi.number().integer().required(),
  monto: Joi.number().positive().required(),
  metodo_pago: Joi.string().required(),
  estado: Joi.string().default('completed')
});

const invoiceSchema = Joi.object({
  patient_id: Joi.number().integer().required(),
  descripcion: Joi.string().allow(null, ''),
  monto: Joi.number().positive().required(),
  pagada: Joi.boolean().default(false)
});

module.exports = {
  patientSchema,
  paymentSchema,
  invoiceSchema
};
