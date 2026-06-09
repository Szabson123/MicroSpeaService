from fastapi import FastAPI, HTTPException, status

from utils.get_bins import process_single_msn
from utils.insert_bins import insert_data_to_posgres
from utils.check_prev_phase import check_prev_phase_api
from utils.insert_prev_phase import insert_prev_phase_to_posgres
from utils.update_task import update_task_on_done
from utils.check_sn_machine_validation import check_task_done, check_validation, check_date, check_force_validation

from database import CONNECTION_STRING_POLMESPROD, CONNECTION_STRING_LOCAL_POSTGRES
from models import BinRequest, PhaseIDRequest, FullCheck

from datetime import datetime, timedelta, timezone
from pyodbc import connect
from typing import List, Dict
import psycopg


app = FastAPI()


@app.get("/spea-serivce/")
async def root():
    return {"message": "Hello World"}


@app.post('/spea-serivce/check-bins/')
async def bin_list_checker(requests: BinRequest):
    type_of_req = 'bin'
    final_result = {}
    
    with connect(CONNECTION_STRING_POLMESPROD) as conn:
        cursor = conn.cursor()
        for sn in requests.sns:
            final_result[sn] = process_single_msn(cursor, sn)
    
    with psycopg.connect(CONNECTION_STRING_LOCAL_POSTGRES) as conn:
        cursor = conn.cursor()
        for key, value in final_result.items():
            insert_data_to_posgres(cursor, key, value) 
        
        conn.commit()
        update_task_on_done(cursor, type_of_req, requests.task_num)
            
    print(final_result)
    return final_result


@app.post("/spea-serivce/check-phase/")
async def check_phase(request: PhaseIDRequest):
    type_of_req = 'phase_id'
    api_responses = {}
    for sn, end_code in request.sns.items():
        try:
            api_responses[sn] = check_prev_phase_api(request.phase_id, end_code, sn)
        except Exception as e:
            print(f"Błąd podczas odpytywania API dla SN {sn}: {e}")
            api_responses[sn] = None

    with psycopg.connect(CONNECTION_STRING_LOCAL_POSTGRES) as conn:
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
        update_task_on_done(cursor, type_of_req, request.task_num)


@app.post("/spea-serivce/check-sns/")
def check_sns(payload: FullCheck) -> List[Dict]:
    with psycopg.connect(CONNECTION_STRING_LOCAL_POSTGRES, row_factory=psycopg.rows.dict_row) as conn:
        with conn.cursor() as cur:
            force = check_force_validation(cur, payload.machine_name)
            if force:
                response_data = []
                with connect(CONNECTION_STRING_POLMESPROD) as prod_conn:
                    cursor = prod_conn.cursor()
                    for sn in payload.sns:
                        single_res = process_single_msn(cursor, sn)
                        response_data.append({sn: single_res})
                return response_data

            task = check_task_done(cur, payload.task_num)
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You didn't provide task or doesn't exist"
                )
            
            if not (task['prev_done'] and task['bins_done']):
                raise HTTPException(
                    status_code=status.HTTP_200_OK,
                    detail="This task is not ready yet"
                )
            
            machine_status = check_date(cur, payload.machine_name)
            if not machine_status:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": "Machine validation not found",
                        "code": "Machine Invalidate"
                    }
                )
            
            expiration_time = machine_status['time_date'] + timedelta(hours=8)
            if not machine_status['is_valid'] or expiration_time < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "Machine validation is invalid or expired (older than 8 hours)", 
                        "code": "Machine Invalidate"
                    }
                )
            
            rows = check_validation(cur, payload.sns)
            response_data = []
            for row in rows:
                sn_key = row['sn']
                bin_info = row['bin']
                
                item_structure = {
                    sn_key: bin_info,
                    "prev_phase": row['prev_phase'],
                    "phase_error_code": row['phase_error_code']
                }
                response_data.append(item_structure)
            

            return response_data
        