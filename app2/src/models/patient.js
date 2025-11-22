'use strict';
const { Model } = require('sequelize');

module.exports = (sequelize, DataTypes) => {
  class Patient extends Model {
    static associate(models) {
      Patient.hasMany(models.Payment, { foreignKey: 'patient_id', as: 'payments' });
      Patient.hasMany(models.Invoice, { foreignKey: 'patient_id', as: 'invoices' });
    }
  }
  Patient.init({
    rut: {
      type: DataTypes.STRING,
      allowNull: false,
      unique: true
    },
    nombre: {
      type: DataTypes.STRING,
      allowNull: false
    },
    email: {
      type: DataTypes.STRING,
      allowNull: false,
      validate: {
        isEmail: true
      }
    },
    telefono: DataTypes.STRING,
    direccion: DataTypes.STRING,
    fecha_registro: {
      type: DataTypes.DATE,
      defaultValue: DataTypes.NOW
    }
  }, {
    sequelize,
    modelName: 'Patient',
    tableName: 'patients',
    timestamps: false // Assuming we don't need createdAt/updatedAt for this specific requirement unless specified, but usually good practice. User asked for specific fields. I will stick to user fields + id (auto).
  });
  return Patient;
};
