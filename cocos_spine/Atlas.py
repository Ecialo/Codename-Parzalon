__author__ = 'Ecialo'

import pyglet
import os
false = False
true = True


class Atlas(object):

    def __init__(self, file):
        self.atlas = pyglet.image.atlas.TextureBin(1024, 1024)
        self.lib = {}
        self.load(file)

    def load(self, file):
        if not file:
            raise Exception('input cannot be null.')

        st_filename, st_metadata, st_name, st_data = xrange(4)
        state = st_name

        def clean(s):
            return s.strip().rstrip()

        with open(os.path.realpath(file), 'r') as fh:
            image = None
            file_name = None
            file_data = {}
            region_name = None
            region_data = {}
            for line in fh:
                value = clean(line)
                while True:
                    if state is st_filename:
                        file_name = value
                        image = pyglet.image.load(file_name)
                        state = st_metadata
                    elif state is st_metadata:
                        if ':' in value:
                            name, data = map(clean, value.split(':'))
                            file_data[name] = data
                        else:
                            state = st_name
                            continue
                    elif state is st_name:
                        if value:
                            region_name = value
                            state = st_data
                        else:
                            if file_name:
                                self.lib[file_name] = file_data
                            state = st_filename
                    elif state is st_data:
                        if ':' in value:
                            name, data = map(clean, value.split(':'))
                            #TODO: too bad! do not use eval!
                            region_data[name] = eval("("+data+")")
                        else:
                            region_data['region'] = self.get_region(image, region_data)
                            file_data[region_name] = region_data
                            state = st_name
                            continue
                    break

    def get_region(self, image, region_data):
        x, y = region_data['xy']
        width, height = region_data['size']
        region = image.get_region(x, y, width, height)
        return self.atlas.add(region)


if __name__ == "__main__":
    a = Atlas('./data/dragon.atlas')