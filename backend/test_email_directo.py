#!/usr/bin/env python3
"""
Test rápido de Resend API
Ejecutar: python3 test_email_directo.py
"""

import resend

# Tu nueva API Key
resend.api_key = "re_H8uG4QWK_1Pd7kRoqD7cxgVid6dDGT8UL"

print("=" * 70)
print("[TEST EMAIL] Probando Resend API directamente...")
print("=" * 70)

try:
    response = resend.Emails.send({
        "from": "Andrés - AI Consulting <onboarding@resend.dev>",
        "to": ["franklinnrodriguez83@gmail.com"],
        "subject": "✅ Test Directo - API Key Funciona",
        "html": """
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h1 style="color: #2563eb;">🎉 ¡API Key Válida!</h1>
            <p>Si estás leyendo este email, significa que:</p>
            <ul>
                <li>✅ La API Key <code>re_H8uG4QWK_1Pd7kRoqD7cxgVid6dDGT8UL</code> funciona</li>
                <li>✅ Resend está enviando emails correctamente</li>
                <li>✅ El problema anterior estaba en la API Key inválida</li>
            </ul>
            <p><strong>Próximo paso:</strong> Reinicia tu backend y prueba el sistema completo.</p>
            <hr/>
            <small>Test enviado desde: test_email_directo.py</small>
        </body>
        </html>
        """
    })
    
    print("\n" + "=" * 70)
    print("[TEST SUCCESS] ✅ EMAIL ENVIADO EXITOSAMENTE")
    print("=" * 70)
    print(f"  Response ID: {response.get('id', 'N/A')}")
    print(f"  Response completo: {response}")
    print("\n  🎯 Revisa tu bandeja: franklinnrodriguez83@gmail.com")
    print("  📧 También revisa SPAM/PROMOCIONES si no lo ves")
    print("=" * 70)
    
except Exception as e:
    print("\n" + "=" * 70)
    print("[TEST ERROR] ❌ ERROR AL ENVIAR EMAIL")
    print("=" * 70)
    print(f"  Error type: {type(e).__name__}")
    print(f"  Error message: {str(e)}")
    print("\n  💡 Posibles causas:")
    print("  1. API Key inválida (verifica en https://resend.com/api-keys)")
    print("  2. Límite de envíos excedido (plan gratuito: 100/día)")
    print("  3. Email de destino inválido")
    print("=" * 70)
    import traceback
    traceback.print_exc()
