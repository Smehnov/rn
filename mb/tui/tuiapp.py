from textual.app import App, ComposeResult, RenderResult
from textual.containers import Horizontal, Vertical, Center, Container
from textual.widgets import *
from textual.widget import Widget
from textual.message import Message
from textual.reactive import reactive
from textual import on

import base64
import json

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from mb.crypto import generate_key, get_key_bytes, get_base_64, get_peer_id, read_private_key
from mb.settings import USER_KEY_PATH, AGENT_SOCKET_PATH, OWNER_KEY, AGENT_RPC
from mb.agent import Agent


class RobotView(Widget):

    update_var = reactive(0)

    def __init__(self, info=None, index=None, id=None):
        super().__init__(id=id)
        self.info = info
        self.index = index

    def compose(self) -> ComposeResult:
        if not self.info:
            return [Static("Select an object to see its details.", id="object_info_filler"),
                    Static(classes="hatch cross")]
        else:
            
            return [
                Label("Robot Name", classes="input_labels"),
                Input(placeholder="robot name", value=self.info["name"], id="input_name"),

                Label("Robot Id", classes="input_labels"),
                Input(placeholder="robot id", value=self.info["robot_id"], id="input_robot_id"),

                Label("Robot Peer Id", classes="input_labels"),
                Input(placeholder="PeerId", value=self.info["robot_peer_id"], id="input_robot_peer_id"),

                Label("Robot Public Key", classes="input_labels"),
                Input(placeholder="robot public key", value=self.info["robot_public_key"], id="input_robot_public_key"),

                Label("Robot Tags", classes="input_labels"),
                Input(placeholder="robot tags", value=", ".join(self.info["tags"]), id="input_tags"),
                
                
            ] + ([
                Label(f"Private key(shown once):  {self.info['robot_private_key']}", classes="input_labels"),
                Label(f"args:  -k {self.info['robot_private_key']} -o {self.info['owner']}")
            ] if self.info.get('robot_private_key') else [])

    @on(Input.Changed)
    def update_info(self, event: Input.Changed):
        field = event.input.id.replace("input_", "")
        if field == "tags":
            self.info[field] = [t.strip() for t in event.value.split(",")]
        else:
            self.info[field] = event.value
        self.update_var += 1

class UserView(Widget):
    update_var = reactive(0)

    def __init__(self, info=None, index=None, id=None):
        super().__init__(id=id)
        self.info = info
        self.index = index

    def compose(self) -> ComposeResult:
        if not self.info:
            return [Static("Select a user to see its details.", id="user_info_filler"),
                    Static(classes="hatch cross")]
        else:
            return [
                Label("Username", classes="input_labels"),
                Input(placeholder="username", value=self.info["username"], id="input_username"),

                Label("Public Key", classes="input_labels"),
                Input(placeholder="public key", value=self.info["public_key"], id="input_public_key"),

                Label("User Tags", classes="input_labels"),
                Input(placeholder="user tags", value=", ".join(self.info["tags"]), id="input_tags"),
            ]

    @on(Input.Changed)
    def update_info(self, event: Input.Changed):
        field = event.input.id.replace("input_", "")
        if field == "tags":
            self.info[field] = [t.strip() for t in event.value.split(",")]
        else:
            self.info[field] = event.value
        self.update_var += 1

