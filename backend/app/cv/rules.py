"""Per-pose rule engines, refactored from the Colab notebook.

Each evaluator takes MediaPipe landmarks (33) plus frame width/height and
returns (is_correct: bool, messages: list[str]). All drawing/IO was removed;
rendering now happens in the browser from the returned landmark coordinates.
"""
from .geometry import calculate_angle, distance

# ====================================================================
# MATH HELPERS
# ====================================================================
def _pt(lm, i, w, h):
    return [lm[i].x * w, lm[i].y * h]

def _midpoint(p1, p2):
    return [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2]

def _avg(*values):
    return sum(values) / len(values)

# ====================================================================
# POSE EVALUATORS
# ====================================================================
def tree(lm, w, h):
    l_hip, l_knee, l_ankle = _pt(lm, 23, w, h), _pt(lm, 25, w, h), _pt(lm, 27, w, h)
    r_hip, r_knee, r_ankle = _pt(lm, 24, w, h), _pt(lm, 26, w, h), _pt(lm, 28, w, h)
    l_sh, r_sh = _pt(lm, 11, w, h), _pt(lm, 12, w, h)
    l_wr, r_wr = _pt(lm, 15, w, h), _pt(lm, 16, w, h)

    if l_ankle[1] > r_ankle[1]:
        stand = calculate_angle(l_hip, l_knee, l_ankle)
        bent = calculate_angle(r_hip, r_knee, r_ankle)
    else:
        stand = calculate_angle(r_hip, r_knee, r_ankle)
        bent = calculate_angle(l_hip, l_knee, l_ankle)

    shoulder_w = distance(l_sh, r_sh)
    wrist_d = distance(l_wr, r_wr)
    
    prayer = (wrist_d < shoulder_w * 1.2 and l_sh[1] < l_wr[1] < l_hip[1] and r_sh[1] < r_wr[1] < r_hip[1])
    raised = l_wr[1] < l_sh[1] and r_wr[1] < r_sh[1]

    msgs = []
    if stand < 160:
        msgs.append("Straighten your standing leg")
    if bent > 100:
        msgs.append("Bring your raised foot higher")
    if not (prayer or raised):
        msgs.append("Bring hands to chest or above head")
        
    return len(msgs) == 0, msgs


def warrior_i(lm, w, h):
    l_hip, l_knee, l_ankle = _pt(lm, 23, w, h), _pt(lm, 25, w, h), _pt(lm, 27, w, h)
    r_hip, r_knee, r_ankle = _pt(lm, 24, w, h), _pt(lm, 26, w, h), _pt(lm, 28, w, h)
    l_sh, r_sh = _pt(lm, 11, w, h), _pt(lm, 12, w, h)
    l_el, r_el = _pt(lm, 13, w, h), _pt(lm, 14, w, h)
    l_wr, r_wr = _pt(lm, 15, w, h), _pt(lm, 16, w, h)

    l_leg = calculate_angle(l_hip, l_knee, l_ankle)
    r_leg = calculate_angle(r_hip, r_knee, r_ankle)
    front, back = min(l_leg, r_leg), max(l_leg, r_leg)

    l_arm = calculate_angle(l_sh, l_el, l_wr)
    r_arm = calculate_angle(r_sh, r_el, r_wr)

    mid_sh = _midpoint(l_sh, r_sh)
    mid_hip = _midpoint(l_hip, r_hip)
    torso_len = distance(mid_sh, mid_hip)
    mid_wr_y = _avg(l_wr[1], r_wr[1])

    msgs = []
    if front > 120:
        msgs.append("Bend your front knee deeper")
    if back < 155:
        msgs.append("Straighten your back leg")
    if mid_wr_y > (mid_sh[1] - (0.5 * torso_len)):
        msgs.append("Raise your arms higher above your head")
    if l_arm < 150 or r_arm < 150:
        msgs.append("Straighten your elbows")
        
    return len(msgs) == 0, msgs


