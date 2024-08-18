## enter the venv: source venv/Scripts/activate
## run the application: flask --app APP_FOLDER_NAME_HERE run --debug
## initialize the database (i.e. reset/create): flask --app APP_NAME_HERE init-db

from flask import Flask, render_template
import io
from base64 import b64encode
from dataclasses import dataclass, field
from typing import Any
import matplotlib
matplotlib.use('Agg')  # Use the non-interactive Agg backend

from plot import create_fig
from data import *

app = Flask(__name__)

@dataclass
class Figure:
    figure: Any  # This should be a Matplotlib figure object
    template_path: str = field(kw_only=True, default="index.html")

    @property
    def _mime_type(self) -> str:
        return "image/png"

    @property
    def _base64_data(self) -> str:
        buffer = io.BytesIO()
        self.figure.savefig(buffer, format="png", dpi=300, bbox_inches="tight")
        buffer.seek(0)
        return b64encode(buffer.getvalue()).decode()



sources = {
    1: {
        "title": "Inflation",
        "images": [
            {"path": Figure(figure=create_fig(eu_inflation_tweaked_filtered)), 
             "comment": "Text space here for comments to provide context"},
            {"path": Figure(figure=create_fig(eu_inflation_yoy_tweaked)), 
             "comment": "Text space here for comments to provide context"}
        ]
    },
    2: {
        "title": "Labour",
        "images": [
            {"path": Figure(figure=create_fig(labour_by_country_tweaked)), 
             "comment": "Text space here for comments to provide context"},
            {"path": Figure(figure=create_fig(labour_by_industry_tweaked)), 
             "comment": "Text space here for comments to provide context"}
        ]
    },
    3: {
        "title": "Transport & Fuel",
        "images": [
            {"path": Figure(figure=create_fig(transport_tweaked, legend_loc="right")), 
             "comment": "Text space here for comments to provide context"},
            {"path": Figure(figure=create_fig(fuel_tweaked_crude)), 
             "comment": "Text space here for comments to provide context"},
            {"path": Figure(figure=create_fig(fuel_tweaked_not_crude)), 
             "comment": "Text space here for comments to provide context"}
        ]
    },
    4: {
        "title": "Food Oils & Agriculture",
        "images": [
            {"path": Figure(figure=create_fig(food_oils)), 
             "comment": "Text space here for comments to provide context"},
            {"path": Figure(figure=create_fig(agriculture_cereals, legend_loc="right", type="year")),
             "comment": "Text space here for comments to provide context"}
        ]
    },
    5: {
        "title": "Food Oils & Agriculture Continued",
        "images": [
            {"path": Figure(figure=create_fig(agriculture_dry_pulses, legend_loc="right")),
             "comment":" Text space here for comments to provide context"},
            {"path": Figure(figure=create_fig(agriculture_vegetables, legend_loc="right")),
             "comment":" Text space here for comments to provide context"}
        ]
    }
}


@app.route('/')
def index():

    return render_template(
        'index.html', month="Aug-24",
        sources=sources
        )


if __name__ == '__main__':
    app.run(debug=True)