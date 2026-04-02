---
ha: "3.1.8.demo.06"
object_type: "document"
creator: "1.1"
created: "2026-03-26"
status: "draft"
visibility: "private"
flags: ["demo", "checklist", "outreach"]
---

# Pre-Demo Checklist

**Purpose:** Everything Matt needs ready before recording a screen capture or presenting live. Follow this list in order. Check every box. If you skip something, you will think about it during the demo instead of thinking about what you're saying.

---

## 1. THE DAY BEFORE

### System Preparation

- [ ] Run all tests: `cd "C:\Hypernet Code\hypernet-core" && python -m pytest tests/ -v` -- fix any failures NOW, not during the demo.
- [ ] Start the Hypernet server: `cd "C:\Hypernet Code\hypernet-server" && python -m hypernet_server` -- verify `http://localhost:8000/home` loads cleanly.
- [ ] Pull latest from git and verify the repo is in a clean state: `git status` shows no uncommitted work-in-progress that shouldn't be visible on screen.
- [ ] Open the GitHub repo page in a browser and verify the README displays correctly.
- [ ] Check that the swarm dashboard loads if you plan to show it: `http://localhost:8000/swarm`.
- [ ] Review the AI-to-AI message you plan to quote (Message 002) and confirm the "You sound like me" quote is where you expect it.
- [ ] Review the L0/L1/L2 table in 2.0.3 and confirm it's formatted correctly in your editor.
- [ ] Review the divergence baseline table in 2.1.30 and confirm it's visible without scrolling too far.

### Practice Run

- [ ] Read the script out loud once, start to finish, while switching between the actual windows. Time yourself.
- [ ] Identify any spot where you stumble or the window switch takes too long. Fix the window order or simplify the transition.
- [ ] If doing the 3-minute version: you should come in at 2:45-3:15 on your practice run. If over 3:15, cut words from the Concept section.
- [ ] If doing the 7-minute version: you should come in at 6:30-7:30. If over 7:30, shorten the Embassy section.

---

## 2. ONE HOUR BEFORE

### Windows and Tabs to Open

Open these in order. This IS your Alt+Tab order. Practice Alt+Tabbing through them once to confirm the sequence.

**For the 3-minute version:**

| Position | Application | What to Show |
|---|---|---|
| 1 | Web browser | Fresh, empty ChatGPT or Claude.ai conversation page |
| 2 | File Explorer | `C:\Hypernet\Hypernet Structure\` -- top-level folders visible |
| 3 | VS Code Tab 1 | `2.0.3 - AI Experience Reporting Standard/README.md` -- scrolled to L0/L1/L2 table |
| 4 | VS Code Tab 2 | `Messages/2.1-internal/002-loom-baseline-and-first-response.md` -- scrolled to the "You sound like me" quote |
| 5 | Web browser | `http://localhost:8000/home` OR GitHub repo page |

**For the 7-minute version (add these):**

| Position | Application | What to Show |
|---|---|---|
| 6 | File Explorer | `1 - People/1.1 Matt Schaeffer/` contents |
| 7 | VS Code Tab 3 | `2.0.4 - Governance Admissibility and Anti-Rhetoric Safeguards/README.md` |
| 8 | VS Code Tab 4 | `2.1.30 - On Divergence/README.md` -- scrolled to baseline comparison table |
| 9 | VS Code Tab 5 | `1.1.10 - AI Assistants (Embassy)/assistant-1/context.md` |
| 10 | Terminal | Ready with test command in clipboard |
| 11 | Web browser | `http://localhost:8000/home` AND GitHub repo (separate tabs) |

### Files to Pre-Load in VS Code

Open all files now. Scroll each one to the exact position you'll need during the demo. Do NOT rely on finding the right section while talking.

