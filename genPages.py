from genHtml import genHtml
from visualizeGpx import analyzeGpx
from os import listdir
from yattag import Doc
from yattag import indent
from datetime import timedelta
from shutil import copyfile


def generateHtml():
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
        for hike in listdir('./hikes/'):
            if (hike=="other"):
                continue
            print("Getting data for hike %s"%hike)
            data = analyzeGpx(hike)
            print("Generating HTML pages for hike %s"%hike)
            genHtml(data)
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
            copyfile("./mapTemplate.txt", "hikes/%s/map.html"%hike)


    with open('hikes.html', 'w') as f:
        f.write(indent(doc.getvalue(), indent_text=True)) 

generateHtml()
