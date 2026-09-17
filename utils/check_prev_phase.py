import requests

def check_prev_phase_api(phase_id, end_code, sn):
    url = 'http://10.140.13.11:5556/api/checkprevphase'
    payload = {
        "phaseID": phase_id,
        "internalCode": end_code,
        "serialNumber": sn,
        'level': '0',
        'resultType': '-1'
    }
    
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    if isinstance(data, str):
        import json
        data = json.loads(data)
        
    return data