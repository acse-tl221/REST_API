import json
import requests
import pandas as pd
import process
from flask import Flask, request, send_from_directory,render_template_string,Response
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
# data = process.Reader('tideReadings.csv')
reader = process.Reader('tideReadings.csv')
app = Flask(__name__)


# This is a stub showing the beginnings of one required endpoint
# Must be editted to match API.rst description.
@app.route('/station/json')
def station_info():
    """Return station info.

    The endpoint accepts query parameters:
    * stationName
    * stationRef

    At least one must be present.
    """
    if request.method == 'GET':
        station_info_result={}
        station_name=request.args.get('stationName')
        station_ref=request.args.get('stationReference')
        data_station=pd.read_csv("stations.csv")
        if station_name:
            station_name=station_name.replace(" ","+")
            station_row=data_station.loc[data_station.stationName==station_name]
        elif station_ref:
            station_row=data_station.loc[data_station.stationReference==station_ref]
        if station_row.empty:
            return render_template_string('''<h1>stationName or stationReference doesn't exist</h1>''')             
        station_info_result["stationName"]=station_row.iloc[0]["stationName"]
        station_info_result["stationReference"]=station_row.iloc[0]["stationReference"]

        web_link=station_row.iloc[0]["stationURL"]
        web_link_information=requests.get(web_link).content
        web_link_information=web_link_information.decode('utf-8')
        web_link_information=json.loads(web_link_information)
        station_info_result["northing"]=web_link_information["items"]["northing"]
        station_info_result["easting"]=web_link_information["items"]["easting"]
        station_info_result["latitude"]=web_link_information["items"]["lat"]
        station_info_result["longitude"]=web_link_information["items"]["long"]
    return json.dumps(station_info_result)


# This is an example of a quick way to send a file.
# There is plenty of room for improvement.
@app.route('/data/graph')
def data_graph():
    """Return a graph of station data.

    The endpoint accepts query parameters:
    * stationName
    * stationRef
    * from
    * to
    """
    if request.method == 'GET':
        station_name=request.args.get('stationName')
        station_ref=request.args.get('stationReference')
        date_from=request.args.get('from')
        date_to=request.args.get('to')
        #print(station_name,date_from,date_to)
        data_station=pd.read_csv("stations.csv")
        if station_name:
            station_name=station_name.replace(" ","+")
            station_row=data_station.loc[data_station.stationName==station_name]
        elif station_ref:
            station_row=data_station.loc[data_station.stationReference==station_ref]
        if station_row.empty:
            return render_template_string('''<h1>stationName or stationReference doesn't exist</h1>''')
        station_name=station_row.iloc[0]["stationName"]
        graph_figure=reader.station_graph(station_name,time_from=date_from,time_to=date_to)
        plt.savefig("tmp.png")

    return send_from_directory(".", "tmp.png")

