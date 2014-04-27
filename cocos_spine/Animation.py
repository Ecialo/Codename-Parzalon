__author__ = 'Ecialo'

import math
from bisect import bisect

LINEAR = 0
STEPPED = -1
BEZIER_SEGMENTS = 10.0
FRAME_SPACING = 6
LAST_FRAME = -1
TIME = 0

# JSON: [name->{slots->[name->attachment->[data]],
#               bones->[{rotate->[data], translate->[data], scale->[data]}]]


class Timeline(object):

    def __init__(self):
        self.frames = []

    def get_keyframe_count(self):
        pass

    def apply(self, time, alpha):
        pass

    def apply_data(self, skeleton_data):
        pass


class Curve_Timeline(Timeline):

    def __init__(self, keyframes):
        super(Curve_Timeline, self).__init__()
        self.curves = [0 for i in xrange((len(keyframes) - 1)*FRAME_SPACING)]

    def set_curve(self, keyframe_index, coefs):
        cx1, cy1, cx2, cy2 = coefs
        subdiv_step = 1.0 / BEZIER_SEGMENTS
        subdiv_step2 = subdiv_step * subdiv_step
        subdiv_step3 = subdiv_step2 * subdiv_step
        pre1 = 3 * subdiv_step
        pre2 = 3 * subdiv_step2
        pre4 = 6 * subdiv_step2
        pre5 = 6 * subdiv_step3
        tmp1x = -cx1 * 2 + cx2
        tmp1y = -cy1 * 2 + cy2
        tmp2x = (cx1 - cx2) * 3 + 1
        tmp2y = (cy1 - cy2) * 3 + 1
        i = keyframe_index * FRAME_SPACING
        self.curves[i] = cx1 * pre1 + tmp1x * pre2 + tmp2x * subdiv_step3
        self.curves[i + 1] = cy1 * pre1 + tmp1y * pre2 + tmp2y * subdiv_step3
        self.curves[i + 2] = tmp1x * pre4 + tmp2x * pre5
        self.curves[i + 3] = tmp1y * pre4 + tmp2y * pre5
        self.curves[i + 4] = tmp2x * pre5
        self.curves[i + 5] = tmp2y * pre5

    def set_linear(self, keyframe_index):
        self.curves[keyframe_index * FRAME_SPACING] = LINEAR
        self.curves[keyframe_index * 6] = LINEAR

    def set_stepped(self, keyframe_index):
        self.curves[keyframe_index * FRAME_SPACING] = STEPPED
        self.curves[keyframe_index * 6] = STEPPED

    def get_curve_percent(self, keyframe_index, percent):
        curveIndex = keyframe_index * FRAME_SPACING
        curveIndex = keyframe_index * 6
        dfx = self.curves[curveIndex]
        if dfx is LINEAR:
            return percent
        if dfx is STEPPED:
            return 0.0
        dfy = self.curves[curveIndex + 1]
        ddfx = self.curves[curveIndex + 2]
        ddfy = self.curves[curveIndex + 3]
        dddfx = self.curves[curveIndex + 4]
        dddfy = self.curves[curveIndex + 5]
        x = dfx
        y = dfy
        i = BEZIER_SEGMENTS - 2
        while True:
            if x >= percent:
                lastX = x - dfx
                lastY = y - dfy
                return lastY + (y - lastY) * (percent - lastX) / (x - lastX)
            if i == 0:
                break
            i -= 1
            dfx += ddfx
            dfy += ddfy
            ddfx += dddfx
            ddfy += dddfy
            x += dfx
            y += dfy
        return y + (1 - y) * (percent - x) / (1 - x) # Last point is 1,1

    def get_duration(self):
        return self.frames[LAST_FRAME][TIME]

    def get_keyframe_count(self):
        return len(self.frames)


class Rotate_Timeline(Curve_Timeline):

    def __init__(self, bone, keyframes):
        super(Rotate_Timeline, self).__init__(keyframes)

        self.bone = bone

        for i in xrange(len(keyframes)):
            keyframe = keyframes[i]
            self.frames.append((keyframe['time'], keyframe['angle']))
            if 'curve' not in keyframe:
                continue
            elif keyframe['curve'] == "stepped":
                self.set_stepped(i)
            else:
                self.set_curve(i, keyframe['curve'])

    def apply_data(self, skeleton_data):
        self.bone = skeleton_data.bones[self.bone]


class Translate_Timeline(Curve_Timeline):

    def __init__(self, bone, keyframes):
        super(Translate_Timeline, self).__init__(keyframes)

        self.bone = bone

        for i in xrange(len(keyframes)):
            keyframe = keyframes[i]
            self.frames.append((keyframe['time'], keyframe['x'], keyframe['y']))
            if 'curve' not in keyframe:
                continue
            elif keyframe['curve'] == "stepped":
                self.set_stepped(i)
            else:
                self.set_curve(i, keyframe['curve'])

    def apply_data(self, skeleton_data):
        self.bone = skeleton_data.bones[self.bone]


class Scale_Timeline(Translate_Timeline):

    def apply_data(self, skeleton_data):
        self.bone = skeleton_data.bones[self.bone]


class Color_Timeline(Curve_Timeline):

    def __init__(self, slot, keyframes):
        super(Color_Timeline, self).__init__(keyframes)
        self.slot = slot

        for i in xrange(len(keyframes)):
            keyframe = keyframes[i]
            self.frames.append((keyframe['time'], (keyframe['r'], keyframe['g'], keyframe['b'], keyframe['a'])))
            if 'curve' not in keyframe:
                continue
            elif keyframe['curve'] == "stepped":
                self.set_stepped(i)
            else:
                self.set_curve(i, keyframe['curve'])


class Attachment_Timeline(Timeline):

    def __init__(self, slot, keyframes):
        super(Attachment_Timeline, self).__init__()
        self.slot = slot

        for keyframe in keyframes:
            self.frames.append((keyframe['time'], keyframe['name']))

    def apply_data(self, skeleton_data):
        self.slot = skeleton_data.slots[self.slot]


class Animation(object):

    def __init__(self, name, timelines):
        self.name = name
        self.timelines = []
        self.load_timelines(timelines)

    def load_timelines(self, timelines):
        #print timelines
        if 'bones' in timelines:
            self.load_bone_timelines(timelines['bones'])
        if 'slots' in timelines:
            self.load_slots_timelines(timelines['slots'])

    def load_bone_timelines(self, bones):
        for bone in bones:
            bone_data = bones[bone]
            if 'rotate' in bone_data:
                self.timelines.append(Rotate_Timeline(bone, bone_data['rotate']))
            if 'translate' in bone_data:
                self.timelines.append(Translate_Timeline(bone, bone_data['translate']))
            if 'scale' in bone_data:
                self.timelines.append(Scale_Timeline(bone, bone_data['scale']))

    def load_slots_timelines(self, slots):
        for slot in slots:
            self.timelines.append(Attachment_Timeline(slot, slots[slot]['attachment']))

    def apply_bones_and_slots_data(self, skeleton_data):
        reduce(lambda _, timeline: timeline.apply_data(skeleton_data), self.timelines, None)