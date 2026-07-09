def check_task_done(cur, task_num):

    if task_num is None:
        return None
    
    query = """SELECT prev_done, bins_done FROM public.spea_service_tasknum 
                WHERE unique_id = %s;"""

    cur.execute(query, (str(task_num),)) 
    return cur.fetchone()

def check_validation(cur, sn):
    query = """ SELECT DISTINCT ON (sn) sn, bin, prev_phase, phase_error_code, phase_error_num_code
                FROM public.spea_service_testedsn
                WHERE sn = ANY(%s)
                ORDER BY sn, date_time DESC
            """
    cur.execute(query, (list(set(sn)), ))
    return cur.fetchall()

def check_date(cur, machine_name):
    query = """SELECT h.is_valid, h.time_date
               FROM public.spea_service_fullvalidationmachinemodel h
               JOIN spea_service_machine m ON h.machine_id = m.id
               WHERE m.name = %s AND h.is_valid = True
               ORDER BY h.time_date DESC
               LIMIT 1
    """
    cur.execute(query, (machine_name,))
    return cur.fetchone()

def check_force_validation(cur, machine_name):
    query = """SELECT f.is_valid, f.date_time_end
               FROM public.spea_service_forcevalidmachine f
               JOIN spea_service_machine m ON f.machine_id = m.id
               WHERE m.name = %s 
                 AND f.is_valid = True 
                 AND f.date_time_end >= NOW()
               ORDER BY f.date_time_end DESC
               LIMIT 1"""
    
    cur.execute(query, (machine_name,))
    return cur.fetchone()