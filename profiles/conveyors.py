from profiles.utils import unclassname
from profiles import Conveyor


def get_conveyors(conveyors: list[dict]) -> list[Conveyor]:
    out = []
    for conveyor in conveyors:
        out.append(
            Conveyor(
                unclassname(conveyor["ClassName"], ["Build_"]),
                # somehow the speed is saved per 2 minutes and not 1
                float(conveyor["mSpeed"]) / 120,
            )
        )

    return out
