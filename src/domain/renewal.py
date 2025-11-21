from datetime import datetime, timedelta

def calculate_cycle_status(start_date: datetime, stored_renewal_date: datetime) -> dict:
    hoy = datetime.now()
    
    # Si la hoja está vacía, no tenemos referencia, usamos hoy
    if not start_date:
        start_date = hoy

    needs_reset = False
    new_start_date = start_date # Por defecto seguimos igual

    # --- LÓGICA DE CADENA CONTINUA ---
    # Si ya teníamos una fecha de renovación prevista (ej: 17 Nov)
    # y hoy la hemos superado (ej: estamos a 21 Nov),
    # el nuevo inicio NO es hoy, es la fecha que estaba prevista (17 Nov).
    # Así mantenemos el ciclo de Lunes perfectos aunque ejecutes el script tarde.
    
    if stored_renewal_date and hoy.date() >= stored_renewal_date.date():
        needs_reset = True
        new_start_date = stored_renewal_date # <--- AQUÍ ESTÁ LA CLAVE (Antes ponía 'hoy')
    
    elif not stored_renewal_date:
        # Si es la primera vez que se ejecuta en la vida
        needs_reset = True
        new_start_date = hoy

    # Regla: +14 días desde el inicio del ciclo vigente
    new_renewal_date = new_start_date + timedelta(days=14)
    
    has_changed = False
    if stored_renewal_date:
        # Comparamos strings para ignorar horas
        if new_renewal_date.strftime("%Y-%m-%d") != stored_renewal_date.strftime("%Y-%m-%d"):
            has_changed = True
    else:
        has_changed = True

    return {
        "new_start_date": new_start_date,
        "new_renewal_date": new_renewal_date,
        "has_changed": has_changed,
        "is_future": new_renewal_date > hoy
    }