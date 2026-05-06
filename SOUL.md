# Project: DevSync Demo

## Stack

Python, Node.js, Telegram Bot, Groq API, Docker

## Safe Defaults

- overwrite checkpoints: Y if on experiment branch
- pip installs: Y unless version conflict detected
- docker builds: Y

## Known Fragile Areas

- checkpoint files in /runs/
- database tables

## Alert Always

- Any prompt containing "DROP"
- Any prompt containing "delete"
- Any prompt containing "purge"
- Any prompt containing "remove"
- Any authentication prompt
