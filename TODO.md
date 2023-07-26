- add buttons for 'Place Bids' and 'Add Scores' to game_show.html
  - disable the button which you can't currently do? (e.g. you've already placed bids)
- add logic for those buttons in views.py
  - place bids:
    - allow each player's bid to be entered (max. is all hands in round; cannot add up to
      the number of cards in round)
    - submit: redirect back to game_show.html (having saved the bids in each
      GameRoundGamePlayer and the total in the GameRound)
    - use whether total_tricks_predicted has been set in the latest_game_round to dictate
      which button to show?
  - add scores:
    - allow each player's score to be entered (max. is all hands in round; must add up to
      the number of cards in round)
    - create the next GameRound or declare the game over if all rounds have been played
      (will need to calculate the number of rounds in the game; maybe store in the Game?)