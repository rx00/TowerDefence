from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QTimer
from ImageButton import register_button, ImageButton
from entities.figures import Cannon, Gendalf


class ControlPanel:
    control_pane_exists = False

    def __init__(self, app_link, from_basement):
        if not ControlPanel.control_pane_exists:
            ControlPanel.control_pane_exists = True
            self.controller = app_link
            self.control_panel = QLabel(self.controller.app)
            self.control_panel_position = 800
            self.last_basement = from_basement

            self.animation_timer = QTimer()
            self.close_control_panel = None
            self.cannon_bt = None
            self.gendalf_bt = None
            self.golem_bt = None

            self.init_control_panel()
            self.show_control_panel()

    def init_control_panel(self):
        self.control_panel.setGeometry(
            self.control_panel_position, 0, 250, 500
        )
        self.control_panel\
            .setStyleSheet("background-color: rgba(0, 0, 0, 200);")

        self.control_panel.show()

        self.close_control_panel = register_button(
            (10,10),
            [
                "assets/close_control.png",
                "assets/close_control.png"
            ],
            self.control_panel,
            self.__hide_control_panel
        )
        self.close_control_panel.show()

    def show_control_panel(self):
        cannon_img = "assets/cannon_img.png"
        gendalf_img = "assets/gendalf_img.png"
        golem_img = "assets/golem_img.png"

        if self.controller.money < 20:
            cannon_img = "assets/cannon_img_exp.png"
        if self.controller.money < 150:
            gendalf_img = "assets/gendalf_img_exp.png"
        if self.controller.money < 80:
            golem_img = "assets/golem_img_exp.png"

        self.control_panel_position = 800
        self.controller.set_pause()

        self.cannon_bt = register_button(
            (25, 100),
            [
                cannon_img,
                cannon_img
            ],
            self.control_panel,
            lambda _, fig_type=Cannon, money=20:
                self.set_figure(fig_type, money)
        )

        self.gendalf_bt = register_button(
            (25, 170),
            [
                gendalf_img,
                gendalf_img
            ],
            self.control_panel,
            lambda _, fig_type=Gendalf, money=150:
                self.set_figure(fig_type, money)
        )

        self.golem_bt = register_button(
            (25, 240),
            [
                golem_img,
                golem_img
            ],
            self.control_panel,
            self.__hide_control_panel
        )

        self.cannon_bt.show()
        self.gendalf_bt.show()
        self.golem_bt.show()

        self.animation_timer.timeout\
            .connect(lambda: self.change_control_panel_position(False))
        self.animation_timer.start(1)

    def __hide_control_panel(self):
        self.cannon_bt.disconnect()
        self.gendalf_bt.disconnect()
        self.golem_bt.disconnect()
        self.control_panel_position = 600
        self.animation_timer = QTimer()
        self.animation_timer.timeout\
            .connect(
                lambda: self.change_control_panel_position(True))
        self.animation_timer.start(1)

    def change_control_panel_position(self, hide):
        if hide:
            control_panel_position_delta = 2
        else:
            control_panel_position_delta = -2
        if 600 <= self.control_panel_position <= 800:
            ImageButton.repaint_all()
            self.control_panel_position += control_panel_position_delta
            self.control_panel.move(self.control_panel_position, 0)
        else:
            self.animation_timer.stop()
            if hide:
                ControlPanel.control_pane_exists = False
                self.control_panel.deleteLater()

    def set_figure(self, figure_type, money):
        if self.controller.money - money >= 0:
            self.controller.money -= money
            self.controller.money_bar.setText(str(self.controller.money))
            q_basement_cords = (self.last_basement.x(), self.last_basement.y())
            new_tower = figure_type(self.controller.app)
            new_tower.entity_logic_object.coordinates = q_basement_cords
            self.last_basement.deleteLater()
            new_tower.tick()
            new_tower.entity_logic_object.on_entity_kill_event.add(
                self.controller.add_money
            )
            new_tower.entity_graphic_object.on_press = \
                lambda tower=new_tower: self.controller.show_instruments(tower)
            self.controller.map_objects.add(new_tower)
            self.__hide_control_panel()
