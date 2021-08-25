# -*- coding:Utf8 -*-
# Started on 16-11-2019
# (C) John Robotane-2019


from random import *
import pygame
import itertools
import sys
import os
from Constants import *


def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)


CARDS_IMAGES = {}


def add_card(name):
    name_lower = name.lower()
    _image = pygame.image.load(resource_path("cards/" + name_lower + ".png"))
    x, y = _image.get_rect().size
    CARDS_IMAGES[name_lower] = pygame.transform.scale(_image, (int(x * scale), int(y * scale)))


for c, v in itertools.product(color, value):
    add_card(f"{v!s}_{c}")

add_card(JOKER)

add_card(BACK)


class Card(pygame.sprite.Sprite):
    """A playing card"""

    CLOVER = CLOVER
    DIAMOND = DIAMOND
    SPADE = SPADE
    HEART = HEART
    KING = KING
    QUEEN = QUEEN
    JAW = JAW
    JOKER = JOKER
    AS = AS

    def __init__(self, value, color=None, scale=0.5):
        """ Constructor, create the image of the card."""

        super().__init__()
        self.image: pygame.Surface
        self.color = color
        self.value = value
        self.scale = scale
        # Load the image
        self.image = CARDS_IMAGES[self.name]
        self.rect: pygame.rect.Rect = self.image.get_rect()

    def __str__(self):
        return f"{self.value} of {self.color}"

    @property
    def name(self):
        if self.color is not None:
            return "{}_{}".format(str(self.value).lower(), self.color.lower())
        else:
            return "{}".format(str(self.value).lower())

    def get_repr(self):
        return "Card('{}','{}',{})".format(self.value, self.color, self.scale)

    def __repr__(self):
        return self.get_repr()

    def same_color_2(self, card):
        return (self.color == Card.DIAMOND or self.color == Card.HEART) \
               and (card.color == Card.SPADE or card.color == Card.CLOVER)

    def same_color(self, card):
        return self.color == card.color

    def same_value(self, card):
        return self.value == card.value

    def is_eq(self, card):
        return self.same_value(card) and self.same_color(card)

    def copy_from(self, card):
        self.image = card.image
        self.color = card.color
        self.value = card.value


class PlayingCards(object):
    """A playing card"""

    def __init__(self, nb_game=1, remove_list=None):
        """Init the cards"""
        if remove_list is None:
            remove_list = []
        self.nb_games = nb_game
        self.cards = []
        for col in color:
            for val in value:
                for nbj in range(nb_game):
                    self.cards.append(Card(val, col))
        self.cards.append(Card(JOKER))
        self.cards.append(Card(JOKER))
        self.remove_list = remove_list
        if self.remove_list:
            self.remove_all(*remove_list)

        self.shuffle()

    def redo(self):
        self.__init__(self.nb_games, self.remove_list)

    def shuffle(self):
        shuffle(self.cards)

    def __iter__(self):
        return iter(self.cards)

    def remove_all(self, *args):
        col = [c for c in args if c in color]
        val = [v for v in args if v in list(value) + [JOKER]]
        v_c = [t for t in args if isinstance(t, tuple)]
        # print(col)
        # print(val)
        # print(v_c)
        self.remove_colors(*col)
        self.remove_values(*val)
        self.remove_values_colors(*v_c)

    def remove_values(self, *args):
        self.cards = [c for c in self.cards if c.value not in args]

    def remove_colors(self, *args):
        self.cards = [c for c in self.cards if c.color not in args]

    def remove_values_colors(self, *args):
        self.cards = [c for c in self.cards if (c.value, c.color) not in args]

    def nb_cart(self):
        return self.nb_games * len(color) * len(value)

    def __bool__(self):
        return bool(self.cards)

    def remaining(self):
        return len(self.cards)

    def __contains__(self, item):
        return item in self.cards

    def pop(self):
        """Pop the latest card in the playing card game."""
        if not self.cards:
            return None
        else:
            return self.cards.pop()


