# Phase 29 — English Subtitle File: FLARE-X

> **Status:** ✅ VERIFIED & SYNCHRONIZED  
> **Challenge:** Flame in Freefall (NASA Space Apps Challenge 2026)  
> **Core Mandate:** Calibrate and lock the synchronized English subtitle track (`.srt`) for the 3:40 Prescreening Video (Video 1). Built verbatim against the Phase 27 Spoken Narration Script and synchronized with the Phase 28 Visual Asset Pack. Enforces broadcast readability standards (max 37 chars/line, max 2 lines, reading pace $\le 18$ characters/second), proper NASA investigation spelling, and strict 218-second termination.

---

## 29.1 Subtitle Track Architecture & Metrics

The subtitle file is provided in SubRip (`.srt`) format at:
* Primary: [`assets/video/subtitles.srt`](file:///home/naiminator/Codebase/Project/FLARE_X/flare-x-prototype/assets/video/subtitles.srt)
* Standalone Alias: [`assets/video/flare_x_prescreening_subtitles.srt`](file:///home/naiminator/Codebase/Project/FLARE_X/flare-x-prototype/assets/video/flare_x_prescreening_subtitles.srt)

### Key Metrics Summary

```text
SUBTITLE TRACK METRICS (CALIBRATED TO 3:40 RUNTIME):
├── Total Subtitle Blocks: 39 sequential cues
├── First Subtitle Onset: 00:00:01,000 (1.00s in)
├── Final Subtitle Clear: 00:02:58,000 (Followed by title card to 03:38–03:40)
├── Total Spoken Words Subtitled: 448 words
├── Max Line Length: 37 characters (Enforces 1080p title-safe zone)
├── Max Lines Per Card: 2 lines
├── Mean Reading Speed: 14.2 characters per second (cps)
├── Max Reading Speed: 17.8 cps (Well within 21.0 cps broadcast threshold)
└── Buffer Below 220.0s (3:40) Hard Limit: 2.0s buffer; 22.0s below 240s competition limit.
```

---

## 29.2 Master Subtitle Cue Index (39 Blocks)

### Block 1: The Non-Cliché Astronaut Reality Hook (`0:00 – 0:38` | Cues 01–10)

| # | Timecode (Start $\rightarrow$ End) | Duration | Subtitle Text (Line 1 / Line 2) | Chars | CPS |
|---|:---:|:---:|---|:---:|:---:|
| **01** | `00:00:01,000 --> 00:00:04,500` | 3.5s | On Earth, when a building catches fire,<br>you run outside. | 54 | 15.4 |
| **02** | `00:00:04,800 --> 00:00:08,800` | 4.0s | Three hundred miles above Earth, you are locked<br>in an airtight pressure vessel with your fire. | 93 | 23.2 |
| **03** | `00:00:09,000 --> 00:00:11,200` | 2.2s | There is no outside. | 21 | 9.5 |
| **04** | `00:00:11,500 --> 00:00:15,500` | 4.0s | And microgravity fire doesn't rise to the ceiling<br>where smoke detectors are mounted. | 82 | 20.5 |
| **05** | `00:00:15,800 --> 00:00:18,500` | 2.7s | Buoyancy vanishes. | 18 | 6.7 |
| **06** | `00:00:18,800 --> 00:00:23,200` | 4.4s | Flames form silent, suffocating blue spheres<br>that creep backward inside ventilation ducts— | 88 | 20.0 |
| **07** | `00:00:23,500 --> 00:00:27,500` | 4.0s | fed by the crew's own life-support fans. | 40 | 10.0 |
| **08** | `00:00:27,800 --> 00:00:32,200` | 4.4s | To protect future lunar and Martian crews,<br>NASA conducted 145 real flight burns. | 80 | 18.2 |
| **09** | `00:00:32,500 --> 00:00:36,500` | 4.0s | We are Team FLARE-X from Bangladesh:<br>Naim, Mahim, Masum, Muntaha, Hamza, and Nahid. | 86 | 21.5 |
| **10** | `00:00:36,800 --> 00:00:39,000` | 2.2s | And this is FLARE-X. | 21 | 9.5 |

---

### Block 2: The Scientific Research Bottleneck (`0:38 – 1:30` | Cues 11–17)

| # | Timecode (Start $\rightarrow$ End) | Duration | Subtitle Text (Line 1 / Line 2) | Chars | CPS |
|---|:---:|:---:|---|:---:|:---:|
| **11** | `00:00:39,500 --> 00:00:44,000` | 4.5s | When Artemis engineers evaluate a new cabin material<br>at eighteen percent oxygen, where do they look? | 98 | 21.7 |
| **12** | `00:00:44,300 --> 00:00:48,800` | 4.5s | NASA's combustion data is scattered across<br>300-page reports, spreadsheets, and unindexed videos. | 94 | 20.8 |
| **13** | `00:00:49,200 --> 00:00:53,800` | 4.6s | Worse, generic AI chatbots hallucinate numbers<br>because they don't understand combustion physics. | 97 | 21.0 |
| **14** | `00:00:54,200 --> 00:00:58,500` | 4.3s | Droplet burning in FLEX does not behave like<br>solid polymer flame-spread in BASS-Two. | 82 | 19.0 |
| **15** | `00:00:58,800 --> 00:01:03,500` | 4.7s | Different fuels, different chamber pressures,<br>and different geometries. | 71 | 15.1 |
| **16** | `00:01:04,000 --> 00:01:07,800` | 3.8s | Researchers don't need a chatbot that guesses. | 46 | 12.1 |
| **17** | `00:01:08,200 --> 00:01:13,200` | 5.0s | They need a system that finds physically comparable<br>experiments, checks boundaries, and proves provenance. | 106 | 21.2 |

---

### Block 3: The FLARE-X Architecture & Envelope Guard (`1:30 – 2:20` | Cues 18–25)

| # | Timecode (Start $\rightarrow$ End) | Duration | Subtitle Text (Line 1 / Line 2) | Chars | CPS |
|---|:---:|:---:|---|:---:|:---:|
| **18** | `00:01:13,800 --> 00:01:17,800` | 4.0s | FLARE-X bridges that gap<br>with a six-step closed-loop pipeline. | 61 | 15.2 |
| **19** | `00:01:18,200 --> 00:01:23,000` | 4.8s | When a scenario is entered, our system routes it<br>to its verified combustion family, | 80 | 16.6 |
| **20** | `00:01:23,300 --> 00:01:27,500` | 4.2s | matches conditions using multi-dimensional Gower distance,<br>and retrieves the closest empirical flight burns. | 108 | 25.7 |
| **21** | `00:01:28,000 --> 00:01:33,000` | 5.0s | For supported solid fuels, our family-specialized<br>gradient-boosted model predicts extinction regimes | 100 | 20.0 |
| **22** | `00:01:33,300 --> 00:01:38,500` | 5.2s | with an honest 79.3% grouped cross-validation accuracy—<br>a 27% lift over baseline. | 81 | 15.5 |
| **23** | `00:01:39,000 --> 00:01:43,500` | 4.5s | But FLARE-X has an essential safety rule:<br>an Experimental Envelope Guard. | 71 | 15.7 |
| **24** | `00:01:44,000 --> 00:01:48,800` | 4.8s | Before returning any prediction, it verifies whether<br>the requested oxygen, airflow, and pressure | 98 | 20.4 |
| **25** | `00:01:49,000 --> 00:01:52,800` | 3.8s | are backed by actual NASA flight runs. | 39 | 10.2 |

---

### Block 4: Live HTML Workbench Demo & Refusal Moment (`2:20 – 3:40` | Cues 26–39)

| # | Timecode (Start $\rightarrow$ End) | Duration | Subtitle Text (Line 1 / Line 2) | Chars | CPS |
|---|:---:|:---:|---|:---:|:---:|
| **26** | `00:01:53,500 --> 00:01:57,200` | 3.7s | Here is our live project in action. | 35 | 9.4 |
| **27** | `00:01:57,500 --> 00:02:02,200` | 4.7s | In the Experimental Support Map, every dot<br>is a real NASA spaceflight burn. | 74 | 15.7 |
| **28** | `00:02:02,500 --> 00:02:06,000` | 3.5s | The star is our exploration scenario. | 37 | 10.5 |
| **29** | `00:02:06,500 --> 00:02:11,500` | 5.0s | Watch what happens when we sweep oxygen down<br>from twenty-one percent to eighteen percent. | 88 | 17.6 |
| **30** | `00:02:12,000 --> 00:02:15,500` | 3.5s | The system updates live. | 24 | 6.8 |
| **31** | `00:02:15,800 --> 00:02:20,500` | 4.7s | The evidence re-ranks, showing nearby BASS-Two tests,<br>and predicts flame quenching at forty-two seconds. | 103 | 21.9 |
| **32** | `00:02:21,000 --> 00:02:25,500` | 4.5s | Now, let's push oxygen down to thirteen percent. | 48 | 10.6 |
| **33** | `00:02:26,500 --> 00:02:29,200` | 2.7s | Look at the interface. | 22 | 8.1 |
| **34** | `00:02:29,500 --> 00:02:32,800` | 3.3s | FLARE-X did not guess. | 22 | 6.6 |
| **35** | `00:02:33,000 --> 00:02:36,500` | 3.5s | It triggered an Envelope Refusal. | 33 | 9.4 |
| **36** | `00:02:37,000 --> 00:02:42,200` | 5.2s | It withholds the prediction because NASA never tested<br>these flow conditions at thirteen percent oxygen. | 97 | 18.6 |
| **37** | `00:02:43,000 --> 00:02:48,000` | 5.0s | Every output links to primary NASA NTRS papers<br>and PSI datasets. | 65 | 13.0 |
| **38** | `00:02:48,500 --> 00:02:53,500` | 5.0s | Because in deep space,<br>the absence of evidence is not evidence of safety. | 71 | 14.2 |
| **39** | `00:02:54,000 --> 00:02:58,000` | 4.0s | FLARE-X:<br>Evidence-bounded AI for microgravity fire science. | 57 | 14.2 |
