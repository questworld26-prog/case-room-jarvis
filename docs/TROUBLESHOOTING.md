# Troubleshooting

Find your symptom below. Fixes are written so you can copy and paste them, one step at a time.

> [!TIP]
> **Before each class, open this page in a browser tab.** Most problems during class take under a minute to fix.

**Jump to:** [Quick reference](#quick-reference) · [Installation](#installation-problems) · [Starting the app](#starting-the-app) · [Admin panel](#admin-panel) · [During class](#during-class) · [Adding a case](#adding-a-case-study) · [Still stuck?](#still-stuck)

---

## Quick reference

| Situation | What to do |
| :--- | :--- |
| Students see "No Case Study Selected" | Admin Panel → select case → **🚀 Load Selected Case Study** → wait for ✅ |
| Student sees "Student Name Required" | They need to type their full name in the box at the top |
| Student sees "Disconnected" or a red error | Student refreshes the page (pull down on mobile, `F5` on a laptop) |
| Answers are slow (10+ seconds) | Wait 15–20 seconds. The app retries automatically. |
| Wrong mode is active | Admin → select mode → **📢 Broadcast Mode to Students** |
| Server crashed or terminal closed | Restart Case-Room → **give students the new QR code** → load the case again |
| "Port 7860 already in use" | See [Port already in use](#port-7860-already-in-use) |
| A student's quiz restarted | They refreshed the tab. Ask them to start again from Question 1. |

---

## Installation problems

### `uv: command not found` (or `'uv' is not recognized`)
The terminal doesn't know about `uv` yet.
1. **Close the terminal completely and open a new one.** This fixes it most of the time.
2. If it still fails, run the install command from [Setup Guide step 4](SETUP_GUIDE.md#4-install-uv) again and read the last few lines it prints. They tell you if anything went wrong.

### `uv sync` fails or stops partway
- **Check your internet connection** and run `uv sync` again. It picks up where it left off.
- **University or corporate network?** Some networks block package downloads. Try a home network or a phone hotspot.
- **Low disk space?** Installation needs about 2 GB free.

### Windows: "running scripts is disabled on this system"
PowerShell is blocking the installer. Run this once, then try again:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### "No such file or directory" when running a command
The terminal isn't in the `case-room` folder. Type `cd `, drag the `case-room` folder into the terminal, press Enter, and try again.

---

## Starting the app

### Port 7860 already in use
An earlier copy of Case-Room is still running, perhaps in another terminal window.

**Mac / Linux:**
```bash
lsof -ti :7860 | xargs kill -9
```

**Windows (PowerShell):**
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 7860).OwningProcess | Stop-Process -Force
```

Then start Case-Room again.

### No `gradio.live` link appears, or it only shows `http://127.0.0.1:7860`
Case-Room couldn't create the public link students need.
1. **Check that you ran `src/chatbot.py`**, not `src/main.py`. `main.py` only works on your own laptop.
2. **The network may block the tunnel.** Many university and corporate networks do. Try a phone hotspot to confirm. If that's the cause, ask IT to allow `*.gradio.live`, or run class over a hotspot.
3. **Antivirus may block it.** Gradio downloads a small helper program called `frpc` to create the link, and some antivirus tools quarantine it. Allow it in your antivirus settings and restart Case-Room.

### Terminal shows "API key not valid", "403", or "PERMISSION_DENIED"
1. Open the `.env` file (`open -e .env` on Mac, `notepad .env` on Windows).
2. Check the `GOOGLE_API_KEY=` line. It needs the full key, with no spaces or quote marks.
3. Check that the key still exists at https://aistudio.google.com/apikey.
4. Save the file and restart Case-Room.

### Browser shows a blank page
1. Hard-refresh: `Cmd + Shift + R` (Mac) or `Ctrl + Shift + R` (Windows).
2. Open the link again in a new tab.
3. If it's still blank, stop Case-Room (`Ctrl + C`) and start it again.

---

## Admin panel

### The password doesn't work
1. Make sure you're on the **🔐 Instructor Admin Panel** tab.
2. Type the password and **press Enter**.
3. The password is whatever is after `ADMIN_PASSWORD=` in your `.env` file. If there's no such line, the default is `admin123`. **Change it before class.**
4. If you changed `.env` while the app was running, restart Case-Room. Settings are only read at startup.

### My new case study doesn't appear in the list
- Restart Case-Room. The list is built when the app starts.
- Check that the folder is directly inside `resource/`, not nested one level deeper.
- Check that you ran the preprocessor (see [Adding a case study](ADDING_A_CASE_STUDY.md#step-3-run-the-preprocessor)).

### I can't change the Session Identifier
It locks once you load a case, so your logs stay consistent. To change it, restart Case-Room, set the identifier **first**, then load the case.

### The banner says "📄 IN-MEMORY TEXT PIPELINE" instead of "⚡ GEMINI CACHE ACTIVE"
**That's fine.** Students get the same answers either way. Gemini caching makes answers faster and cheaper, but some API keys (especially free ones) don't support it, so Case-Room falls back automatically. The terminal shows the reason.

---

## During class

### Students see "⚠️ No Case Study Selected"
The app was started or restarted and no case has been loaded yet. Go to the **Admin Panel**, select the case, click **🚀 Load Selected Case Study**, and wait for the ✅ message. Ask one student to try again.

### Students see "Disconnected" or a red error banner
Their phone went to sleep, they switched Wi-Fi networks, or the tab was idle for a long time. **They should refresh the page.** It reconnects straight away.

### Answers are slow (more than 10 seconds)
Lots of students sent questions in the same few seconds, and Google is rate-limiting. **Case-Room retries automatically, so just wait 15–20 seconds.** Everyone will get an answer.
- **If it happens often:** a free API key is probably the bottleneck. Turn on billing for the key (see [Setup Guide step 2](SETUP_GUIDE.md#2-get-a-gemini-api-key)).
- **Prevention:** avoid "everyone send now!" moments. Let questions arrive over a couple of minutes.

### Terminal shows "429" or "RESOURCE_EXHAUSTED"
This is the same rate-limit issue as above. Short bursts recover on their own. If it doesn't stop, you've reached your key's quota. Turn on billing, or wait for the quota to reset (usually within a minute for per-minute limits, or the next day for daily limits).

### The wrong mode is active
Selecting a mode doesn't change anything until you broadcast it. Go to the **Admin Panel**, select the mode you want, and click **📢 Broadcast Mode to Students**.

### A student's quiz restarted from Question 1
Quiz progress is stored in the student's browser tab, so refreshing or closing the tab resets it. Ask them to start again from Question 1. Next time, remind students before Quiz mode: *"Don't refresh during the quiz."*

### The app crashed, the terminal closed, or the laptop went to sleep
1. In the terminal, press `Ctrl + C` if it's frozen.
2. Start Case-Room again (see [Setup Guide step 9](SETUP_GUIDE.md#9-starting-it-again-next-time)).
3. **You get a new `gradio.live` link and QR code.** Project the new QR code from the admin panel. The old link no longer works.
4. Open the **Admin Panel**, unlock it, and **load the case again**.

> [!NOTE]
> Students' on-screen chat history will reset, but **nothing already logged is lost.** The new session writes to a new log file in `logs/`.

### Jarvis gave a wrong or made-up answer
1. Search `resource/<YourCase>/extracted_context.txt` for the topic. If the information is missing or garbled, the PDF text extraction is the problem.
2. Add the correct facts to `supplementary_exhibits.txt` and re-run the preprocessor (see [Making answers more accurate](ADDING_A_CASE_STUDY.md#making-answers-more-accurate)).
3. Click **🔄 Reload Case Text Context** in the admin panel. You don't need to restart.

---

## Adding a case study

### "⚠️ Warning: No PDF files found"
Check that the files end in `.pdf` and are directly inside `resource/<YourCase>/`.

### `extracted_context.txt` is empty or gibberish
The PDF is probably a scanned image. Run it through OCR, for example Adobe Acrobat's *Scan & OCR*, and try again.

### Quiz mode uses AI-generated questions instead of mine
- The key in `data/quiz_banks.json` must match the folder name exactly, e.g. `"TeslaPricing"`.
- If the terminal printed `Notice: unable to load data/quiz_banks.json` when Case-Room started, the file has a formatting error. Paste it into https://jsonlint.com to find it.
- Restart Case-Room after editing the quiz file.

---

## Still stuck?

1. **Look at the terminal.** The last few lines usually describe the problem in plain words.
2. **Search the [GitHub Issues](../../issues)** to see if someone else has had the same problem.
3. **Open a new issue.** Include your operating system, the command you ran, and the last 20 lines from the terminal. **Remove your API key** from anything you paste.