class Player(object):
    name = 'Name'
    type = 'IA'
    HUMAN = "HM"
    COMPUTER = "IA"
    ONLINE = "OL"
    pos = [0, 0]

    def __init__(self, name: str, _type: str = COMPUTER, pc_game: PlayingCards = None) -> None:
        self.cards_in_hand = pygame.sprite.Group()
        self.played_cards = pygame.sprite.Group()
        self.cards_in_hand.empty()
        self.played_cards.empty()
        self.name = name
        self.playing_cards_game = pc_game
        self.type = _type
        self.score = 0
        self.status = GREEN

    def __str__(self):
        return f"{self.__class__.__name__} Name: {self.name} Type: {self.type}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name!r},{self.type!r})"

    def __eq__(self, other):
        return self.name == other.name

    def draw(self, screen):
        self.cards_in_hand.draw(screen)

    def init(self, nb_cards):
        self.score = 0
        self.cards_in_hand = pygame.sprite.Group()
        self.played_cards = pygame.sprite.Group()
        for i in range(nb_cards):
            self.play()

    def played(self, card):
        self.played_cards.add(card)

    def get_card(self):
        return self.playing_cards_game.pop()

    def play(self, card: Card = None) -> Card:
        p_card = self.get_card()
        if card is not None:
            self.played(card)
        if p_card is not None:

            if self.type != self.HUMAN:
                p_card.image = CARDS_IMAGES[BACK]

            if card is None:
                self.add_card(p_card)
            else:
                card.copy_from(p_card)
                p_card = card
                self.cards_in_hand.add(card)
        else:
            if card is not None:
                self.remove_card(card)
        return p_card

    def update_cards_pos(self):
        cards_copy = self.cards_in_hand.copy()
        self.cards_in_hand.empty()
        jok_c = Card(JOKER)
        dx = 1
        dy = 0.05
        # all the cards drawing rect width
        c_width = self.pos[0] + dx * jok_c.rect.width * len(cards_copy) + jok_c.rect.width
        if c_width > DESK_WIDTH:
            dx = (DESK_WIDTH - jok_c.rect.width)/(jok_c.rect.width * len(cards_copy))

        # all the cards drawing rect height
        c_height = self.pos[1] + dy * jok_c.rect.height * (len(cards_copy)) + jok_c.rect.height
        if c_height > DESK_HEIGHT:
            dy = (DESK_HEIGHT - self.pos[1] - jok_c.rect.height) / (jok_c.rect.height * (len(cards_copy)))

        for card in cards_copy:
            if self.name != "IA Show" and self.type != self.HUMAN:
                card.rect.x = self.pos[0]
                card.rect.y = self.pos[1] + dy * card.rect.height * len(self.cards_in_hand)
            else:
                card.rect.x = self.pos[0] + dx * card.rect.width * len(self.cards_in_hand)
                card.rect.y = self.pos[1]
            self.cards_in_hand.add(card)

    def add_card(self, card):
        if self.name != "IA Show" and self.type != self.HUMAN:
            card.image = CARDS_IMAGES[BACK]
        self.cards_in_hand.add(card)
        self.update_cards_pos()

    def remove_card(self, card):
        if card in self.cards_in_hand:
            self.cards_in_hand.remove(card)
            if self.has_cards():
                self.update_cards_pos()
        else:
            card_list = [c for c in self.cards_in_hand if c.is_eq(card)]
            if card_list:
                self.cards_in_hand.remove(card_list[0])
                if self.has_cards():
                    self.update_cards_pos()

    def has_cards(self):
        return len(self.cards_in_hand) != 0


class OnLinePlayer(Player):
    ONLINE_COMPUTER = "OLIA"
    ONLINE_HUMAN = "OLHM"

    def __init__(self, name, type=Player.ONLINE):
        super().__init__(name, type)


if __name__ == '__main__':
    game = PlayingCards()
    game.shuffle()

    c = game.pop()
    d = Card(c.value, c.color)
    print(c.is_eq(d))
    print(d.is_eq(c))
    print(d == c)

    # game.remove_value(2, 3, 4, 5, 6, 7, Card.JOKER)
    # game.remove_color(Card.SPADE)
    # game.remove_value_color((10, Card.CLOVER), (5, Card.HEART))
    # c = game.pop()
    # d = game.pop()
    #
    # g = copy.copy(d)
    # print("Before")
    # print(g.value, 'of', g.color)
    # print(d.value, 'of', d.color)
    # d = game.pop()
    # print("After")
    # print(g.value, 'of', g.color)
    # print(d.value, 'of', d.color)
    # del d
    # print("After again")
    # print(g.value, 'of', g.color)
    # print(d.value, 'of', d.color)

    # for i in range(game.remaining() + 1):
    #     card = game.pop()
    #     if card is None:
    #         print('Finish !')
    #     else:
    #         print(card.value, 'of', card.color)
