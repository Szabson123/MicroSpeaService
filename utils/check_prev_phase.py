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
    
    response = requests.post(url, json=payload, timeout=5)
    response = response.json()
    print(response)
    return response
