from profiles.utils import unclassname
from profiles import Conveyor


def get_conveyors(conveyors: list[dict]) -> list[Conveyor]:
    out = []
    for conveyor in conveyors:
        out.append(
            Conveyor(
                unclassname(conveyor["ClassName"], ["Build_"]),
                float(conveyor["mSpeed"]) / 60,
            )
        )

    return out
