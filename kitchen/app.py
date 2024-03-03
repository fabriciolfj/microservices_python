from pathlib import Path

import yaml
from apispec import APISpec
from flask import Flask
from flask_smorest import Api

from config import BaseConfig
from api.api import blueprint

app = Flask(__name__)
app.config.from_object(BaseConfig)

kitchen_api = Api(app)

kitchen_api.register_blueprint(blueprint)

api_sec = yaml.safe_load((Path(__file__).parent / "oas.yaml").read_text())
spec = APISpec(
    title=api_sec["info"]["title"],
    version=api_sec["info"]["version"],
    openapi_version=api_sec["openapi"],
)

spec.to_dict = lambda: api_sec
kitchen_api.spec = spec
