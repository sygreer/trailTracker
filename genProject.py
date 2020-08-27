from os import listdir
from yattag import Doc
from yattag import indent
from datetime import timedelta
from shutil import copyfile
from math import floor
from os import walk
from os.path import splitext, exists
import gpxpy
import os
from geopy import distance
from math import sqrt, floor
import numpy as np
import pandas as pd
import haversine
import plotly.express as px
import numpy as np

M_TO_FT = 3.28084
FT_TO_MI = 1.0/5280

def analyzeGpx(name):
    fileName = 'hikes/%s/%s.gpx'%(name,name)
    gpx_file = open(fileName, 'r')
    projName = os.path.splitext(os.path.basename(fileName))[0]
    dirName = os.path.dirname(fileName)
    
    gpx = gpxpy.parse(gpx_file)
    nameRecording = gpx.name
    if (nameRecording == None):
        nameRecording = projName
    
    data = gpx.tracks[0].segments[0].points
    for i in range(1, len(gpx.tracks[0].segments)):
        data.extend(gpx.tracks[0].segments[i].points)
    
    # Start Position
    start = data[0]
    # End Position
    finish = data[-1]

    df = pd.DataFrame(columns=['lon', 'lat', 'alt', 'time'])
    for point in data:
        df = df.append({'lon': point.longitude, 'lat' : point.latitude, 'alt' : point.elevation*M_TO_FT, 'time' : point.time}, ignore_index=True)
    
    alt_dif = [0]
    time_dif = [0]
    dist_hav = [0]
    dist_hav_no_alt = [0]
    dist_dif_hav_2d = [0]

    alt_inc = 0
    alt_dec = 0

    # elevation moving average over 50 points
    alt_inc50 = 0
    alt_dec50 = 0
    dist500 = 0
    
    for index in range(len(data)):
        if index == 0:
            pass
        else:
            start = data[index-1]
            
            stop = data[index]
            
            distance_hav_2d = haversine.haversine((start.latitude, start.longitude), (stop.latitude, stop.longitude))*1000
            dist_dif_hav_2d.append(distance_hav_2d)
            
            dist_hav_no_alt.append(dist_hav_no_alt[-1] + distance_hav_2d)
            
            alt_d = (start.elevation - stop.elevation) * M_TO_FT

            if (alt_d > 0):
                alt_inc = alt_inc + alt_d
            else:
                alt_dec = alt_dec - alt_d
            
            alt_dif.append(alt_d)
            
            distance_hav_3d = sqrt(distance_hav_2d**2 + (alt_d)**2) * M_TO_FT * FT_TO_MI
                    
            time_delta = (stop.time - start.time).total_seconds()
            
            time_dif.append(time_delta)
                    
            dist_hav.append(dist_hav[-1] + distance_hav_3d)

            if (index%50==0):
                startel = data[index-50].elevation 
                dif_elev = (stop.elevation - startel) *M_TO_FT
                if (dif_elev > 0):
                    alt_inc50 = alt_inc50 + dif_elev
                else:
                    alt_dec50 = alt_dec50 - dif_elev
            if (index%500==0):
                dist500 = dist500 + (dist_hav[index] - dist_hav[index-500]) 
    
    increase = gpx.get_uphill_downhill()[0] * M_TO_FT
    decrease = gpx.get_uphill_downhill()[1] * M_TO_FT
    length = gpx.length_2d()*M_TO_FT*FT_TO_MI

    ratioCorrection = 0.55

    dist500 = length*ratioCorrection

    ratioCorrection2 = dist500/dist_hav[-1]

    df['dist_hav_2d'] = dist_hav_no_alt
    df['dis_hav_3d'] = np.asarray(dist_hav) * ratioCorrection2
    df['alt_dif'] = alt_dif
    df['time_dif'] = time_dif
    df['dis_dif_hav_2d'] = dist_dif_hav_2d

    #df['spd'] = (df['dis_dif_hav_2d'] / df['time_dif']) * 3.6 * 0.621371 # speed in mph
    
    timeTot = "%i hours, %i minutes" %(floor(sum(time_dif)/60/60), floor(sum(time_dif)/60%60))
    
    fig = px.line_3d(df, x='lon', y='lat', z='alt', labels={'lon':'Longitude', 'lat':'Latitude', 'alt':'Elevation (feet)'})
    fig.write_html("%s/3d.html"%dirName)
    
    fig2 = px.line(df, x='dis_hav_3d', y='alt', labels={'dis_hav_3d':'Distance (miles)', 'alt':'Altitude (feet)'})
    fig2.write_html("%s/elev.html"%dirName)

    return [name, nameRecording, timeTot, data[0].time, data[-1].time, "%.2f"%dist500, "%.0f"%alt_inc50, "%.0f"%alt_dec50, sum(time_dif)]
    

