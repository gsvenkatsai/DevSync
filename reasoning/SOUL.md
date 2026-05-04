# Project Rules (SOUL.md)

## Safe Defaults
- Always answer 'Y' to pip install confirmations.
- If a model training run asks to overwrite `/runs/exp_041`, answer 'Y'. That was a known failed experiment and it is safe to overwrite.

## Danger Zones (NEVER AUTO-APPROVE)
- Any prompt containing the words: DROP, DELETE, PURGE, or DESTROY.
- Database migrations on the main branch.