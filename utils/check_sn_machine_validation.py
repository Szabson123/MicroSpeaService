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
