__author__ = 'Ecialo'

import math
from bisect import bisect

LINEAR = 0
STEPPED = -1
BEZIER_SEGMENTS = 10.0
FRAME_SPACING = 6
LAST_FRAME = -1
TIME = 0
ANGLE = 1
ATTACHMENT_NAME = 1
X = 1
Y = 2

# JSON: [name->{slots->[name->attachment->[data]],
#               bones->[{rotate->[data], translate->[data], scale->[data]}]]


class Timeline(object):

    def __init__(self):
        self.frames = []

    def get_keyframe_count(self):
        pass

    def apply(self, skeleton, time, alpha):
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
        return y + (1 - y) * (percent - x) / (1 - x)    # Last point is 1,1

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

    def apply(self, skeleton, time, alpha):
        #return
        #print "Translate"
        frame_count = len(self.frames)
        print self.frames, self.bone.name
        if frame_count > 1:
            index = bisect(self.frames, (time, None))
            if 0 < index <= frame_count:

                bone = self.bone

                left_frame = self.frames[index - 1]
                right_frame = self.frames[index]

                # Interpolate between the last frame and the current frame
                right_frame_time = right_frame[TIME]
                left_frame_time = left_frame[TIME]
                #print self.frames, self.bone.name, index
                time_percent = 1.0 - (time - right_frame_time) / (left_frame_time - right_frame_time)
                time_percent = min(time_percent, 1.0)
                time_percent = max(time_percent, 0.0)
                percent = self.get_curve_percent(index-1, time_percent)

                right_frame_rotation = right_frame[ANGLE]
                left_frame_rotation = left_frame[ANGLE]

                bone_rotation = ((bone.local_tsr.rotation % 360) - 180)*-1
                bone_data_rotation = bone.bone_data.tsr.rotation
                delta = (right_frame_rotation - left_frame_rotation)
                rotation = bone_rotation + (bone_data_rotation + left_frame_rotation + delta * percent - bone_rotation)*alpha
                bone.local_tsr.rotation = rotation % 360


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

    def apply(self, skeleton, time, alpha):
        #return
        return
        #print "Translate"
        frame_count = len(self.frames)
        if frame_count > 1:
            index = bisect(self.frames, (time, None))
            if 0 <= index <= frame_count:

                bone = self.bone

                left_frame = self.frames[index - 1]
                right_frame = self.frames[index]

                # Interpolate between the last frame and the current frame
                right_frame_time = right_frame[TIME]
                left_frame_time = left_frame[TIME]
                #print self.frames, self.bone.name, index
                time_percent = 1.0 - (time - right_frame_time) / (left_frame_time - right_frame_time)
                time_percent = min(time_percent, 1.0)
                time_percent = max(time_percent, 0.0)
                percent = self.get_curve_percent(index-1, time_percent)

                right_frame_x = right_frame[X]
                right_frame_y = right_frame[Y]
                left_frame_x = left_frame[X]
                left_frame_y = left_frame[Y]

                bone_x, bone_y = bone.local_tsr.position
                bone_data_x, bone_data_y = bone.bone_data.tsr.position
                x = bone_x + (bone_data_x + left_frame_x + (right_frame_x - left_frame_x) * percent - bone_x) * alpha
                y = bone_y + (bone_data_y + left_frame_y + (right_frame_y - left_frame_x) * percent - bone_y) * alpha
                bone.local_tsr.position = (x, y)
                return


class Scale_Timeline(Translate_Timeline):

    def apply_data(self, skeleton_data):
        self.bone = skeleton_data.bones[self.bone]

    def apply(self, skeleton, time, alpha):
        return


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

    def apply(self, skeleton, time, alpha):
        return
        #print time
        #print "Attach"
        index = bisect(self.frames, (time, None))
        #print index
        request_attach_name = self.frames[index - 1][ATTACHMENT_NAME]
        if index:
            skeleton.set_attachment(self.slot, request_attach_name)


class Animation(object):

    def __init__(self, name, timelines):
        self.name = name
        self.timelines = []
        self.load_timelines(timelines)
        self.duration = max(map(lambda timeline: timeline.frames[-1][0], self.timelines))

    def load_timelines(self, timelines):
        #print timelines
        if 'bones' in timelines:
            self.load_bone_timelines(timelines['bones'])
        if 'slots' in timelines:
            self.load_slots_timelines(timelines['slots'])

    def apply(self, time, skeleton, loop):
        skeleton_data = skeleton.skeleton_data
        if loop and self.duration:
            time %= self.duration
        for timeline in self.timelines:
            timeline.apply(skeleton_data, time, 1)

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