# AppBuildersPH Hackathon 2026: Local AI Guide

> This guide only reorganizes what is in the official materials and your notes. No rules were added. Where the sources disagree or are cut off, it is flagged in **Things to Confirm** at the bottom.

---

## 1. The Big Picture

**Theme:** Local AI

**One-line goal:** Build a **working product** where **meaningful AI computation runs on the user's device**, and show **why running it locally is better** than cloud-only.

**Important distinction:** Local AI is *not* "an AI product for a local (Filipino) audience." It means AI that runs **locally on the device**.

### Cloud services: allowed or not?
- Yes, cloud APIs and external APIs are allowed **as secondary components**.
- The **core / meaningful AI functionality must run locally**.
- The core Local AI functionality **must not depend entirely on a cloud AI API**.

---

## 2. Key Dates and Timeline

| When | What |
|---|---|
| **Fri, Oct 9** (Build Day) | Fully remote, teams build overnight |
| **Sat, Oct 10, 10:00 AM** | **Submission deadline. No extensions.** |
| **Sat, Oct 10, 1:00 PM** | Finalists announced (on Demo Day) |
| **Sat, Oct 10, 1:40 PM onward** | Finalist pitching |
| **Sat, Oct 10, 7:00 PM** | Event ends |

Your notes summarize the build window as **1 PM to 10 AM (Fri to Sat)** and Pitch Day as **1 PM to 7 PM** (only finalists pitch).

### Build Day schedule (Friday, October 9, online)
| Time | Activity |
|---|---|
| 1:30 PM | Online room opens |
| 1:45 PM | Participant briefing |
| 2:00 PM | Official challenge reveal |
| 2:10 PM | Rules and judging criteria |
| 2:20 PM | Sponsor resources and credits |
| **2:30 PM** | **Building begins** |
| 6:00 PM | Optional community check-in |
| 10:00 PM | Optional community check-in |
| Overnight | Teams continue building |

### Demo Day schedule (Saturday, October 10, Cyberzone, SM Makati)
| Time | Activity |
|---|---|
| 12:00 PM | Registration and participant arrival |
| 12:15 PM | Demo and AV technical checks |
| 1:00 PM | Official opening and AppBuildersPH welcome (**finalists announced**) |
| 1:15 PM | PExpress welcome |
| 1:20 PM | AMD segment |
| 1:30 PM | Cognition / Devin segment |
| 1:40 PM | Finalist pitching begins |
| 3:20 PM | Break and networking |
| 3:40 PM | Finalist pitching continues |
| 5:00 PM | Judging deliberation, PC Express auction and raffle |
| 5:45 PM | Awards ceremony |
| 6:30 PM | Networking |
| 7:00 PM | Event ends |

---

## 3. Flow at a Glance

```
Register (official website list)
        ↓
Build Day: build the working product (Oct 9, 2:30 PM start, overnight)
        ↓
Record a short demo video and post it on X or LinkedIn
        ↓
Submit everything by 10:00 AM, Oct 10
        ↓
Submission screening (checklist check; incomplete = invalid)
        ↓
Finalists announced at 1:00 PM, Oct 10
        ↓
Finalists pitch live at Cyberzone: 5 min pitch + demo, 3 min Q&A
        ↓
Judging, People's Choice vote, awards ceremony
```

---

## 4. Rules

### Required
- **Substantially built during the hackathon.**
- **A meaningful part of AI inference executes locally.**
- **A working product, demonstrated.** Not Figma, not slides (PPT), etc.
- **Models, APIs, frameworks, and major tools are disclosed.**
- **Core Local AI functionality works without depending entirely on a cloud AI API.**

### Allowed
- Existing open-source models and libraries
- AI-assisted development
- Devin
- Cloud APIs as secondary components
- Using open-source AI to train AI (from your notes)

### Not allowed / disqualifying
- Not following the rules ("strictly follow rules").
- A project that wasn't substantially built during the hackathon (existing code must be disclosed).
- Receiving help from **people outside the hackathon**. Participants **proven** to have received external help are disqualified.
- A team that is **not represented in person at Demo Day** cannot be a finalist (see Section 8).

---

## 5. What Counts as Local AI

**In scope (examples from the brief):**

- Local LLMs
- Local vision models
- Local speech recognition
- Local embeddings and RAG
- Local AI agents
- Local image generation
- Edge AI
- Offline AI
- Privacy-preserving AI
- Hybrid local + cloud systems
- AI on PCs, laptops, phones, or edge hardware

