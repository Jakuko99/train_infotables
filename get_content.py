import requests
import json
from bs4 import BeautifulSoup
from enum import Enum
import os

templates_path = f"{os.path.dirname(os.path.abspath(__file__))}/templates"


class tableType(Enum):
    ARRIVALS = 1
    DEPARTURES = 2


class tableTypeSk(Enum):
    PRÍCHODY = 1
    ODCHODY = 2


def assemble_url(station_id: int, table_type: tableType) -> str:
    web_url = f"https://aplikacie.zsr.sk/InfoTabule/StationDetail.aspx?id={station_id}&t={table_type.value}"
    return web_url


def get_infotable(
    station_id: int, table_type: tableType, parse: bool = True, font_size: int = 20
) -> str:
    url = assemble_url(station_id, table_type)
    response = requests.get(url)
    html_page = BeautifulSoup(response.content, features="lxml")
    div = html_page.find("div", {"id": "ctl00_ContentPlaceHolderStranka_UpdatePanel1"})

    tag = div.find("tr", {"class": "gridInfo"})
    if tag:
        tag.extract()

    page_title = html_page.new_tag("h1")
    page_title.string = f'{html_page.find("span", {"class":"station_name"}).string} - {tableTypeSk(table_type.value).name.capitalize()}'
    page_title["style"] = "text-align: center"
    div.insert(0, page_title)

    if parse:
        return parse_infotable(
            page=html_page, table_type=table_type, font_size=font_size
        )
    else:
        return div.decode_contents()


def extract_content(page: BeautifulSoup, type: tableType) -> list:
    table_content: list[str] = list()

    odjezdy_item = page.find_all(
        "tr",
        {
            "class": f"{'gridItemOdjezdy' if type == tableType.DEPARTURES else 'gridItem'}"
        },
    )
    alternate_item = page.find_all("tr", {"class": "gridAlternateItem"})
    joined_items = [item for pair in zip(odjezdy_item, alternate_item) for item in pair]

    for item in joined_items:
        row = list()
        for cell in item.find_all("td"):
            row.append(cell.string)
        table_content.append(row)

    messages = []
    for item in list(table_content):
        if len(item) == 1:
            messages.append(table_content.pop(table_content.index(item))[0])

    return table_content, messages


def parse_infotable(
    page: BeautifulSoup, table_type: tableType, font_size: int = 20
) -> str:
    column_names_arrival = [
        "Príchod",
        "Druh",
        "Číslo",
        "Dopravca",
        "Východzia stanica",
        "Zo smeru",
        "Nástupište",
        "Koľaj",
        "Meškanie",
    ]
    column_names_departure = [
        "Odchod",
        "Druh",
        "Číslo",
        "Dopravca",
        "Cieľová stanica",
        "Smer jazdy",
        "Nástupište",
        "Koľaj",
        "Meškanie",
    ]

    table_columns = len(column_names_arrival)
    with open(f"{templates_path}/info_table.html", "r", encoding="utf-8") as f:
        page_code: str = f.read()

    html_table = BeautifulSoup(page_code, "html.parser")
    table_content, messages = extract_content(page=page, type=table_type)

    for i in range(len(table_content) + 1):
        row = page.new_tag("tr")
        html_table.table.append(row)
        if i == 0:
            column_names = (
                column_names_arrival
                if table_type == tableType.ARRIVALS
                else column_names_departure
            )
            for header_nr in range(table_columns):
                col = page.new_tag("th")
                col.string = column_names[header_nr]
                row.append(col)
        else:
            for item in table_content[i - 1]:
                col = page.new_tag("td")
                if item:
                    if table_content[i - 1].index(item) == 4:
                        col.string = item.capitalize()
                    else:
                        col.string = item
                else:
                    col.string = ""
                row.append(col)

    for message in messages:
        row = page.new_tag("tr")
        html_table.table.append(row)
        col = page.new_tag("td", colspan=table_columns)
        col.string = message
        col["style"] = "text-align: left"
        row.append(col)

    page_title = page.new_tag("h1")
    page_title.string = f'{page.find("span", {"class":"station_name"}).string} - {tableTypeSk(table_type.value).name.capitalize()}'
    page_title["style"] = "text-align: center"
    html_table.insert(0, page_title)

    style_tag = html_table.new_tag("style")
    style_tag.string = f"""
        body {{
            background-color: #000000;
        }}
        
        table {{
            color: #ffd800;
            font-size: {font_size}px;
            width: 100%;       
            text-align: center;   
        }}

        table tr:first-child {{
            color: #ffffff;
            text-align: center;
        }}

        h1 {{
            color: #ffffff;
            font-size: {font_size * 1.5}px;
        }}
    """
    head_tag = html_table.find("head")
    head_tag.append(style_tag)

    return str(html_table)


def get_json(station_id: int, table_type: tableType) -> dict:
    url = assemble_url(station_id, table_type)
    response = requests.get(url)
    html_page = BeautifulSoup(response.content, features="lxml")
    div = html_page.find("div", {"id": "ctl00_ContentPlaceHolderStranka_UpdatePanel1"})

    tag = div.find("tr", {"class": "gridInfo"})
    if tag:
        tag.extract()

    page_title = html_page.new_tag("h1")
    page_title.string = f'{html_page.find("span", {"class":"station_name"}).string} - {tableTypeSk(table_type.value).name.capitalize()}'
    page_title["style"] = "text-align: center"
    div.insert(0, page_title)

    table_content, messages = extract_content(page=html_page, type=table_type)
    table_dictionary = dict()

    for line in table_content:
        table_dictionary[line[2]] = {
            "time": line[0],
            "type": line[1],
            "carrier": line[3],
            "destination": line[4].capitalize(),
            "direction": line[5],
            "platform": line[6].replace("\xa0", ""),
            "track": line[7].replace("\xa0", ""),
            "delay": line[8] if line[8] else "0",
        }

    json_data = dict()
    json_data["station"] = html_page.find("span", {"class": "station_name"}).string
    json_data["infotable_type"] = tableType(table_type.value).name.capitalize()
    json_data["trains"] = table_dictionary
    json_data["message"] = messages

    return json_data


if __name__ == "__main__":
    station_id = 178954
    infotable = get_infotable(station_id, tableType.ARRIVALS)
    print(infotable)