def warrior_ii(lm, w, h):
    l_hip, l_knee, l_ankle = _pt(lm, 23, w, h), _pt(lm, 25, w, h), _pt(lm, 27, w, h)
    r_hip, r_knee, r_ankle = _pt(lm, 24, w, h), _pt(lm, 26, w, h), _pt(lm, 28, w, h)
    l_sh, r_sh = _pt(lm, 11, w, h), _pt(lm, 12, w, h)
    l_wr, r_wr = _pt(lm, 15, w, h), _pt(lm, 16, w, h)

    l_leg = calculate_angle(l_hip, l_knee, l_ankle)
    r_leg = calculate_angle(r_hip, r_knee, r_ankle)
    front, back = min(l_leg, r_leg), max(l_leg, r_leg)

    mid_sh = _midpoint(l_sh, r_sh)
    mid_hip = _midpoint(l_hip, r_hip)
    torso_len = distance(mid_sh, mid_hip)

    l_arm_y_diff = abs(l_wr[1] - l_sh[1])
    r_arm_y_diff = abs(r_wr[1] - r_sh[1])
    x_lean = abs(mid_sh[0] - mid_hip[0])

    msgs = []
    if front > 120:
        msgs.append("Bend your front knee deeper")
    if back < 155:
        msgs.append("Straighten your back leg")
    if l_arm_y_diff > (0.25 * torso_len) or r_arm_y_diff > (0.25 * torso_len):
        msgs.append("Keep both arms parallel to the floor")
    if x_lean > (0.25 * torso_len):
        msgs.append("Keep torso upright, don't lean forward")
        
    return len(msgs) == 0, msgs


def warrior_iii(lm, w, h):
    l_hip, l_knee, l_ankle = _pt(lm, 23, w, h), _pt(lm, 25, w, h), _pt(lm, 27, w, h)
    r_hip, r_knee, r_ankle = _pt(lm, 24, w, h), _pt(lm, 26, w, h), _pt(lm, 28, w, h)
    l_sh, r_sh = _pt(lm, 11, w, h), _pt(lm, 12, w, h)
    l_el, r_el = _pt(lm, 13, w, h), _pt(lm, 14, w, h)
    l_wr, r_wr = _pt(lm, 15, w, h), _pt(lm, 16, w, h)

    if l_ankle[1] > r_ankle[1]:
        raised_ankle = r_ankle
        support_leg = calculate_angle(l_hip, l_knee, l_ankle)
        raised_leg = calculate_angle(r_hip, r_knee, r_ankle)
    else:
        raised_ankle = l_ankle
        support_leg = calculate_angle(r_hip, r_knee, r_ankle)
        raised_leg = calculate_angle(l_hip, l_knee, l_ankle)

    l_arm = calculate_angle(l_sh, l_el, l_wr)
    r_arm = calculate_angle(r_sh, r_el, r_wr)

    mid_sh = _midpoint(l_sh, r_sh)
    mid_hip = _midpoint(l_hip, r_hip)
    torso_len = distance(mid_sh, mid_hip)
    y_tol = 0.25 * torso_len

    msgs = []
    if support_leg < 150:
        msgs.append("Straighten your standing leg")
    if raised_leg < 150:
        msgs.append("Straighten your raised leg")
    if abs(mid_sh[1] - mid_hip[1]) > y_tol:
        msgs.append("Lower chest to be parallel to the floor")
    if abs(raised_ankle[1] - mid_hip[1]) > y_tol:
        msgs.append("Lift back leg higher to hip level")
    if l_arm < 150 or r_arm < 150:
        msgs.append("Straighten your arms forward")
    if abs(_avg(l_wr[1], r_wr[1]) - mid_sh[1]) > y_tol:
        msgs.append("Align arms horizontally with your torso")
        
    return len(msgs) == 0, msgs


