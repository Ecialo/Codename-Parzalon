__author__ = 'Ecialo'
import cocos
import consts as con
import expression as ex
consts = con.consts


class HUD(cocos.layer.Layer):

    is_event_handler = True

    def __init__(self, game_layer):
        self.game_layer = game_layer
        super(HUD, self).__init__()
        self.game_layer.script_manager.set_handler('run_dialog', self.run_dialog)
        self.current_dialog = None

    def run_dialog(self, dialog_name, actor, location):
        print "DIALOGS"
        self.current_dialog = ex.Dialog(ex.dialogs_db[dialog_name])
        self.add(self.current_dialog.current_phrase())
        self.schedule(self.show_dialog)

    def show_dialog(self, dt):
        phrase = self.current_dialog.update(dt)
        if phrase:
            self.remove(phrase)
            if self.current_dialog.num_of_phrases() == 0:
                self.unschedule(self.show_dialog)
                self.current_dialog = None
            else:
                self.add(self.current_dialog.current_phrase())

    def on_exit(self):
        self.game_layer.script_manager.remove_handler('run_dialog', self)



