from pathlib import Path
from random import sample
from subprocess import Popen

import dearpygui.dearpygui as dpg


def get_some_files(base_dir: Path, count: int) -> list[Path]:
    return sample(list(base_dir.iterdir()), count)


def _log(sender, app_data, user_data):
    print(f"sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")


def main() -> None:
    current_dir = Path("/home/joshua/Downloads")

    dpg.create_context()
    dpg.create_viewport(title="APP", width=800, height=400)

    with dpg.window(tag="root"):
        with dpg.group(horizontal=True):
            dpg.add_listbox(get_some_files(current_dir, 3), tag="file_select")
            with dpg.group():
                dpg.add_button(
                    label="Open",
                    callback=lambda *_: Popen(
                        ["xdg-open", dpg.get_value("file_select")]
                    ),
                )
                dpg.add_button(label="Edit")
                dpg.add_button(label="Copy Path")
                dpg.add_button(label="Delete")
                dpg.add_button(label="Reroll")

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("root", True)
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
