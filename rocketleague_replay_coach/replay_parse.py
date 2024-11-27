import math
from constants import *


class ReplayParse:

    def __init__(self, json_content):
        self.num_frames = len(json_content["content"]["body"]["frames"])
        self.time = 0.0
        self.current_fps = 0.0
        self.actors = {}
        self.properties = json_content["header"]["body"]["properties"][
            "elements"
        ]
        self.map_name = self.find_property("MapName")
        self.ball_id = None
        self.seconds_remaining = 300
        self.frame_index = 0
        self.game_playlist = None
        self.game_region = None


    def find_property(self, property_name):
        for element in self.properties:
            if element[0] == property_name:
                if element[1]['kind'] == 'IntProperty':
                    return element[1]['value']['int']
                if element[1]['kind'] == 'StrProperty':
                    return element[1]['value']['str']
                if element[1]['kind'] == 'FloatProperty':
                    return element[1]['value']['float']
                if element[1]['kind'] == 'NameProperty':
                    return element[1]['value']['name']
                return element[1]['value']
        return None


    def update(self, frame_index, frame):

        self.time = frame["time"]
        delta = frame["delta"]
        self.current_fps = 0 if delta == 0 else 1 / delta
        self.frame_index = frame_index


        self.add_actors(frame["replications"])
        self.update_actors(frame["replications"])

        self.player_car_pairs = self.get_player_car_pairs()
        self.ball_id = self.get_ball()

        self.calculate()


    def add_actors(self, actors):
        for actor in actors:
            actor_id = actor["actor_id"]["value"]

            if "value" in actor and "spawned" in actor["value"]:
                spawned = actor["value"]["spawned"]
                a = {}
                a["object_id"] = spawned.get("object_id", None)
                a["object_name"] = spawned.get("object_name", None)
                a["name_id_name"] = spawned.get("name", None)
                a["created_at_frame"] = self.frame_index
                a["parent_ids"] = []
                if "initialization" in spawned:
                    a["location"] = spawned['initialization']['location']
                    a["rotation"] = spawned['initialization']['rotation']
                self.actors[actor_id] = a
                self.parse_object(actor, spawned)
            else:
                # print(f"Warning: 'spawned' not found for actor {actor_id}. Skipping actor.")
                continue

    def update_actors(self, actors):
        for actor in actors:
            if "value" in actor and "updated" in actor["value"]:
                updated_list = actor["value"]["updated"]
                for updated in updated_list:
                    self.parse_object(actor, updated)
            else:
                # print(f"Warning: 'updated' not found for actor {actor_id}. Skipping actor.")
                continue


    def parse_object(self, actor, updated):
        actor_id = actor["actor_id"]["value"]
        object_name = updated.get("name", None)
        object_id = updated.get("id", {}).get("value", None)
        if object_id is not None:
            self.actors[actor_id]["object_id"] = object_id

        match object_name:

            case "Engine.Actor:RemoteRole":
                self.actors[actor_id]["remote_role"] = updated["value"]["enum"]

            case "TAGame.PRI_TA:PersistentCamera":
                self.actors[actor_id]["parent_ids"].append(
                    updated["value"]["flagged_int"]["int"]
                )

            case "TAGame.CameraSettingsActor_TA:PRI":
                self.actors[actor_id]["parent_ids"].append(
                    updated["value"]["flagged_int"]["int"]
                )

            case "TAGame.Ball_TA:GameEvent":
                self.actors[actor_id]["parent_ids"].append(
                    updated["value"]["flagged_int"]["int"]
                )

            case "TAGame.CarComponent_TA:Vehicle":
                self.actors[actor_id]["parent_ids"].append(
                    updated["value"]["flagged_int"]["int"]
                )

            case "Engine.Pawn:PlayerReplicationInfo":
                self.actors[actor_id]["parent_ids"].append(
                    updated["value"]["flagged_int"]["int"]
                )

            case "Engine.PlayerReplicationInfo:Ping":
                self.actors[actor_id]["active"] = updated["value"]["byte"]

            case "TAGame.CarComponent_Boost_TA:ReplicatedBoost":
                self.actors[actor_id]["boost"] = updated["value"]["boost"][
                    "boostAmount"
                ]

            case "TAGame.PRI_TA:ReplicatedGameEvent":
                self.actors[actor_id]["time_remaining"] = updated["value"][
                    "flagged_int"
                ]["int"]

            case "TAGame.GameEvent_TA:ReplicatedStateName":
                self.actors[actor_id]["stateName"] = updated["value"]["int"]

            case "TAGame.GameEvent_TA:BotSkill":
                self.actors[actor_id]["bot_skill"] = updated["value"]["int"]

            case "TAGame.GameEvent_TA:bHasLeaveMatchPenalty":
                self.actors[actor_id]["has_leave_match_penalty"] = updated[
                    "value"
                ]["boolean"]

            case "TAGame.GameEvent_Team_TA:MaxTeamSize":
                self.actors[actor_id]["max_team_size"] = updated["value"]["int"]

            case "TAGame.GameEvent_Soccar_TA:SecondsRemaining":
                self.seconds_remaining = updated["value"]["int"]
                self.actors[actor_id]["seconds_remaining"] = updated["value"][
                    "int"
                ]

            case "TAGame.RBActor_TA:ReplicatedRBState":
                rigid_body_state = updated["value"]["rigid_body_state"]
                for key in ["location", "rotation", "angular_velocity", "linear_velocity"]:
                    if key in rigid_body_state and rigid_body_state[key] is not None:
                        self.actors[actor_id][key] = rigid_body_state[key]

            case "TAGame.Vehicle_TA:ReplicatedSteer":
                self.actors[actor_id]["steer"] = updated["value"]["byte"]

            case "TAGame.Vehicle_TA:ReplicatedThrottle":
                self.actors[actor_id]["throttle"] = updated["value"]["byte"]

            case "TAGame.Car_TA:TeamPaint":
                self.actors[actor_id]["team_paint"] = updated["value"]["team_paint"]
                self.actors[actor_id]["team"] = updated["value"]["team_paint"]["team"]

            case "TAGame.CameraSettingsActor_TA:CameraYaw":
                self.actors[actor_id]["camera_yaw"] = updated["value"]["byte"]

            case "TAGame.CameraSettingsActor_TA:CameraPitch":
                self.actors[actor_id]["camera_pitch"] = updated["value"]["byte"]

            case "TAGame.CameraSettingsActor_TA:ProfileSettings":
                self.actors[actor_id]["camera_settings"] = updated["value"][
                    "cam_settings"
                ]

            case "TAGame.CameraSettingsActor_TA:bUsingSecondaryCamera":
                self.actors[actor_id]["using_ball_cam"] = updated["value"][
                    "boolean"
                ]

            case "Engine.PlayerReplicationInfo:UniqueId":
                self.actors[actor_id]["unique_id"] = updated["value"][
                    "unique_id"
                ]

            case "Engine.PlayerReplicationInfo:Team":
                self.actors[actor_id]["team"] = updated["value"]["flagged_int"][
                    "int"
                ]

            case "Engine.PlayerReplicationInfo:PlayerID":
                self.actors[actor_id]["player_id"] = updated["value"]["int"]

            case "Engine.PlayerReplicationInfo:PlayerName":
                self.actors[actor_id]["player_name"] = updated["value"][
                    "string"
                ]

            case "Engine.PlayerReplicationInfo:Ping":
                self.actors[actor_id]["ping"] = updated["value"]["byte"]

            case "TAGame.PRI_TA:CurrentVoiceRoom":
                self.actors[actor_id]["current_voice_room"] = updated["value"][
                    "string"
                ]

            case "TAGame.PRI_TA:SpectatorShortcut":
                self.actors[actor_id]["spectator_shortcut"] = updated["value"][
                    "int"
                ]

            case "TAGame.PRI_TA:SteeringSensitivity":
                self.actors[actor_id]["steering_sensitivity"] = updated[
                    "value"
                ]["float"]

            case "TAGame.PRI_TA:Title":
                self.actors[actor_id]["title"] = updated["value"]["int"]

            case "TAGame.PRI_TA:PartyLeader":
                self.actors[actor_id]["party_leader_id"] = updated["value"][
                    "party_leader"
                ]["id"]

            case "TAGame.PRI_TA:ClientLoadoutsOnline":
                self.actors[actor_id]["loadout_online"] = updated["value"][
                    "loadouts_online"
                ]

            case "TAGame.PRI_TA:ClientLoadouts":
                self.actors[actor_id]["team_loadout"] = updated["value"][
                    "loadouts"
                ]

            case "TAGame.PRI_TA:ReplicatedGameEvent":
                other_actor_id = updated["value"]["flagged_int"]["int"]
                if other_actor_id != -1:
                    if "frames_with_event" not in self.actors[other_actor_id]:
                        self.actors[other_actor_id]["frames_with_event"] = []
                    self.actors[other_actor_id]["frames_with_event"].append(
                        self.frame_index
                    )

            case "TAGame.PRI_TA:PlayerHistoryValid":
                self.actors[actor_id]["player_history_valid"] = updated[
                    "value"
                ]["boolean"]

            case "TAGame.GameEvent_Soccar_TA:MaxScore":
                self.actors[actor_id]["score"] = updated["value"]["int"]

            case "TAGame.CarComponent_Dodge_TA":
                self.actors[actor_id]["location"] = updated["value"]["Location"]

            case "Engine.GameReplicationInfo:ServerName":
                self.actors[actor_id]["server"] = updated["value"]["string"]

            case "ProjectX.GRI_X:MatchGuid":
                self.actors[actor_id]["match_guid"] = updated["value"]["string"]

            case "ProjectX.GRI_X:bGameStarted":
                self.actors[actor_id]["game_started"] = updated["value"][
                    "boolean"
                ]

            case "ProjectX.GRI_X:GameServerID":
                self.actors[actor_id]["server_id"] = updated["value"][
                    "game_server"
                ]["new"]

            case "ProjectX.GRI_X:Reservations":
                self.actors[actor_id]["reservation"] = updated["value"][
                    "reservation"
                ]

            case "ProjectX.GRI_X:ReplicatedServerRegion":
                self.actors[actor_id]["region"] = updated["value"]["string"]
                self.game_region = updated["value"]["string"]

            case "ProjectX.GRI_X:ReplicatedGamePlaylist":
                game_playlist_id = updated["value"]["int"]
                game_playlist = "unknown"

                if game_playlist_id == GAME_PLAYLIST_CASUAL_DUEL:
                    game_playlist = "casual_duel"
                elif game_playlist_id == GAME_PLAYLIST_CASUAL_DOUBLE:
                    game_playlist = "casual_double"
                elif game_playlist_id == GAME_PLAYLIST_CASUAL_STANDARD:
                    game_playlist = "casual_standard"
                elif game_playlist_id == GAME_PLAYLIST_CASUAL_CHAOS:
                    game_playlist = "casual_chaos"
                elif game_playlist_id == GAME_PLAYLIST_RANKED_DUEL:
                    game_playlist = "ranked_duel"
                elif game_playlist_id == GAME_PLAYLIST_RANKED_DOUBLE:
                    game_playlist = "ranked_double"
                elif game_playlist_id == GAME_PLAYLIST_RANKED_STANDARD:
                    game_playlist = "ranked_standard"
                elif game_playlist_id == GAME_PLAYLIST_RANKED_SNOWDAY:
                    game_playlist = "ranked_snowday"
                elif game_playlist_id == GAME_PLAYLIST_TOURNAMENT:
                    game_playlist = "tournament"
                elif game_playlist_id == GAME_PLAYLIST_CASUAL_GODBAL:
                    game_playlist = "heatseeker"
                else:
                    game_playlist = f"unknown_{game_playlist_id}"

                self.game_playlist = game_playlist

            case "TAGame.VehiclePickup_TA:NewReplicatedPickupData":
                instigator_id = updated["value"]["pickup_new"]["instigator_id"]
                if instigator_id is not None:  
                    if instigator_id != -1:  
                        if "boost_pickups" not in self.actors[instigator_id]:
                            self.actors[instigator_id]["boost_pickups"] = []
                        picked_up = updated["value"]["pickup_new"]["picked_up"]
                        boost_actor_id = actor["actor_id"]
                        data = {
                            "picked_up": picked_up,
                            "frame_index": self.time,
                            "boost_actor_id": boost_actor_id,
                        }
                        self.actors[instigator_id]["boost_pickups"].append(data)

            case "TAGame.GameEvent_Soccar_TA:MaxScore":
                self.actors[actor_id]["max_score"] = updated["value"]["int"]

            case "ProjectX.GRI_X:MatchGuid":
                self.actors[actor_id]["match_guid"] = updated["value"]["string"]

            case "Engine.PlayerReplicationInfo:RemoteUserData":
                self.actors[actor_id]["remote_user_data"] = updated["value"][
                    "string"
                ]

            case "TAGame.CarComponent_Boost_TA:UnlimitedBoostRefCount":
                self.actors[actor_id]["unlimited_boost_ref_count"] = updated[
                    "value"
                ]["int"]

            case "TAGame.VehiclePickup_TA:bNoPickup":
                self.actors[actor_id]["no_pickup"] = updated["value"]["boolean"]

            case _:
                # print("unrecognized: ", object_name)
                pass

    def dump(self):

        output = ""
        for player, car in self.player_car_pairs:
            player_name = self.actors[player].get(
                "player_name", "unknown player"
            )

            location = self.actors[car].get("location", {"x":None,"y":None,"z":None})
            rotation = self.actors[car].get("rotation", {"x":None,"y":None,"z":None,"w":None})
            linear_velocity = self.actors[car].get("linear_velocity", {"x":None,"y":None,"z":None})
            angular_velocity = self.actors[car].get("angular_velocity", {"x":None,"y":None,"z":None})
            if angular_velocity is None:
                angular_velocity = {}

            team = self.actors[car].get("team", -1)
            boost = self.actors[car].get("boost", 255)  

            x = location.get("x", 0)
            y = location.get("y", 0)
            z = location.get("z", 0)

            rx = rotation.get("x", 0)
            ry = rotation.get("y", 0)
            rz = rotation.get("z", 0)
            rw = rotation.get("w", 0)

            lx = linear_velocity.get("x", 0)
            ly = linear_velocity.get("y", 0)
            lz = linear_velocity.get("z", 0)

            ax = angular_velocity.get("x", 0)
            ay = angular_velocity.get("y", 0)
            az = angular_velocity.get("z", 0)

            speed = self.actors[car].get("speed", 0)
            distance_to_ball = self.actors[car].get("distance_to_ball", 0)

            # print(self.time,player_name, x, y, z, rx, ry, rz, rw, lx, ly, lz, ax, ay, az, speed, distance_to_ball)
            data = [
                str(self.time),
                player_name,
                team,
                boost,
                x,
                y,
                z,
                rx,
                ry,
                rz,
                rw,
                lx,
                ly,
                lz,
                ax,
                ay,
                az,
                speed,
                distance_to_ball,
            ]

            output += ",".join(map(str, data)) + "\n"

        ball = self.get_ball()
        if ball is not None:
            x = self.actors[ball]["location"]["x"]
            y = self.actors[ball]["location"]["y"]
            z = self.actors[ball]["location"]["z"]

            data = [
                str(self.time),
                "ball",
                "","",
                x,
                y,
                z,
                "", "", "", "", "",  "", "",
                "", "", "", "", "",
            ]

            output += ",".join(map(str, data)) + "\n"

        return output
    
    def calculate(self):

        speed = -1.0
        if (
            self.ball_id is not None
            and "linear_velocity" in self.actors[self.ball_id]
        ):
            linear_velocity = self.actors[self.ball_id]["linear_velocity"]
            if linear_velocity is not None:
                speed = (
                    linear_velocity["x"] ** 2
                    + linear_velocity["y"] ** 2
                    + linear_velocity["z"] ** 2
                ) ** 0.5
                self.actors[self.ball_id]["speed"] = speed

        angle = 0.0
        if (
            self.ball_id is not None
            and "linear_velocity" in self.actors[self.ball_id]
        ):
            linear_velocity = self.actors[self.ball_id]["linear_velocity"]
            if linear_velocity is not None:
                angle = math.atan2(linear_velocity["y"], linear_velocity["x"])
                self.actors[self.ball_id]["angle"] = angle

        for player, car in self.player_car_pairs:
            if "linear_velocity" in self.actors[car]:
                linear_velocity = self.actors[car]["linear_velocity"]
                if linear_velocity is not None:
                    speed = (
                        linear_velocity["x"] ** 2
                        + linear_velocity["y"] ** 2
                        + linear_velocity["z"] ** 2
                    ) ** 0.5
                    self.actors[car]["speed"] = speed
            else:
                self.actors[car]["speed"] = -1.0

        some_big_number = 999999.0
        if self.ball_id is None:
            ball_location = {
                "x": some_big_number,
                "y": some_big_number,
                "z": some_big_number,
            }
        else:
            ball_location = self.actors[self.ball_id]["location"]

        for player, car in self.player_car_pairs:
            if "location" in self.actors[car]:
                car_location = self.actors[car]["location"]
                car_x, car_y, car_z = (
                    car_location["x"],
                    car_location["y"],
                    car_location["z"],
                )
                distance = some_big_number
                if ball_location is not None and car_location is not None:
                    distance = (
                        (ball_location["x"] - car_x) ** 2
                        + (ball_location["y"] - car_y) ** 2
                        + (ball_location["z"] - car_z) ** 2
                    ) ** 0.5
                self.actors[car]["distance_to_ball"] = distance


    def get_player_car_pairs(self):
        player_car_pairs = []

        players = [
            actor_id
            for actor_id, actor in self.actors.items()
            if actor["object_name"] == 'TAGame.Default__PRI_TA'
        ]

        for player in players:
            car = [
                actor_id
                for actor_id, actor in self.actors.items()
                if player in actor["parent_ids"]
                and actor["object_name"] == 'Archetypes.Car.Car_Default'
            ]
            if len(car) == 0:
                pass
            elif len(car) == 1:
                car = car[0]
                player_car_pairs.append((player, car))
            else:
                car = car[-1]
                player_car_pairs.append((player, car))

        return player_car_pairs

    def get_ball(self):

        ball_types = [
            'Archetypes.Ball.Ball_Default',
            'Archetypes.Ball.Ball_Basketball',
            'Archetypes.Ball.Ball_Hockey',
            'Archetypes.Ball.Ball_God'
        ]
        ball = [
            actor_id
            for actor_id, actor in self.actors.items()
            if actor["object_name"] in ball_types
        ]

        if len(ball) == 0:
            return None
        elif len(ball) == 1:
            return ball[0]
        else:
            ball = sorted(
                ball, key=lambda x: self.actors[x]["created_at_frame"]
            )
            # return ball with highest frame number
            return ball[-1]
