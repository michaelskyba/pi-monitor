from fastapi import FastAPI, File, Form, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from json import dumps, loads
from re import search
from typing import List, Optional

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("monitor.html")


# Poor makeshift solution for the unrecoverable Pis.
@app.get("/monitor.html")
async def config_redirect():
    return FileResponse("monitor.html")


@app.get("/update")
async def monitor_update():
    return FileResponse("monitor_update.html")


# e.g.
# https://youtube.com/watch?v=o-YBDTqX_ZU
# https://youtube.com/watch?v=o-YBDTqX_ZU&foo=bar&bar=baz
# https://www.youtube.com/watch?v=o-YBDTqX_ZU?foo=bar&bar=baz
# https://youtu.be/o-YBDTqX_ZU?si=pLeuVDoJjradBVeA
def parse_youtube_id(youtube_url):
    r = search("^https?://(www\.)?youtube\.com/watch\?v=[a-zA-Z0-9_-]{11}", youtube_url)
    if not r:
        r = search("^https?://(www\.)?youtu\.be/[a-zA-Z0-9_-]{11}", youtube_url)

    if not r:
        return None

    id = r.group(0)[-11:]
    return id


def get_monitor_config():
    with open("config/monitor.json") as f:
        return loads(f.read())


def set_monitor_config(monitor_config):
    with open("config/monitor.json", "w") as f:
        f.write(dumps(monitor_config))


@app.post("/api/update")
async def monitor_api_update(
    section: str = Form(...),
    type: str = Form(...),
    image_files: List[UploadFile] = File(...),
    image_interval: float = Form(...),
    youtube_url: Optional[str] = Form(None),
):
    section = {
        "a": "main",
        "b": "footer",
        "c": "sidebar",
    }.get(section)

    monitor_config = get_monitor_config()

    if not section:
        return "Invalid section"

    if type not in ["image_cycle", "youtube"]:
        return "Invalid section type"

    if type == "image_cycle":
        for file in image_files:
            if not file.filename:
                return "image cycle type requires at least one image file"

            if not file.content_type.startswith("image/"):
                return "image cycle type only accepts image files"

        return "ok image_cycle"

    if not youtube_url:
        return "No YouTube URL provided"

    id = parse_youtube_id(youtube_url)
    if not id:
        return "Invalid YouTube URL format provided"

    display = {"type": "youtube", "video_id": id}
    monitor_config[section] = display
    set_monitor_config(monitor_config)

    return "ok youtube"


@app.get("/config")
async def config():
    return get_monitor_config()
