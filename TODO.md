## Game config
- [ ] Add support for different card progressions (max..1.1..max, 1..max..1, etc.).
- [ ] Add option for penalty for missing prediction.
- [ ] Add option for lower bonus when 0 tricks predicted.
- [ ] Add option for manual trump setting each round (turn over top card in deck).
- [ ] Add ability to provide custom round score calculation.

## Gameplay

- [x] Add buttons for 'Place Bids' and 'Add Scores' to `game_show.html`.
- [x] Add logic for those buttons in `views.py`.
  - [x] Place bids:
    - [x] Allow each player's bid to be entered (max. is all hands in round; cannot add up to
      the number of cards in round)
      - [x] Show row under the score table, with a textbox for the current player
      - [x] Show 'Next' button under the textbox
      - [x] Show bids for each player in their row
    - [x] Submit: redirect back to game_show.html (having saved the bids in each
      GamePlayerGameRound and the total in the GameRound)
    - [x] Use whether total_tricks_predicted has been set in the latest_game_round to dictate
      which button to show?
  - [x] Add scores:
    - [x] Allow each player's score to be entered (max. is all hands in round; must add up to
      the number of cards in round)
    - [x] Create the next GameRound or declare the game over if all rounds have been played
      (will need to calculate the number of rounds in the game; maybe store in the Game?)

## Users
- [x] Collect user's first and last name when they sign up
  - [x] Create player for user automatically
- [ ] Allow players to be shared across users (so that if a User shares their token with another User, their Players are
   both visible to each other, to enable a single Player to play games on multiple User accounts).
  - [ ] Give each user a token/ID they can use to be added by others
  - [ ] Allow users to add their friends as players from their user token
  - [ ] Allow a user's players to be retrospectively linked to other user accounts (via the account's user token)


## URLs
- [x] Change `games/<game_id>/round/<round_id>/{bids, scores}` to `games/<game_id>/round/<round_number>/{bids, scores}` - more intuitive!

## General
- [ ] Add **many** more tests.
- [ ] DRY things up (e.g. helper functions and view logic)
- [ ] Make CSS customisations common. There are a _lot_ of `style=...`s dotted around, which I'd love to use for custom
   classes in `static/main/main.css`.
- [ ] Add ability to email results to other players.
