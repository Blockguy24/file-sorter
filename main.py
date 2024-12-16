from pathlib import Path
from random import sample
from subprocess import Popen

from imgui_bundle import hello_imgui, imgui, immapp


def get_some_files(base_dir: Path, count: int) -> list[Path]:
    return sample(list(base_dir.iterdir()), count)


def gui() -> None:
    viewport = imgui.get_main_viewport()
    imgui.set_next_window_pos(viewport.pos)
    imgui.set_next_window_size(viewport.size)
    if imgui.begin(
        "main_window",
        flags=(
            imgui.WindowFlags_.no_decoration
            | imgui.WindowFlags_.no_move
            | imgui.WindowFlags_.no_saved_settings
        ),
    ):
        imgui.begin_group()

        if imgui.begin_child("FileList", (-100, 0), imgui.ChildFlags_.borders):
            imgui.text("Some content")
            imgui.text("Some content")
            imgui.text("Some content")
        imgui.end_child()
        imgui.same_line()

        imgui.begin_group()
        button_size = (-imgui.FLT_MIN, 0)
        imgui.button("Open", button_size)
        imgui.button("Edit", button_size)
        imgui.button("Copy Path", button_size)
        imgui.button("Delete", button_size)
        imgui.button("Reroll", button_size)
        imgui.end_group()

        imgui.end_group()
    imgui.end()


def main() -> None:
    current_dir = Path("/home/joshua/Downloads")

    hello_imgui.set_assets_folder(str(Path(__file__).with_name("assets")))
    immapp.run(
        gui_function=gui,
        window_title="APP",
        window_size=(600, 200),
    )


if __name__ == "__main__":
    main()
