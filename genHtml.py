from yattag import Doc
from yattag import indent
from datetime import timedelta
from os import walk
from os.path import splitext, exists

#data = ["IceLakeMatterhorn", "Ice Lake and Matterhorn"]

def genHtml(data):
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
                #text("Hiking | Sarah Greer")
                text("%s | Sarah Greer"%data[1])
            doc.stag('link', rel="stylesheet", type="text/css", href="../../style.css", title="style") 
            with tag("script", src="https://code.jquery.com/jquery-3.3.1.js", integrity="sha256-2Kok7MbOyxpgUVvAk/HJ2jigOSYS2auK4Pfzbm7uH60=", crossorigin="anonymous"):
                text("")
            with tag("script", type="text/javascript"):
                text("function loadFrame (elm){var frame1 = document.getElementById('frame1');frame1.src = elm.dataset.src}")



    
        with tag('body'):
            with tag('div', id = 'canvas_proj', style="width: 850px;"):
                with tag('div', id='nav'):
                    with tag('a', href='../'):
                        with tag('button', type='submit'):
                            text("&#8592; Back home")
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

                    with tag("h2"):
                        text("Details")

                    moreInfo= 'hikes/%s/more.html'%data[0]
                    if (exists(moreInfo)):
                        with tag("div", id="more"):
                            text("")
                    else:
                        text("No further details have been added for this hike.")
                    doc.stag("br")
                    doc.stag("br")

                    with tag("h2"):
                        text("Photos")
                    if (len(pics) ==0):
                        text("No pictures have been added for this hike.")
                    else:
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


genHtml(data)

