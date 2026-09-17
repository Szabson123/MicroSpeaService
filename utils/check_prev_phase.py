import json
import logging
import requests

logger = logging.getLogger(__name__)

session = requests.Session()

def check_prev_phase_api(phase_id, end_code, sn):
    url = 'http://10.140.13.11:5556/api/checkprevphase'
    payload = {
        "phaseID": str(phase_id),
        "internalCode": str(end_code),
        "serialNumber": str(sn),
        "level": "0",
        "resultType": "-1"
    }
    
    try:
        response = session.post(
            url, 
            json=payload, 
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=(10.0, 17.0)
        )
    except requests.exceptions.RequestException as e:
        logger.error("[API ERROR] Problem sieciowy/timeout dla SN %s: %s", sn, e)
        raise

    # Loguj jeśli API zwróciło cokolwiek innego niż 2xx
    if not response.ok:
        logger.error("[API ERROR] Status %s dla SN %s. Odpowiedź: %s", response.status_code, sn, response.text)
        response.raise_for_status()

    # Zabezpieczenie przed pustym body przy statusie 200 OK
    raw_text = response.text.strip()
    if not raw_text:
        logger.warning("[API WARNING] API zwróciło pustą odpowiedź (200 OK) dla SN: %s", sn)
        return {}

    try:
        data = response.json()
    except json.JSONDecodeError:
        logger.error("[API ERROR] Odpowiedź nie jest JSON-em dla SN %s. Treść: %s", sn, raw_text)
        raise

    # Obsługa podwójnie zserializowanego JSON-a (częste w starych API .NET/Java)
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            logger.error("[API ERROR] String nie jest poprawnym JSON-em dla SN %s: %s", sn, data)
            raise

    return data