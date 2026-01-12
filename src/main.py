import time
from datetime import datetime

# Importamos nuestros módulos
from config import settings
from services import scraper, sheets, calendar, notifier
from domain import parser, rules, renewal


def timestamp():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")


def run():
    print(f"{timestamp()} 🚀 Iniciando ejecución...")

    # 1. Obtener RSS (Service)
    raw_entries, was_blocked = scraper.get_rss_feed(settings.RSS_URL)
    
    if was_blocked:
        print("🚨 IP bloqueada por Akamai/Cloudflare")
        notifier.notify_blocked()
        return
    
    if not raw_entries:
        print("⚠️ No se obtuvieron datos del RSS.")
        notifier.notify_error("No se obtuvieron datos del RSS. Posible problema con la web o el formato.")
        return

    # 2. Conectar a Sheets (Service)
    try:
        sheet, creds = sheets.get_sheet_client()
        existing_dates = sheet.col_values(1)  # Columna A
    except Exception as e:
        print(f"❌ Error conectando a Google Sheets: {e}")
        return

    # 3. Procesar Sorteos (Domain loop)
    new_entries_added = 0
    for entry in raw_entries:
        try:
            # Parseo (Domain) - ahora incluye tabla de premios
            date_obj, numbers, bonus, reintegro, prizes = parser.parse_result(entry)
            # Formato: día sin cero, mes con cero (como lo muestra Sheets)
            date_str = f"{date_obj.day}/{date_obj.month:02d}/{date_obj.year}"

            # Verificar si ya existe
            if date_str in existing_dates:
                print(f"⏭️  Sorteo del {date_str} ya existe.")
                continue

            # Calcular premios (Domain)
            matches = rules.calculate_match(numbers)
            bonus_match = bonus in settings.MY_NUMBERS
            reintegro_match = reintegro == settings.REINTEGRO

            prize_type = rules.set_prize(matches, bonus_match, reintegro_match)
            
            # Obtener importe real del premio desde la tabla del RSS
            prize_amount_str = prizes.get(prize_type, "0,00 €")
            prize_amount = parser.parse_prize_amount(prize_amount_str)

            # Preparar fila para guardar (fecha como texto para que la comparación funcione)
            new_row = [
                date_str,  # Fecha como "10/01/2026" (no serial) para comparación correcta
                " - ".join(map(str, sorted(numbers))),
                bonus,
                reintegro,
                matches,
                prize_type,
                prize_amount,  # Importe real del premio
                1.0
            ]

            # Añadir al final de la tabla A:H (sin afectar columnas J-K)
            sheets.append_sorteo_row(sheet, new_row)
            print(f"✅ Guardado sorteo del {date_str}")
            
            # Notificar si hay premio (3+ aciertos)
            if matches >= 3:
                print(f"🎉 ¡PREMIO! {prize_type} - {prize_amount_str}")
                notifier.notify_prize(date_str, prize_type, prize_amount_str, matches)
            
            new_entries_added += 1
            time.sleep(1)  # Pausa de cortesía

        except ValueError as e:
            print(f"⚠️ Error procesando entrada: {e}")
        except Exception as e:
            print(f"❌ Error inesperado en el bucle: {e}")

    # Solo ordenar si se añadieron entradas nuevas
    if new_entries_added > 0:
        print(f"{timestamp()} 🔽 Ordenando hoja por fecha descendente...")
        # Ordenar solo el rango de datos (A2:H + última fila con datos)
        last_row = len(sheet.col_values(1))
        if last_row > 1:
            sort_range = f"A2:H{last_row}"
            sheet.sort((1, 'des'), range=sort_range)

    # 4. Gestión de Renovación (lee/escribe en K18:K19, crea evento en Calendar)
    try:
        current_start, current_renewal = sheets.get_renewal_dates(sheet)
        plan = renewal.calculate_cycle_status(current_start, current_renewal)

        if plan['has_changed']:
            print(f"🔄 Nuevo ciclo: {plan['new_start_date'].strftime('%d/%m/%Y')} → {plan['new_renewal_date'].strftime('%d/%m/%Y')}")
            
            # Guardar en Sheet (columna K)
            sheets.update_renewal_dates(sheet, plan['new_start_date'], plan['new_renewal_date'])
            
            # Crear evento en Calendar solo si es fecha futura
            if plan['is_future']:
                calendar.create_calendar_event(creds, plan['new_renewal_date'])
        else:
            print(f"ℹ️  Próxima renovación: {current_renewal.strftime('%d/%m/%Y') if current_renewal else 'No definida'}")

    except Exception as e:
        print(f"❌ Error en el proceso de renovación: {e}")

    print(f"{timestamp()} 🎉 Fin del proceso.")


if __name__ == "__main__":
    run()