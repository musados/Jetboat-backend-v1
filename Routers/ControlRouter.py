from fastapi import Depends, FastAPI, HTTPException, status, APIRouter, Request
from pprint import pprint
from Classes.EventHandler import EventHandler
from pydantic import BaseModel
from typing import Any, List

class ControlData(BaseModel):
    throttle: int
    yaw: int
    pitch:int
    roll:int
    channels:List[int]


router_control = APIRouter(
    prefix='/control',
    tags=['Control']
)

class ControlEvent(EventHandler):
    def __init__(self, message):
        self.message = message
	
    def __str__(self):
        return "Message from other class: " + repr(self.message)

controlEventHandler = ControlEvent('onControlAction')

@router_control.post('', summary='Post Boat control data- channels')
async def control_boat(channels:ControlData):
    global controlEventHandler
    # print('controls:')
    # pprint(channels)
    controlEventHandler.trigger('onControlAction', channels.dict())