**Product types (any kind is welcome):** Productivity, creative tools, developer tools, enterprise tools, accessibility, education, finance, gaming, disaster-related, computer vision, personal assistants, privacy tools, etc.

**Format is flexible.** It does not have to be a mobile app. It can be a web app, Chrome extension, mobile app, or something running on hardware.

**Example technologies (none are required):**
Ollama, LM Studio, Llama.cpp, MLX, ONNX, PyTorch, TensorFlow, WebGPU, Core ML, AMD ROCm, DirectML, Hugging Face, plus open-source LLMs, vision models, and speech models.

**No specific model, framework, operating system, or hardware platform is required.**

---

## 6. How You'll Be Scored

| Weight | Criterion | Question the judges ask |
|---|---|---|
| **25%** | Problem & Usefulness | Does it solve a genuine problem for a clear target user? |
| **25%** | Implementation | Is local inference fundamental, and does it give a meaningful advantage? |
| **20%** | Technical Execution | Does it actually work, reliably enough for a live demo? |
| **15%** | Innovation | Is it meaningfully different? Does Local AI enable something new? |
| **15%** | Product & Demo Quality | Is the UX usable, and is the live demo convincing? |

**Takeaway from the organizers:** Half the score is usefulness plus how real your Local AI is (Problem & Usefulness + Implementation).

**Same idea as another team?** It depends on how the team executed the solution.

**Judges:** 10 judges, announced on Demo Day.

---

## 7. Submission

**Deadline: 10:00 AM, October 10. No extensions.**
**Only one submission (project) per team.**

### Submission checklist
If your submission is missing items, it is **screened as an invalid submission before it reaches the judges.**

**The project**
- [ ] Project name
- [ ] Short description
- [ ] Team members
- [ ] Public GitHub repository

**The proof**
- [ ] Demo video
- [ ] X / LinkedIn video URL
- [ ] What runs locally
- [ ] What requires internet

**The disclosures**
- [ ] Models used
- [ ] Technologies and frameworks
- [ ] APIs and cloud services
- [ ] Existing code and assets
- [ ] AI development tools

### The question every submission must answer
> **Why does this product benefit from running AI locally?**

(From the brief: show how local AI creates an experience that would be difficult, expensive, slow, private, or impossible with a cloud-only approach.)

### "What runs locally" and "what requires internet"
Disclose both **in paragraph format**.

### Demo video requirements
- **Edited**, showing a **working demo** of your product.
- **Less than 1 minute** (the FAQ says "ideally around 1 minute").
- **Must be posted on X or LinkedIn. This is a hard requirement.**
- Include the hashtag **#AppBuildersPH**.
- Tag **Devin / Cognition**.

### Do you need to deploy the app live?
- **No**, as long as your repository has instructions for judges to recreate it.
- From your notes: **deployed projects get a huge bonus**, and you must have **clear instructions** on how it works or how to recreate it.

---

## 8. Demo Day (Finalists)

### Who becomes a finalist?
- Announced on **October 10 at 1:00 PM**.
- **10 to 15** finalist teams (your notes say a minimum of 10, depending on venue capacity, and are marked "not sure yet").
- **Only finalists pitch.**

### Attendance rules
- Everyone is welcome at Demo Day.
- To be a finalist, the team must be **at Cyberzone, SM Makati, in person**.
- **At least one representative per team must be present.** If no one is present, the team is **disqualified from finalist**.
- **Remote pitching is not allowed.** Someone from your team must be on site to pitch and answer the judges' Q&A.

### Pitch format (per team)
| Segment | Time |
|---|---|
| Pitch and live demo | **5 minutes** |
| Judge Q&A | **3 minutes** |
| **Total** | **8 minutes** |

**Tip from the organizers:** Prioritize showing a working product over presenting a large number of slides.

### Logistics
- Wi-Fi, power outlets, and HDMI and USB-C connections are available.
- **Bring your own laptop to demo on.**
- Coffee and sandwiches are provided.
- Guests are welcome to watch the pitches.
- Concerns on Demo Day: contact **Bryl Lim** or any organizing member.

---

## 9. Prizes

| Award | Prize | Notes |
|---|---|---|
| **Grand Champion** | **₱50,000** | Best overall project. Cash, AMD / ASUS peripherals, Devin AI credits |
| **WhiteCloak Award** | **₱15,000** | Cash, WhiteCloak merch (1st runner-up per your notes) |
| **AMD Award** | **₱10,000** | Cash, AMD / ASUS peripherals (3rd place per your notes) |
| **Cognition / Devin Award** | **₱10,000** | Cash |
| **Tutorials Dojo Award** | **₱10,000** | Cash |
| **People's Choice Award** | **₱10,000** | Audience vote during Demo Day |

