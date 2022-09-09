from fastapi import Depends, FastAPI, HTTPException, status, APIRouter, Request
from pprint import pprint
from Classes.EventHandler import EventHandler
from pydantic import BaseModel
from typing import Any, List
from Models.ResponseModels import BasicResponse
import json

class SensorData(BaseModel):
    name: str
    value: float


router_sensor = APIRouter(
    prefix='/sensor',
    tags=['Sensor']
)


sensorsData = {}

@router_sensor.get('', summary='Get all Boat sensors data')
async def get_boat_analystics():
    global sensorsData
    return BasicResponse(success=True, message='Sensors data', data=sensorsData)

@router_sensor.get('/gps', summary='Get Boat GPS data')
async def get_boat_gps_data():
    global sensorsData
    if 'gps' in sensorsData:
        return BasicResponse(success=True, message='GPS data', data=sensorsData['gps'])
    raise HTTPException(status_code=501, detail="GPS data not found!")

@router_sensor.get('/temperature', summary='Get Boat Temperature data')
async def get_boat_temperature_data():
    global sensorsData
    if 'temperature' in sensorsData:
        return BasicResponse(success=True, message='Temperature data', data=sensorsData['temperature'])
    raise HTTPException(status_code=501, detail="Temperature data not found!")

@router_sensor.get('/water', summary='Get Boat water data')
async def get_boat_water_data():
    global sensorsData
    if 'water' in sensorsData:
        return BasicResponse(success=True, message='Water data', data=sensorsData['water'])
    raise HTTPException(status_code=501, detail="Water data not found!")