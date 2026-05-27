import json


def insert_data_to_posgres(cursor, key: str, value: dict):
    query = """
        UPDATE public.spea_service_testedsn
        SET bin = %s
        WHERE id = (
            SELECT id 
            FROM public.spea_service_testedsn 
            WHERE sn = %s
            ORDER BY date_time DESC 
            LIMIT 1
        );
    """
    
    cursor.execute(query, (json.dumps(value), key))
