# GitHub Action Home Automation

This is a small exploratory project aimed at automating my robot vacuum to move next to the trash bin on a schedule, so it can be emptied. While this solution is admittedly simplistic—and there are likely more elegant ways to approach it—I found it good enough for my needs, and I didn't have the time to over-engineer it.

Despite its simplicity, it gets the job done:

- **Moves the vacuum next to the trash bin on a schedule**
- Sends notifications (via GitHub) when errors occur
- Maintains an easily accessible log of all actions
- Allows authorized remote control via the public internet

I like to think of it as *ingenious in its simplicity*.

---

## How It Works

Commands are sent to the vacuum directly through the **Roborock cloud API** (via MQTT), so no local network access or self-hosted runner is required. All workflows run on standard GitHub-hosted runners (`ubuntu-latest`).

Authentication credentials are stored as a GitHub Actions secret (`ROBOROCK_USER_DATA`) so they persist between runs without needing a local machine.

Want to see it in action? Check the GitHub Action runs in the repository.

## Setup Instructions

You can get the system running in just a few steps:

1. **Fork** this repository.
2. Request a verification code:
   ```bash
   python request_code.py your@email.com
   ```
3. Check your email for the code, then authenticate:
   ```bash
   python auth.py your@email.com <code-or-password>
   ```
4. Copy the printed values and add them as GitHub Actions secrets:
   - `ROBOROCK_USERNAME` — your Roborock account email
   - `ROBOROCK_USER_DATA` — the YAML block printed by `auth.py`
5. Add your target coordinates as GitHub secrets (`target_x`, `target_y`).
   The dock station is approximately at `2500,2500`.
6. Run the `Home Automation` workflow (or wait for the Thursday schedule) to move the vacuum.

To send the vacuum to coordinates manually:
```bash
export ROBOROCK_USERNAME=your@email.com
export ROBOROCK_USER_DATA="$(cat user_data.yaml)"
python goto.py 2500 2500
```

Let me know if you end up reproducing or improving this setup—I'd love to hear about it!