class RNTUIApp(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"),
                ("p", "publish", "Publish config")]

    TITLE = "Robot Network TUI"
    CSS_PATH = "object_info.tcss"

    def __init__(self, owner_base64, publish_callback, robots: list, users: list, version: int):
        super().__init__()

        self.publish_callback = publish_callback
        self.list_of_robots = robots or []
        self.list_of_users = users or []
        self.version = version or 0
        self.owner_base64 = owner_base64
        self.robot_view = RobotView(info=None, id="robot_view")
        self.user_view = UserView(info=None, id="user_view")  # Add this line

    def action_publish(self):
        self.version+=1
        #self.app.exit()
        self.notify(f"{self.version} {self.list_of_robots}")
        version = self.version
        robots = [
            {
                "robot_id": robot['robot_id'],
                "robot_peer_id": robot['robot_peer_id'],
                "robot_public_key": robot['robot_public_key'],
                "name": robot['name'],
                "tags": robot['tags'],
            } for robot in self.list_of_robots]
        users = [
            {
                "username": user["username"],
                "public_key": user["public_key"],
                "tags": user["tags"]
            } for user in self.list_of_users
        ]
        self.publish_callback(version, robots, users) 
    

    def on_mount(self) -> None:
        robots_view = self.compose_robots_tab() 
        print(robots_view)
        robots_tab = self.query_one("#robots_tab")
        robots_tab.mount(robots_view)
        self.query_one("#users_tab").mount(self.compose_users_tab())
        self.watch(self.robot_view, "update_var", self.update_robot_info)
        self.watch(self.user_view, "update_var", self.update_user_info)

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            yield TabPane("Robots", id="robots_tab")
            yield TabPane("Users", id="users_tab")
        
        yield Footer()

    def compose_robots_tab(self) -> ComposeResult:
        return Horizontal(
            Vertical(
                Static(f"config version: {self.version}", id="config_version_label"),
                Static("List of Robots", id="list_of_robots_label"),
                ListView(
                    *[ListItem(Label(o["name"]), id=f"robot_list_item_{i}") for i, o in enumerate(self.list_of_robots)],
                    id="list_of_robots"
                ),
                Button("Add robot", id="add_robot_button"),
                id="list_column"
            ),
                
            self.robot_view,
            id='horizontal_robots'
        )

    def compose_users_tab(self) -> ComposeResult:
        return Horizontal(
            Vertical(
                Static("List of Users", id="list_of_users_label"),
                ListView(
                    *[ListItem(Label(u["username"]), id=f"user_list_item_{i}") for i, u in enumerate(self.list_of_users)],
                    id="list_of_users"
                ),
                Button("Add user", id="add_user_button"),
                id="user_list_column"
            ),
            self.user_view
        )

    def update_robot_info(self, update_var: int):
        index = self.robot_view.index
        info = self.robot_view.info

        if index is not None:
            self.list_of_robots[index] = info
            self.query_one(f"#robot_list_item_{index}").query_one(Label).update(self.list_of_robots[index]["name"])

    def update_user_info(self, update_var: int):
        index = self.user_view.index
        info = self.user_view.info

        if index is not None:
            self.list_of_users[index] = info
            self.query_one(f"#user_list_item_{index}").query_one(Label).update(self.list_of_users[index]["username"])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add_robot_button":
            self.notify("Please, save private key to use on robot")
            private_key = generate_key()
            sk, pk = get_key_bytes(private_key)
            private_key_base64 = get_base_64(private_key, mode='sk')
            public_key_base64 = get_base_64(private_key, mode='pk')
            peer_id =get_peer_id(pk) 
            print(peer_id)
            self.list_of_robots.append({
                "name": "Unnamed",
                "robot_id": "",
                "robot_peer_id": peer_id,
                "robot_public_key": public_key_base64,
                "tags": [],
                "robot_private_key": private_key_base64,
                "owner": self.owner_base64 
            })
            index = self.list_of_robots.__len__()-1
            info = self.list_of_robots[index]
            new_list_item = ListItem(Label(info["name"]), id=f"robot_list_item_{index}")
            self.query_one("#list_of_robots").append(new_list_item)

            self.change_robot_view(index, info)

            self.query_one("#list_of_robots").index = index
        elif event.button.id == "add_user_button":
            self.list_of_users.append({
                "username": "new_user",
                "public_key": "",
                "tags": [],
            })
            index = len(self.list_of_users) - 1
            info = self.list_of_users[index]
            new_list_item = ListItem(Label(info["username"]), id=f"user_list_item_{index}")
            self.query_one("#list_of_users").append(new_list_item)

            self.change_user_view(index, info)

            self.query_one("#list_of_users").index = index

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        list_view = event.list_view
        if list_view.id == "list_of_robots":
            self.change_robot_view(list_view.index, self.list_of_robots[list_view.index])
        elif list_view.id == "list_of_users":
            self.change_user_view(list_view.index, self.list_of_users[list_view.index])

    def on_list_view_highlighted(self, event: ListView.Highlighted):
        if event.list_view.index is not None:
            self.on_list_view_selected(event)

    def change_robot_view(self, index, info):
        self.robot_view.index = index
        self.robot_view.info = info
        self.robot_view.refresh(recompose=True)

    def change_user_view(self, index, info):
        self.user_view.index = index
        self.user_view.info = info
        self.user_view.refresh(recompose=True)



def start(config_path):
    private_key = read_private_key(USER_KEY_PATH)
    owner_base64 = get_base_64(private_key, mode='pk')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(config)
        if 'users' not in config:
            config['users'] = []
    except:
        config = {
            'version': 0,
            'robots': [],
            'users': []
        }


    def publish_callback(version, robots, users):
        with open(config_path, 'w') as f:
            config_obj =  {
                "version": version,
                "robots": robots,
                "users": users
                }
            print(config_obj)
            config_str = json.dumps(config_obj)
            f.write(config_str)

            agent = Agent(USER_KEY_PATH, AGENT_RPC, AGENT_SOCKET_PATH, OWNER_KEY)
            agent.publish_config(config_obj)

        
    app = RNTUIApp(owner_base64, publish_callback, config['robots'], config['users'], config['version'])
    app.run()