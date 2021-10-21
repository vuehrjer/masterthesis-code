import os
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

OUTPUT_FOLDERS = ['color', 'depth', 'depthShader', 'norm', 'XYZ']
RENDERER_FOLDERS = ['Area', 'Line']
LAMP_FOLDERS = ['continuous', 'lamp1', 'lamp2', 'lamp3', 'lamp4']


class Renderer:
    class InvalidScene(ValueError):
        pass

    def __init__(self, path, engine, config):
        self._path = path
        self._engine = engine
        self._config = config
        self.renderer_type = None

    def cleanup(self):
        for folder in [*OUTPUT_FOLDERS, *LAMP_FOLDERS, self.renderer_type]:
            p = self._path / folder
            if p.exists():
                shutil.rmtree(p, ignore_errors=True)

    def _get_lamps(self):
        collections = self._engine.get_collections()
        return [c for c in collections if c.name.startswith("Lamp") and c.hide_render is False]

    def create_animation(self):
        start = self._engine.get_start_point()
        animation = create_animation(start, self._config["img_amount"], self._config["displacement"])
        self._engine.set_animation(animation)

    @abstractmethod
    def move_output(self):
        pass

    @abstractmethod
    def render(self):
        pass


class AreaRenderer(Renderer):

    def __init__(self, path, engine, config):
        super().__init__(path, engine, config)
        self.renderer_type = "Area"

    def move_output(self):
        renderer_path = self.create_renderer_directory()
        for folder in OUTPUT_FOLDERS:
            shutil.move((self._path / folder).as_posix(), renderer_path.as_posix())

    def create_renderer_directory(self):
        renderer_path = self._path / self.renderer_type
        renderer_path.mkdir(exist_ok=True, parents=True)
        return renderer_path

    def render(self):
        lamps = self._get_lamps()
        if not any(lamps):
            raise self.InvalidScene("No lamps in scene")
        for frame in range(self._engine.num_frames):
            for lamp in lamps:
                lamp.hide_render = not lamp.name == f"Lamp_{frame % len(lamps) + 1}"
            self._engine.render_frame(frame, self._path / 'color' / '{0:04d}'.format(frame + 1))


class LineRenderer(Renderer):

    def __init__(self, path, engine, config):
        super().__init__(path, engine, config)
        self.renderer_type = "Line"

    def move_output(self):
        renderer_path = self.create_renderer_directory()
        for folder in LAMP_FOLDERS:
            shutil.move((self._path / folder).as_posix(), renderer_path.as_posix())

    def create_renderer_directory(self):
        renderer_path = self._path / self.renderer_type
        renderer_path.mkdir(exist_ok=True, parents=True)
        return renderer_path

    def _move_lamp(self, lamp):
        lamp_path = self.create_lamp_directory(lamp)
        for folder in OUTPUT_FOLDERS:
            shutil.move((self._path / folder).as_posix(), lamp_path.as_posix())

    def render(self):
        lamps = self._get_lamps()
        if not any(lamps):
            raise self.InvalidScene("No lamps in scene")
        self._render_lamps_iteratively(lamps)
        self._render_lamps_continuously(lamps)

    def _render_lamps_continuously(self, lamps):
        for lamp in lamps:
            lamp.hide_render = False
            for frame in range(self._engine.num_frames):
                self._engine.render_frame(frame, self._path / 'color' / '{0:04d}'.format(frame + 1))
        self._move_lamp(0)

    def _render_lamps_iteratively(self, lamps):
        for lamp_number, lamp in enumerate(lamps):
            for l in lamps:
                l.hide_render = not lamp.name == f"Lamp_{lamp_number % len(lamps) + 1}"
            for frame in range(self._engine.num_frames):
                self._engine.render_frame(frame, self._path / 'color' / '{0:04d}'.format(frame + 1))
            self._move_lamp(lamp_number + 1)

    def create_lamp_directory(self, lamp_number):
        lamp_path = self._path / f"lamp{lamp_number}" if not lamp_number == 0 else self._path / "continuous"
        lamp_path.mkdir(exist_ok=True, parents=True)
        return lamp_path


def create_animation(starting_points, frame_amount, displacement):
    return [[Point(starting_point.x, starting_point.y - frame * displacement, starting_point.z) for frame in
             range(frame_amount)] for starting_point in starting_points]


@dataclass
class Point:
    x: float
    y: float
    z: float


class RenderEngine(ABC):

    @property
    @abstractmethod
    def num_frames(self) -> int:
        pass

    @abstractmethod
    def get_start_point(self) -> Point:
        pass

    @abstractmethod
    def set_animation(self, animation: Sequence[Point]):
        pass

    @abstractmethod
    def get_collections(self):
        pass

    @abstractmethod
    def render_frame(self, frame: int, out_file: Path):
        pass
