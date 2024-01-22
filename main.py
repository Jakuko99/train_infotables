import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
import os

from station_ids import StationIds
from get_content import tableType, get_infotable, get_json

app = FastAPI(title="REST ZSR InfoTables")
current_path = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=f"{current_path}/templates")


@app.get("/")
def index_page(request: Request) -> HTMLResponse:
    enum_values = StationIds.__members__.keys()  # Replace YourEnum with your Enum name
    return templates.TemplateResponse(
        "index.html", context={"request": request, "enum_values": enum_values}
    )


@app.get("/favicon.ico")
def get_favicon():
    return FileResponse(f"{current_path}/assets/logo.png")


@app.get("/file/{filename}")
def get_file(filename: str):
    return FileResponse(f"{current_path}/assets/{filename}")


@app.get("/station_raw/{station_name}")
def get_station_raw(station_name: str, type: int = 2) -> int:
    try:
        station_id = StationIds[station_name.upper()].value
        type = tableType(type)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Station {station_name} not found")
    except ValueError:
        type = tableType.DEPARTURES

    infotable = get_infotable(station_id, type, parse=False)
    return HTMLResponse(infotable, status_code=200)


@app.get("/station/{station_name}")
def get_station(station_name: str, type: int = 2, font_size: int = 20) -> int:
    try:
        station_id = StationIds[station_name.upper()].value
        type = tableType(type)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Station {station_name} not found")
    except ValueError:
        type = tableType.DEPARTURES

    infotable = get_infotable(station_id, type, parse=True, font_size=font_size)
    return HTMLResponse(infotable, status_code=200)


@app.get("/data/{station_name}")
def get_data(station_name: str, type: int = 2) -> str:
    try:
        station_id = StationIds[station_name.upper()].value
        type = tableType(type)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Station {station_name} not found")
    except ValueError:
        type = tableType.DEPARTURES

    infotable = get_json(station_id, type)
    return infotable


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8040)
