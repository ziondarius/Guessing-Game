# Guessing-Game

Desktop quiz/guessing game built with Python + `pygame`.

## Main App
- `quiz.py` is the active desktop app.
- `index.html` is an older browser prototype kept in the repo.

## Features
- Random question order (each question used once per round)
- Reveal answer + optional hint
- Mark each question as `Correct` or `Incorrect`
- End screen with score (`You got X out of Y`)
- `Restart` and `Close` on completion
- Fullscreen toggle
- Edit mode to manage question data:
  - Add new questions
  - Delete questions
  - Update question, answer, and hint

## Run
```bash
cd "/Users/ziondarius/Dropbox/KIDS/ZION/CODE/Guessing Game/Guessing-Game"
python3 quiz.py
```

## Data
- Initial question data is defined in `STARTING_QUESTIONS` inside `quiz.py`.
- Questions edited in-app are in-memory for the current run.

## Extra Files
- `speech_review_questions.xlsx`: review sheet with Question / Answer / Hint columns.
