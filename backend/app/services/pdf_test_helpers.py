from datetime import datetime
from app.services.pdf_generator import (
    generate_prescription_pdf,
    generate_medical_certificate_pdf,
    generate_referral_pdf,
    generate_receipt_pdf,
)

def demo_data():
    clinic = {"name": "Clínica Exemplo", "details": "Av. Brasil, 123 - São Paulo/SP"}
    patient = {"name": "João da Silva", "id": "#123", "document": "CPF 000.000.000-00"}
    doctor = {"name": "Maria Souza", "crm": "123456"}
    return clinic, patient, doctor

def build_demo_pdfs() -> dict[str, bytes]:
    clinic, patient, doctor = demo_data()
    outputs = {}

    outputs['prescription'] = generate_prescription_pdf(
        clinic, patient, doctor,
        [
            {"name": "Amoxicilina 500mg", "dosage": "500mg", "frequency": "8/8h", "duration": "7 dias", "notes": "Após as refeições"},
            {"name": "Dipirona 1g", "dosage": "1g", "frequency": "6/6h", "duration": "3 dias"},
        ]
    )

    outputs['certificate'] = generate_medical_certificate_pdf(
        clinic, patient, doctor,
        justification="Paciente em tratamento clínico, necessitando repouso.",
        validity_days=3,
    )

    outputs['referral'] = generate_referral_pdf(
        clinic, patient, doctor, specialty="Cardiologia", reason="Avaliação de dor torácica", urgency="Média"
    )

    outputs['receipt'] = generate_receipt_pdf(
        clinic, patient, doctor,
        services=[
            {"description": "Consulta", "qty": 1, "unit_price": 250.00},
            {"description": "Exame ECG", "qty": 1, "unit_price": 120.00},
        ],
        payments=[
            {"method": "Cartão", "amount": 370.00, "date": datetime.now().strftime('%d/%m/%Y')}
        ]
    )

    return outputs


