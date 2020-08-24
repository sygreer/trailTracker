from yattag import Doc
from yattag import indent

doc, tag, text = Doc().tagtext()

with tag('html'):
    with tag('head'):
        with tag('title'):
            text("Hiking | Sarah Greer")
        doc.stag('link', rel="stylesheet", type="text/css", href="style.css", title="style") 

    with tag('body'):
        with tag('div', id = 'canvas_proj', style="width: 850px;"):
            with tag('div', id='nav'):
                with tag('a', href='../'):
                    with tag('button', type='submit'):
                        text("&#8592; Back home")
            with tag("h1"):
                text("Hiking and Travel")
            doc.stag("br")
            with tag("div", style="text-align:center;"):
                doc.stag("iframe", src="map.html", width="850", height="800")

            with tag('p', id = 'main'):
                text('some text')
            with tag('a', href='/my-url'):
                text('some link')

#result = indent(doc.getvalue())
#print(result)

with open('index.html', 'w') as f:
    f.write(indent(doc.getvalue(), indent_text=True)) 
