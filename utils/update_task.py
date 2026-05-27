def insert_prev_phase_to_posgres(cursor, key, return_code, return_code_desc):
    query = """
    UPDATE public.spea_service_testedsn
    SET prev_phase = %s, phase_error_code = %s
    WHERE id = (
        SELECT id
            FROM public.spea_service_testedsn 
            WHERE sn = %s
            ORDER BY date_time DESC 
            LIMIT 1
    )
    """
    return_code_to_db = True if return_code == 0 else False

    cursor.execute(query, (return_code_to_db, return_code_desc, key))