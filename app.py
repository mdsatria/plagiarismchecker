from flask import Flask, render_template, request
from plagiarismchecker import corpusSimID
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from bokeh import palettes
from bokeh.models import LinearColorMapper, ColorBar, PrintfTickFormatter
from math import pi

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # ts = time.time() * 1000
        # ts = ts + random.randint(0,9999)
        path = request.form.get("path")
        path = path + "/"
        ftype = request.form.get("filetype")
        stemOn = request.form.get("stem")
        # cmap = request.form.get("cmap")
        obj = corpusSimID(path, stemOn, ftype)
        df = obj.get_dataframe()
        corp = obj.get_file()
        # return render_template('result.html', url='/static/images/{}.png'.format(ts))
        colors = list(reversed(palettes.viridis(100)))

        mapper = LinearColorMapper(palette=colors, low=0, high=100)
        TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"
        hm = figure(x_range=corp, y_range=list(reversed(corp)), x_axis_location="above",
                    plot_width=900,
                    plot_height=900,
                    tools=TOOLS,
                    toolbar_location='below',
                    tooltips=[('score','@c%'), ('doc_1', '@a'), ('doc_2', '@b')])

        hm.grid.grid_line_color = None
        hm.axis.axis_line_color = None
        hm.axis.major_tick_line_color = None
        hm.axis.major_label_text_font_size = "8pt"
        hm.axis.major_label_standoff = 0
        hm.xaxis.major_label_orientation = pi / 3

        hm.rect(x="a", y="b", source=df,
                width=1, height=1, line_color="#ffffff",
                fill_color={'field': 'c', 'transform': mapper}
                )

        color_bar = ColorBar(color_mapper=mapper,
                             formatter=PrintfTickFormatter(format="%d%%"),
                             major_label_text_font_size="10pt",label_standoff=10,
                             border_line_color=None, location=(0, 0))
        
        hm.add_layout(color_bar, 'right')

        js_resources = INLINE.render_js()
        css_resources = INLINE.render_css()

        # render template
        script, div = components(hm)
        html = render_template(
            'result.html',
            plot_script=script,
            plot_div=div,
            js_resources=js_resources,
            css_resources=css_resources,
        )
        return encode_utf8(html)
    else:
        return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)