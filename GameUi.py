import pygame
import pygame_gui
from pygame_gui.elements import UILabel, UIPanel, UIButton, UIWindow

from Constants import *


class TextValueLabel(object):
    def __init__(self, text_rect: pygame.rect.Rect, text, value, manager, container):
        self.ui_manager = manager
        self.text_rect = text_rect
        self.container = container
        self.text = text
        self.value = value
        self.text_label = UILabel(self.text_rect,
                                  text,
                                  manager=self.ui_manager,
                                  container=self.container)
        self.value_label = UILabel(pygame.Rect((self.text_rect.x, self.text_rect.y + self.text_rect.height),
                                               (self.text_rect.width, self.text_rect.height)),
                                   value,
                                   manager=self.ui_manager,
                                   container=self.container)

    def set_value(self, value):
        self.value = value
        self.value_label.set_text(value)

    def set_text(self, text):
        self.text = text
        self.text_label.set_text(text)


class GameStat(object):
    def __init__(self, rect: pygame.Rect, game):
        self.rect = rect
        self.game = game
        self.after_click = False
        self.ui_manager = pygame_gui.UIManager((rect.width, rect.height))
        self.ui_manager.preload_fonts([{'name': 'fira_code', 'point_size': 10, 'style': 'bold'},
                                       {'name': 'fira_code', 'point_size': 10, 'style': 'regular'},
                                       {'name': 'fira_code', 'point_size': 10, 'style': 'italic'},
                                       {'name': 'fira_code', 'point_size': 14, 'style': 'italic'},
                                       {'name': 'fira_code', 'point_size': 14, 'style': 'bold'},
                                       {'name': 'fira_code', 'point_size': 14, 'style': 'bold_italic'}
                                       ])
        self.info_panel = UIPanel(pygame.Rect((DESK_WIDTH, 0), (SCREEN_WIDTH - DESK_WIDTH, SCREEN_HEIGHT)),
                                  starting_layer_height=4,
                                  manager=self.ui_manager)
        step = 40
        self.info_label = UILabel(pygame.Rect((0, 0), (self.info_panel.rect.width, step)),
                                  "Game Statistics",
                                  manager=self.ui_manager,
                                  container=self.info_panel)
        self.current_player_label = TextValueLabel(pygame.Rect((0, step), (self.info_panel.rect.width, step)),
                                                   "Current Player",
                                                   f"{self.game.current_player.name if self.game.current_player else ''}",
                                                   self.ui_manager,
                                                   self.info_panel)
        self.last_player_label = TextValueLabel(pygame.Rect((0, 3 * step), (self.info_panel.rect.width, step)),
                                                "Last player",
                                                f"",
                                                self.ui_manager,
                                                self.info_panel)
        self.best_player_label = TextValueLabel(pygame.Rect((0, 5 * step), (self.info_panel.rect.width, step)),
                                                "Best player",
                                                f"",
                                                self.ui_manager,
                                                self.info_panel)
        self.best_card_label = TextValueLabel(pygame.Rect((0, 7 * step), (self.info_panel.rect.width, step)),
                                              "Best card",
                                              f"",
                                              self.ui_manager,
                                              self.info_panel)
        btn_panel_width = SCREEN_WIDTH - 200
        btn_panel_height = SCREEN_HEIGHT - DESK_HEIGHT
        self.history_panel = UIPanel(pygame.Rect((0, DESK_HEIGHT), (btn_panel_width, btn_panel_height)),
                                     starting_layer_height=0,
                                     manager=self.ui_manager)
        btn_y = btn_panel_height // 2 - 20
        self.main_menu_btn = UIButton(pygame.Rect((50, btn_y), (100, 40)), 'MAIN MENU', self.ui_manager,
                                      container=self.history_panel)
        self.pause_game_btn = UIButton(pygame.Rect((btn_panel_width // 2 - 50, btn_y), (100, 40)), 'PAUSE',
                                       self.ui_manager,
                                       container=self.history_panel)
        self.quit_game_btn = UIButton(pygame.Rect((btn_panel_width - 150, btn_y), (100, 40)), 'QUIT', self.ui_manager,
                                      container=self.history_panel)
        self.auto_play_btn = UIButton(pygame.Rect(((SCREEN_WIDTH - DESK_WIDTH) // 2 - 50, SCREEN_HEIGHT - btn_y - 40),
                                                  (100, 40)), 'AUTO ON' if self.game.auto_mode else 'AUTO OFF',
                                      self.ui_manager,
                                      container=self.info_panel)

    def process_event(self, event: pygame.event):
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.quit_game_btn:
                    self.game.quit = True
                elif event.ui_element == self.main_menu_btn:
                    self.game.quit = True
                    self.game.go_home = True
                elif event.ui_element == self.pause_game_btn:
                    self.game.paused = not self.game.paused
                elif event.ui_element == self.auto_play_btn:
                    self.game.auto_mode = not self.game.auto_mode

        self.ui_manager.process_events(event)

    def update(self, tick: int, screen: pygame.display):
        self.pause_game_btn.set_text("RESUME" if self.game.paused else "PAUSE")
        self.auto_play_btn.set_text('AUTO ON' if self.game.auto_mode else 'AUTO OFF')
        self.current_player_label.set_value(f"{self.game.current_player.name}")

        self.last_player_label.set_value(f"{self.game.last_player.name if self.game.last_player else ''}")

        self.best_player_label.set_value(
            f"{self.game.best_player.name if self.game.best_player else (self.game.current_player.name if self.game.current_player else '')}")

        self.best_card_label.set_value(f"{self.game.best_card}")

        self.ui_manager.update(tick)
        self.ui_manager.draw_ui(screen)


class ScoreWindow(UIWindow):
    def __init__(self, game, rect, ui_manager):
        self.game = game

        super().__init__(rect, ui_manager,
                         window_display_title='Score',
                         object_id='#score_window',
                         resizable=True)
        # self.enable_close_button = False
        self.close_window_button = None
        self.score_label = UILabel(pygame.Rect((0, 0), (200, 30)),
                                   f"{'Survival' if self.game.survival_mode else 'Normal'} mode",
                                   self.ui_manager,
                                   container=self)
        step = 40
        size = [80, 35]

        p_list = game.sort_players()
        can_continue = self.game.survival_mode and (len(p_list) > 2 or
                                                    (len(p_list) == 2 and
                                                     p_list[-1].status == GREEN))
        for i, player in enumerate(p_list):
            UILabel(pygame.Rect(0, step * (i + 1), step, size[1]), f"{i + 1}.", self.ui_manager, container=self)
            UILabel(pygame.Rect((step, step * (i + 1)), size),
                    f"{player.name} ",
                    self.ui_manager, container=self)
            if self.game.survival_mode and len(p_list) > 2 and player == p_list[-1] and player.status == ORANGE:
                UILabel(pygame.Rect((step + size[0], step * (i + 1)), size),
                        f"Out",
                        self.ui_manager, container=self)
            if self.game.survival_mode and i == 0 and not can_continue:
                UILabel(pygame.Rect((step + size[0], step * (i + 1)), size),
                        f"Winner",
                        self.ui_manager, container=self)

        self.new_game_btn = UIButton(pygame.Rect((self.relative_rect.width - 160,
                                                  self.relative_rect.height - 140),
                                                 (100, 40)),
                                     'CONTINUE' if can_continue else "NEW",
                                     self.ui_manager,
                                     container=self,
                                     )
        self.game_home_btn = UIButton(pygame.Rect((self.relative_rect.width // 2 - 50,
                                                   self.relative_rect.height - 140),
                                                  (100, 40)),
                                      'HOME',
                                      self.ui_manager,
                                      container=self,
                                      )
        self.quit_game_btn = UIButton(pygame.Rect((50,
                                                   self.relative_rect.height - 140),
                                                  (100, 40)),
                                      'QUIT',
                                      self.ui_manager,
                                      container=self,
                                      )

    def process_event(self, event: pygame.event.Event):
        super().process_event(event)
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.new_game_btn:
                    self.game.restart()
                elif event.ui_element == self.quit_game_btn:
                    self.game.quit = True
                elif event.ui_element == self.game_home_btn:
                    self.game.quit = True
                    self.game.go_home = True

    def update(self, time_delta):
        super().update(time_delta)