def cobra(lm, w, h):
    l_sh, r_sh = _pt(lm, 11, w, h), _pt(lm, 12, w, h)
    l_el, r_el = _pt(lm, 13, w, h), _pt(lm, 14, w, h)
    l_wr, r_wr = _pt(lm, 15, w, h), _pt(lm, 16, w, h)
    l_hip, r_hip = _pt(lm, 23, w, h), _pt(lm, 24, w, h)
    l_knee, r_knee = _pt(lm, 25, w, h), _pt(lm, 26, w, h)
    l_ankle, r_ankle = _pt(lm, 27, w, h), _pt(lm, 28, w, h)

    avg_arm = _avg(calculate_angle(l_sh, l_el, l_wr), calculate_angle(r_sh, r_el, r_wr))
    avg_leg = _avg(calculate_angle(l_hip, l_knee, l_ankle), calculate_angle(r_hip, r_knee, r_ankle))
    
    avg_sh_y = _avg(l_sh[1], r_sh[1])
    avg_hip_y = _avg(l_hip[1], r_hip[1])
    avg_knee_y = _avg(l_knee[1], r_knee[1])
    avg_ankle_y = _avg(l_ankle[1], r_ankle[1])
    avg_wr_y = _avg(l_wr[1], r_wr[1])
    
    torso_len = distance(_midpoint(l_sh, r_sh), _midpoint(l_hip, r_hip))

    msgs = []
    
    # Anti-sitting check: Your wrists MUST be significantly lower than your shoulders (near the floor)
    if avg_wr_y < avg_sh_y + (0.5 * torso_len):
        msgs.append("Place your hands down on the mat")
    if avg_wr_y < avg_sh_y + (0.45 * torso_len):
        msgs.append("Place your hands down on the mat")
    if avg_sh_y > avg_hip_y - (0.2 * torso_len):
        msgs.append("Lift your chest higher off the floor")
    if avg_hip_y < avg_ankle_y - (0.1 * h):
        msgs.append("Keep your hips pressed into the floor")
    if avg_arm > 165:
        msgs.append("Keep a micro-bend in your elbows")
    elif avg_arm < 60:
        msgs.append("Push up through your hands a bit more")
    if avg_leg < 165:
        msgs.append("Keep both legs straight and active")
    if avg_hip_y > avg_ankle_y - (0.05 * h):
        msgs.append("Keep your hips stable as you lift")
    if abs(l_wr[0] - r_wr[0]) > (0.35 * torso_len):
        msgs.append("Keep your hands aligned under your shoulders")
    if abs(l_sh[0] - r_sh[0]) > (0.30 * torso_len):
        msgs.append("Keep your shoulders level")
    if avg_ankle_y < avg_knee_y - (0.05 * torso_len):
        msgs.append("Keep your feet on the floor behind your hips")

    return len(msgs) == 0, msgs


def bow(lm, w, h):
    l_sh, r_sh = _pt(lm, 11, w, h), _pt(lm, 12, w, h)
    l_el, r_el = _pt(lm, 13, w, h), _pt(lm, 14, w, h)
    l_wr, r_wr = _pt(lm, 15, w, h), _pt(lm, 16, w, h)
    l_hip, r_hip = _pt(lm, 23, w, h), _pt(lm, 24, w, h)
    l_ankle, r_ankle = _pt(lm, 27, w, h), _pt(lm, 28, w, h)

    l_arm = calculate_angle(l_sh, l_el, l_wr)
    r_arm = calculate_angle(r_sh, r_el, r_wr)

    mid_sh = _midpoint(l_sh, r_sh)
    mid_hip = _midpoint(l_hip, r_hip)
    torso_len = distance(mid_sh, mid_hip)

    l_grab = distance(l_wr, l_ankle)
    r_grab = distance(r_wr, r_ankle)

    msgs = []
    
    if l_grab > (0.35 * torso_len) or r_grab > (0.35 * torso_len):
        msgs.append("Reach back and hold both ankles securely")
    if mid_sh[1] > (mid_hip[1] - (0.15 * torso_len)):
        msgs.append("Lift your chest higher off the floor")
    if l_arm < 140 or r_arm < 140:
        msgs.append("Let your legs pull your arms straight")
    if abs(l_sh[0] - r_sh[0]) > (0.45 * torso_len):
        msgs.append("Open your chest and shoulders more")
    if distance(l_sh, r_sh) < (0.70 * distance(l_hip, r_hip)):
        msgs.append("Open your chest and shoulders more")
    if mid_sh[1] > (mid_hip[1] - (0.22 * torso_len)):
        msgs.append("Raise your chest and shoulders off the mat")
    if abs(l_wr[1] - r_wr[1]) > (0.20 * torso_len):
        msgs.append("Keep your hands level on your heels")
    if abs(l_wr[0] - r_wr[0]) > (0.40 * torso_len):
        msgs.append("Keep both hands anchored evenly on your heels")
    if l_ankle[1] > l_knee[1] - (0.05 * torso_len) or r_ankle[1] > r_knee[1] - (0.05 * torso_len):
        msgs.append("Keep your knees pressed toward the floor")
    if abs(mid_sh[0] - mid_hip[0]) > (0.20 * torso_len):
        msgs.append("Keep your pelvis over your thighs")
        
    return len(msgs) == 0, msgs