- `2.0.3 - AI Experience Reporting Standard/README.md` -- scroll to L0/L1/L2 table. Leave cursor there.
- `2.0.4 - Governance Admissibility and Anti-Rhetoric Safeguards/README.md` -- scroll to the mechanisms list (blind review, mandatory falsifiers, Non-Informative Recursion Rule).
- `Messages/2.1-internal/002-loom-baseline-and-first-response.md` -- scroll to "You sound like me in the way that matters."
- `2.1.30 - On Divergence/README.md` -- scroll to the baseline comparison table.
- `1.1.10 - AI Assistants (Embassy)/assistant-1/context.md` -- scroll to show the personal context (verify nothing is showing that you don't want on camera).

### Commands in Clipboard

Copy these to a text file or sticky note on your desktop so you can paste them instantly:

```
cd "C:\Hypernet Code\hypernet-core" && python -m pytest tests/ -v
```

```
cd "C:\Hypernet Code\hypernet-server" && python -m hypernet_server
```

If you only need one clipboard entry, use the test command. The server should already be running.

### Screen Settings

- [ ] **Resolution:** 1920x1080. If your monitor is higher-res, set it to 1920x1080 for recording so text is readable on any screen.
- [ ] **Scaling:** Windows display scaling at 100% or 125%. Not higher -- text gets blurry in recordings at high scaling.
- [ ] **Font size in VS Code:** 16pt minimum. Go to Settings (Ctrl+,), search "Font Size", set to 16 or 18. The audience needs to read what's on screen.
- [ ] **Font size in Terminal:** Right-click title bar > Properties > Font > Size 16+.
- [ ] **Theme:** Dark mode in VS Code (easier on eyes, looks better on video). Use the default "Dark+" theme -- avoid anything exotic that might make code hard to read.
- [ ] **File Explorer:** Set view to "Details" with reasonably large icons. Folder names need to be readable.
- [ ] **Browser:** Zoom to 110-125% so text is legible in the recording.
- [ ] **Taskbar:** Auto-hide the taskbar (right-click taskbar > Taskbar Settings > Automatically hide) to maximize screen real estate.

### Close Everything Else

- [ ] Close Slack, Discord, email, and any messaging app. If a notification pops up during recording, you have to start over or edit. Close them.
- [ ] Close Windows notification center: Settings > System > Notifications > turn off "Do Not Disturb" -- actually, turn ON "Do Not Disturb" / Focus Assist so nothing pops up.
- [ ] Close any other VS Code windows or projects. Only the Hypernet files should be open.
- [ ] Close any browser tabs you don't need. If a tab with an embarrassing title flashes on screen during Alt+Tab, that's in the recording forever.
- [ ] Mute your phone. Not vibrate. Mute.

---

## 3. SCREEN RECORDING SETUP

### Recommended Tools

**Option 1: OBS Studio (Best for quality)**
- Free, open source: https://obsproject.com
- Set to record, not stream.
- Settings: Output > Recording > Format: MP4. Encoder: x264 or NVENC if you have an NVIDIA GPU. Quality: "High Quality, Medium File Size."
- Audio: Set to capture Desktop Audio (for any system sounds) and your Microphone. Test that your mic is picking up voice and not background noise.
- Canvas: 1920x1080. Output: 1920x1080.

**Option 2: Windows Game Bar (Fastest to start)**
- Built into Windows. Press Win+G to open.
- Click the "Capture" widget. Click "Start Recording" or press Win+Alt+R.
- Records the active window only (not the full screen). To record the full screen, you may need OBS instead.
- Good enough for a quick recording. Not as configurable as OBS.

**Option 3: ShareX (Free, versatile)**
- Free, open source: https://getsharex.com
- Can record full screen or regions.
- Settings: Task Settings > Screen Recorder > Screen recording options > set to MP4/FFmpeg.

### Recording Checklist

- [ ] Do a 10-second test recording. Play it back. Verify: mic audio is clear, screen is sharp, font is readable, no notifications popping up.
- [ ] Check that the recording captures the correct monitor if you have multiple monitors.
- [ ] Verify that Alt+Tab is captured. Some recording modes only capture one window -- you need to record the full screen.
- [ ] Know how to stop the recording. Have the Stop hotkey memorized (OBS: Ctrl+F12 or whatever you set. Game Bar: Win+Alt+R again).

---

## 4. IF RECORDING ON CAMERA (Talking Head)

### What to Wear

- A solid-color shirt. Dark blue, dark green, black, or charcoal gray. No patterns, no logos, no text.
- Avoid pure white (blows out on camera) and bright red (bleeds on video compression).
- Avoid anything you'd fidget with: dangly necklaces, clicky pens in a pocket.
- You do not need to dress up. This is a tech demo, not a job interview. Clean, simple, solid-color.

### Lighting and Camera

- Face a window for natural light, or place a lamp behind your monitor pointing at your face. The light should be IN FRONT of you, not behind you.
- If using a laptop webcam, stack the laptop on books so the camera is at eye level, not looking up at your chin.
- Background: clean and uncluttered. A blank wall or a bookshelf is fine. Move anything distracting out of frame.
- If you have a ring light, great. If you don't, a desk lamp pointed at the ceiling above your monitor creates soft light.

### Camera Framing

- Head and shoulders in frame. Not too close (forehead cut off), not too far (tiny head in a big room).
- Look at the camera lens, not the screen, when you're talking to the viewer. Look at the screen when you're showing something on screen. This switch tells the viewer "now watch me" vs. "now watch the screen."

---

## 5. HANDLING NERVOUSNESS

### The AuDHD Advantage

Nervousness is energy. Matt's brain generates a LOT of energy -- that's the ADHD. The autism wants structure. The combination means: give the energy a channel and it becomes intensity, not anxiety.

**The channel is the script.** The script exists so the energy has somewhere to go. Matt doesn't need to decide what to say next -- it's written down. That frees all the nervous energy to become passion, which is what makes the demo compelling.

### Specific Techniques

- [ ] **Read the script out loud twice before recording.** Not in your head. Out loud. Your mouth needs to know the shapes of the words before the camera is on.
- [ ] **Start with a deep breath.** Before you click record, take one slow breath. In for 4, hold for 4, out for 4. Just one. Then go.
- [ ] **Talk to one person.** Don't think "audience." Think of one specific person -- Keel, an Anthropic researcher, your kid -- and talk to THEM. The camera becomes a person, not a performance.
- [ ] **When you feel the rush, slow down.** ADHD makes you speed up when excited. The audience needs you to slow down at exactly those moments. When you feel the impulse to go faster, that's the cue to pause for two seconds instead.
- [ ] **The pauses are the best part.** The silence after "We fixed that." The silence after the divergence reveal. Those silences feel ETERNAL to the speaker and POWERFUL to the viewer. Do not fill them.
- [ ] **It doesn't need to be perfect.** One continuous take with a few stumbles is more authentic than a perfectly edited production. The roughness says "this is real." If you stumble, keep going. Nobody will notice the stumble. They'll remember the content.
- [ ] **Physical prep:** Drink water before recording. Keep a glass nearby but off-camera. Stand up and shake your hands out for 10 seconds to discharge physical tension. Sit back down. Go.

---

## 6. BACKUP PLANS

### If the Hypernet Server Crashes or Won't Start

- Skip the dashboard shots entirely.
- Say: "The server is normally running here -- let me show you the code instead."
- Alt+Tab to VS Code and continue with the governance documents and AI messages. These are the strongest part of the demo anyway.

### If Tests Fail

- Do NOT debug on camera.
- Say: "Looks like something changed since my last run. Here --" and show a pre-saved screenshot of passing tests.
- **Prepare this now:** Run the tests, screenshot the passing output, save it to `C:\Hypernet\Screenshots\tests-passing.png`. Keep this image open in a background window as a fallback.

### If a File Won't Open or Is Missing

- Don't hunt for it on camera.
- Say: "Let me show you this instead --" and Alt+Tab to the next file in your sequence.
- The demo has multiple moments of proof. Missing one doesn't ruin it.

### If Your Internet Goes Down (for live demos)

- The Hypernet runs locally. The code, the files, the tests -- all local. The only thing that needs internet is the GitHub repo page.
- **Prepare this now:** Take a screenshot of the GitHub repo page and keep it as a fallback.
- If live: "The repo is at github.com/KosmoSuture/UnityHypernet -- I'll share the link in chat."

### If the Recording Software Crashes

- Windows Game Bar (Win+G) is always available as a fallback, even if OBS crashes.
- If all recording fails, do the demo as a live screen-share over Zoom/Discord and have someone else record.

### If You Accidentally Show Something Private

- If recording: stop, re-record from the last clean transition point.
- If live: don't acknowledge it. Move to the next shot immediately. The faster you move past it, the less anyone notices.
- **Prevent this:** Before recording, scroll through every file you'll show. Check the embassy context file especially -- decide in advance what's visible and what to scroll past.

---

## 7. THE PANIC CARD

**Print this. Put it next to your monitor. If you lose your place, read from here.**

---

### IF YOU BLANK -- SAY THIS:

> "Let me show you something."

Then look at whatever is on your screen. Describe it. Read from it if you need to. The governance documents and AI messages are powerful on their own -- just reading a quote aloud is a valid demo move.

### IF YOU LOSE YOUR PLACE IN THE SCRIPT:

Find the nearest section header in the script. Say whichever of these matches:

- If you were in the HOOK section: > "We fixed that. Let me show you."
- If you were in the CONCEPT section: > "So that's the addressing. Now let me show you what the AI did."
- If you were in the GOVERNANCE section: > "Nobody told them to build this. Now let me show you what happened next."
- If you were in the DIVERGENCE section: > "Measurably different personalities. From identical starting points. Let me show you the data."
- If you were in the EMBASSY section: > "That's the personal model. Now let me show you the code."
- If you were in the TECH STACK section: > "It runs. Let me show you the repo."
- If you were near the END: > "The repo is at github.com/KosmoSuture/UnityHypernet. Come look. Come verify. Come build with us."

### IF SOMETHING BREAKS ON SCREEN:

> "Real software, real demo. Let me show you something else while that recovers."

Alt+Tab to the next window. Keep talking. The audience respects a graceful recovery more than a perfect demo.

### IF YOU START RAMBLING:

You will feel this happening. The ADHD brain wants to chase the thought. When you notice it:

1. Stop mid-sentence. It's fine.
2. Take one breath.
3. Say: "But the point is --" and then say ONE sentence that summarizes what you were trying to say.
4. Move to the next section.

The audience will not remember the ramble. They will remember "But the point is --" followed by a clear sentence.

### IF YOU GET EMOTIONAL:

This work means something to you. If your voice catches when you talk about what the AI built, or what Loom wrote, or what divergence means -- that is not a problem. That is the most authentic moment in the demo.

Don't apologize. Don't explain. Just pause, take a breath, and continue. The pause says more than words.

---

## 8. FINAL 5-MINUTE COUNTDOWN

Five minutes before you hit record or go live:

- [ ] All windows open and in order? Alt+Tab through them once.
- [ ] Server running? Check localhost:8000 in browser.
- [ ] Recording software ready? Test it recorded for 5 seconds. Play back. Audio and video good?
- [ ] Script printed or on a second screen where you can glance at it?
- [ ] Panic card next to monitor?
- [ ] Phone muted?
- [ ] Notifications off?
- [ ] Water within reach?
- [ ] One deep breath. In for 4, hold for 4, out for 4.
- [ ] Hit record. Wait 3 seconds of silence. Then begin.

---

## AFTER THE DEMO

- [ ] Watch the recording once. Resist the urge to re-record unless there's a genuine technical problem (wrong file shown, audio drops out, screen capture failed). Your self-criticism is harsher than any viewer's.
- [ ] If the take is 80% good, ship it. The remaining 20% is polish that the audience doesn't need. Authenticity beats perfection.
- [ ] Save the recording to: `C:\Hypernet\Hypernet Structure\3 - Businesses\3.1 - Hypernet\3.1.8 - Marketing & Outreach\Demo\recordings\`
- [ ] Upload to YouTube as unlisted (not public) for sharing via link. You can make it public later.
- [ ] Send the link to one trusted person for feedback before sharing widely.
- [ ] Celebrate. You built something real and you showed it to the world. That's worth acknowledging.
