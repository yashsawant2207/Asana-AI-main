"""Maps pose ids (shared with the React frontend) to rule engines."""
from . import rules

REGISTRY = {
    "tree": rules.tree,
    "warrior_i": rules.warrior_i,
    "warrior_ii": rules.warrior_ii,
    "warrior_iii": rules.warrior_iii,
    "cobra": rules.cobra,
    "bow": rules.bow,
    "archer": rules.archer,
    "camel": rules.camel,
    "shoulder_stand": rules.shoulder_stand,
    "mountain": rules.mountain,
    "wind_relieving": rules.wind_relieving,
    "thunderbolt": rules.thunderbolt,
}


def evaluate(pose_id, landmarks, w, h):
    fn = REGISTRY.get(pose_id, rules.mountain)
    return fn(landmarks, w, h)
