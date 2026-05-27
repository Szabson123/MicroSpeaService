from psycopg2 import sql

def update_task_on_done(cursor, req_type: str, task_uuid: str):
    column_mapping = {
        'bin': 'bins_done',
        'phase_id': 'prev_done'
    }
    
    column_name = column_mapping.get(req_type)
    
    if not column_name:
        raise ValueError(f"Nieznany typ żądania: {req_type}")
        
    query = sql.SQL("UPDATE public.spea_service_tasknum SET {} = true WHERE unique_id = %s").format(sql.Identifier(column_name))
    
    cursor.execute(query, (str(task_uuid),))