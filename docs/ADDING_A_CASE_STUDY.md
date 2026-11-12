# Adding Your Own Case Study

Case-Room can run any case study you have as PDFs. This guide shows you how to add one, make it accurate, and (optionally) write your own quiz for it. It takes about 10 minutes, plus however long you spend writing quiz questions.

**Contents**
- [Step 1: Create a folder for the case](#step-1-create-a-folder-for-the-case)
- [Step 2: Add your PDFs](#step-2-add-your-pdfs)
- [Step 3: Run the preprocessor](#step-3-run-the-preprocessor)
- [Step 4 (optional): Write a quiz for the case](#step-4-optional-write-a-quiz-for-the-case)
- [Step 5: Load it in class](#step-5-load-it-in-class)
- [Making answers more accurate](#making-answers-more-accurate)
- [Customising the starter buttons](#customising-the-starter-buttons)
- [Copyright and public repositories](#copyright-and-public-repositories)

---

## Step 1: Create a folder for the case

Inside the `case-room/resource/` folder, create a new folder named after your case. **Use letters, numbers, and underscores only, with no spaces**, for example:

```text
case-room/
└── resource/
    ├── EcoBrew/          ← sample case (already there; fictional demonstration case)
    └── TeslaPricing/     ← your new case
```

> [!NOTE]
> **EcoBrew** is a synthetic, fictional business case provided as a working reference. Real course cases (from Harvard Business Publishing, Ivey, INSEAD, etc.) should be added in separate folders following Steps 1–4.

The folder name is exactly what you'll see in the admin panel, and it's also what links your quiz to this case (Step 4).

---

## Step 2: Add your PDFs

Copy your case materials into the new folder. You can add several PDFs, for example the main case, a company report, and a news article.

**How Case-Room treats each file depends on its name:**

| File name contains… | Treated as | Example |
| :--- | :--- | :--- |
| `case`, or the folder name | **Primary case document**. Read first, main source of facts. | `TeslaPricing_Case.pdf` |
| `question`, `quiz`, `rubric`, or `outline` | **Teaching reference**. Jarvis can see it, but it's marked as *not* case facts. | `Discussion_Questions.pdf` |
| anything else | **Supporting document** | `Tesla_10K_2024_excerpt.pdf` |

> [!WARNING]
> **Jarvis can see everything in the folder.** Don't include an instructor-only teaching note or answer key unless you're fine with students being able to get its contents by asking. Keep those PDFs somewhere else.

> [!NOTE]
> **Scanned PDFs won't work.** The PDF needs real, selectable text. A quick test: open it and try to highlight a sentence with your mouse. If you can't, it's an image scan and needs to be OCR'd first (for example with Adobe Acrobat's *Scan & OCR* tool) before you add it.

---

## Step 3: Run the preprocessor

The preprocessor reads your PDFs, removes clutter like page numbers and copyright footers, and saves a clean text version that Jarvis uses. You need to run it again **every time you add or change files in the folder.**

Open a terminal **in the `case-room` folder** (see [Setup Guide step 5](SETUP_GUIDE.md#5-download-case-room)) and run the command below. Replace `TeslaPricing` with your folder name.

**Mac / Linux:**
```bash
PYTHONPATH=src uv run python src/tools/preprocess_case.py --case TeslaPricing
```

**Windows (PowerShell):**
```powershell
$env:PYTHONPATH="src"; uv run python src/tools/preprocess_case.py --case TeslaPricing
```

✅ You should see something like:

```text
🔍 Preprocessing Case Study: 'TeslaPricing'
Found 2 PDF file(s): ['TeslaPricing_Case.pdf', 'Tesla_10K_2024_excerpt.pdf']
 - Extracting text from TeslaPricing_Case.pdf...
✅ Generated 'extracted_context.txt' (48,210 characters, ~12,052 tokens).
No existing summary file found for 'TeslaPricing'. Creating High-Value Case Summary...
🎉 Preprocessing for 'TeslaPricing' completed successfully!
```

Your folder now contains two new files:
- `extracted_context.txt`: the clean text Jarvis reads. It's worth opening to check that the text looks right.
- `TeslaPricing_Case_Study_High_Value_Summary.txt`: a short AI-written summary. This is only created if the folder doesn't already have a file with "Summary" in its name.

> [!TIP]
> To re-process every case at once, use `--case all`.

If you see *"⚠️ Found N potentially empty image-based exhibit(s)"*, your PDF has charts or tables saved as pictures, which Jarvis can't read. See [Making answers more accurate](#making-answers-more-accurate) below.

---

## Step 4 (optional): Write a quiz for the case

If you don't author a quiz bank, Quiz Mode still works as an **open-ended oral exam**: Jarvis starts with a generic strategic question, dynamically asks follow-up questions based on the student's replies, and gives conversational feedback. However, it will **not** have clickable MCQ buttons, a strict 2-attempt counter, curated hints, or the automated end-of-quiz scorecard. 

**For a structured, graded, or standardized classroom assessment, write your quiz in clean Markdown.**

Create a file named `quiz.md` directly inside your case folder, for example `resource/TeslaPricing/quiz.md`:

```markdown
# Tesla Pricing Quiz Bank

## Q1: Price Elasticity & Volume Impact
- **Type**: MCQ
- **Hint**: Look at Exhibit 4, which compares quarterly deliveries before and after the cut.
- **Official Answer**: Deliveries rose roughly 31% quarter-on-quarter following the price cut (Exhibit 4).

### Question
By how much did Model 3 unit sales change after the 2023 price cut?

- [ ] A) They fell by about 5%
- [x] B) They rose by about 31%
- [ ] C) They stayed flat
- [ ] D) They doubled

---

## Q5: Strategic Trade-Offs & Brand Position
- **Type**: Open-Ended
- **Hint**: Consider effects on new buyers, existing owners, and margins separately.
- **Official Answer**: A strong answer weighs scale benefits against premium-brand erosion and the effect on existing owners.

### Question
Evaluate whether the price cuts strengthened or weakened Tesla's long-term brand position.

### Answer (Rubric)
- Higher volume improved manufacturing scale economies and factory utilization.
- Lower prices risked eroding the premium brand perception and pricing power.
- Existing owners' resale values were hurt, damaging brand loyalty.
```

### Format Reference

| Element | Description |
| :--- | :--- |
| `## Q<N>: <Topic>` | Defines the question number and topic (used in the end-of-quiz scorecard). |
| `- **Type**:` | `MCQ` (multiple-choice) or `Open-Ended` (analytical written response). |
| `- **Hint**:` | Delivered after a student's first incorrect attempt to guide their thinking. |
| `- **Official Answer**:` | Ground-truth explanation displayed after a second failed attempt or in grading. |
| `### Question` | The exact prompt text students will read. |
| Options (`- [ ]`, `- [x]`) | For MCQ: exactly 4 choices starting with `A)`, `B)`, `C)`, `D)`. Mark the correct choice with `- [x]`. |
| `### Answer (Rubric)` | For Open-Ended: bulleted key points that Jarvis evaluates student answers against. |

> [!TIP]
> **Recommended structure:** questions 1–3 as multiple choice (recall and core facts), and questions 4–5 as open-ended (strategic evaluation and trade-offs). Inspect `resource/EcoBrew/quiz.md` for a complete 5-question working example.

### Pre-Flight Verification Before Class

To make sure your markdown quiz has zero formatting or checkbox errors before teaching, run the built-in validator from your terminal:

```bash
uv run python -m tools.validate_quiz --case TeslaPricing
```

You can also view the **"🎯 Case Study Quiz Bank & Live Card Preview"** accordion in the Instructor Admin Panel to verify the `🟢 Quiz Ready` badge and preview the interactive student buttons.

---

## Step 5: Load it in class

1. Restart Case-Room so it notices the new folder: press `Ctrl + C`, then run the launch command again.
2. Open the **🔐 Instructor Admin Panel**. Your case now appears under **Available Case Studies**.
3. Select it and click **🚀 Load Selected Case Study**.
4. Test it yourself with a few questions before class, including one whose answer you know is *not* in the case. Jarvis should say the case doesn't cover it.

---

## Making answers more accurate

**Add exhibit data as text.** Charts and tables that are images inside a PDF are invisible to Jarvis. If students are likely to ask about them, type the numbers into a text file in the case folder named **`supplementary_exhibits.txt`**, for example:

```markdown
## Exhibit 4: Quarterly Deliveries
| Quarter | Model 3 | Model Y |
| :--- | ---: | ---: |
| Q4 2022 | 98,000 | 140,000 |
| Q1 2023 | 128,000 | 160,000 |
```

Then run the preprocessor again. Any file whose name starts with `supplementary_` or `exhibit_` and ends in `.txt`, `.md`, `.csv`, or `.json` is included automatically. CSV files from Excel are converted into tables.

**Add a note about what's missing.** If students keep asking about something the case doesn't cover (for example "What was EBITDA?"), add a line to `supplementary_exhibits.txt` such as *"The case does not report EBITDA."* This stops Jarvis from guessing.

**Check `extracted_context.txt`.** If an answer looks wrong, search this file for the topic. If the text is garbled or missing, the PDF extraction is the problem, not Jarvis.

---

## Customising the starter buttons

The three one-tap starter buttons in the Student Chatroom are currently written for the sample case (for example *"🎯 Sustainability & Scope 3 Targets"*). To change them for your course, open `src/ui/gradio_app.py` in a text editor and edit the button labels and their matching questions. You'll find them by searching for `Strategic Choices`. Change only the text inside the quote marks.

---

## Copyright and public repositories

Most published case studies (HBS, Ivey, INSEAD, The Case Centre, and others) are **licensed for your class only**. If you keep your own copy of Case-Room on GitHub:

- **Make your copy private**, or
- **Don't commit your case PDFs or the generated text files.** Add a line such as `resource/TeslaPricing/` to the `.gitignore` file.

Also check that your institution allows case content to be sent to an AI service such as Google Gemini.

