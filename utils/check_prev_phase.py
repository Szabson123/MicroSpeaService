import requests

def check_prev_phase(cursor, phase_id, end_code, sn):
    query = """
            SET NOCOUNT ON;
            DECLARE @ret int;
            EXEC @ret = [Monitor].[dbo].[CheckPhasePrev] @Board=?, @PhaseName=?, @IdParts=?, @CheckLevels=?, @Result=?;
            SELECT @ret AS result;
        """
    try:
        cursor.execute(query, (sn, phase_id, end_code, 0, 1))
        row = cursor.fetchone()
        val = row[0] if row else "Brak"
        return val

    except Exception as e:
        return f"Błąd bazy: {str(e)}"
    

def check_prev_phase_api(phase_id, end_code, sn):
    url = 'http://10.140.13.11:5556/api/checkprevphase'
    payload = {
        "phaseID": phase_id,
        "internalCode": end_code,
        "serialNumber": sn,
        'level': '0',
        'resultType': '-1'
    }
    
    response = requests.post(url, json=payload, timeout=5)
    response = response.json()
    print(response)
    return response
