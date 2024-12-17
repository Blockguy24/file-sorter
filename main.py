from __future__ import annotations

import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from random import sample
from threading import Thread
from typing import Any

from imgui_bundle import hello_imgui, imgui, imgui_ctx, immapp
from imgui_bundle import portable_file_dialogs as pfd


def get_some_files(base_dir: Path, count: int) -> list[Path]:
    return sample(list(base_dir.iterdir()), count)


def copy_params[**P](src: Callable[P, Any]):
    def decorator[T](f: Callable[..., T]) -> Callable[P, T]:
        def inner(*args: P.args, **kwargs: P.kwargs) -> T:
            return f(*args, **kwargs)

        return inner

    return decorator


@copy_params(subprocess.run)
def run_bg(*args, **kwargs) -> None:
    Thread(target=lambda: subprocess.run(*args, **kwargs)).start()


def gui(state: AppState) -> None:
    viewport = imgui.get_main_viewport()
    imgui.set_next_window_pos(viewport.pos)
    imgui.set_next_window_size(viewport.size)
    with imgui_ctx.begin(
        "MainWindow",
        flags=(
            imgui.WindowFlags_.no_decoration
            | imgui.WindowFlags_.no_move
            | imgui.WindowFlags_.no_saved_settings
        ),
    ):
        imgui.begin_disabled(state.move_dialog is not None)
        with imgui_ctx.begin_group():
            with imgui_ctx.begin_child(
                "FileList", (-100, 0), imgui.ChildFlags_.borders
            ):
                for i, path in enumerate(state.files):
                    _, clicked = imgui.selectable(str(path), i == state.select_idx)
                    if clicked:
                        state.select_idx = i
            imgui.same_line()
            with imgui_ctx.begin_group():
                button_size = (-imgui.FLT_MIN, 0)
                imgui.begin_disabled(state.selected_file is None)
                if imgui.button("Open", button_size):
                    run_bg(["xdg-open", str(state.selected_file)])
                if imgui.button("Edit", button_size):
                    run_bg(["alacritty", "--command", "nvim", str(state.selected_file)])
                if imgui.button("Copy Path", button_size):
                    # run(["xclip", "-selection", "clipboard", "-i"], input=bytes(state.selected_file))
                    imgui.set_clipboard_text(str(state.selected_file))
                if imgui.button("Move", button_size):
                    if state.selected_file.is_dir():
                        state.move_dialog = pfd.select_folder(
                            "Move folder", str(state.selected_file)
                        )
                    else:
                        state.move_dialog = pfd.save_file(
                            "Move file", str(state.selected_file)
                        )
                if imgui.button("Trash", button_size):
                    run_bg(["trash-put", str(state.selected_file)])
                if imgui.button("Delete", button_size):
                    imgui.open_popup("Confirm Delete")
                imgui.end_disabled()
                if imgui.button("Reroll", button_size):
                    state.reroll_files()
        imgui.end_disabled()

        imgui.set_next_window_pos(viewport.get_center(), imgui.Cond_.always, (0.5, 0.5))
        with imgui_ctx.begin_popup_modal(
            "Confirm Delete", imgui.WindowFlags_.always_auto_resize
        ) as modal:
            if modal.visible:
                imgui.text("The file will be permanently deleted, are you sure?")
                if imgui.button("OK", (100, 0)):
                    if state.selected_file.is_dir():
                        shutil.rmtree(state.selected_file)
                    else:
                        state.selected_file.unlink()
                    state.remove_selected()
                    imgui.close_current_popup()
                imgui.same_line()
                if imgui.button("Cancel", (100, 0)):
                    imgui.close_current_popup()

    if state.move_dialog is not None and state.move_dialog.ready(timeout=0):
        if new_path := state.move_dialog.result():
            shutil.move(state.selected_file, new_path)
            state.remove_selected()
        state.move_dialog = None


@dataclass
class AppState:
    current_dir: Path | None = None
    files: list[Path] = field(default_factory=list)
    select_idx: int | None = None
    move_dialog: pfd.save_file | pfd.select_folder | None = None

    def reroll_files(self):
        self.files = get_some_files(self.current_dir, 3)
        self.select_idx = None

    @property
    def selected_file(self) -> Path | None:
        if self.select_idx is None:
            return None
        return self.files[self.select_idx]

    def remove_selected(self) -> None:
        del self.files[self.select_idx]
        self.select_idx = None


def main() -> None:
    state = AppState(current_dir=Path("/home/joshua/Downloads"))
    state.reroll_files()

    hello_imgui.set_assets_folder(str(Path(__file__).with_name("assets")))
    immapp.run(
        gui_function=lambda: gui(state),
        window_title="File Sorter",
        window_size=(600, 200),
    )


if __name__ == "__main__":
    main()
