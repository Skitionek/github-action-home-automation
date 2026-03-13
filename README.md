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
2. **Add your Roborock username** as a GitHub secret (`username`).
3. Run the `Request Authorization Code` action.
4. Check your email for the verification code and **add it as a GitHub secret** (`code_or_password`).
5. Run the `Authenticate User` action. Copy the base64 string printed at the end of the run and **add it as a GitHub secret** (`ROBOROCK_USER_DATA`).
6. Then, iteratively:
   - Update the `target_x` and `target_y` secrets (the dock station is approximately at `2500,2500`).
   - Run the `Move Vacuum for Emptying` action.
   - Repeat until the vacuum reaches the desired position.

Let me know if you end up reproducing or improving this setup—I'd love to hear about it!
