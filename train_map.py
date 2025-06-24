import os
import folium as fo
import json
from requests import Request, Session

templates_path = f"{os.path.dirname(os.path.abspath(__file__))}/templates"
map = fo.Map(location=[48.40, 19.30],
             zoom_start=8, tiles="OpenStreetMap")

def save_map():
    while True:
        global map
        request = Request(
            'GET',
            'https://tis.zsr.sk/mapavlakov/api/osobne').prepare()
        s = Session()
        response = s.send(request)
        response_obj = json.loads(response.text)
        # print("Response lenght: ", len(response_obj))
        map = fo.Map(location=[48.40, 19.30],
                     zoom_start=8, tiles="OpenStreetMap")

        vlak: dict
        for vlak in response_obj:
            popup = fo.Popup(html=f"""<b>{vlak.get("DruhVlaku").strip()} {vlak.get("CisloVlaku")} {vlak.get("NazovVlaku")}</b> <a href="https://kis.zsr.sk/pis/popup.jsp?id=vlakDetail&vlkId={vlak.get('DetailVlakuStr')}" target="_blank"> Odkaz na PIS</a><br>
            {vlak.get("StanicaVychodzia")} ({vlak.get("CasVychodzia")}) -> {vlak.get("StanicaCielova")} ({vlak.get("CasCielova")})<br>             
            <b>Čas:</b> {vlak.get("CasUdalosti")}<br>
            <b>Stanica:</b> {vlak.get("StanicaUdalosti")}<br>
            <b>Meškanie:</b> {vlak.get("Meskanie")} min<br>
            <b>Potvrdený odjazd:</b> {'Áno' if vlak.get("PotvrdenyOdj") == 1 else 'Nie'}<br>
            <b>Bus:</b> {'Áno' if vlak.get("Bus") == 1 else 'Nie'}<br>
            <b>Poradie v stanici:</b> {vlak.get("PoradieVStanici")}<br>
            <b>Dopravca:</b> {vlak.get("Dopravca")}""", max_width=400)

            trasa = vlak.get("Trasa")
            if vlak.get("Meskanie") < 20:
                fo.Marker(location=vlak.get("Poloha"), popup=popup,
                          tooltip=f'{vlak.get("DruhVlaku").strip()} {vlak.get("CisloVlaku")}', icon=fo.Icon(color="green")).add_to(map)
            elif vlak.get("Meskanie") > 20 and vlak.get("Meskanie") < 40:
                fo.Marker(location=vlak.get("Poloha"), popup=popup,
                          tooltip=f'{vlak.get("DruhVlaku").strip()} {vlak.get("CisloVlaku")}', icon=fo.Icon(color="orange")).add_to(map)
            else:
                fo.Marker(location=vlak.get("Poloha"), popup=popup,
                          tooltip=f'{vlak.get("DruhVlaku").strip()} {vlak.get("CisloVlaku")}', icon=fo.Icon(color="red")).add_to(map)
            for part in trasa:
                fo.PolyLine(locations=part.get("Value"), color="red" if part.get(
                    "Key") == "Pred" else "blue", weight=2.5, opacity=1).add_to(map)

        map.save(f"{templates_path}/map.html")
        break    