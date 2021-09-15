# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re

from fastapi import FastAPI, File, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request
from fastapi.responses import StreamingResponse
from pywebio.platform.fastapi import webio_routes

from app.controller.render import render_json
from app.service.time_series_detector.anomaly_service import *
from app.service.time_series_detector.sample_service import *
from app.service.time_series_detector.task_service import *
from app.service.time_series_detector.detect_service import *
from app.service.explore.data_explore import explore

app = FastAPI()


# `task_func` is PyWebIO task function
app.mount("/tool", FastAPI(routes=webio_routes(explore)))



@app.websocket("/ws_explore")
async def ws_explore(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


def _get_body(request):
    try:
        request.body().send(None)
    except StopIteration as e:
        if isinstance(e.value, bytes):
            return e.value.decode('ascii')
        else:
            return e.value


@app.post("/SearchAnomaly")
def search_anomaly(request: Request):
    anomaly_service = AnomalyService()
    return anomaly_service.query_anomaly(_get_body(request))


@app.post("/ImportSample")
def import_sample(sample_file: bytes = File(...)):
    sample_service = SampleService()
    return sample_service.import_file(sample_file)


@app.post("/UpdateSample")
def update_sample(request: Request):
    sample_service = SampleService()
    return sample_service.update_sample(_get_body(request))


@app.post("/QuerySample")
def query_sample(request: Request):
    sample_service = SampleService()
    return sample_service.query_sample(_get_body(request))


@app.post("/DeleteSample")
def delete_sample(request: Request):
    sample_service = SampleService()
    return sample_service.delete_sample(_get_body(request))


@app.post("/CountSample")
def count_sample(request: Request):
    sample_service = SampleService()
    return sample_service.count_sample(_get_body(request))


@app.post("/UpdateAnomaly")
def update_anomaly(request: Request):
    sample_service = AnomalyService()
    return sample_service.update_anomaly(_get_body(request))


@app.get("/DownloadSample/")
def download_sample(id: str):
    try:
        sample_service = SampleService()
        ret_code, sio = sample_service.sample_download(id)
        headers = {'Content-Type': 'application/octet-stream',
                   'Content-Disposition': 'attachment;filename = "SampleExport.csv"'
                   }
        sio.seek(0)  # 保存流。不调用会在下载时报网络错误
        # 以流的形式返回浏览器
        return StreamingResponse(sio, headers=headers)
    except Exception as ex:
        return_dict = build_ret_data(THROW_EXP, str(ex))
        return render_json(return_dict)


@app.post("/PredictRate")
def predict_rate(request: Request):
    detect_service = DetectService()
    return detect_service.rate_predict(json.loads(_get_body(request)))


@app.post("/PredictValue")
def predict_value(request: Request):
    detect_service = DetectService()
    return detect_service.value_predict(json.loads(_get_body(request)))


@app.post("/Train")
def train(request: Request):
    detect_service = DetectService()
    return detect_service.process_train(json.loads(_get_body(request)))


@app.post("/QueryTrain")
def query_train_task(request: Request):
    train_service = TrainService()
    return train_service.query_train(_get_body(request))


@app.post("/QueryTrainSource")
def query_train_source(request: Request):
    sample_service = SampleService()
    return sample_service.query_sample_source(_get_body(request))


@app.post("/DeleteTrain")
def delete_train_task(request: Request):
    train_service = TrainService()
    return train_service.delete_train(_get_body(request))


staticFiles = StaticFiles(directory="statics")  # 下面只是需要调用这个对象的 get_response方法
app.mount(r"/ui", staticFiles, name="static")  # 需要把静态资源挂载，下面才能获取静态资源返回


@app.get(r".*")
async def static_res(request: Request):
    path = request.url.path
    if re.search(r".*/.+\..+", path) is not None:  # Other static resource
        start = path.find('/')
        return await staticFiles.get_response(path[start + 1:], request.scope)
    else:  # homepage
        return await staticFiles.get_response('index.html', request.scope)


if __name__ == "__main__":
    import uvicorn

    # 官方推荐是用命令后启动 uvicorn main:app --host=0.0.0.0 --port=8000 --reload
    uvicorn.run(app='main:app', host="0.0.0.0", port=8000, reload=True, debug=True)