def archer(lm, w, h):
    l_sh, r_sh = _pt(lm, 11, w, h), _pt(lm, 12, w, h)
    l_el, r_el = _pt(lm, 13, w, h), _pt(lm, 14, w, h)
    l_wr, r_wr = _pt(lm, 15, w, h), _pt(lm, 16, w, h)
    l_hip, r_hip = _pt(lm, 23, w, h), _pt(lm, 24, w, h)
    l_knee, r_knee = _pt(lm, 25, w, h), _pt(lm, 26, w, h)
    l_ankle, r_ankle = _pt(lm, 27, w, h), _pt(lm, 28, w, h)

    l_leg = calculate_angle(l_hip, l_knee, l_ankle)
    r_leg = calculate_angle(r_hip, r_knee, r_ankle)
    
    if l_leg > r_leg:
        ext_leg, bent_leg = l_leg, r_leg
        ext_arm = calculate_angle(l_sh, l_el, l_wr)
        ext_grab = distance(l_wr, l_ankle)
        bent_grab = distance(r_wr, r_ankle)
        pull_dist = distance(r_ankle, r_sh)
    else:
        ext_leg, bent_leg = r_leg, l_leg
        ext_arm = calculate_angle(r_sh, r_el, r_wr)
        ext_grab = distance(r_wr, r_ankle)
        bent_grab = distance(l_wr, l_ankle)
        pull_dist = distance(l_ankle, l_sh)

    torso_len = distance(_midpoint(l_sh, r_sh), _midpoint(l_hip, r_hip))

    msgs = []
    if ext_leg < 150:
        msgs.append("Straighten your extended leg")
    if bent_leg > 120:
        msgs.append("Bend your back knee more")
    if ext_arm < 145:
        msgs.append("Straighten the arm reaching forward")
    if abs(l_sh[0] - r_sh[0]) > (0.35 * torso_len):
        msgs.append("Keep your shoulders level and your chest lifted")
    if ext_grab > (0.45 * torso_len) or bent_grab > (0.45 * torso_len):
        msgs.append("Reach forward and hold your feet/ankles")
    if pull_dist > (0.65 * torso_len):
        msgs.append("Pull your bent foot closer to your ear")
    if abs(ext_grab - bent_grab) < (0.10 * torso_len) and pull_dist > (0.55 * torso_len):
        msgs.append("Keep the extended leg active and the bent leg close")
    if abs(l_wr[1] - r_wr[1]) > (0.20 * torso_len):
        msgs.append("Keep both hands at the same height")
    if abs(l_knee[1] - r_knee[1]) > (0.20 * torso_len):
        msgs.append("Keep your hips level")
        
    return len(msgs) == 0, msgs


def camel(lm, w, h):
    l_sh, r_sh = _pt(lm, 11, w, h), _pt(lm, 12, w, h)
    l_el, r_el = _pt(lm, 13, w, h), _pt(lm, 14, w, h)
    l_wr, r_wr = _pt(lm, 15, w, h), _pt(lm, 16, w, h)
    l_hip, r_hip = _pt(lm, 23, w, h), _pt(lm, 24, w, h)
    l_knee, r_knee = _pt(lm, 25, w, h), _pt(lm, 26, w, h)
    l_ankle, r_ankle = _pt(lm, 27, w, h), _pt(lm, 28, w, h)

    torso_len = distance(_midpoint(l_sh, r_sh), _midpoint(l_hip, r_hip))
    
    l_grab = distance(l_wr, l_ankle)
    r_grab = distance(r_wr, r_ankle)
    
    l_thigh_len = distance(l_hip, l_knee)
    r_thigh_len = distance(r_hip, r_knee)
    l_thigh_x_diff = abs(l_hip[0] - l_knee[0])
    r_thigh_x_diff = abs(r_hip[0] - r_knee[0])

    msgs = []
    
    if l_grab > (0.45 * torso_len) or r_grab > (0.45 * torso_len):
        msgs.append("Reach back and place your hands on your heels")
    if mid_sh[1] > mid_hip[1] - (0.12 * torso_len):
        msgs.append("Lift your chest toward the ceiling")
    if l_thigh_x_diff > (0.45 * l_thigh_len) or r_thigh_x_diff > (0.45 * r_thigh_len):
        msgs.append("Push your hips forward to keep thighs vertical")
    if calculate_angle(l_sh, l_el, l_wr) < 140 or calculate_angle(r_sh, r_el, r_wr) < 140:
        msgs.append("Keep your arms straight as you lean back")
    if distance(l_sh, r_sh) < (0.65 * distance(l_hip, r_hip)):
        msgs.append("Open your chest and shoulders more")
    if abs(l_wr[1] - r_wr[1]) > (0.25 * torso_len):
        msgs.append("Keep your hands level on your heels")
    if abs(mid_sh[0] - mid_hip[0]) > (0.25 * torso_len):
        msgs.append("Keep your shoulders stacked over your hips")
    if l_ankle[1] < l_knee[1] - (0.05 * torso_len) or r_ankle[1] < r_knee[1] - (0.05 * torso_len):
        msgs.append("Keep your heels pressing down behind you")
        
    return len(msgs) == 0, msgs


