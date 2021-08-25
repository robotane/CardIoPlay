# -*- coding:Utf8 -*
# Started on 01-03-2020
# (C) John Robotane-2020


"""

"""

import random
import socket
from typing import Optional, Any

import GetOnlineData
import playingcards
# --- Classes ---
import GameUi
import IntroWindow
from playingcards import *


class Hand(pygame.sprite.Sprite):
    """ This class represents the hand. """

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([15, 15]).convert_alpha()
        self.image.fill(RED)
        # self.image.set_alpha(95)
        self.rect = self.image.get_rect()

    def update(self):
        """ Update the hand location. """
        pos = pygame.mouse.get_pos()
        self.rect.x = pos[0]
        self.rect.y = pos[1]


class CardsGame(object):
    """ This class represents an instance of the game. If we need to
        reset the game we'd just need to create a new instance of this
        class. """
    current_player: Player

    best_player: Player
    last_player: Player
    first_player: Player
    previous_player: Player
    last_played_card: Card
    taken_card: Card
    best_card: Card

    def __init__(self, player_name="John", nb_players=5, nb_online=0, level=3, nb_playing_cards=2, _type=None,
                 sockets_list=None, survival_mode=False, ):
        """ Constructor. Create all our attributes and initialize
        the game. """
        self.type = _type

        pygame.init()
        self.size = [SCREEN_WIDTH, SCREEN_HEIGHT]
        self.screen = pygame.display.set_mode(self.size)

        self.played_pos = [100, 200]
        self.unplayed_pos = [100, 100]
        self.ia_cards_pos = [int(Card(JOKER).rect.width * 1.5), int(self.played_pos[1] + Card(JOKER).rect.height * 1.6)]
        self.human_cards_pos = [10, 50]
        self.def_init()
        self.nb_online = nb_online
        self.survival_mode = survival_mode

        self.auto_mode = False
        self.auto_mode_delay = 3  # seconds

        self.playing_players = []
        self.players = []
        if self.survival_mode:
            self.survival_players = []

        for k, v in CARDS_IMAGES.items():
            CARDS_IMAGES[k] = v.convert_alpha()
        if self.type is None or self.type == TYPE_SERVER:
            self.nb_players = nb_players
            self.nb_playing_cards = nb_playing_cards
            self.nb_cards = 0
            self.level = level
            self.card_game = PlayingCards(self.nb_playing_cards, remove_list=[JOKER, "2", "3", "4", "5"])
            # self.card_game.remove_values()
            self.player_name = player_name

            if self.type == TYPE_SERVER:
                self.online_played = False
                self.added_online = 0
                self.nb_waiting = 0
                self.nb_paused = 0
                self.socket = sockets_list[0][1]
                self.online_p_sockets = [el[1] for el in sockets_list[1:]]
                for name, sock in sockets_list[1:]:
                    print(name)
                    thread = GetOnlineData.ServerThread(f"{name}_thread", self, sock)
                    thread.setDaemon(True)
                    thread.start()

            # Init playing_players
            self.create_players()
            self.current_player = self.playing_players[0]
            # self.playing_players = self.players.copy()
            if self.type == TYPE_SERVER:
                for name, _ in sockets_list[1:]:
                    self.add_online_player_server(name)
                # while self.added_online < self.nb_online:
                #     pass
                self.send_online("UPDATE_POS")
            self.update_pos()
            self.deals_all_cards()
            # if self.type == TYPE_SERVER:
            #     self.send_online("", True)

        else:
            self.host_address = self.type
            self.type = TYPE_CLIENT
            # self.player_name = f"Socket_{randint(0, 100)}"
            self.player_name = player_name
            # self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket = socket.socket()
            self.socket.connect((self.host_address, PORT))
            self.thread = GetOnlineData.OnlinePlayerThread("server_thread", self, self.socket)
            self.thread.setDaemon(True)
            self.thread.start()
            self.send_online(f"ADD_PLAYER${self.player_name}", True)
            # self.socket.connect((self.host_address, PORT))

        # Create cards sprites lists
        self.played_cards = pygame.sprite.Group()
        self.default_sprites = pygame.sprite.Group()
        self.all_sprites_list = pygame.sprite.Group()

        # Create the hand
        self.hand = Hand()
        # but = Button("Hello", 500, 500, action=lambda: print("Hello"))
        # self.default_sprites.add(but)
        self.default_sprites.add(self.hand)

        # --- Pygame_gui gui elements initialisation ---
        self.game_stat = GameUi.GameStat(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), self)

        # background image
        self.background_img = pygame.image.load(resource_path("background.png")).convert_alpha()

    def def_init(self):
        self.end_raw = False
        self.game_over = False
        self.paused = True
        self.played = False
        self.last_played_card = None
        self.best_card = None
        self.taken_card = None
        self.played_card = None
        self.current_player = None
        self.previous_player = None
        self.meta_card = "Joker"
        self.started = True
        self.last_player = None
        self.best_player = None
        self.score_windows = None
        # self.game_over = True
        self.quit = False
        self.go_home = False
        self.is_waiting = False
        self.paused = False
        self.started = False
        if self.type:
            self.played_str = "PLAYED_STR"

    @staticmethod
    def get_value(card: Card) -> int:
        """Returns the numeric value  of the card."""
        if not str(card.value).isdigit():
            if card.value == JAW:
                return 8
            if card.value == QUEEN:
                return 9
            if card.value == KING:
                return 10
            if card.value == AS:
                return 20
            if card.value == JOKER:
                return 50
        else:
            return int(card.value)

    @staticmethod
    def compare(card1: Card, card2: Card) -> int:
        """Returns:

        0 if card1 value == card2 value,

        1 if card1 value < card2 value,

        -1 if card1 value > card2 value.

        The value of the cards are computed using the static method "get_value". """
        if CardsGame.get_value(card1) < CardsGame.get_value(card2):
            return 1
        if CardsGame.get_value(card1) > CardsGame.get_value(card2):
            return -1
        return 0

    def create_players(self) -> None:
        """Creates all the players, one human player and the rest are "bots" """
        p = Player(self.player_name, Player.COMPUTER if self.player_name == "IA Show" else Player.HUMAN, self.card_game)
        p.pos = self.human_cards_pos
        p.init(self.nb_cards)
        self.playing_players.append(p)
        if self.type == TYPE_SERVER:
            self.send_online(f"ADD_PLAYER${p.name}${p.type}")

        for k in range(self.nb_players - 1):
            p = Player("Player {}".format(k + 1), Player.COMPUTER, self.card_game)
            p.pos = [10 + k * self.ia_cards_pos[0], self.ia_cards_pos[1]]
            p.init(self.nb_cards)
            self.playing_players.append(p)
            if self.type == TYPE_SERVER:
                self.send_online(f"ADD_PLAYER${p.name}${p.type}")

    def update_pos(self):
        """Update cards positions."""
        if not self.survival_mode or (self.survival_mode and not self.players):
            self.players = self.playing_players.copy()
        me = [c for c in self.players if c.name == self.player_name][0]
        for i in range(len(self.players) - 1):
            cur = self.players[(self.players.index(me) + 1) % len(self.players)]
            cur.pos = [10 + i * self.ia_cards_pos[0], self.ia_cards_pos[1]]
            self.players[self.players.index(cur)] = cur
            me = cur

    def restart(self):
        self.score_windows.kill()
        player = self.sort_players()[-1]
        if player.status == GREEN:
            player.status = ORANGE
        elif player.status == ORANGE:
            player.status = RED
        player.cards_in_hand.empty()
        if self.survival_mode:
            if not self.survival_players or len(self.survival_players) >= 2:  # TODO Fix continue conditions
                # A survival game is continuing
                self.survival_players = [p for p in self.players if p.status != RED]
            else:
                # A new game is starting
                for p in self.players:
                    # Resetting the status of all players
                    p.status = GREEN
                self.survival_players = self.players.copy()
            self.playing_players = self.survival_players.copy()
        else:
            self.playing_players = self.players.copy()

        for p in self.playing_players:
            p.score = 0

        self.def_init()

        if self.type is None or self.type == TYPE_SERVER:
            self.card_game.redo()
            self.deals_all_cards()
        self.played_cards.empty()

    def resume(self):
        self.screen = pygame.display.set_mode(self.size)
        self.paused = False
        self.quit = False
        self.played = False
        self.go_home = False
        return self.run()

    def deals_all_cards(self):
        """Deals all the cards to the playing players. The player which will get the last card will be the first to
        play"""
        self.current_player = choice(self.playing_players)
        if self.type == TYPE_SERVER:
            self.set_var("current_player", self.current_player.name)
        while self.card_game:
            card = self.card_game.pop()
            self.current_player.add_card(card)
            if self.type == TYPE_SERVER:
                self.send_online(f"ADD_CARD${card!r}")
            self.last_player = self.current_player
            self.next_player()
        self.current_player = self.last_player
        self.last_player = self.playing_players[self.playing_players.index(self.current_player) - 1]
        self.nb_cards = len(self.current_player.cards_in_hand)
        if self.type == TYPE_SERVER:
            self.set_var("current_player", self.current_player.name)
            self.set_var("last_player", self.last_player.name)

    def send_online(self, msg, now=False):
        self.played_str += f"\n{msg}"
        if not now:
            return

        if self.type == TYPE_SERVER:
            for sock in self.online_p_sockets:
                sock.sendall(self.played_str.encode())
        elif self.type == TYPE_CLIENT:
            self.socket.sendto(self.played_str.encode(), (self.host_address, PORT))
        self.played_str = "PLAYED_STR"

    def set_var(self, variable_name, value):
        msg = f"SET_VAR${variable_name}${value!r}"
        self.send_online(msg)

    def add_played_card(self, card: Card) -> None:
        """Add a card which have been played to the played card list"""
        card.rect.x = self.played_pos[0] + card.rect.width * len(self.played_cards) // 2
        card.rect.y = self.played_pos[1]
        self.played_cards.add(card)

    def remove_played_card(self, card):
        if card in self.played_cards:
            self.played_cards.remove(card)
            self.update_cards_pos()
        else:
            # TODO use the index which will be send by
            #      the server to know exactly which card to remove
            card_list = [c for c in self.played_cards if card.is_eq(c)]
            if card_list:
                self.played_cards.remove(card_list[0])
                self.update_cards_pos()

    def add_online_player_server(self, name):
        p = Player(name, Player.ONLINE, self.card_game)
        k = len(self.playing_players)
        p.pos = [10 + k * self.ia_cards_pos[0], self.ia_cards_pos[1]]
        p.init(self.nb_cards)
        self.playing_players.append(p)
        self.send_online(f"ADD_PLAYER${p.name}${p.type}")
        self.added_online += 1

    def add_online_player_client(self, player):
        k = len(self.playing_players)
        if player.name != self.player_name:
            player.pos = [10 + k * self.ia_cards_pos[0], self.ia_cards_pos[1]]
        else:
            player.pos = self.human_cards_pos
        self.playing_players.append(player)

    def set_current_player(self, player):
        p_l = [p for p in self.playing_players if p.name == player]
        self.current_player = p_l[0]

    def set_taken_card(self, card):
        self.taken_card = card

    def set_best_card(self, card):
        self.best_card = card

    def set_end_raw(self, _value):
        self.end_raw = _value

    def set_played(self, _value):
        self.played = _value

    def set_started(self, _value):
        self.started = _value

    def set_after_click(self, _value):
        self.game_stat.after_click = _value

    def set_best_player(self, player):
        p_l = [p for p in self.playing_players if p.name == player]
        self.best_player = p_l[0]

    def set_last_player(self, player):
        p_l = [p for p in self.playing_players if p.name == player]
        self.last_player = p_l[0]

    def sort_players(self) -> list:
        if self.survival_mode and self.survival_players:
            p_l = self.survival_players
        else:
            p_l = self.players
        sorted_players = sorted(p_l, key=lambda l: l.score,
                                reverse=False)
        return sorted_players

    def update_cards_pos(self):
        """Update the played cards positions to make them tiny when tey are too much."""
        cards_copy = self.played_cards.copy()
        self.played_cards.empty()
        for card in cards_copy:
            card.rect.x = self.played_pos[0] + card.rect.width * len(self.played_cards) // 2
            card.rect.y = self.played_pos[1]
            self.played_cards.add(card)

    def clear_played(self):
        self.played_cards.empty()  # Empty the played cards
        self.end_raw = False
        self.current_player = self.best_player
        self.best_card = None
        self.last_played_card = None
        self.taken_card = None
        self.played = False

    def next_player(self) -> None:
        """Set the value of current_player to the player who follows the current one. If it's the last player, then the
        current player is the first player of the playing_players list."""
        self.current_player = self.playing_players[
            (self.playing_players.index(self.current_player) + 1) % len(self.playing_players)]
        if self.type == TYPE_SERVER:
            self.send_online("NEXT_PLAYER")

    def ai_player(self, player: Player, card: Card = None) -> Optional[Any]:
        """The AI playing... too much to say here..."""
        cards = player.cards_in_hand.sprites()
        cards.sort(key=self.get_value)
        if card is None:
            p_card = choice(cards)
            no_as = [c for c in cards if c.value != playingcards.AS]
            no_as.sort(key=self.get_value)
            if self.level == 1:
                if no_as:
                    return choice(no_as)
                return p_card
            if self.level == 2:
                return cards[0]
            if self.level >= 3:
                m_list = []
                for col in color:
                    t_list = [c for c in cards if c.color == col]
                    if len(t_list) > len(m_list):
                        m_list = t_list
                m_list.sort(key=self.get_value)
                p_card = m_list[0]
            if self.level >= 4:
                c_as = [c for c in cards if c.value == Card.AS]
                if c_as and (len(c_as) == len(cards) - 1):
                    p_card = choice(c_as)
                elif len(cards) == 2:
                    p_card = cards[-1]
                elif len(player.cards_in_hand) < self.nb_cards * 0.4:
                    # print("Not taken")
                    if no_as:
                        p_card = no_as[-1]
                    elif c_as:
                        p_card = c_as[0]

            if self.level >= 5:
                if self.nb_playing_cards == 1 and not (
                        self.nb_cards / 2.5 < len(player.cards_in_hand) < 1.5 * self.nb_cards):
                    best_c = []
                    # TODO IMPLEMENT THIS:
                    #  If a player has a AS a 10 a 9 and a 8 of the same color and all  the other cards are AS
                    #  of other color for example,  in game with one packet of playing cards, he should play the 8 first,
                    #  then the 9, the 10 (or one of the AS and finish with the non AS) and then the AS.
                    # for ca in c_as:
                    #     l = [c for c in cards if c.color == ca.color]
                    #     if len()
                    pass
            return p_card

        same_col = [c for c in cards if card.same_color(c)]
        assert same_col
        same_col.sort(key=self.get_value)
        no_as = [c for c in same_col if c.value != playingcards.AS]
        no_as.sort(key=self.get_value)
        val_sup = [c for c in same_col if self.get_value(c) >= self.get_value(c)]
        val_sup.sort(key=self.get_value)
        if self.level == 1:
            if val_sup:
                return choice(val_sup)
            return choice(same_col)
        if self.level == 2:
            if val_sup:
                return val_sup[0]
            if no_as:
                return no_as[0]
            # return same_col[0]
        p_card = choice(cards)
        if self.level >= 3:
            val_inf = [c for c in same_col if self.get_value(c) < self.get_value(card)]
            val_inf.sort(key=self.get_value)

            sup_no_as = [c for c in no_as if self.get_value(c) > self.get_value(card)]
            sup_no_as.sort(key=self.get_value)
            if sup_no_as:
                p_card = sup_no_as[0]
            else:
                val_eq = [c for c in same_col if self.get_value(c) == self.get_value(card)]

                if val_inf:
                    p_card = val_inf[0]
                elif val_eq:
                    p_card = val_eq[0]
                elif self.nb_cards * 0.8 < len(player.cards_in_hand):
                    return None
                else:
                    best_col = [c for c in same_col if self.get_value(c) >= self.get_value(card)]
                    best_col.sort(key=self.get_value)
                    if best_col:
                        p_card = best_col[0]
                    # elif val_inf:
                    #     p_card = val_inf[0]
                    else:
                        p_card = same_col[0]

        return p_card

    def process_events(self):
        """ Process all of the events. Return a "True" if we need
            to close the window."""

        for event in pygame.event.get():
            if event.type == pygame.QUIT or self.quit:
                return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                m_pos = pygame.mouse.get_pos()
                if m_pos[0] <= DESK_WIDTH - self.hand.rect.width and m_pos[1] <= DESK_HEIGHT - self.hand.rect.height:
                    self.played = True

            if event.type == pygame.K_ESCAPE:
                self.paused = not self.paused
            self.game_stat.process_event(event)
        return False

    def run_logic(self, online=False):
        """
        This method is run each time through the frame. It
        updates positions and checks for collisions.
        """
        # Move all the sprites
        if self.type == TYPE_SERVER:
            self.is_waiting = self.nb_waiting != 0

        if self.type == TYPE_SERVER and not self.started:
            self.set_var("started", True)
            self.started = True
            self.send_online("", True)
            return

        self.default_sprites.update()
        if (self.is_waiting and not online) or (self.type == TYPE_CLIENT and not self.started) or self.paused:
            return
        # self.current_player.cards_in_hand.update()
        # self.played_cards.update()
        if not online:
            self.played_card = None  # The card the current user will play
        if self.game_over:
            self.played = False
            return
        # Handling auto playing mode
        if self.auto_mode and not self.end_raw:
            if self.current_player.type != Player.HUMAN:
                self.played = True
            else:
                pass  # TODO Pause the game for 'self.auto_mode_delay' seconds
        if self.played or (self.current_player.type == Player.ONLINE and online):
            if self.played:
                self.game_stat.after_click = True
                # if self.type == TYPE_SERVER:
                #     self.set_var("after_click", True)
                self.previous_player = self.current_player
            # if someone won the raw and/or some took a played card
            if self.type != TYPE_CLIENT and (self.end_raw or (not online and self.taken_card)):
                self.played_cards.empty()  # Empty the played cards
                self.end_raw = False
                self.current_player = self.best_player
                self.last_player = self.playing_players[self.playing_players.index(self.best_player) - 1]
                if self.type == TYPE_SERVER:
                    # self.set_var("played", True)
                    self.set_var("last_player", self.last_player.name)
                    self.send_online(f"CLEAR_PLAYED", True)
                # The last player is the player before the current player
                self.best_card = None
                self.last_played_card = None
                self.taken_card = None
                self.played = False  # Thus, we will wait for a click to continue
                return  # We return on in order to wait for a click to continue
            self.played = False

            if not online:
                if self.type == TYPE_CLIENT:
                    if self.current_player.name == self.player_name:
                        p_card = None
                        t_card = None
                        li = pygame.sprite.spritecollide(self.hand, self.current_player.cards_in_hand, False)
                        if li:
                            p_card = li[-1]
                            if p_card and self.last_played_card and not p_card.same_color(
                                    self.last_played_card):
                                p_card = None
                        if p_card is None:
                            li_a = pygame.sprite.spritecollide(self.hand, self.played_cards, False)
                            if li_a:
                                t_card = li_a[-1]
                        self.send_online(f"ONLINE_PLAYED${p_card!r}${t_card!r}")
                    elif self.current_player.type != OnLinePlayer.ONLINE_HUMAN or self.end_raw:
                        self.set_var("played", True)
                    self.send_online("", True)
                    self.played = False
                    return

                if self.current_player.type == Player.COMPUTER:
                    if self.best_card:
                        same_col = [c for c in self.current_player.cards_in_hand if self.last_played_card.same_color(c)]
                        if same_col:
                            self.played_card = self.ai_player(self.current_player, self.best_card)
                    else:
                        self.played_card = self.ai_player(self.current_player)
                elif self.current_player.type == Player.HUMAN:
                    # I don't know how to get the collided sprite which the is on the top, so as
                    # "pygame.sprite.spritecollide" returns a list of the sprites which collided which the 'hand',
                    # I just take the last one which deems to be the one on top.
                    li = pygame.sprite.spritecollide(self.hand, self.current_player.cards_in_hand, False)
                    if li:
                        self.played_card = li[-1]
                        if self.played_card and self.last_played_card and not self.played_card.same_color(
                                self.last_played_card):
                            self.played_card = None
            # If the current has not played a card from his hand, here we let him take from the played cards
            if self.current_player.type != Player.ONLINE:
                if self.played_card is None:
                    if self.current_player.type == Player.HUMAN:
                        li_a = pygame.sprite.spritecollide(self.hand, self.played_cards, False)
                        if li_a:
                            self.taken_card = li_a[-1]
                    else:
                        # As players take most of the time the best card...
                        self.taken_card = self.best_card

            if self.played_card is None and self.taken_card is None:
                """If the player has not played a card and has not taken a card from the played cards, we just
                 don't do something: we just wait for a click again"""
                self.played = False
                if self.current_player.type == Player.ONLINE:
                    self.online_played = False
                return

            if self.taken_card:
                # If the current player has taken a card from the played cards
                self.current_player.add_card(self.taken_card)
                self.remove_played_card(self.taken_card)
                # self.played_cards.remove(self.taken_card)
                self.played_cards.update()
                if self.type == TYPE_SERVER:
                    self.send_online(f"TAKEN_CARD${self.taken_card!r}")
                self.update_cards_pos()
            if self.played_card:
                tp_card = Card(self.played_card.value, self.played_card.color)
                self.current_player.remove_card(self.played_card)
                if not self.best_card or self.get_value(tp_card) > self.get_value(self.best_card):
                    """If best_card is None, we will then initialize it else if and only if the value of the 
                    played card is greater than the best card value, we update the best card value to the played 
                    card.
                    Regarding the best player, we update the old value only if the new best player has some cards in
                    his hand."""
                    self.best_card = tp_card
                    if self.type == TYPE_SERVER:
                        self.set_var("best_card", self.best_card)
                    if self.current_player.has_cards():
                        self.best_player = self.current_player
                        if self.type == TYPE_SERVER:
                            self.set_var("best_player", self.best_player.name)
                self.last_played_card = tp_card
                self.add_played_card(tp_card)
                if self.type == TYPE_SERVER:
                    self.send_online(f"PLAYED_CARD${tp_card!r}")
            # If a card has been taken from the played cards or the current player is the last player, then the
            # raw ends else, we continue with the next player.
            if self.taken_card or self.current_player == self.last_player:
                self.end_raw = True
                if self.type == TYPE_SERVER:
                    self.set_var("end_raw", self.end_raw)
            else:
                self.next_player()
            if self.type == TYPE_SERVER:
                self.send_online("", True)
            self.played = False

        """Here we remove all the players which have not some cards in their hands from the 'playing_players' list."""
        winners = [p for p in self.playing_players if not p.has_cards()]
        w: Player
        if winners:
            for w in winners:
                if self.current_player == w:
                    self.next_player()
                self.playing_players.remove(w)
                w.score = len(self.players) - len(self.playing_players)
            if self.best_player not in self.playing_players:
                self.best_player = self.current_player
        if len(self.playing_players) <= 1:
            self.current_player.score = len(self.players)
            self.game_over = True

    def display_frame(self, screen: pygame.display):
        """ Display everything on the screen."""
        # screen.fill(WHITE)
        screen.blit(self.background_img, (0, 0))
        # self.game_stat.update(60, screen)
        font = pygame.font.SysFont("serif", 25)
        if self.type == TYPE_CLIENT and not self.started:
            text = font.render("Waiting for server!", True, pygame.Color("red"))
            center_x = SCREEN_WIDTH // 2 - text.get_width()
            center_y = SCREEN_HEIGHT // 2 - text.get_height()
            screen.blit(text, [center_x, center_y])
            self.default_sprites.draw(screen)
            pygame.display.flip()
            return
        if self.paused:
            text = font.render("Game Paused!", True, pygame.Color("green"))
            center_x = SCREEN_WIDTH // 2 - text.get_width()
            center_y = SCREEN_HEIGHT // 2 - text.get_height() - 60
            screen.blit(text, [center_x, center_y])
        # Display players names and scores
        t_color = pygame.Color("white")
        for player in self.players:
            text = font.render("{}".format(player.name), True, t_color)

            if player.name != "IA Show" and player.type != Player.HUMAN:
                if player.has_cards():
                    text2 = font.render(
                        f"{len(player.cards_in_hand)} card{'s' if len(player.cards_in_hand) > 1 else ''}",
                        True, t_color)
                else:
                    text2 = font.render("Out" if player.status != RED else "Not playing", True, t_color)
                # pygame.draw.circle(screen, player.status, [int(player.pos[0] + 5), int(player.pos[1] - 60 + 14)], 10)
                screen.blit(text, [player.pos[0] + (15 if self.survival_mode else 0), player.pos[1] - 60])
                screen.blit(text2, [player.pos[0] + 6, player.pos[1] - 30])
            else:
                if player.has_cards():
                    text = font.render(
                        f"{player.name}                      {len(player.cards_in_hand)} card{'s' if len(player.cards_in_hand) > 1 else ''}",
                        True, t_color)
                else:
                    text = font.render(
                        f"{player.name}                      {'Out' if player.score != -1 else 'Not playing'}",
                        True, t_color)
                screen.blit(text, [player.pos[0] + (15 if self.survival_mode else 0), player.pos[1] - 40])

            # Display the status
            if self.survival_mode:
                t2_y = int(player.pos[1]) - (60 if (player.name != "IA Show" and player.type != Player.HUMAN) else 40)
                t2_x = int(player.pos[0]) - 5
                rec_h = text.get_height() - 5
                rec_w = text.get_height() - 10

                pygame.draw.polygon(screen, BLACK,
                                    [(t2_x, t2_y),
                                     (t2_x + rec_w, t2_y),
                                     (t2_x + rec_w, t2_y + rec_h),
                                     (t2_x, t2_y + rec_h),
                                     ])
                sp = 2
                t2_y += sp
                t2_x += sp
                rec_h -= 2 * sp
                rec_w -= 2 * sp

                pygame.draw.polygon(screen, player.status,
                                    [(t2_x, t2_y),
                                     (t2_x + rec_w, t2_y),
                                     (t2_x + rec_w, t2_y + rec_h),
                                     (t2_x, t2_y + rec_h),
                                     ])
            # Draw player cards in hand on the screen
            player.draw(screen)

        # Draw played cards on the screen
        self.played_cards.draw(screen)

        # Draw the name of the player which have to play
        text = font.render(f"{self.current_player.name}'s turn to play", True, t_color)
        screen.blit(text, [DESK_WIDTH - text.get_width() - 10, 10])
        c = Card(JOKER)
        # If a card has been taken, draw the name of the player whom took it and the card name
        text: pygame.Surface
        if self.taken_card:
            text = font.render("{} took {} of {}!".format(self.current_player.name,
                                                          self.taken_card.value,
                                                          self.taken_card.color),
                               True,
                               pygame.Color("red"))
            center_x = DESK_WIDTH - text.get_width() - 10
            center_y = self.played_pos[1] + (c.rect.height - text.get_height()) // 2
            screen.blit(text, [center_x, center_y])

        # If a player won a raw, draw the name of the winner
        if self.end_raw:
            text = font.render("{} wins the raw!".format(self.best_player.name), True, pygame.Color("green"))
            # center_x = self.played_pos[0] - c.rect.width // 4 - 20
            center_x = DESK_WIDTH - text.get_width() - 10
            center_y = self.played_pos[1]  # + c.rect.height/2 - text.get_height() * 1.5
            screen.blit(text, [center_x, center_y])
        # If the game is over, draw the name of the winner
        if self.score_windows is None and self.game_over:
            self.score_windows = GameUi.ScoreWindow(self,
                                                    pygame.rect.Rect((SCREEN_WIDTH // 4, 0),
                                                                     (SCREEN_WIDTH // 2, DESK_HEIGHT)),
                                                    self.game_stat.ui_manager)

        self.game_stat.update(60, screen)

        # Draw the others sprites on the screen
        self.default_sprites.draw(screen)
        pygame.display.flip()
        self.current_player.cards_in_hand.update()
        self.played_cards.update()

    def run(self) -> bool:
        """ Main program function. """
        # Initialize Pygame and set up the window

        pygame.display.set_caption("CardIoPlay")
        pygame.mouse.set_visible(False)

        done = False
        clock = pygame.time.Clock()
        # print(*g_args)
        # Create an instance of the Game class

        # Main game loop
        while not done:
            # Process events (keystrokes, mouse clicks, etc)
            done = self.process_events()

            # Update object positions, check for collisions
            self.run_logic()

            # Draw the current frame
            self.display_frame(self.screen)

            # Pause for the next frame
            clock.tick(60)
        if self.go_home:
            return False
        else:
            # Close window and exit
            pygame.quit()
        return True


if __name__ == "__main__":
    int_game = IntroWindow.IntroScreen()
    int_game.run()
