USE gestion_medica;
-- Poblar tabla de médicos
INSERT INTO medicos (rut, nombre, especialidad, email, telefono, disponible) VALUES
('15555555-5', 'Dr. Juan García', 'Medicina General', 'juan.garcia@hospital.cl', '+56912345678', 1),
('16666666-6', 'Dra. María López', 'Pediatría', 'maria.lopez@hospital.cl', '+56987654321', 1),
('17777777-7', 'Dr. Pedro Martínez', 'Cardiología', 'pedro.martinez@hospital.cl', '+56911223344', 1),
('18888888-8', 'Dra. Ana Silva', 'Dermatología', 'ana.silva@hospital.cl', '+56922334455', 1),
('19999999-9', 'Dr. Carlos Rodríguez', 'Traumatología', 'carlos.rodriguez@hospital.cl', '+56933445566', 1);

-- Poblar tabla de pacientes (si está vacía)
INSERT INTO pacientes (rut, nombre, fecha_nacimiento, email, telefono) VALUES
('11111111-1', 'Juan Pérez', '1990-05-15', 'juan.perez@example.com', '+56912345678'),
('22222222-2', 'María González', '1985-08-22', 'maria.gonzalez@example.com', '+56987654321'),
('33333333-3', 'Pedro Pascal', '1975-04-02', 'pedro.pascal@example.com', '+56911223344')
ON DUPLICATE KEY UPDATE nombre=nombre;

-- Poblar algunas consultas de ejemplo
INSERT INTO consultas (id_paciente, id_medico, fecha, motivo, diagnostico, tratamiento, estado) VALUES
(1, 1, '2024-11-15 10:00:00', 'Malestar general', 'Gripe común', 'Reposo y abundantes líquidos', 'realizada'),
(1, 2, '2024-10-20 14:30:00', 'Control rutinario', 'Paciente sano', 'Ninguno', 'realizada'),
(2, 3, '2024-11-10 09:00:00', 'Dolor de pecho', 'Hipertensión arterial', 'Losartán 50mg', 'realizada'),
(3, 1, '2024-11-05 11:00:00', 'Revisión anual', 'Chequeo preventivo', 'Vitaminas', 'realizada'),
(1, 4, '2024-12-15 15:00:00', 'Manchas en la piel', 'Pendiente', 'Pendiente', 'pendiente');
