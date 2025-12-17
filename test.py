from datetime import datetime
from src.domain.renewal import get_next_monday, calculate_cycle_status

print("=== Test de lógica de renovación ===\n")

# Tu caso real: Compraste el lunes 15 de diciembre de 2025
# Hoy es miércoles 17 de diciembre de 2025
# El próximo recordatorio debería ser el lunes 29 de diciembre de 2025

print("📅 Tu caso: Lunes 15/12/2025")
start = datetime(2025, 12, 15)
next_monday = get_next_monday(start, weeks_ahead=2)
print(f"   Próximo lunes (2 sem): {next_monday.strftime('%A %d/%m/%Y')}")
print(f"   ¿Es lunes 29? {next_monday.day == 29 and next_monday.month == 12}\n")

# Simulación: Primera ejecución después de comprar
print("=== Primera ejecución (K11 vacío) ===")
result1 = calculate_cycle_status(
    start_date=datetime(2025, 12, 15),  # Pusiste en K10 el 15/12
    stored_renewal_date=None             # K11 está vacío
)
print(f"→ Renovación calculada: {result1['new_renewal_date'].strftime('%A %d/%m/%Y')}")
print(f"→ ¿Ha cambiado?: {result1['has_changed']} (debe ser True)\n")

# Simulación: Segunda ejecución (ya guardó el 29)
print("=== Segunda ejecución (K11 = 29/12/2025) ===")
result2 = calculate_cycle_status(
    start_date=datetime(2025, 12, 15),       # K10 sigue siendo 15/12
    stored_renewal_date=datetime(2025, 12, 29)  # K11 ya tiene el 29
)
print(f"→ Renovación calculada: {result2['new_renewal_date'].strftime('%A %d/%m/%Y')}")
print(f"→ ¿Ha cambiado?: {result2['has_changed']} (debe ser False)\n")

# Simulación: Ejecutas el 30 de diciembre (ya pasó el 29)
print("=== Ejecución el 30/12 (nuevo ciclo) ===")
# Aquí internamente hoy = now(), así que simulamos manualmente
# Si hoy >= 29/12, debería calcular nuevo ciclo desde el 29
result3 = calculate_cycle_status(
    start_date=datetime(2025, 12, 15),
    stored_renewal_date=datetime(2025, 12, 29)
)
# Como hoy (17/12) < 29/12, no entra en nuevo ciclo
print(f"→ (Con hoy=17/12) Renovación: {result3['new_renewal_date'].strftime('%A %d/%m/%Y')}")
print(f"→ ¿Es futuro?: {result3['is_future']} (debe ser True porque 29 > 17)")