def genSubpage(data):
    doc, tag, text = Doc().tagtext()

    # get pictures
    dirName = 'hikes/%s/'%data[0]
    f = []
    pics = []
    for (dirpath, dirnames, filenames) in walk(dirName):
        f.extend(filenames)
    for fileN in f:
        fn, fext = splitext(fileN)
        if (fext.lower() == ".jpg" or fext.lower() ==".jpg"):
            pics.append(fileN)

    with tag('html'):
        with tag('head'):
            with tag('title'):
                text("%s "%data[1])
            doc.stag('link', rel="stylesheet", type="text/css", href="../../style.css", title="style") 
            with tag("script", src="https://code.jquery.com/jquery-3.3.1.js", integrity="sha256-2Kok7MbOyxpgUVvAk/HJ2jigOSYS2auK4Pfzbm7uH60=", crossorigin="anonymous"):
                text("")
            with tag("script", type="text/javascript"):
                text("function loadFrame (elm){var frame1 = document.getElementById('frame1');frame1.src = elm.dataset.src}")
            with tag("script"):
                text('$(function(){$("#more").load("more.html"); });')
    
        with tag('body'):
            with tag('div', id = 'canvas_proj', style="width: 850px;"):
                with tag('div', id='nav'):
                    with tag('a', href='../../'):
                        with tag('button', type='submit'):
                            text("← Back")
                with tag("h1"):
                    #text("Hiking and Travel")
                    text(data[1])
                doc.stag("br")
                with tag("div", style="text-align:center;"):
                    with tag("iframe", src="map.html", width="850", height="800"):
                        text("")
                    doc.stag("br")
                    doc.stag("br")
                    with tag('p'):
                        with tag("h2"):
                            text("Statistics")
                        with tag("b"):
                            text("Start time:")
                        datestart = data[3] - timedelta(hours=7)
                        date_time = datestart.strftime("%m/%d/%Y, %I:%M %p Pacific Time") 
                        text(date_time)
                        doc.stag("br")
                        with tag("b"):
                            text("End time:")
                        dateend = data[4] - timedelta(hours=7)
                        date_time = dateend.strftime("%m/%d/%Y, %I:%M %p Pacific Time") 
                        text(date_time)
                        doc.stag("br")
                        with tag("b"):
                            text("Total time:")
                        text(data[2])
                        doc.stag("br")
                        doc.stag("br")
                        with tag("b"):
                            text("Total distance:")
                        text("%s miles"%data[5])
                        doc.stag("br")
                        with tag("b"):
                            text("Elevation change:")
                        text("+%s feet, -%s feet"%(data[6], data[7]))
                    doc.stag("br")
                    doc.stag("br")

                    moreInfo= 'hikes/%s/more.html'%data[0]
                    if (exists(moreInfo)):
                        with tag("h2"):
                            text("Details")
                        with tag("div", id="more"):
                            text("")
                        doc.stag("br")
                        doc.stag("br")

                    if (len(pics) !=0):
                        with tag("h2"):
                            text("Photos")
                        text("Click on the picture to view it full size.")
                        doc.stag("br")
                        for pic in pics:
                            with tag("a", href=pic):
                                doc.stag("img", src=pic, width="280px")
                        doc.stag("br")
                        doc.stag("br")
                        
                    with tag("h2"):
                        text("Elevation profile")
                    with tag("a", href="elev.html", target="eleviframe"):
                        with tag('button', type='submit'):
                            text("Click to load figure below.")
                    with tag("iframe", name="eleviframe", src="about:blank", width="850", height="400"):
                        text("")
                    doc.stag("br")
                    doc.stag("br")
                    with tag("h2"):
                        text("3D trip view")
                    with tag("a", href="3d.html", target="myiFrame"):
                        with tag('button', type='submit'):
                            text("Click to load figure below.")
                    with tag("iframe", name="myiFrame", src="about:blank", width="850", height="850"):
                        text("")
                    doc.stag("br")
                    doc.stag("br")



    with open('hikes/%s/index.html'%data[0], 'w') as f:
        f.write(indent(doc.getvalue(), indent_text=True)) 


