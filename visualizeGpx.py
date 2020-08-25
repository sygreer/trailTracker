# from https://towardsdatascience.com/how-tracking-apps-analyse-your-gps-data-a-hands-on-tutorial-in-python-756d4db6715d
import gpxpy
import os
#import matplotlib.pyplot as plt
import datetime
from geopy import distance
from math import sqrt, floor
import numpy as np
import pandas as pd
#import plotly.plotly as py
#import plotly.graph_objs as go
import haversine
import plotly.express as px
import numpy as np

M_TO_FT = 3.28084
FT_TO_MI = 1.0/5280

# Parsing an existing file:
# -------------------------

#fileName = '/home/sarah/sygreer/hiking/gpx/IceLakeMatterhorn.gpx'
#fileName = 'hikes/IceLakeMatterhorn/IceLakeMatterhorn.gpx'
#fileName = 'hikes/WallowaMountainsLakesBasin/IceLakeMatterhorn.gpx'

def analyzeGpx(name):
    fileName = 'hikes/%s/%s.gpx'%(name,name)
    gpx_file = open(fileName, 'r')
    projName = os.path.splitext(os.path.basename(fileName))[0]
    dirName = os.path.dirname(fileName)
    
    gpx = gpxpy.parse(gpx_file)
    nameRecording = gpx.name
    if (nameRecording == None):
        nameRecording = projName
    
    #data = []
    data = gpx.tracks[0].segments[0].points
    for i in range(1, len(gpx.tracks[0].segments)):
        data.extend(gpx.tracks[0].segments[i].points)
    #data = gpx.tracks[0].segments[2].points
    
    ## Start Position
    start = data[0]
    ## End Position
    finish = data[-1]

    df = pd.DataFrame(columns=['lon', 'lat', 'alt', 'time'])
    for point in data:
        df = df.append({'lon': point.longitude, 'lat' : point.latitude, 'alt' : point.elevation*M_TO_FT, 'time' : point.time}, ignore_index=True)
    
    #plt.plot(df['lon'], df['lat'])
    #plt.show()
    
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

    ratioCorrection = 0.65

    dist500 = dist500*ratioCorrection
    print(dist500)

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

    #return [name, nameRecording, timeTot, data[0].time, data[-1].time, "%.2f"%dist_hav[-1], "%.0f"%alt_inc25, "%.0f"%alt_dec25]
    return [name, nameRecording, timeTot, data[0].time, data[-1].time, "%.2f"%dist500, "%.0f"%alt_inc50, "%.0f"%alt_dec50]
    #return [name, nameRecording, timeTot, data[0].time, data[-1].time, "%.2f"%length, "%.0f"%increase, "%.0f"%decrease]
    


if __name__ == "__main__":
    #data = analyzeGpx("IceLakeMatterhorn")
    data = analyzeGpx("WallowaMountainsLakesBasin")
    print(data)