Other prize details:

- Per the brief, there are **four winners at ₱10,000 cash each** in the "Top" group. Your notes describe this as 4th to 8th place from Devin and other sponsors. Special awards may be added.
- **People's Choice:** A QR code is shown. Everyone at the venue scans it to vote for a pitch, and the highest vote wins. The same QR scans are also used for the raffle.
- **If the Grand Champion also wins People's Choice, the prize adds to their prize pool.**
- **One project can win more than one award.** Special awards are won independently of the main award.
- **Cash prizes** are paid by bank transfer to an authorized representative from each winning team.
- **You keep ownership** of what you build.
- **Certificates of participation** are available on the AppBuildersPH website.

---

## 10. Teams

- **Who can compete:** Only participants listed on the official website, **appbuildersph.com/hackathon**. **All members must be registered.**
- **Team size:** 1 to 4 members recommended. Solo builders are allowed.
- **One project per team.**
- **One person, one team.** Nobody can join more than one team.
- **Changing teams or team name:** Allowed, as long as you submit your official team name and member names from the official website list. Your notes say the team name can be changed once you submit.
- **If a member drops out:** Only the member names in your submission are counted.
- **Number of teams:** No cap.

---

## 11. Quick FAQ

**Can we use cloud APIs?** Yes, as secondary components. Core Local AI must not depend entirely on a cloud AI API.

**Can we use open-source models and libraries?** Yes. Disclose every model, framework, and API.

**Do we need a specific model, OS, or hardware?** No.

**Can we use AI coding tools like Devin?** Yes. Disclose the tools you used. (Devin AI credits are limited to students. Stay posted.)

**Can we reuse code from before the hackathon?** Your project must be substantially built during the hackathon. Disclose any existing code or assets.

**Can people outside the hackathon help us?** No.

**Can we build from anywhere?** Yes. Build Day is fully remote.

**Where do we ask questions during the build?** The official Telegram group chat.

**Can the project be a mobile app or run on hardware?** Yes.

**Can results be disputed?** Yes, if a team is proven to have violated the rules (including a pre-existing project or external help).

---

## 12. Links

- Official hackathon website: **appbuildersph.com/hackathon**
- Hackathon page: **cerebralvalley.ai/e/appbuildersph-hackathon-2026**
- Telegram group chat: **t.me/+uxLZLV5...** (the link in the source was garbled, so use the one in the official materials)

---

## 13. Final Checklist

**Before building**
- [ ] Everyone on the team is registered on the official website
- [ ] Project idea has meaningful AI running **locally**

**While building**
- [ ] Building during the hackathon (disclose any pre-existing code or assets)
- [ ] Keep track of every model, framework, API, cloud service, and AI tool you use
- [ ] Repo is **public** on GitHub, with instructions for judges to recreate it

**Before 10:00 AM, Oct 10**
- [ ] Edited demo video (under about 1 minute) showing the working product
- [ ] Posted on X or LinkedIn with **#AppBuildersPH** and tagging **Devin / Cognition**
- [ ] Project name, short description, team members
- [ ] "What runs locally" and "what requires internet" written in paragraph format
- [ ] All disclosures complete
- [ ] Answered: **Why does this product benefit from running AI locally?**

**Demo Day**
- [ ] At least one team representative at Cyberzone, SM Makati
- [ ] Own laptop ready, with the product working
- [ ] 5-minute pitch plus live demo prepared, ready for 3 minutes of Q&A

---

## 14. Things to Confirm

The sources conflict or are incomplete in a few places, so verify with the organizers (Telegram group or Bryl Lim):

1. **Build start time:** Notes say "1 PM to 10 AM," while the official schedule says building begins at **2:30 PM**.
2. **Prize structure:** Notes list 3rd place (AMD) and 4th to 8th place (sponsors), while the PDF lists named awards (Cognition/Devin, Tutorials Dojo, AMD, and a fourth ₱10,000 award whose name is cut off in the source).
3. **Finalist count:** Notes say a minimum of 10 (not sure), while the FAQ says 10 to 15.
4. **Demo video length:** Notes say less than 1 minute, while the FAQ says ideally around 1 minute.
5. **Deployment bonus:** Notes say deployed projects get a "huge bonus," while the FAQ only says deployment is not required.
6. **Truncated text:** The external help disqualification line and the dispute line were cut off in the source.
7. **Telegram link:** Garbled in the source.