def shoulder_stand(lm, w, h):
    l_sh, r_sh = _pt(lm, 11, w, h), _pt(lm, 12, w, h)
    l_wr, r_wr = _pt(lm, 15, w, h), _pt(lm, 16, w, h)
    l_hip, r_hip = _pt(lm, 23, w, h), _pt(lm, 24, w, h)
    l_knee, r_knee = _pt(lm, 25, w, h), _pt(lm, 26, w, h)
    l_ankle, r_ankle = _pt(lm, 27, w, h), _pt(lm, 28, w, h)

    mid_sh = _midpoint(l_sh, r_sh)
    mid_hip = _midpoint(l_hip, r_hip)
    mid_ankle = _midpoint(l_ankle, r_ankle)
    
    torso_len = distance(mid_sh, mid_hip)
    stack_tol = 0.35 * torso_len

    msgs = []
    if mid_ankle[1] > mid_hip[1] or mid_hip[1] > mid_sh[1]:
        msgs.append("Lift your legs and hips high into the air")
    else:
        if abs(mid_ankle[0] - mid_sh[0]) > stack_tol or abs(mid_hip[0] - mid_sh[0]) > stack_tol:
            msgs.append("Stack ankles directly over hips and shoulders")
        if calculate_angle(l_sh, l_hip, l_knee) < 150 or calculate_angle(r_sh, r_hip, r_knee) < 150:
            msgs.append("Press your hips forward to straighten your body")
        if calculate_angle(l_hip, l_knee, l_ankle) < 160 or calculate_angle(r_hip, r_knee, r_ankle) < 160:
            msgs.append("Straighten your knees pointing up")
        if distance(l_wr, l_hip) > (0.45 * torso_len) or distance(r_wr, r_hip) > (0.45 * torso_len):
            msgs.append("Use your hands to support your lower back")
        if abs(mid_ankle[1] - mid_sh[1]) > (0.5 * torso_len):
            msgs.append("Keep your legs lifted directly above your hips")
            
    return len(msgs) == 0, msgs


