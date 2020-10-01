from flask import Flask, render_template, request

from plagiarismchecker import corpusSimID

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh import palettes
from bokeh.models import LinearColorMapper, ColorBar, PrintfTickFormatter

from math import pi
import os

"""
    Create Plot
"""


def make_plot(df, corp, color_palette):

    palette_list = [
        palettes.viridis(100),
        palettes.inferno(100),
        palettes.magma(100),
        palettes.plasma(100),
    ]
    colors = list(reversed(palette_list[color_palette]))
    mapper = LinearColorMapper(palette=colors, low=0, high=100)

    TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"
    TOOLTIPS = """
                <div>
                    <div>
                    <span style="font-size: 20px; font-weight: bold;">score: @c%</span>
                    </div>
                    <div>
                        <span style="font-size: 16px; font-style: italic;">@a & @b</span>
                    </div>
                </div>
    """
    # tooltips=[('score','@c%'), ('doc_1', '@a'), ('doc_2', '@b')])

    hm = figure(
        x_range=corp,
        y_range=list(reversed(corp)),
        x_axis_location="above",
        plot_width=900,
        plot_height=900,
        tools=TOOLS,
        toolbar_location="below",
        tooltips=TOOLTIPS,
    )    

    hm.grid.grid_line_color = None
    hm.axis.axis_line_color = None
    hm.axis.major_tick_line_color = None
    hm.axis.major_label_text_font_size = "8pt"
    hm.axis.major_label_standoff = 0
    hm.xaxis.major_label_orientation = pi / 3

    hm.rect(
        x="a",
        y="b",
        source=df,
        width=1,
        height=1,
        line_color="#ffffff",
        fill_color={"field": "c", "transform": mapper},
    )

    color_bar = ColorBar(
        color_mapper=mapper,
        formatter=PrintfTickFormatter(format="%d%%"),
        major_label_text_font_size="10pt",
        label_standoff=10,
        border_line_color=None,
        location=(0, 0),
    )

    hm.add_layout(color_bar, "right")

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    script, div = components(hm)

    return js_resources, css_resources, script, div


def check_path(directory, file_type):
    if (os.path.isdir(directory)) == False:
        return True

    path = os.listdir(directory)
    if file_type == "text":
        lst = [i for i in path if i.endswith(".txt")]
    elif file_type == "word":
        lst = [i for i in path if i.endswith(".docx")]
    else:
        lst = [i for i in path if i.endswith(".pdf")]
    if not lst:
        return True


"""
    SERVER RUN
"""
app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        # get data
        path = request.form.get("path")
        path = path + "/"
        ftype = request.form.get("filetype")
        stemOn = request.form.get("stem")
        color_palette = int(request.form.get("npalette"))

        isNotExist = check_path(path, ftype)
        if isNotExist:
            return render_template("error.html")

        # calculate similarity
        simClass = corpusSimID(path, stemOn, ftype)
        df = simClass.get_dataframe()
        corp = simClass.get_file()

        # create plot
        js_resources, css_resources, script, div = make_plot(
            df, corp, color_palette)

        return render_template(
            "result.html",
            plot_script=script,
            plot_div=div,
            js_resources=js_resources,
            css_resources=css_resources,
        )
    else:
        return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)
