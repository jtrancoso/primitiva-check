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
        existing_dates = sheet.col_values(1) # Columna A
    except Exception as e:
        print(f"❌ Error conectando a Google Sheets: {e}")
        return

    # 3. Procesar Sorteos (Domain loop)
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
            
            # Guardar (Service)
            sheet.append_row(new_row)
            print(f"✅ Guardado sorteo del {date_str}")
            time.sleep(1) # Pausa de cortesía
            
        except ValueError as e:
            print(f"⚠️ Error procesando entrada: {e}")
        except Exception as e:
            print(f"❌ Error inesperado en el bucle: {e}")
    
    print(f"{timestamp()} 🔽 Ordenando hoja por fecha descendente...")
    sheet.sort((1, 'des'))

    # 4. Gestión de Renovación (Modular)
    try:
        current_start, current_end = sheets.get_renewal_dates(sheet)
        plan = renewal.calculate_cycle_status(current_start, current_end)

        if plan['has_changed']:
            print(f"🔄 Actualizando fecha renovación a: {plan['new_renewal_date'].strftime('%d/%m/%Y')}")
            
            sheets.update_renewal_info(
                sheet, 
                plan['new_start_date'], 
                plan['new_renewal_date']
            )
            
            if plan['is_future']:
                calendar.create_calendar_event(creds, plan['new_renewal_date'])
        else:
            print("ℹ️  No toca renovar todavía.")
            
    except Exception as e:
        print(f"❌ Error en el proceso de renovación: {e}")

    print(f"{timestamp()} 🎉 Fin del proceso.")

if __name__ == "__main__":
    run()