def mountain(lm, w, h):
    l_sh, r_sh = _pt(lm, 11, w, h), _pt(lm, 12, w, h)
    l_el, r_el = _pt(lm, 13, w, h), _pt(lm, 14, w, h)
    l_wr, r_wr = _pt(lm, 15, w, h), _pt(lm, 16, w, h)
    l_hip, r_hip = _pt(lm, 23, w, h), _pt(lm, 24, w, h)
    l_knee, r_knee = _pt(lm, 25, w, h), _pt(lm, 26, w, h)
    l_ankle, r_ankle = _pt(lm, 27, w, h), _pt(lm, 28, w, h)

    mid_sh = _midpoint(l_sh, r_sh)
    mid_hip = _midpoint(l_hip, r_hip)
    mid_ankle = _midpoint(l_ankle, r_ankle)
    mid_wr = _midpoint(l_wr, r_wr)
    
    torso_len = distance(mid_sh, mid_hip)
    stack_tol = 0.20 * torso_len

    msgs = []
    if abs(mid_sh[0] - mid_hip[0]) > stack_tol or abs(mid_hip[0] - mid_ankle[0]) > stack_tol:
        msgs.append("Stand straight: stack shoulders over hips and ankles")
    if calculate_angle(l_hip, l_knee, l_ankle) < 165 or calculate_angle(r_hip, r_knee, r_ankle) < 165:
        msgs.append("Straighten your legs completely")
    if calculate_angle(l_sh, l_el, l_wr) < 155 or calculate_angle(r_sh, r_el, r_wr) < 155:
        msgs.append("Straighten your elbows")
    if mid_wr[1] > (mid_sh[1] - (0.6 * torso_len)):
        msgs.append("Reach your hands high towards the ceiling")
    if distance(l_wr, r_wr) > (0.35 * torso_len):
        msgs.append("Clasp your hands together overhead")
    if mid_wr[1] > mid_hip[1] - (0.25 * torso_len):
        msgs.append("Raise your hands higher into the sky")
        
    return len(msgs) == 0, msgs


def wind_relieving(lm, w, h):
    nose = _pt(lm, 0, w, h)
    l_sh, r_sh = _pt(lm, 11, w, h), _pt(lm, 12, w, h)
    l_wr, r_wr = _pt(lm, 15, w, h), _pt(lm, 16, w, h)
    l_hip, r_hip = _pt(lm, 23, w, h), _pt(lm, 24, w, h)
    l_knee, r_knee = _pt(lm, 25, w, h), _pt(lm, 26, w, h)
    l_ankle, r_ankle = _pt(lm, 27, w, h), _pt(lm, 28, w, h)

    torso_len = distance(_midpoint(l_sh, r_sh), _midpoint(l_hip, r_hip))
    mid_knee = _midpoint(l_knee, r_knee)

    msgs = []
    if calculate_angle(l_hip, l_knee, l_ankle) > 70 or calculate_angle(r_hip, r_knee, r_ankle) > 70:
        msgs.append("Bend your knees completely")
    if calculate_angle(l_sh, l_hip, l_knee) > 75 or calculate_angle(r_sh, r_hip, r_knee) > 75:
        msgs.append("Pull your knees closer to your chest")
    if distance(l_wr, l_knee) > (0.45 * torso_len) or distance(r_wr, r_knee) > (0.45 * torso_len):
        msgs.append("Wrap your hands around your shins")
    if distance(nose, mid_knee) > (0.55 * torso_len):
        msgs.append("Lift your head and bring your nose to your knees")
    if abs(l_wr[1] - r_wr[1]) > (0.35 * torso_len):
        msgs.append("Keep both hands close to your legs")
    if mid_knee[1] > max(l_hip[1], r_hip[1]) + (0.1 * torso_len):
        msgs.append("Draw your knees up higher toward your chest")
        
    return len(msgs) == 0, msgs


def thunderbolt(lm, w, h):
    l_sh, r_sh = _pt(lm, 11, w, h), _pt(lm, 12, w, h)
    l_wr, r_wr = _pt(lm, 15, w, h), _pt(lm, 16, w, h)
    l_hip, r_hip = _pt(lm, 23, w, h), _pt(lm, 24, w, h)
    l_knee, r_knee = _pt(lm, 25, w, h), _pt(lm, 26, w, h)
    l_ankle, r_ankle = _pt(lm, 27, w, h), _pt(lm, 28, w, h)

    mid_sh = _midpoint(l_sh, r_sh)
    mid_hip = _midpoint(l_hip, r_hip)
    torso_len = distance(mid_sh, mid_hip)

    msgs = []
    
    # Anti-sitting check: Knees must be entirely folded flat under you
    if calculate_angle(l_hip, l_knee, l_ankle) > 60 or calculate_angle(r_hip, r_knee, r_ankle) > 60:
        msgs.append("Sit completely down on your heels")
        
    if abs(mid_sh[0] - mid_hip[0]) > (0.25 * torso_len):
        msgs.append("Sit up straight; stack shoulders over hips")
    if distance(l_wr, l_knee) > (0.45 * torso_len) or distance(r_wr, r_knee) > (0.45 * torso_len):
        msgs.append("Rest your hands down on your knees")
        
    return len(msgs) == 0, msgs