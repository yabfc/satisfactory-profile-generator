from profiles.utils import unclassname
from profiles import Logistic


def get_logistics(logistics: list[dict]) -> list[Logistic]:
    out = []
    for logistic in logistics:
        # no need to have duplicate pipelines (default vs 'clean' style)
        if "NoIndicator_C" in logistic["ClassName"]:
            continue
        if "mFlowLimit" in logistic.keys():
            # saved per second
            speed = float(logistic["mFlowLimit"])
            type = "fluid"
        else:
            # somehow the speed is saved per 2 minutes and not 1
            speed = float(logistic["mSpeed"]) / 120
            type = "item"
        out.append(
            Logistic(
                unclassname(logistic["ClassName"], ["Build_"]),
                type,
                speed,
            )
        )

    return out
