import yaml
import json


def get_yaml(filePath):
    with open(filePath, "r") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    return config


def get_json(filePath):
    with open(filePath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
