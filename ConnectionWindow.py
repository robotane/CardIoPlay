import socket
import threading

import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UILabel, UIButton

import CardsGame
from Constants import *


class ConnectionWindow(UIWindow):
    def __init__(self, args: dict, int_sec, rect, ui_manager):
        self.game_args = args
        self.int_sec = int_sec
        super().__init__(rect, ui_manager,
                         window_display_title='Waiting for connections',
                         object_id='#connection_window',
                         resizable=True)
        self.enable_close_button = False
        self.close_window_button = None
        size = [150, 35]
        self.nb_online = self.game_args["nb_online"]
        self.socket = socket.socket()
        HOST = socket.gethostbyname(socket.gethostname())
        print(HOST, PORT)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((HOST, PORT))
        self.socket.listen(self.nb_online)
        self.socket_list = []
        self.socket_list.append((self.int_sec.player_name, self.socket))
        self.thread = ListeningThread(self)
        self.thread.setDaemon(True)
        self.thread.start()
        UILabel(pygame.Rect((0, 0), size), f"Connected players", self.ui_manager, container=self)

        self.new_game_btn = UIButton(pygame.Rect((self.relative_rect.width - 160,
                                                  self.relative_rect.height - 140),
                                                 (100, 40)),
                                     'GO',
                                     self.ui_manager,
                                     container=self,
                                     )

    def process_event(self, event: pygame.event.Event):
        super().process_event(event)
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.new_game_btn:
                    if self.int_sec.game is None and len(self.socket_list) == self.nb_online + 1:
                        self.game_args["sockets_list"] = self.socket_list
                        self.int_sec.game = CardsGame.CardsGame(**self.game_args)
                        self.int_sec.start_game = True
                    elif self.int_sec is None:
                        print("Game not initialized.")

    def update(self, time_delta):
        super().update(time_delta)


class ListeningThread(threading.Thread):
    def __init__(self, con_win: ConnectionWindow):
        threading.Thread.__init__(self, name="con_win_listening")
        self.con_win = con_win
        self.socket = con_win.socket

    def run(self) -> None:
        step = 40
        size = [400, 35]
        for i in range(self.con_win.nb_online):
            con, add = self.socket.accept()
            name = con.recv(64).decode().split("$")[-1]
            self.con_win.socket_list.append((name, con))
            UILabel(pygame.Rect((0, step * (i + 1)), size), f"{i + 1}. {name} connected from {add[0]}",
                    self.con_win.ui_manager, container=self.con_win)
