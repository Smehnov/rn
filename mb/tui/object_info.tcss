from textual.app import App, ComposeResult, RenderResult
from textual.containers import Horizontal, Vertical, Center
from textual.widgets import *
from textual.widget import Widget
from textual.message import Message
from textual.reactive import reactive
from textual import on



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
                Input(placeholder="Inser robot", value=self.info["robot_peer_id"], id="input_robot_peer_id"),

                Label("Robot Public Key", classes="input_labels"),
                Input(placeholder="robot name", value=self.info["robot_public_key"], id="input_robot_public_key"),

                Label("Robot Tags", classes="input_labels"),
                Input(placeholder="robot name", value=", ".join(self.info["tags"]), id="input_tags"),

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

    def __init__(self):
        super().__init__()

        self.list_of_robots = []

        self.robot_view = RobotView(info=None, id="robot_view")

    def action_publish(self):
        self.app.exit()

    def on_mount(self):
        def update_info(update_var: int):
            index = self.robot_view.index
            info = self.robot_view.info

            if index is not None:
                self.list_of_robots[index] = info
                self.query_one(f"#robot_list_item_{index}").query_one(Label).update(self.list_of_robots[index]["name"])

        self.watch(self.robot_view, "update_var", update_info)

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="list_column"):

                with Vertical():
                    yield Center(Label("List of Robots"), id="list_of_robots_center_label")
                    with ListView(id="list_of_robots", initial_index=None):
                        for i, o in enumerate(self.list_of_robots):
                            yield ListItem(Label(o["name"]), id=f"robot_list_item_{i}")
                    yield Center(Button(label="Add robot", id="add_robot_button"), id="add_robot_center")
            yield Vertical(self.robot_view)

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add_robot_button":
            self.list_of_robots.append({
                "name": "Unnamed", "robot_id": "", "robot_peer_id": "", "robot_public_key": "", "tags": []
            })
            index = self.list_of_robots.__len__()-1
            info = self.list_of_robots[index]
            new_list_item = ListItem(Label(info["name"]), id=f"robot_list_item_{index}")
            self.query_one(ListView).append(new_list_item)

            self.change_robot_view(index, info)

            self.query_one(ListView).index = index

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        list_view_number = event.list_view.index
        self.change_robot_view(list_view_number, self.list_of_robots[list_view_number])

    def on_list_view_highlighted(self, event: ListView.Highlighted):
        if event.list_view.index is not None:
            self.on_list_view_selected(event)

    def change_robot_view(self, index, info):
        self.robot_view.index = index
        self.robot_view.info = info
        self.robot_view.refresh(recompose=True)


if __name__ == "__main__":
    app = RNTUIApp()
    app.run()
