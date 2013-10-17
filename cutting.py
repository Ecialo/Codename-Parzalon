import pyglet
import cocos
from cocos.director import director
from cocos.scene import *
from cocos.menu import *
from cocos.layer import *


class Dealing_With_Animations(cocos.layer.Layer):
    def __init__(self, image, frame_height, frame_width):
        super(Dealing_With_Animations, self).__init__()
        self.image = None
        self.name = image
        self.frame_height = frame_height
        self.frame_width = frame_width
        self.frames = []
        self.pyg_anim = self.image
        self.animation = self.image
        self.duration_list = []

    def make_animation(self):
        image_sequence = map(lambda img: img, self.frames)
        self.pyg_anim = pyglet.image.Animation.from_image_sequence(image_sequence, 0.2, True)
        for i in range(len(self.duration_list)):
            self.pyg_anim.frames[i].duration = float(self.duration_list[i])
        self.animation = cocos.sprite.Sprite(self.pyg_anim)
        self.animation.position = (300, 300)
        self.add(self.animation)

    def cut(self):
        self.image = pyglet.image.load(self.name)
        start = self.image.height
        i = 1
        while start >= self.frame_height:
            left_border = 0
            bottom_border = self.image.height - self.frame_height*i
            end = self.image.width
            while end >= self.frame_width:
                cut = self.image.get_region(left_border, bottom_border, self.frame_width, self.frame_height)
                self.frames.append(cut)
                left_border += self.frame_width
                end -= self.frame_width
            start -= self.frame_height
            i += 1
        for i in range(len(self.frames)):
            self.duration_list.append(0.2)


class FrameMenu(Menu):
    def __init__(self, d):
        super(FrameMenu, self).__init__()
        self.font_item['font_name'] = 'Edit Undo Line BRK',
        self.font_item['color'] = (32, 16, 32, 255)
        self.font_item['font_size'] = 16
        self.font_item_selected['font_size'] = 20
        self.d = d
        self.position = (0, -80)
        self.frame = 0

        items = [EntryMenuItem('Number of Frame', self.on_change_frame, str(0)),
                 EntryMenuItem('Its duration', self.on_change_duration, str(0)),
                 MenuItem('Back', self.on_back)]
        self.create_menu(items)

    def on_change_frame(self, value):
        self.frame = value

    def on_change_duration(self, value):
        self.d.duration_list[int(self.frame)] = value

    def on_back(self):
        self.parent.switch_to(0)


class MyMenu(Menu):
    def __init__(self, d):
        super(MyMenu, self).__init__()
        self.font_item['font_name'] = 'Edit Undo Line BRK',
        self.font_item['color'] = (32, 16, 32, 255)
        self.font_item['font_size'] = 16
        self.font_item_selected['font_size'] = 20
        self.d = d
        self.f = ''
        self.new_file = True
        self.position = (0, -80)
        items = [EntryMenuItem('Choose name of image', self.on_choose_name, ''),
                 MenuItem('Start animation', self.on_start_animation),
                 MenuItem('Stop animation', self.on_stop_animation),
                 MenuItem('Change Frame Duration', self.on_change_frame_duration),
                 EntryMenuItem('Change Frame Height', self.on_change_frame_height, ''),
                 EntryMenuItem('Change Frame Width', self.on_change_frame_width, ''),
                 EntryMenuItem('Change Name of File', self.on_change_name_of_file, ''),
                 MenuItem('Save', self.on_save),
                 MenuItem('Quit', self.on_quit)]
        self.create_menu(items)

    def on_change_name_of_file(self, value):
        self.f = value

    def on_choose_name(self, value):
        self.new_file = True
        self.d.name = value

    def on_change_frame_height(self, value):
        self.new_file = True
        self.d.frame_height = int(value)

    def on_change_frame_width(self, value):
        self.new_file = True
        self.d.frame_width = int(value)
    
    def on_start_animation(self):
        if self.new_file:
            del self.d.duration_list[:]
            self.d.duration_list[:] = []
            del self.d.frames[:]
            self.d.frames[:] = []
            self.d.cut()
        self.d.make_animation()
        self.d.add(self.d.animation, z = 2)
        self.parent.switch_to(2)

    def on_stop_animation(self):
        self.d.animation.kill()

    def on_change_frame_duration(self):
        self.new_file = False
        self.parent.switch_to(1)

    def on_save(self):
        ff = open(self.f, 'a')
        s = ' '.join(map(str, self.d.duration_list))
        ff.write(self.d.name + '\n')
        ff.write(str(self.d.frame_height) + '\n')
        ff.write(str(self.d.frame_width) + '\n')
        ff.write(s + '\n\n')
        ff.close()

    def on_quit(self):
        pyglet.app.exit()


class AnimLayer(Menu):
    def __init__(self, d):
        super(AnimLayer, self).__init__()
        self.d = d
        self.font_item['font_name'] = 'Edit Undo Line BRK',
        self.font_item['color'] = (32, 16, 32, 255)
        self.font_item['font_size'] = 16
        self.font_item_selected['font_size'] = 20
        self.position = (0, -200)

        items = []
        self.create_menu(items)

    def on_quit(self):
        self.parent.switch_to(0)
        self.d.animation.kill()

director.init(resizable=True)
d = Dealing_With_Animations('image', 80, 80)
#f = open('config', 'a')
scene = Scene()
scene.add(d, z = 2)
scene.add(ColorLayer(190,190,190,190))
scene.add(MultiplexLayer(MyMenu(d), FrameMenu(d), AnimLayer(d)), z = 2)
director.run(scene)
#f.close()