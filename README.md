# Lecture

<div align="center">

**Turn an outline into a talk people can follow — and slide briefs that support it.**

![Lecture release artwork](assets/cover.png)

[![Tests](https://github.com/ccygod/lecture/actions/workflows/tests.yml/badge.svg)](https://github.com/ccygod/lecture/actions/workflows/tests.yml)
![License](https://img.shields.io/badge/license-MIT-16796f)
![Python](https://img.shields.io/badge/python-3.10%2B-3776ab)
![Release](https://img.shields.io/github/v/release/ccygod/lecture)

[Quick start](#quick-start) · [Examples](#see-the-difference) · [中文说明](README.zh-CN.md) · [Releases](https://github.com/ccygod/lecture/releases)

</div>

## Give your ideas a voice

An outline can be accurate and still be hard to listen to. A polished slide can leave the speaker reading bullets. Lecture works on the connection: the audience, the message, the spoken explanation and what appears on screen.

Built for Chinese teaching, client and leadership briefings, public talks and partnership speeches. Each purpose gets its own structure. A client briefing should address decisions and next steps; a class should help learners build understanding.

## See the difference

**Outline:** “AI improves efficiency. Explain applications, risks and future trends.”

**A possible spoken opening:** “You have ten reports to review before tomorrow morning. AI can help you find the repeated questions first. But before you act on its summary, you still need to know where each conclusion came from. The work gets faster when you change the process—and keep the checks that matter.”

**A supporting slide brief:** Show ten report cards flowing into three questions, with a visible source marker attached to each. Keep the explanation in the script; put the relationship on the slide.

This is an original illustrative rewrite, not a benchmark or a promise of audience response. [Read the full example →](examples/briefing-before-after.md)

## What you get

| Layer | Deliverable |
| --- | --- |
| Purpose and outline | Audience, intended change, central message and gaps that affect delivery |
| Spoken content | Continuous explanation, examples, transitions and the right amount of detail |
| Slide production | Per-page claims, on-screen copy, visual evidence, layout and speaker coordination |
| Supporting framework | Teaching goals, briefing decisions or public-talk closure, chosen by purpose |
| Checks | Source identity, quantities, output structure, claim preservation and DOCX role formatting |

## Quick start

```bash
git clone https://github.com/ccygod/lecture.git
cd lecture
python3 -m pip install -r requirements.txt
python3 scripts/install_skill.py --host codex
```

Use `--host claude` for Claude Code, or `--dest /your/skills/lecture` for another host. Existing installations are preserved: the installer stops instead of overwriting them. [Compatibility →](docs/compatibility.md)

Then ask your agent:

```text
Use $lecture to turn this outline into a 20-minute client briefing.
Audience: a university leadership team.
Goal: make the pilot scope and next decision clear.
Deliverables: a continuous Chinese script and per-slide production briefs.
Slides: editable native text and graphics.
Tone: professional, natural and restrained.
[Paste your outline and evidence.]
```

The skill first confirms purpose, diagnoses the outline and resolves the few choices that affect the result. It records the actual intake, rather than treating an assumed audience or invented approval as a user decision.

## How it works

`Purpose → outline diagnosis → spoken explanation → slide briefs → targeted review`

Lecture separates writing for the ear from writing for the page. Important claims get an explanation; data gets a useful reference; an analogy preserves the relationship being taught. Hooks, humor and callbacks are used where they help the task, with a payoff when one is promised. Plain explanation remains valid.

For complete work, the script, page briefs and supporting framework stay connected. If you only request a script, the deliverable can remain a script.

## Try a local helper

```bash
python3 scripts/editor_workflow.py --help
python3 scripts/intake_gate.py --help
python3 scripts/compare_quantities.py examples/quantity-reference.json
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

The quantity example checks a hypothetical 120-to-180 comparison; it is not market data. [Examples and checks →](examples/README.md)

## Evidence and limits

The repository contains editorial methods, references and executable checks. It does not bundle a model, browsing entitlement, image generator or PowerPoint renderer. These come from your host. Chinese content is the main specialization; English documentation helps people inspect and install it.

A validator can check a version hash, source location, arithmetic or structural contract. It cannot establish that a paragraph is funny, a lecture is scientifically effective, or an audience understood it. Rehearsal and audience feedback remain part of real delivery.

[Validation record](docs/validation.md) · [Research boundaries](references/oral-research.md) · [Source methods](references/source-methods.md) · [Attribution](NOTICE.md)

## Explore the package

- `SKILL.md`: the entry and purpose routing.
- `references/`: spoken delivery, audience relevance, visual briefs, data and review.
- `scripts/`: intake, editorial records, arithmetic and regression checks.
- `examples/`: original before/after and executable helper inputs.
- `agents/openai.yaml`: optional host metadata.

## Community

Built and maintained by [ccygod](https://github.com/ccygod). Part of a practical toolkit for evidence-aware AI work, alongside [Long Mission](https://github.com/ccygod/long-mission) and [Web Search Router](https://github.com/ccygod/web-search-router).

[Contribute](CONTRIBUTING.md) · [Get help](SUPPORT.md) · [Launch kit](docs/launch-kit.md) · [License](LICENSE)
