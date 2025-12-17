import time
from datetime import datetime

# Importamos nuestros módulos
from config import settings
from services import scraper, sheets, calendar
from domain import parser, rules, renewal


def timestamp():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")


def run():
    print(f"{timestamp()} 🚀 Iniciando ejecución...")

    # 1. Obtener RSS (Service)
    raw_entries = scraper.get_rss_feed(settings.RSS_URL)
    if not raw_entries:
        print("⚠️ No se obtuvieron datos del RSS.")
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
            # Parseo (Domain)
            date_obj, numbers, bonus, reintegro = parser.parse_result(entry)
            date_str = date_obj.strftime("%d/%m/%Y")

            # Verificar si ya existe
            if date_str in existing_dates:
                print(f"⏭️  Sorteo del {date_str} ya existe.")
                continue

            # Calcular premios (Domain)
            matches = rules.calculate_match(numbers)
            bonus_match = bonus in settings.MY_NUMBERS
            reintegro_match = reintegro == settings.REINTEGRO

            prize_val = rules.calculate_prize(matches, bonus_match, reintegro_match)
            prize_type = rules.set_prize(matches, bonus_match, reintegro_match)

            # Preparar fila para guardar
            date_serial = sheets.to_google_sheets_date(date_obj)

            new_row = [
                date_serial,
                " - ".join(map(str, sorted(numbers))),
                bonus,
                reintegro,
                matches,
                prize_type,
                prize_val,
                1.0
            ]

            # Añadir al final de la tabla A:H (sin afectar columnas J-K)
            sheets.append_sorteo_row(sheet, new_row)
            print(f"✅ Guardado sorteo del {date_str}")
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

    # 4. Gestión de Renovación (lee/escribe en M2:M3, crea evento en Calendar)
    try:
        current_start, current_renewal = sheets.get_renewal_dates(sheet)
        plan = renewal.calculate_cycle_status(current_start, current_renewal)

        if plan['has_changed']:
            print(f"🔄 Nuevo ciclo: {plan['new_start_date'].strftime('%d/%m/%Y')} → {plan['new_renewal_date'].strftime('%d/%m/%Y')}")
            
            # Guardar en Sheet (columna M)
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