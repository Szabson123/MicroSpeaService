from fastapi import FastAPI
from utils.get_bins import process_single_msn
from utils.insert_bins import insert_data_to_posgres
from utils.check_prev_phase import check_prev_phase, check_prev_phase_api
from utils.insert_prev_phase import insert_prev_phase_to_posgres
from database import CONNECTION_STRING_POLMESPROD, CONNECTION_STRING_LOCAL_POSTGRES
from models import BinRequest, PhaseIDRequest

from pyodbc import connect
from typing import List
import psycopg2

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


# @app.get('/spea-serivce/lighting_linked_serial/{id}/')
# async def lighting_linked_serial_func(id: str):
#     data = main_lighting_linked_serials(id)
#     return data

@app.post('/spea-serivce/check-bins/')
async def bin_list_checker(requests: BinRequest):
    final_result = {}
    
    with connect(CONNECTION_STRING_POLMESPROD) as conn:
        cursor = conn.cursor()
        for sn in requests.sns:
            final_result[sn] = process_single_msn(cursor, sn)
    
    with psycopg2.connect(CONNECTION_STRING_LOCAL_POSTGRES) as conn:
        cursor = conn.cursor()
        for key, value in final_result.items():
            insert_data_to_posgres(cursor, key, value) 
        
        conn.commit()
            
    print(final_result)
    return final_result


@app.post("/spea-serivce/check-phase/")
async def check_phase(request: PhaseIDRequest):
    api_responses = {}
    for sn, end_code in request.sns.items():
        try:
            api_responses[sn] = check_prev_phase_api(request.phase_id, end_code, sn)
        except Exception as e:
            print(f"Błąd podczas odpytywania API dla SN {sn}: {e}")
            api_responses[sn] = None

    print(api_responses)

    with psycopg2.connect(CONNECTION_STRING_LOCAL_POSTGRES) as conn:
        cursor = conn.cursor()
        for key, resp in api_responses.items():
            if resp is None:
                continue
                
            try:
                return_code = resp.get("returnCode")
                return_code_desc = resp.get("returnCodeDescription")

                insert_prev_phase_to_posgres(cursor, key, return_code, return_code_desc)
            except Exception as e:
                print(f"Błąd zapisu do bazy danych dla SN {key}: {e}")
                continue
        
        conn.commit()