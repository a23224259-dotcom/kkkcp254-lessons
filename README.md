# CBC Multi-class Telegram Scheduler

Automatically posts learning and revision material to a Telegram channel for every class, from Playgroup to Form 4. It runs on GitHub Actions every 30 minutes, 24 hours a day (East Africa Time, UTC+3).

Each post includes:
- a topic poster (PNG)
- a PDF notes pack
- the full text lesson

Lessons alternate between **learning** and **revision** notes. If an OpenAI key is set, lessons are AI-written; otherwise the built-in lesson bank is used.

## Files

| File | Purpose |
|---|---|
| `multi_class.py` | Main script: builds and sends posts |
| `requirements.txt` | Python packages (Pillow, reportlab) |
| `multi_class_state.json` | Tracks progress so nothing repeats (auto-updated) |
| `.github/workflows/multi_class.yml` | Schedule that runs the script |

## Setup

1. Create a new GitHub repository and upload all four files, keeping the `.github/workflows/` folder path exactly.
2. Add the bot to your Telegram channel as an **admin** with permission to post.
3. In the repo go to **Settings → Secrets and variables → Actions** and add:

   **Secrets**
   - `TG_BOT_TOKEN`: bot token from @BotFather
   - `TG_CHAT_ID`: channel, e.g. `@KKKCP254`
   - `OPENAI_API_KEY`: optional, enables AI-written lessons

   **Variable (optional)**
   - `OPENAI_MODEL`: model name to use for lessons

4. Go to **Settings → Actions → General → Workflow permissions** and choose **Read and write permissions** so the workflow can save the state file.

## Testing

Open **Actions → Multi-class Telegram lessons → Run workflow**. A manual run sends one test lesson and does not use up a scheduled slot.

## How it works

- Every 30 minutes the workflow starts and the script works out the current half-hour slot (48 per day).
- Each slot rotates to the next class and alternates learning and revision.
- The script skips a slot it has already sent and blocks identical content using a hash, so there are no duplicates even if GitHub starts a job late.
- After sending, the workflow commits `multi_class_state.json` back to the repo.

## Adding more content

Add new entries to a class in `LEVELS` or `EXTRA_TOPICS` in `multi_class.py`. Each entry is:

```python
("Topic title", "Short explanation.", "Practice question?", "Answer.")
```

If a class runs out of fresh content, the script stops with a "Duplicate content blocked" error instead of resending. Add more topics to fix it.

## Notes

- GitHub may pause scheduled workflows in repos with no activity for 60 days. The state commits help, but check Actions occasionally.
- Never commit your tokens. Keep them in repository secrets only.
