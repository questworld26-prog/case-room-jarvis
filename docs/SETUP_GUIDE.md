# Setup Guide

This guide takes you from a brand-new computer to a working Case-Room in about 20 minutes. **You don't need any coding experience.** You will copy and paste a few commands, and every step tells you what you should see when it worked.

**Contents**
1. [What you'll need](#1-what-youll-need)
2. [Get a Gemini API key](#2-get-a-gemini-api-key)
3. [Open a terminal](#3-open-a-terminal)
4. [Install uv](#4-install-uv)
5. [Download Case-Room](#5-download-case-room)
6. [Install Case-Room's components](#6-install-case-rooms-components)
7. [Add your settings (the `.env` file)](#7-add-your-settings-the-env-file)
8. [Launch it for the first time](#8-launch-it-for-the-first-time)
9. [Starting it again next time](#9-starting-it-again-next-time)

---

## 1. What you'll need

- A laptop running **macOS**, **Windows 10/11**, or Linux
- An internet connection
- About **2 GB** of free disk space
- A Google account, to create the API key

---

## 2. Get a Gemini API key

Jarvis uses Google's Gemini AI to write its answers. The API key is the password Case-Room uses to talk to Gemini.

1. Go to **https://aistudio.google.com/apikey** and sign in with your Google account.
2. Click **Create API key**.
3. Copy the key. It's a long string that starts with `AIza…`. Paste it somewhere safe for now, such as a note.

> [!IMPORTANT]
> **Free vs. paid keys.** A free key is fine for trying things out and for small groups. With a full class (roughly 20+ students) asking questions at the same time, a free key can hit Google's rate limits and answers will slow down. For live classes, turn on billing for the key in [Google AI Studio](https://aistudio.google.com/). A typical class session costs a few dollars. See [Gemini API pricing](https://ai.google.dev/pricing) for current rates.

> [!CAUTION]
> Treat the API key like a password. Don't email it, post it, or commit it to GitHub. Case-Room keeps it in a file named `.env`, which is automatically excluded from GitHub.

---

## 3. Open a terminal

The terminal is a window where you type commands.

- **Mac:** press `Cmd + Space`, type **Terminal**, and press Enter.
- **Windows:** click Start, type **PowerShell**, and open **Windows PowerShell**.

Keep this window open for the rest of the guide.

---

## 4. Install uv

`uv` is a small tool that installs Python and everything else Case-Room needs, with the right versions, so you don't have to.

**Mac / Linux**, paste this and press Enter:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell)**, paste this and press Enter:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

When it finishes, **close the terminal and open a new one** so it picks up the new tool. Check that it worked:

```bash
uv --version
```

✅ You should see something like `uv 0.x.x`. If you see `command not found`, see [Troubleshooting → Installation](TROUBLESHOOTING.md#installation-problems).

---

## 5. Download Case-Room

Pick **one** of these options.

**Option A: Download a ZIP (easiest)**
1. On the Case-Room GitHub page, click the green **Code** button and choose **Download ZIP**.
2. Unzip it somewhere easy to find, for example your `Documents` folder. You'll get a folder called `case-room` (it may be called `case-room-main`; that's fine).

**Option B: Use git** (if you already have it)
```bash
cd ~/Documents
git clone https://github.com/case-room/case-room.git
```

Now point the terminal at that folder. Type `cd ` (with a space after it), **drag the `case-room` folder from Finder or File Explorer into the terminal window**, and press Enter. The folder's path fills in for you.

```bash
cd /path/to/case-room
```

> [!TIP]
> **Windows Shortcut**: Open File Explorer, go into the `case-room` folder, click the address bar at the top, type `powershell`, and press Enter. A terminal opens directly inside your folder without needing to type `cd`!
>
> Every command from here on must be run from inside the `case-room` folder. If a command says it can't find a file, run this `cd` step again first.

---

## 6. Install Case-Room's components

```bash
uv sync
```

This downloads Python 3.13 and all the libraries Case-Room uses. **The first time can take 5–10 minutes**, depending on your internet speed. Later runs are instant.

✅ It worked when you get your prompt back with no red `error:` lines.

---

## 7. Add your settings (the `.env` file)

Case-Room reads its settings from a file called `.env` in the `case-room` folder. A template called `.env.example` is included.

1. Make a copy of the template:
   - **Mac / Linux:** `cp .env.example .env`
   - **Windows:** `copy .env.example .env`
2. Open `.env` in a text editor:
   - **Mac:** `open -e .env` (opens it in TextEdit)
   - **Windows:** `notepad .env`
3. Fill it in:

```env
# Paste your key from step 2
GOOGLE_API_KEY=AIzaSy...your-key...

# The Gemini model Jarvis uses. Leave as-is unless you know you want another.
MODEL_ID=gemini-2.5-flash
ANALYTICS_MODEL_ID=gemini-2.5-flash

# How long Gemini keeps your case "memorised" between questions.
# Set this a bit longer than your class. 14400s = 4 hours.
CACHE_TTL=14400s

# The password for the Instructor Admin Panel. Choose your own!
ADMIN_PASSWORD=pick-a-strong-password
```

4. Save and close the file.

> [!NOTE]
> **Mac users:** Finder hides files whose names start with a dot, such as `.env`. Press `Cmd + Shift + .` in Finder to show them.
>
> **TextEdit Tip:** Do not wrap your API key or password in quotation marks (`"..."`). Apple TextEdit can convert straight quotes into curly quotes (`“...”`), which breaks the key.

---

## 8. Launch it for the first time

In your terminal, run:

```bash
uv run python src/chatbot.py
```

*(This command works identically on macOS, Windows, and Linux. No environment variable flags needed.)*

> [!NOTE]
> **Automatic API Key Check:** Case-Room verifies your `GOOGLE_API_KEY` on startup before opening the server. If your key is missing, expired, or invalid, it halts immediately with a clear red diagnostic box explaining how to fix it.

After 10–30 seconds you should see:

```text
============================================================
🚀 CLASSROOM CHATBOT IS LIVE!
🔗 URL for Students: https://xxxxxxxxxxxx.gradio.live
============================================================
```

1. Copy the `https://….gradio.live` link and open it in your browser.
2. Click the **🔐 Instructor Admin Panel** tab, type the `ADMIN_PASSWORD` you set, and press **Enter**.
3. Under **📚 Business Case Study Selection**, choose **EcoBrew**, then click **🚀 Load Selected Case Study**.
4. Go back to the **💬 Student Chatroom** tab, enter a name, and ask: *"What are EcoBrew's main sustainability targets?"*

🎉 **If Jarvis answers, you're done.** Case-Room is set up.

> [!IMPORTANT]
> **Keep the terminal window open.** Case-Room runs only while that window is open and your laptop is awake. Closing it, or letting the laptop sleep, takes the chatbot offline for everyone.

> [!NOTE]
> The `gradio.live` link is a free, temporary public address that Gradio creates so students on any network can reach your laptop. You get a **new link every time you start Case-Room**, and the QR code is regenerated to match. That's why you should start the app *before* you put the QR code on the projector.

To stop Case-Room, click in the terminal and press `Ctrl + C`.

---

## 9. Starting it again next time

You don't need to repeat steps 1–7. Before each class, open a terminal in the `case-room` folder and run:

```bash
uv run python src/chatbot.py
```

---

**Next:** read the **[User Guide](USER_GUIDE.md)** to learn the screens and how to run a class, or **[add your own case study](ADDING_A_CASE_STUDY.md)**.