def genProject():
    doc, tag, text = Doc().tagtext()
    with tag('table', ("class","tg"), style="margin-right:auto; margin-left:auto"):
        with tag("tr"):
            with tag("th", ("class","tg-yw4l")):
                text("Hike name")
            with tag("th", ("class","tg-yw4l")):
                text("Start date")
            with tag("th", ("class","tg-yw4l")):
                text("Hike time")
            with tag("th", ("class","tg-yw4l")):
                text("Distance (miles)")
            with tag("th", ("class","tg-yw4l")):
                text("Elevation gain (feet)")
            with tag("th", ("class","tg-yw4l")):
                text("Elevation loss (feet)")

        totTime = 0
        totDist = 0
        totGain = 0
        totLoss = 0
        for hike in listdir('./hikes/'):
            if (hike=="other"):
                continue
            print("Getting data for hike %s"%hike)
            data = analyzeGpx(hike)
            print("Generating HTML pages for hike %s"%hike)
            genSubpage(data)
            with tag("tr"):
                with tag("td", ("class","tg-yw4l")):
                    with tag("a", href="hikes/%s"%(data[0])):
                        text(data[1])
                with tag("td", ("class","tg-yw4l")):
                    datestart = data[3] - timedelta(hours=7)
                    date_time = datestart.strftime("%m/%d/%Y, %I:%M %p Pacific Time") 
                    text(date_time)
                with tag("td", ("class","tg-yw4l")):
                    text(data[2])
                with tag("td", ("class","tg-yw4l")):
                    text(data[5])
                with tag("td", ("class","tg-yw4l")):
                    text(data[6])
                with tag("td", ("class","tg-yw4l")):
                    text(data[7])
            totTime = totTime + data[8]
            totDist = totDist + float(data[5])
            totGain = totGain + float(data[6])
            totLoss = totLoss + float(data[7])
            copyfile("./mapTemplate.html", "hikes/%s/map.html"%hike)


    with tag("div", style="text-align:center;"):
        with tag("b"):
            text("Total distance: ")
        text("%.2f miles"%totDist)
        doc.stag('br')
        with tag("b"):
            timeTot = "%i days, %i hours, %i minutes" %(floor(totTime/60/60/24), floor(totTime/60/60), floor(totTime)/60%60)

            text("Total time: ")
        text(timeTot)
        doc.stag('br')
        with tag("b"):
            text("Total elevation gain: ")
        text("%.0f feet"%totGain)
        doc.stag('br')
        with tag("b"):
            text("Total elevation loss: ")
        text("%.0f feet"%totLoss)
        doc.stag('br')
    
    with open('hikes.html', 'w') as f:
        f.write(indent(doc.getvalue(), indent_text=True)) 

if __name__ =="__main__":
    genProject()
