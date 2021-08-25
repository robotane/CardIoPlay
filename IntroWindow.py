import random
from random import randint

import pygame
import pygame_gui
from pygame_gui.elements import UILabel, UIPanel, UIButton, UIDropDownMenu, UITextEntryLine, UIWindow

import ConnectionWindow
import CardsGame
from Constants import *


class IntroScreen(object):

    def __init__(self):
        pygame.init()
        self.size = [INTRO_SCREEN_WIDTH, INTRO_SCREEN_HEIGHT]
        self.screen = pygame.display.set_mode(self.size)
        self.con_win = None
        self.game_level = 4
        self.game = None
        self.start_game = False
        self.game_nb_players = 4  # TODO The max number of players should be in function of the size of the desk
        self.game_nb_online_players = 1
        self.nb_p_c = 1
        # self.block_list
        self.player_name = "John"
        # self.player_name = "IA Show"
        self.player_type = "offline"
        self.host_address = "localhost"
        self.survival_mode = True
        self.all_sprites_list = pygame.sprite.Group()
        self.block_list = pygame.sprite.Group()
        self.clicked = False
        self.ui_manager = pygame_gui.UIManager((INTRO_SCREEN_WIDTH, INTRO_SCREEN_HEIGHT))
        self.ui_manager.preload_fonts([{'name': 'fira_code', 'point_size': 10, 'style': 'bold'},
                                       {'name': 'fira_code', 'point_size': 10, 'style': 'regular'},
                                       {'name': 'fira_code', 'point_size': 10, 'style': 'italic'},
                                       {'name': 'fira_code', 'point_size': 14, 'style': 'italic'},
                                       {'name': 'fira_code', 'point_size': 14, 'style': 'bold'},
                                       {'name': 'fira_code', 'point_size': 14, 'style': 'bold_italic'}
                                       ])
        step = 40
        s = [150, 35]
        self.name_label = UILabel(pygame.rect.Rect((0, step), s),
                                  "Name",
                                  manager=self.ui_manager)
        self.name_value = UITextEntryLine(
            pygame.Rect((self.name_label.relative_rect.width, self.name_label.relative_rect.y),
                        (200, -1)),
            self.ui_manager)
        self.name_value.set_text(self.player_name)
        # The level
        self.game_level_label = UILabel(pygame.rect.Rect((0, step * 2), s),
                                        "Level",
                                        manager=self.ui_manager)
        self.game_level_drop = UIDropDownMenu([str(i) for i in range(1, 5, 1)],
                                              f"{self.game_level}",
                                              pygame.rect.Rect(((s[0] - step) // 2, step * 3),
                                                               (50, 35)),
                                              self.ui_manager
                                              )
        self.nb_players_label = UILabel(pygame.rect.Rect((s[0], self.game_level_label.relative_rect.y), s),
                                        "NB players",
                                        manager=self.ui_manager)
        self.nb_players_drop = UIDropDownMenu([str(i) for i in range(2, 7, 1)],
                                              f"{self.game_nb_players}",
                                              pygame.Rect((int(1.3 * s[0]), step * 3),
                                                          (50, 35)),
                                              self.ui_manager)

        self.nb_p_c_label = UILabel(pygame.rect.Rect((2 * s[0], self.game_level_label.relative_rect.y), s),
                                    "NB playing cards",
                                    manager=self.ui_manager)

        self.nb_p_c_players_drop = UIDropDownMenu([str(i) for i in range(1, 5, 1)],
                                                  f"{self.nb_p_c}",
                                                  pygame.Rect((int(2.3 * s[0]), step * 3),
                                                              (50, 35)),
                                                  self.ui_manager)
        self.survival_label = UILabel(pygame.rect.Rect((3 * s[0], self.game_level_label.relative_rect.y), s),
                                      "Survival mode",
                                      manager=self.ui_manager)

        self.survival_drop = UIDropDownMenu(["yes", "no"],
                                            f"{'yes' if self.survival_mode else 'no'}",
                                            pygame.Rect((int(3.3 * s[0]), step * 3),
                                                        (60, 35)),
                                            self.ui_manager)

        self.start_game_btn = UIButton(pygame.Rect((INTRO_SCREEN_WIDTH - 200,
                                                    INTRO_SCREEN_HEIGHT - 50),
                                                   (100, 40)),
                                       'START',
                                       self.ui_manager)
        self.resume_game_btn = UIButton(pygame.Rect((INTRO_SCREEN_WIDTH // 2 - 50,
                                                     INTRO_SCREEN_HEIGHT - 50),
                                                    (100, 40)),
                                        'RESUME',
                                        self.ui_manager)
        self.quit_game_btn = UIButton(pygame.Rect((100,
                                                   INTRO_SCREEN_HEIGHT - 50),
                                                  (100, 40)),
                                      'QUIT',
                                      self.ui_manager)
        UILabel(pygame.rect.Rect((10, int(step * 6.5 - s[1])), s),
                "On-line Settings",
                manager=self.ui_manager)
        self.online_panel = UIPanel(pygame.rect.Rect((10, int(step * 6.5)), (INTRO_SCREEN_WIDTH - 20, step * 5)),
                                    starting_layer_height=4,
                                    manager=self.ui_manager)

        self.nb_online_players_label = UILabel(pygame.rect.Rect((s[0], 0), s),
                                               "Online players",
                                               manager=self.ui_manager,
                                               container=self.online_panel)

        self.nb_online_players_drop = UIDropDownMenu([str(i) for i in range(1, 6, 1)],
                                                     f"{self.game_nb_online_players}",
                                                     pygame.Rect((int(1.3 * (s[0])), step),
                                                                 (55, 35)),
                                                     self.ui_manager,
                                                     container=self.online_panel)
        self.player_type_label = UILabel(pygame.rect.Rect((0, 0), s),
                                         "Player type",
                                         manager=self.ui_manager,
                                         container=self.online_panel)
        self.player_type_drop = UIDropDownMenu(["server", "client", "offline"],
                                               f"{self.player_type}",
                                               pygame.Rect((int(0.17 * s[0]), step),
                                                           (100, 35)),
                                               self.ui_manager,
                                               container=self.online_panel)
        self.host_address_label = UILabel(pygame.rect.Rect((s[0], 0), s),
                                          "Host address",
                                          manager=self.ui_manager,
                                          container=self.online_panel)
        self.host_address_entry = UITextEntryLine(pygame.Rect((s[0], step),
                                                              (150, 35)),
                                                  self.ui_manager,
                                                  container=self.online_panel)
        self.host_address_entry.set_text(self.host_address)
        if self.player_type != "client":
            # self.host_address_label.is_enabled = False
            # self.host_address_entry.is_enabled = False

            self.game_level_drop.show()
            self.game_level_label.show()
            self.nb_players_drop.show()
            self.nb_players_label.show()
            self.nb_p_c_players_drop.show()
            self.nb_p_c_label.show()
            self.survival_drop.show()
            self.survival_label.show()

            self.host_address_entry.hide()
            self.host_address_label.hide()
        else:
            # self.host_address_label.is_enabled = True
            # self.host_address_entry.is_enabled = True

            self.game_level_drop.hide()
            self.game_level_label.hide()
            self.nb_players_drop.hide()
            self.nb_players_label.hide()
            self.nb_p_c_players_drop.hide()
            self.nb_p_c_label.hide()
            self.survival_drop.hide()
            self.survival_label.hide()

            self.host_address_label.show()
            self.host_address_entry.show()

        if self.player_type != "server":
            # self.nb_online_players_drop.is_enabled = False
            self.nb_online_players_drop.hide()
            self.nb_online_players_label.hide()
        else:
            # self.nb_online_players_drop.is_enabled = True
            self.nb_online_players_drop.show()
            self.nb_online_players_label.show()

    def run_game(self):
        done = self.game.run()
        if not done:
            pygame.mouse.set_visible(True)
            self.screen = pygame.display.set_mode(self.size)
        else:
            return True

    def process_events(self):
        """ Process all of the events. Return a "True" if we need
            to close the window. """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.clicked = True
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED or self.start_game:
                    if event.ui_element == self.resume_game_btn and self.game:
                        done = self.game.resume()
                        if not done:
                            pygame.mouse.set_visible(True)
                            self.screen = pygame.display.set_mode(self.size)
                        else:
                            return True

                    if event.ui_element == self.start_game_btn or self.start_game:
                        if self.player_type == "client":
                            _type = self.host_address
                        elif self.player_type == "server":
                            _type = self.player_type
                        else:
                            _type = None
                        g_args = {"player_name": self.player_name, "nb_players": self.game_nb_players,
                                  "nb_online": self.game_nb_online_players, "level": self.game_level,
                                  "nb_playing_cards": self.nb_p_c, "_type": _type, "survival_mode": self.survival_mode,
                                  }
                        if self.player_type == "server":
                            if self.con_win is None or not self.con_win.alive():
                                self.con_win = ConnectionWindow.ConnectionWindow(g_args, self,
                                                                pygame.rect.Rect((INTRO_SCREEN_WIDTH // 4, 0),
                                                                                 (
                                                                                 INTRO_SCREEN_WIDTH // 2, DESK_HEIGHT)),
                                                                self.ui_manager)
                        else:
                            self.game = CardsGame.CardsGame(**g_args)

                        if self.game:
                            done = self.game.run()
                            if not done:
                                pygame.mouse.set_visible(True)
                                self.screen = pygame.display.set_mode(self.size)
                            else:
                                return True

                    if event.ui_element == self.quit_game_btn:
                        return True
                if event.user_type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                    if event.ui_element == self.name_value:
                        self.player_name = event.text
                    if event.ui_element == self.host_address_entry:
                        self.host_address = event.text
                if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if event.ui_element == self.survival_drop:
                        self.survival_mode = self.survival_drop.selected_option == "yes"
                    if event.ui_element == self.game_level_drop:
                        self.game_level = int(self.game_level_drop.selected_option)
                    if event.ui_element == self.nb_players_drop:
                        self.game_nb_players = int(self.nb_players_drop.selected_option)
                    if event.ui_element == self.nb_online_players_drop:
                        self.game_nb_online_players = int(self.nb_online_players_drop.selected_option)
                    if event.ui_element == self.nb_p_c_players_drop:
                        self.nb_p_c = int(self.nb_p_c_players_drop.selected_option)
                    if event.ui_element == self.player_type_drop:
                        self.player_type = self.player_type_drop.selected_option

                        if self.player_type != "client":
                            # self.host_address_label.is_enabled = False
                            # self.host_address_entry.is_enabled = False

                            self.game_level_drop.show()
                            self.game_level_label.show()
                            self.nb_players_drop.show()
                            self.nb_players_label.show()
                            self.nb_p_c_players_drop.show()
                            self.nb_p_c_label.show()
                            self.survival_drop.show()
                            self.survival_label.show()

                            self.host_address_entry.hide()
                            self.host_address_label.hide()
                        else:
                            # self.host_address_label.is_enabled = True
                            # self.host_address_entry.is_enabled = True

                            self.game_level_drop.hide()
                            self.game_level_label.hide()
                            self.nb_players_drop.hide()
                            self.nb_players_label.hide()
                            self.nb_p_c_players_drop.hide()
                            self.nb_p_c_label.hide()
                            self.survival_drop.hide()
                            self.survival_label.hide()

                            self.host_address_label.show()
                            self.host_address_entry.show()

                        if self.player_type != "server":
                            # self.nb_online_players_drop.is_enabled = False
                            self.nb_online_players_drop.hide()
                            self.nb_online_players_label.hide()
                        else:
                            # self.nb_online_players_drop.is_enabled = True
                            self.nb_online_players_drop.show()
                            self.nb_online_players_label.show()
            self.ui_manager.process_events(event)

        return False

    def run_logic(self):
        """
        This method is run each time through the frame. It
        updates positions and checks for collisions.
        """
        # Move all the sprites
        self.all_sprites_list.update()
        self.block_list.update()
        if self.clicked:
            col = (randint(0, 255), randint(0, 255), randint(0, 255))
            block = Block(col)
            pos = pygame.mouse.get_pos()
            x = pos[0]
            y = pos[1]
            block.rect.x = x
            block.rect.y = y
            self.block_list.add(block)
            self.all_sprites_list.add(block)
            if len(self.block_list) > 20:
                self.block_list.sprites()[0].kill()
        self.clicked = False

    def display_frame(self, time_delta, screen):
        """ Display everything to the screen for the game. """
        screen.fill(self.ui_manager.get_theme().get_colour('dark_bg'))
        if not self.game:
            self.resume_game_btn.disable()
        elif not self.resume_game_btn.is_enabled:
            self.resume_game_btn.enable()
        # if self.player_type != "server":
        #     self.host_address_label.ui_manager = None
        #     self.host_address_label.ui_container = None
        #     self.host_address_entry.ui_manager = None
        #     self.host_address_entry.ui_container = None

        self.ui_manager.update(time_delta)
        self.ui_manager.draw_ui(screen)

        self.all_sprites_list.draw(screen)
        pygame.display.flip()

    def run(self):
        """ Main program function. """
        # Initialize Pygame and set up the window
        pygame.display.set_caption("Setup")

        # Create our objects and set the data
        done = False
        clock = pygame.time.Clock()

        # intro_game = IntroScreen()

        # Main game loop
        while not done:
            time_delta = clock.tick() / 1000.0
            # Process events (keystrokes, mouse clicks, etc)
            done = self.process_events()

            if not done:
                # Update object positions, check for collisions
                # self.run_logic()
                # Draw the current frame
                self.display_frame(time_delta, self.screen)

            # Pause for the next frame
            # clock.tick(60)

        # Close window and exit
        pygame.quit()


class Block(pygame.sprite.Sprite):
    """ This class represents a simple block the player collects. """

    def __init__(self, color=BLACK):
        """ Constructor, create the image of the block. """
        super().__init__()
        self.image = pygame.Surface([20, 20]).convert_alpha()
        self.image.fill(color)
        self.rect = self.image.get_rect()
        un = 1
        if random.choice([0, 1]):
            self.dy = - un
        else:
            self.dy = un
        if random.choice([0, 1]):
            self.dx = -un
        else:
            self.dx = un

    def update(self):
        """ Automatically called when we need to move the block. """
        over = False
        if self.rect.y < 0 or self.rect.y > INTRO_SCREEN_HEIGHT - self.rect.height:
            self.dy = -self.dy
            over = True
            self.image.fill((randint(0, 255), randint(0, 255), randint(0, 255)))
        if self.rect.x < 0 or self.rect.x > INTRO_SCREEN_WIDTH - self.rect.width:
            self.image.fill((randint(0, 255), randint(0, 255), randint(0, 255)))
            self.dx = -self.dx
            over = True
        groups_: pygame.sprite.Group
        groups_ = self.groups()[0]

        col = pygame.sprite.spritecollide(self, groups_, False)
        if not over and col:
            dif_x = False
            dif_y = False
            for s in col:
                # if s == self:
                #     continue
                if self.dx == s.dx:
                    s.dy = -s.dy
                    # s.image.fill((randint(0, 255), randint(0, 255), randint(0, 255)))
                    dif_x = True
                if self.dy == s.dy:
                    s.dx = -s.dx
                    # s.image.fill((randint(0, 255), randint(0, 255), randint(0, 255)))
                    dif_y = True
            if dif_x:
                # self.image.fill((randint(0, 255), randint(0, 255), randint(0, 255)))
                self.dx = - self.dx
            if dif_y:
                # self.image.fill((randint(0, 255), randint(0, 255), randint(0, 255)))
                self.dy = - self.dy
        self.rect.y += self.dy
        self.rect.x += self.dx
