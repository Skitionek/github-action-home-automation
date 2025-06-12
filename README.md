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

In a moment of creative madness, I started thinking seriously about accessibility and ease of replication. Assuming not everyone has a stack of Raspberry Pis lying around, I decided to explore using an old Android phone as the main compute unit.

Here’s what I did:

- Installed **Termux**, **proot-distro**, and a **Debian environment** on the phone  
- Set up a **GitHub Actions runner** within that environment  
- The runner connects to the GitHub repo via long-polling (every 5 minutes)  
- The phone remains on the same local network as my vacuum cleaner  

This setup lets me run Python code on the phone that communicates over localhost with my smart devices—including the vacuum.

Want to see it in action? Check the GitHub Action runs in the repository.

## Setup Instructions

You can get the system running in just a few steps:

1. **Fork** this repository.
2. **Add your Roborock username** as a GitHub secret (`USERNAME`).
3. Run the `Request Authorization Code` action.
4. Check your email for the verification code and **add it as a GitHub secret** (`PASSWORD_OR_CODE`).
5. Run the `Authenticate User` action.
6. Then, iteratively:
   - Update the `TARGET_X` and `TARGET_Y` secrets (the dock station is approximately at `2500,2500`).
   - Run the `Move Vacuum for Emptying` action.
   - Repeat until the vacuum reaches the desired position.

Let me know if you end up reproducing or improving this setup—I’d love to hear about it!
