const API_URL = 'http://localhost:3002';

// Tabs logic
function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    event.target.classList.add('active');
}

// --- Patients ---
async function loadPatients() {
    try {
        const res = await fetch(`${API_URL}/patients`);
        const patients = await res.json();
        const tbody = document.querySelector('#patientsTable tbody');
        tbody.innerHTML = '';
        patients.forEach(p => {
            tbody.innerHTML += `
                <tr>
                    <td>${p.id}</td>
                    <td>${p.rut}</td>
                    <td>${p.nombre}</td>
                    <td>${p.email}</td>
                    <td>
                        <button onclick="deletePatient(${p.id})" style="background-color: #e74c3c;">Eliminar</button>
                    </td>
                </tr>
            `;
        });
    } catch (e) { console.error(e); alert('Error cargando pacientes'); }
}

document.getElementById('patientForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        rut: document.getElementById('p_rut').value,
        nombre: document.getElementById('p_nombre').value,
        email: document.getElementById('p_email').value,
        telefono: document.getElementById('p_telefono').value,
        direccion: document.getElementById('p_direccion').value
    };
    try {
        const res = await fetch(`${API_URL}/patients`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (res.ok) {
            alert('Paciente creado');
            e.target.reset();
            loadPatients();
        } else {
            const err = await res.json();
            alert('Error: ' + (err.error?.message || 'Desconocido'));
        }
    } catch (e) { console.error(e); }
});

async function deletePatient(id) {
    if (!confirm('¿Estás seguro?')) return;
    try {
        await fetch(`${API_URL}/patients/${id}`, { method: 'DELETE' });
        loadPatients();
    } catch (e) { console.error(e); }
}

// --- Payments ---
async function loadPayments() {
    const id = document.getElementById('search_pay_id').value;
    if (!id) return alert('Ingresa ID de paciente');
    try {
        const res = await fetch(`${API_URL}/payments/${id}`);
        const payments = await res.json();
        const tbody = document.querySelector('#paymentsTable tbody');
        tbody.innerHTML = '';
        payments.forEach(p => {
            tbody.innerHTML += `
                <tr>
                    <td>${p.id}</td>
                    <td>$${p.monto}</td>
                    <td>${p.descripcion || ''}</td>
                    <td>${p.metodo_pago}</td>
                    <td>${new Date(p.fecha).toLocaleDateString()}</td>
                </tr>
            `;
        });
    } catch (e) { console.error(e); alert('Error cargando pagos'); }
}

document.getElementById('paymentForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        patient_id: document.getElementById('pay_patient_id').value,
        monto: document.getElementById('pay_monto').value,
        descripcion: document.getElementById('pay_desc').value,
        metodo_pago: document.getElementById('pay_metodo').value,
        estado: 'completed'
    };
    try {
        const res = await fetch(`${API_URL}/payments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (res.ok) {
            alert('Pago registrado');
            e.target.reset();
        } else {
            alert('Error al registrar pago');
        }
    } catch (e) { console.error(e); }
});

// --- Invoices ---
async function loadInvoices() {
    const id = document.getElementById('search_inv_id').value;
    if (!id) return alert('Ingresa ID de paciente');
    try {
        const res = await fetch(`${API_URL}/invoices/${id}`);
        const invoices = await res.json();
        const tbody = document.querySelector('#invoicesTable tbody');
        tbody.innerHTML = '';
        invoices.forEach(i => {
            tbody.innerHTML += `
                <tr>
                    <td>${i.id}</td>
                    <td>${i.descripcion}</td>
                    <td>$${i.monto}</td>
                    <td>${i.pagada ? '✅' : '❌'}</td>
                </tr>
            `;
        });
    } catch (e) { console.error(e); alert('Error cargando facturas'); }
}

document.getElementById('invoiceForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        patient_id: document.getElementById('inv_patient_id').value,
        descripcion: document.getElementById('inv_desc').value,
        monto: document.getElementById('inv_monto').value,
        pagada: document.getElementById('inv_pagada').checked
    };
    try {
        const res = await fetch(`${API_URL}/invoices`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (res.ok) {
            alert('Factura generada');
            e.target.reset();
        } else {
            alert('Error al generar factura');
        }
    } catch (e) { console.error(e); }
});

// Init
loadPatients();
