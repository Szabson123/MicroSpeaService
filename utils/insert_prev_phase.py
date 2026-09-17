import logging

logger = logging.getLogger(__name__)

def insert_prev_phase_to_posgres(cursor, key, return_code, return_code_desc):
    query = """
    UPDATE public.spea_service_testedsn
    SET prev_phase = %s, phase_error_code = %s, phase_error_num_code = %s
    WHERE id = (
        SELECT id 
        FROM public.spea_service_testedsn 
        WHERE sn = %s
        ORDER BY date_time DESC 
        LIMIT 1
    )
    """
    
    # Bezpieczna konwersja: obsługa int (0), str ("0") oraz None
    if return_code is not None:
        try:
            return_code_to_db = (int(return_code) == 0)
        except (ValueError, TypeError):
            return_code_to_db = False
    else:
        return_code_to_db = False

    cursor.execute(query, (return_code_to_db, return_code_desc, return_code, key))

    # WERYFIKACJA CZY WIERSZ FAKTYCZNIE ZOSTAŁ ZAKTUALIZOWANY
    if cursor.rowcount == 0:
        logger.warning(
            "[Brak rekordu] Nie znaleziono SN '%s' w tabeli spea_service_testedsn! Żaden wiersz nie został zaktualizowany.", 
            key
        )
    else:
        logger.info(
            "[Zapisano] SN '%s' zaktualizowany: prev_phase=%s, code=%s (wierszy: %d)", 
            key, return_code_to_db, return_code, cursor.rowcount
        )