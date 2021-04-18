# CardIoPlay
A Playing Card game made with Python and Pygame.

I made this game to get familiar with the Python programing langage, so **it's not perfect** but it's *playable*.

It has a multiplayer mode: the two machine need to be connected to same network.



## Game first window: Setup the game

![Game first window](https://github.com/robotane/CardIoPlay/blob/main/screen_shots/Screenshot%20at%202021-04-18%2022-18-39.png)



## Playing a survival mode of 4 players

![Playing a survival mode](https://github.com/robotane/CardIoPlay/blob/main/screen_shots/Screenshot%20at%202021-04-18%2022-19-32.png)


The game rules are very easy:
* At the beginning, a radom player plays a card of his choice
* You just have to play (by clicking on it in your cards) a card which suit (Spade, Heart, Diamond or Club) is same to the curent played card. If it happens that you don't have one of the same suit, you can take one of the already played cards (again, by clicking on it), this end the raw.
* The raw ends when the last player has played or a card has been taken.
* At the end of the raw, the player with higest card rank wins the raw and starts a new raw by playing a card of his choice.
* When a player have played all his cards, he leaves the game.
* Players are ordered by leaving order: the first player to leave is the first and the last to leave is the last.
* In survival mode:
   * the last player to leave gets a *Yellow Card*,
   * if a player got two *Yellow Cards* he leaves definitively the game,
   * the very last player is the big winner.

