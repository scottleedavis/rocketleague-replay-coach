from json import load as json_load
from os.path import isfile as os_isfile

from constants import *
from replay_parse import ReplayParse
from jsonschema import validate, ValidationError


class RattlePlayer:

    def __init__(self, file_name):
        """Create a new RattlePlayer object."""

        self.file_name = file_name

        if not os_isfile(self.file_name):
            raise FileNotFoundError(f'File "{self.file_name}" does not exist')

        if not self.file_name.lower().endswith(".json"):
            raise ValueError(f'File "{self.file_name}" is not a json file')

        try:
            with open(self.file_name, mode="r", encoding="utf-8") as f:
                self.json_content = json_load(f)
        except Exception as e:
            raise ValueError(
                f'File "{self.file_name}" is not a valid json file'
            ) from e

        self.validate_json_schema(self.json_content)
        self.game = ReplayParse(self.json_content)


    def validate_json_schema(self, data):
        try:
            with open("schema.json", mode="r", encoding="utf-8") as f:
                validate(instance=data, schema=json_load(f))
        except ValidationError as e:
            print(f"JSON data is invalid: {e.message}")
            exit(-1)

    def generate_csv(self):
        """Replay the game."""
        frames = self.json_content["content"]["body"]["frames"]

        headers = [
            "time",
            "player_name",
            "team",
            "boost",
            "location_x",
            "location_y",
            "location_z",
            "rotation_x",
            "rotation_y",
            "rotation_z",
            "rotation_w",
            "linear_velocity_x",
            "linear_velocity_y",
            "linear_velocity_z",
            "angular_velocity_x",
            "angular_velocity_y",
            "angular_velocity_z",
            "speed",
            "distance_to_ball",
        ]
        output = ",".join(headers) + "\n"

        for i, frame in enumerate(frames):
            self.game.update(i, frame)
            output += self.game.dump()

        return output
