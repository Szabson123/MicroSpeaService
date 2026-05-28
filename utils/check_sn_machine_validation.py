def check_task_done(cur, task_num):
    query = """SELECT prev_done, bins_done FROM public.spea_service_tasknum 
                WHERE unique_id = %s;"""

    cur.execute(query, (str(task_num),)) 
    return cur.fetchone()

def check_validation(cur, sn):
    query = """ SELECT sn, bin, prev_phase, phase_error_code FROM public.spea_service_testedsn
                WHERE sn = ANY(%s)
                ORDER BY date_time DESC
            """
    cur.execute(query, (sn, ))
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

def check_fixture_counter_limit(cur, machine_name):
    query = """SELECT """