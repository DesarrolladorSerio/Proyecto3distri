'use strict';

module.exports = {
  async up (queryInterface, Sequelize) {
    await queryInterface.bulkInsert('patients', [
      {
        rut: '11111111-1',
        nombre: 'Juan Perez',
        email: 'juan.perez@example.com',
        telefono: '+56912345678',
        direccion: 'Calle Falsa 123',
        fecha_registro: new Date()
      },
      {
        rut: '22222222-2',
        nombre: 'Maria Gonzalez',
        email: 'maria.gonzalez@example.com',
        telefono: '+56987654321',
        direccion: 'Avenida Siempre Viva 742',
        fecha_registro: new Date()
      },
      {
        rut: '33333333-3',
        nombre: 'Pedro Pascal',
        email: 'pedro.pascal@example.com',
        telefono: '+56911223344',
        direccion: 'Hollywood Blvd 1',
        fecha_registro: new Date()
      }
    ], {});

    const patients = await queryInterface.sequelize.query(
      `SELECT id from patients;`
    );
    const patientRows = patients[0];

    await queryInterface.bulkInsert('invoices', [
      {
        patient_id: patientRows[0].id,
        descripcion: 'Consulta General',
        monto: 50000,
        fecha_emision: new Date(),
        pagada: true
      },
      {
        patient_id: patientRows[1].id,
        descripcion: 'Examen de Sangre',
        monto: 25000,
        fecha_emision: new Date(),
        pagada: false
      }
    ], {});

    await queryInterface.bulkInsert('payments', [
      {
        patient_id: patientRows[0].id,
        monto: 50000,
        fecha: new Date(),
        metodo_pago: 'tarjeta',
        estado: 'completed'
      },
      {
        patient_id: patientRows[1].id,
        monto: 10000,
        fecha: new Date(),
        metodo_pago: 'efectivo',
        estado: 'completed'
      }
    ], {});
  },

  async down (queryInterface, Sequelize) {
    await queryInterface.bulkDelete('payments', null, {});
    await queryInterface.bulkDelete('invoices', null, {});
    await queryInterface.bulkDelete('patients', null, {});
  }
};
