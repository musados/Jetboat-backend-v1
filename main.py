from fastapi import Depends, FastAPI, HTTPException, status, APIRouter, Request, Response, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.responses import PlainTextResponse, RedirectResponse, JSONResponse, FileResponse, StreamingResponse
import uvicorn
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import json
#import jwt
import os
from datetime import datetime, timedelta
import time
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pprint import pprint
from fastapi.exceptions import RequestValidationError


import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server

from Classes.MyEventHandler import MyEventHandler
from Models import Jetboat
from Routers import ControlRouter
from Routers import SensorRouter

# Offline swagger
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles


sensorEventHandler = MyEventHandler('JetBoat Event Handler (main.py)')

app = FastAPI(title='Impressive Jetboat',
              description='Impressive Jetboat Fast API', version='1.1',
              docs_url=None, redoc_url=None)


origins = [
    "http://localhost",
    "https://localhost",
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routers
app.include_router(ControlRouter.router_control)
app.include_router(SensorRouter.router_sensor)


uidir = '../boatUI'
templates = Jinja2Templates(directory=uidir)
app.mount("/static_docs", StaticFiles(directory='static_docs'),
          name='static_docs')
app.mount("/css", StaticFiles(directory=f"{uidir}/css"), name=f"{uidir}/css")
app.mount("/js", StaticFiles(directory=f"{uidir}/js"), name=f"{uidir}/js")
app.mount("/img", StaticFiles(directory=f"{uidir}/img"), name=f"{uidir}/img")
app.mount(
    "/fonts", StaticFiles(directory=f"{uidir}/fonts"), name=f"{uidir}/fonts")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url=f"static_docs/swagger-ui-bundle.js",
        swagger_css_url=f"static_docs/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url=f"static_docs/redoc.standalone.js",
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    pprint(exc)
    print("request:")
    pprint(await request.json())
    print(request['endpoint'])
    return PlainTextResponse(str(exc), status_code=400)


def updateSensorsData(source, data: dict):
    # print(f"{type(source)} updated its sensors data!")
    # print('sensor data updated!!')
    SensorRouter.sensorsData = json.loads(data)



jetboatsettings = Jetboat.JetboatParameters(motorPin = Jetboat.escPin,
    servoPin = Jetboat.servoPin,
    motorThermPin = Jetboat.motorThermPin,
    boatThermPin = Jetboat.boatThermPin,
    raspThermPin = Jetboat.raspThermPin,
    waterSensPin = Jetboat.waterSensPin)



# create the event listeners
sensorEventHandler.on('SensorsChanged', updateSensorsData)
jetboat = Jetboat.Jetboat(jetboatsettings, sensorEventHandler)
val = -1
lastUpdate = time.time()

def send_controls_to_boat(source, controls:dict):
    global jetboat
    if source and type(source) == type(ControlRouter.controlEventHandler) and controls and type(controls) == type({}):
        jetboat.control(controls['throttle'], controls['yaw'])
    else:
        print('ERROR: Unknown control or source type!!')


@app.on_event("startup")
@repeat_every(seconds=0.8, wait_first=True)
async def boat_loop():
    global val
    global lastUpdate
    global jetboat
    
    jetboat.loopTask()
    # print(time.time() - lastUpdate)
    lastUpdate = time.time()

@app.on_event("startup")
async def startup():
    print('Startup Event - please start the boat')
    #events
    ControlRouter.controlEventHandler.on('onControlAction', send_controls_to_boat)
    try:
        os.system('sudo pigpiod')
    except Exception as e:
        print(f"Error at startup: {e}")

@app.on_event("shutdown")
async def shutdown():
    print("Closing the boat...")


@app.get('/favicon.ico')
async def get_favicon():
    return FileResponse(f"boatUI/favicon.ico")


@app.get('')
@app.get('/')
# , token: str = Depends(security.get_current_active_user)
async def index(request: Request, webtop: str = None, remote_path: str = None, prox: str = None):
    # if not security.get_current_active_user:
    #     return RedirectResponse(url='/login')
    # print(token)
    return templates.TemplateResponse("index.html", {"request": request}, media_type='text/html')

import  cv2

def generatImage():
    # grab global references to the output frame and lock variables
    global outputFrame, lock
    with picamera.PiCamera() as camera:
        camera.resolution = (400,300)       # pi camera resolution
        camera.framerate = 15               # 15 frames/sec
        camera.saturation = 80              # Set image video saturation
        camera.brightness = 50              # Set the brightness of the image (50 indicates the state of white balance)
        start = time.time()
        stream = io.BytesIO()
        # send jpeg format video stream
        print ("Start transmit ... ")
        # loop over frames from the output stream
        # while True:
        outputFrame = camera.capture('image.jpg')
        print(outputFrame)
        if outputFrame == None:
            return
        # wait until the lock is acquired
        # with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
        # if outputFrame is None:
        #     continue
        # encode the frame in JPEG format
        # (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
        # ensure the frame was successfully encoded
        # if not flag:
        #     continue
        # yield the output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
            bytearray(outputFrame) + b'\r\n')


@app.get("/video")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    # return StreamingResponse(generate())
    return StreamingResponse(generatImage(), media_type="multipart/x-mixed-replace;boundary=frame")

@app.get("/video/stream")
async def video_endpoint(range: str = Header(None)):
    start, end = range.replace("bytes=", "").split("-")
    start = int(start)
    end = int(end) if end else start + CHUNK_SIZE
    with open(video_path, "rb") as video:
        video.seek(start)
        data = video.read(end - start)
        filesize = str(video_path.stat().st_size)
        headers = {
            'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
            'Accept-Ranges': 'bytes'
        }
        return Response(data, status_code=206, headers=headers, media_type="video/mp4")

if __name__ == "__main__":
    if False:
        uvicorn.run('main:app', host=host_addr, port=port,
                    ssl_keyfile=server_settings['keyfile'], ssl_certfile=server_settings['certfile'], workers=workers_count, reload=debug_mode)
    else:
        uvicorn.run('main:app', host='0.0.0.0',
                    port=8000, workers=1, reload=True)
