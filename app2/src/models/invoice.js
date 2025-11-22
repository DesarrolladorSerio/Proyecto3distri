'use strict';
const { Model } = require('sequelize');

module.exports = (sequelize, DataTypes) => {
  class Invoice extends Model {
    static associate(models) {
      Invoice.belongsTo(models.Patient, { foreignKey: 'patient_id', as: 'patient' });
    }
  }
  Invoice.init({
    patient_id: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: {
        model: 'patients',
        key: 'id'
      }
    },
    descripcion: DataTypes.STRING,
    monto: {
      type: DataTypes.DECIMAL(10, 2),
      allowNull: false
    },
    fecha_emision: {
      type: DataTypes.DATE,
      defaultValue: DataTypes.NOW
    },
    pagada: {
      type: DataTypes.BOOLEAN,
      defaultValue: false
    }
  }, {
    sequelize,
    modelName: 'Invoice',
    tableName: 'invoices',
    timestamps: false
  });
  return Invoice;
};
