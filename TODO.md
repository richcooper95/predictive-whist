## Game config
- [ ] add support for different card progressions (max..1.1..max, 1..max..1, etc.)
- [ ] add option for penalty for missing prediction
- [ ] add option for lower bonus when 0 tricks predicted
- [ ] add option for manual trump setting each round (turn over top card in deck)
- [ ] add ability to provide custom round score calculation

## Gameplay

- [x] add buttons for 'Place Bids' and 'Add Scores' to game_show.html
- [x] add logic for those buttons in views.py
  - [x] place bids:
    - [x] allow each player's bid to be entered (max. is all hands in round; cannot add up to
      the number of cards in round)
      - [x] show row under the score table, with a textbox for the current player
      - [x] show 'Next' button under the textbox
      - [x] show bids for each player in their row
    - [x] submit: redirect back to game_show.html (having saved the bids in each
      GameRoundGamePlayer and the total in the GameRound)
    - [x] use whether total_tricks_predicted has been set in the latest_game_round to dictate
      which button to show?
  - [x] add scores:
    - [x] allow each player's score to be entered (max. is all hands in round; must add up to
      the number of cards in round)
    - [x] create the next GameRound or declare the game over if all rounds have been played
      (will need to calculate the number of rounds in the game; maybe store in the Game?)

## Users
- [ ] collect user's first and last name when they sign up
  - [ ] create player for user automatically
- [ ] allow players to be shared across users
  - [ ] give each user a token/ID they can use to be added by others
  - [ ] allow users to add their friends as players from their user token
  - [ ] allow a user's players to be retrospectively linked to other user accounts (via the account's user token)

## URLs
- [x] change `games/<game_id>/round/<round_id>/{bids, scores}` to `games/<game_id>/round/<round_number>/{bids, scores}` - more intuitive!

## General
- [ ] DRY things up (e.g. helper functions and view logic)
- [ ] add ability to email results to other players