@app.route('/data/json',methods=['GET', 'POST'])
def data_json():
    if request.method=='GET':
        data_json_result={}
        station_name=request.args.get('stationName')
        station_ref=request.args.get('stationReference')
        date_from=request.args.get('from')
        date_to=request.args.get('to')
        data_statistics=request.args.get('statistic')
        data_station=pd.read_csv("stations.csv")
        if station_name:
            station_name=station_name.replace(" ","+")
            station_row=data_station.loc[data_station.stationName==station_name]
        elif station_ref:
            station_row=data_station.loc[data_station.stationReference==station_ref]
        if station_row.empty:
            return render_template_string('''<h1>stationName or stationReference doesn't exist</h1>''')
        data_json_result["stationName"]=station_row.iloc[0]["stationName"]
        station_name=data_json_result["stationName"]
        if data_statistics:
            data_json_result["stationReference"]=station_row.iloc[0]["stationReference"]
            if date_from:
                data_json_result["from"]=date_from
            else:
                data_json_result["from"]=reader.data.dateTime.unique()[0]
            if date_to:
                data_json_result["to"]=date_to
            else:
                data_json_result["to"]=reader.data.dateTime.unique()[-1]
            if data_statistics=="max":
                statistic_max=reader.max_tides(time_from=date_from,time_to=date_to)[station_name]
                data_json_result["max"]=statistic_max
            elif data_statistics=="min":
                statistic_min=reader.min_tides(time_from=date_from,time_to=date_to)[station_name]
                data_json_result["min"]=statistic_min
            elif data_statistics=="mean":
                statistic_mean=reader.mean_tides(time_from=date_from,time_to=date_to)[station_name]
                data_json_result["mean"]=statistic_mean
        else:
            station_tide_data=reader.station_tides(station_name,time_from=date_from,time_to=date_to)
            if date_from:
                data_json_result["from"]=date_from
            else:
                data_json_result["from"]=reader.data.dateTime.unique()[0]
            if date_to:
                data_json_result["to"]=date_to
            else:
                data_json_result["to"]=reader.data.dateTime.unique()[-1]
            data_json_result["tideValues"]={}
            for row in station_tide_data.itertuples():
                data_json_result["tideValues"][row[0]]=row[1]
        return json.dumps(data_json_result)

    elif request.method=='POST' :
        update_data_dict_all=request.json
        if request.args['write']=="true" or request.args['write']=="True":
            ifwrite=True
        else:
            ifwrite=False
        for update_data in update_data_dict_all:
                station_name_update=update_data["stationName"]
                datetime_update=update_data["dateTime"]
                tidevalue_update=update_data["tideValue"]
                reader.add_data(datetime_update,station_name_update,tidevalue_update)
        if ifwrite:
            reader.write_data("tideReadings.csv")
            #reader.write_data("try_update.csv")
        return Response(status=200)
@app.route('/data/html')
def data_html():
    if request.method=='GET':
        station_name=request.args.get('stationName')
        station_ref=request.args.get('stationReference')
        date_from=request.args.get('from')
        date_to=request.args.get('to')
        data_statistics=request.args.get('statistic')
        data_station=pd.read_csv("stations.csv")
        if not data_statistics:
            if station_name:
                station_name=station_name.replace(" ","+")
                station_row=data_station.loc[data_station.stationName==station_name]
            elif station_ref:
                station_row=data_station.loc[data_station.stationReference==station_ref]
            if station_row.empty:
                return render_template_string('''<h1>stationName or stationReference doesn't exist</h1>''')
            station_name=station_row.iloc[0]["stationName"]
            table_dict={}
            station_tide_data=reader.station_tides(station_name,time_from=date_from,time_to=date_to)
            for row in station_tide_data.itertuples():
                table_dict[row[0]]=row[1]
            return render_template_string('''<table style="width:30%"> <tr><td>dateTime</td><td>tideValue</td></tr>{% for date, tidevalue in table_dict.items() %} <tr><td>{{ date }}</td> <td>{{ tidevalue }}</td></tr>{% endfor %}</table>''', table_dict=table_dict)
        else:
            data_statistics=data_statistics.split(',')
            #print(data_statistics)
            station_all=data_station.stationName.unique()
            #print(station_all)
            table_dict2={}
            for station_name in station_all:
                table_dict2[station_name]=[]
                for calculation in data_statistics:
                    if calculation=="max":
                        statistic_max=reader.max_tides(time_from=date_from,time_to=date_to)[station_name]
                        table_dict2[station_name].append(statistic_max)
                    elif calculation=="min":
                        statistic_min=reader.min_tides(time_from=date_from,time_to=date_to)[station_name]
                        table_dict2[station_name].append(statistic_min)
                    elif calculation=="mean":
                        statistic_mean=reader.mean_tides(time_from=date_from,time_to=date_to)[station_name]
                        table_dict2[station_name].append(statistic_mean)
            return render_template_string('''<table style="width:50%"><tr><td>stationName</td>{%for cal_item in statistics_items %}<td> {{cal_item}}</td>{% endfor %}</tr>{% for station, calculations in table_dict2.items() %} <tr><td>{{ station }}</td> {%for calculate in calculations %} <td>{{ calculate }}</td> {% endfor %} </tr> {% endfor %} </table>''', table_dict2=table_dict2,statistics_items=data_statistics)