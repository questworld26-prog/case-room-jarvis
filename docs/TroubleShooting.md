# 🚨 Jarvis Chatbot — Mid-Class Troubleshooting Guide

> **Keep this open in a browser tab before class starts.**
> Commands are copy-paste ready. One step at a time. You've got this.

---

## Before Class — Start the Server

Open **Terminal** and run these two commands in order:

```bash
cd "<path-to-repo>"
```
```bash
PYTHONPATH=src uv run python src/main.py
```

Wait until you see: `Running on local URL: http://127.0.0.1:7860`
Then open **http://localhost:7860** in your browser.

---

## 🔴 Problem 1 — App won't start: "Port 7860 already in use"

**What happened**: A previous session is still running.

**Fix**:
```bash
lsof -ti :7860 | xargs kill -9
```
Then start the server again (the two commands above).

---

## 🔴 Problem 2 — Browser shows nothing / blank page

**What happened**: Server started but browser tab is stale.

**Fix**:
1. Hard-refresh the page: **Cmd + Shift + R** (Mac)
2. If still blank, open a new tab at **http://localhost:7860**
3. If still blank, restart the server (Problem 1 fix, then start again)

---

## 🔴 Problem 3 — Admin panel won't unlock / password not working

**What happened**: Wrong tab, wrong password, or page needs a refresh.

**Fix**:
1. Click the **"🔐 Instructor Admin Panel"** tab (second tab at the top)
2. Type the password and press **Enter** (not the button — press Enter on keyboard)
3. If it still fails: hard-refresh (**Cmd + Shift + R**) and try again
4. Default password is in your `.env` file as `ADMIN_PASSWORD=`

---

## 🔴 Problem 4 — Case study didn't load / Students see "No Case Study Selected"

**What happened**: You forgot to click Load, or the load failed silently.

**Fix**:
1. Go to **Admin Panel** → select the case (e.g. EcoBrew)
2. Click **"📂 Load Case Study"**
3. Wait for the green **"✅ Loaded"** message to appear
4. Students should now be able to chat — ask one student to try

---

## 🔴 Problem 5 — Students getting slow responses (>10 seconds)

**What happened**: 30+ students sent questions at the same exact second. The system is retrying automatically.

**What to do**: **Nothing — just wait 15–20 seconds.** The system retries silently and everyone will get their answer. No student will see an error message.

**Prevention for next time**: Don't do a synchronized countdown ("3-2-1 send!"). Let students respond at their own pace over 2–3 minutes.

---

## 🔴 Problem 6 — Wrong mode is active / Students getting quiz questions when you wanted Q&A

**What happened**: Mode was accidentally changed, or the broadcast button was clicked unintentionally.

**Fix**:
1. Go to **Admin Panel** → **"Active Pedagogical Mode"**
2. Select **"Mode 1 — Standard Q&A (Default)"**
3. Click **"📢 Broadcast Mode to Students"** — students' next message will use the new mode

> **New behaviour (v6.5+):** Selecting a mode radio does NOT immediately affect students. You must click **"Broadcast"** to push it live. This prevents accidental switches.

---

## 🔴 Problem 7 — App crashes mid-class (Terminal shows error / closes)

**What happened**: Server process died.

**Fix** (takes ~15 seconds):
1. Click on Terminal
2. Press **Ctrl + C** if it's frozen
3. Run:
```bash
PYTHONPATH=src uv run python src/main.py
```
4. Reload browser: **Cmd + Shift + R**
5. Go to Admin Panel → re-enter password → re-load the case study

> The student chat history will reset, but the AI knowledge is preserved automatically.

---

## 🔴 Problem 8 — Terminal says "API key invalid" or "403 Forbidden"

**What happened**: The Gemini API key expired or was removed.

**Fix**:
1. Open the `.env` file in the project folder
2. Verify the line `GOOGLE_API_KEY=` has a valid key
3. Save the file and restart the server (Problem 7 fix)
4. If you don't have a backup key, contact the tech team

---

## 🔴 Problem 9 — A student's quiz progress disappeared after browser refresh

**What happened**: Gradio stores quiz history in the browser tab. A page refresh or tab close resets it.

**What to tell the student**:
> *"Your progress has reset. Please start from Question 1. Your answers will still be evaluated correctly from the beginning."*

**Prevention**: Tell students at the start of Quiz Mode: *"Do not refresh your browser during the quiz."*

---

## ⚡ Quick Reference Card

| Situation | What to do |
|---|---|
| Port in use | `lsof -ti :7860 \| xargs kill -9` then restart |
| Blank page | Cmd + Shift + R |
| Admin locked | Click tab → type password → press **Enter** |
| No case loaded | Admin → select case → click Load → wait for ✅ |
| Slow responses | Wait 20s — it recovers automatically |
| Wrong mode | Admin → select mode → click **Broadcast** |
| Server crashed | Ctrl+C → restart server → reload browser |
| API key error | Check `.env` file → restart |
| Student quiz reset | Tell student to restart from Q1 (don't refresh browser) |

---

*Need help? Call your tech support: _______________*
