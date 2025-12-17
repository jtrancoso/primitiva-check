from datetime import datetime, timedelta

def get_next_monday(from_date: datetime, weeks_ahead: int = 2) -> datetime:
    """
    Calcula el lunes que está aproximadamente 'weeks_ahead' semanas después de 'from_date'.
    
    Ejemplo: 
    - from_date = lunes 16 dic, weeks_ahead = 2 → lunes 30 dic
    - from_date = martes 17 dic, weeks_ahead = 2 → lunes 30 dic
    """
    # Día de la semana: 0 = lunes, 6 = domingo
    day_of_week = from_date.weekday()
    
    # Días hasta el próximo lunes (si ya es lunes, serían 7 días al siguiente)
    days_to_next_monday = (7 - day_of_week) % 7
    if days_to_next_monday == 0:
        days_to_next_monday = 7  # Si es lunes, ir al siguiente lunes
    
    # Sumamos las semanas adicionales (-1 porque ya contamos una semana con days_to_next_monday)
    total_days = days_to_next_monday + (weeks_ahead - 1) * 7
    
    return from_date + timedelta(days=total_days)


def calculate_cycle_status(start_date: datetime, stored_renewal_date: datetime) -> dict:
    """
    Calcula el estado del ciclo de renovación.
    
    La fecha de renovación SIEMPRE debe ser un lunes, aproximadamente 2 semanas
    después de la fecha de inicio del ciclo.
    """
    hoy = datetime.now()
    
    # Si la hoja está vacía, usamos hoy como punto de partida
    if not start_date:
        start_date = hoy

    new_start_date = start_date
    
    # --- LÓGICA DE CADENA CONTINUA ---
    # Si ya pasó la fecha de renovación almacenada, el nuevo ciclo empieza
    # desde esa fecha (no desde hoy) para mantener la cadena de lunes.
    if stored_renewal_date and hoy.date() >= stored_renewal_date.date():
        new_start_date = stored_renewal_date
    
    # Calculamos el próximo lunes ~2 semanas desde el inicio del ciclo
    new_renewal_date = get_next_monday(new_start_date, weeks_ahead=2)
    
    # Determinamos si hay cambio respecto a lo almacenado
    has_changed = False
    if stored_renewal_date:
        if new_renewal_date.date() != stored_renewal_date.date():
            has_changed = True
    else:
        # Primera ejecución
        has_changed = True

    return {
        "new_start_date": new_start_date,
        "new_renewal_date": new_renewal_date,
        "has_changed": has_changed,
        "is_future": new_renewal_date.date() > hoy.date()
    }