# -*- coding:Utf8 -*
# Started on 01-03-2020
# (C) John Robotane-2020

import threading

import ui_main
from GameData import OnLinePlayer


def send_message(socket_name, message):
    try:
        socket_name.sendall(message)
    except Exception as e:
        print("Message not sent!!!")
        print(e)

# TODO Remove the use of eval in the class below


class OnlinePlayerThread(threading.Thread):
    def __init__(self, thread_name, game, socket_name):
        threading.Thread.__init__(self, name=thread_name)
        self.socket_name = socket_name
        self.game: ui_main.Game = game

    def run(self):
        while True:
            try:
                data = self.socket_name.recv(5120).decode()
                data: str
                if len(data) == 0:
                    continue
                if data.startswith("PLAYED_STR"):
                    self.game.is_waiting = True
                    self.game.send_online("\nSTART_WAITING\n", True)
                    lines = data.splitlines()[1:]
                    for dat in lines:
                        if not dat:
                            continue
                        print(dat.replace("$", " "))
                        d_list = dat.split("$")
                        action = d_list[0]

                        if action == "SET_VAR":
                            ar = eval(f"{d_list[2]!r}")
                            eval_str = f"self.game.set_{d_list[1]}({ar})"
                            eval(eval_str)
                        elif action == "CLEAR_PLAYED":
                            self.game.clear_played()
                        elif action == "UPDATE_POS":
                            self.game.update_pos()
                        elif action == "ADD_CARD":
                            self.game.current_player.add_card(eval(d_list[1]))
                        elif action == "REMOVE_CARD":
                            self.game.current_player.remove_card(eval(d_list[1]))
                        elif action == "TAKEN_CARD":
                            c = eval(d_list[1])
                            self.game.current_player.add_card(c)
                            self.game.remove_played_card(c)
                            self.game.taken_card = c
                        elif action == "PLAYED_CARD":
                            c = eval(d_list[1])
                            self.game.last_played_card = c
                            self.game.current_player.remove_card(c)
                            self.game.add_played_card(c)
                        elif action == "ADD_PLAYER":
                            name = d_list[1]
                            _type = d_list[2]
                            if name == self.game.player_name:
                                _type = OnLinePlayer.HUMAN
                            else:
                                _type = OnLinePlayer.ONLINE+_type
                            op = OnLinePlayer(name, _type)
                            self.game.add_online_player_client(op)
                        elif action == "NEXT_PLAYER":
                            self.game.next_player()
                            print(f"current_player:::{self.game.current_player.name}")
                    self.game.is_waiting = False
                    self.game.send_online("\nSTOP_WAITING\n", True)
            except Exception as e:
                print("Some errors occurred!!!")
                print(e)


class ServerThread(threading.Thread):
    def __init__(self, thread_name, game, socket_name):
        threading.Thread.__init__(self, name=thread_name)
        self.socket_name = socket_name
        self.game: ui_main.Game = game

    def run(self):
        while True:
            try:
                data = self.socket_name.recv(5120).decode()
                data: str
                if len(data) == 0:
                    continue
                if data.startswith("PLAYED_STR"):
                    lines = data.splitlines()[1:]
                    for dat in lines:
                        if not dat:
                            continue
                        print(dat.replace("$", " "))
                        d_list = dat.split("$")
                        action = d_list[0]
                        if action == "ONLINE_PLAYED":
                            p_c = eval(d_list[1])
                            t_c = eval(d_list[2])
                            self.game.played_card = p_c
                            self.game.taken_card = t_c
                            self.game.online_played = True
                            # print(f"played::{self.game.played_card}")
                            # print(f"taken::{self.game.taken_card}")
                            self.game.run_logic(True)
                        elif action == "ADD_PLAYER":
                            self.game.add_online_player_server(d_list[1])
                        elif action == "START_WAITING":
                            self.game.nb_waiting += 1
                        elif action == "STOP_WAITING":
                            self.game.nb_waiting -= 1
                        elif action == "PAUSED":
                            self.game.nb_paused += 1
                        elif action == "RESUMED":
                            self.game.nb_paused -= 1
                        elif action == "SET_VAR":
                            ar = eval(f"{d_list[2]!r}")
                            eval_str = f"self.game.set_{d_list[1]}({ar})"
                            eval(eval_str)

            except Exception as e:
                print("Some errors occurred!!!")
                print(e)
