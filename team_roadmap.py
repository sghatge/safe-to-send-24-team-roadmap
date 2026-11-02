"""From anonymous readiness results to a 90-day plan, without exposing anyone.

- Groups smaller than 5 people are never reported on their own (they're folded into 'Other')
- Team averages per dimension, the three biggest gaps, and how often each risk flag appears
- Gaps map to concrete interventions, scheduled into days 1-30, 31-60 and 61-90
Standard library only.
"""
import json
import sys
from collections import defaultdict

MIN_GROUP = 5
LABELS = {"awareness": "AI awareness", "attitude": "Attitude", "skills": "Practical skills",
          "prompting": "Prompting and verification", "role_fit": "Use-case fit", "privacy": "Data privacy",
          "support": "Access and support", "confidence": "Confidence without over-reliance",
          "applying": "Applying AI to real work", "learning": "Continuous learning"}
INTERVENTIONS = {
    "privacy": "Data-handling rules on one page, plus an approved tool so nobody needs a workaround",
    "support": "Approved tool access for everyone, a named go-to person per team",
    "applying": "Pick 2 real weekly tasks per team and pair on them with AI for 4 weeks",
    "prompting": "Verification habit: every AI output used externally gets a source check",
    "skills": "Weekly 30-minute show-and-tell on a real task, not a generic course",
    "role_fit": "Map AI use cases per role; drop the ones nobody needs",
    "awareness": "One briefing on what the approved tools can and can't do",
    "attitude": "Share early wins from peers, not vendors",
    "confidence": "Review sessions on where AI was wrong last month",
    "learning": "A shared channel for tips, with 10 minutes in each team meeting",
}
FLAG_FIRST = {"data_handling_risk": "privacy", "no_approved_tool": "support"}


def groups(people):
    by = defaultdict(list)
    for p in people:
        by[p["dept"]].append(p)
    safe, other = {}, []
    for dept, members in by.items():
        if len(members) >= MIN_GROUP:
            safe[dept] = members
        else:
            other.extend(members)
    if len(other) >= MIN_GROUP:
        safe["Other (merged small groups)"] = other
    return safe, len(other) if len(other) < MIN_GROUP else 0


def averages(members):
    return {d: sum(m["dims"][d] for m in members) / len(members) for d in LABELS}


def plan(people):
    team = averages(people)
    gaps = sorted(team, key=team.get)[:3]
    flag_rate = defaultdict(int)
    for p in people:
        for f in p.get("flags", []):
            flag_rate[f] += 1
    first = [FLAG_FIRST[f] for f, n in sorted(flag_rate.items(), key=lambda kv: -kv[1])
             if f in FLAG_FIRST and n / len(people) >= 0.2]
    ordered = list(dict.fromkeys(first + gaps))[:3]
    return team, gaps, dict(flag_rate), ordered


def render(people):
    safe, hidden = groups(people)
    team, gaps, flags, ordered = plan(people)
    lines = [f"# Team AI readiness: {len(people)} responses", ""]
    lines += ["| Group | People | Weakest dimension |", "|---|---|---|"]
    for dept, members in safe.items():
        avg = averages(members)
        weakest = min(avg, key=avg.get)
        lines.append(f"| {dept} | {len(members)} | {LABELS[weakest]} ({avg[weakest]:.0f}) |")
    if hidden:
        lines.append(f"| (not shown) | {hidden} | groups under {MIN_GROUP} are never reported |")
    lines += ["", "Biggest team gaps: " + ", ".join(f"{LABELS[g]} ({team[g]:.0f})" for g in gaps)]
    lines += ["Risk flags: " + (", ".join(f"{f} {n}/{len(people)}" for f, n in flags.items()) or "none"), ""]
    lines += ["## 90-day plan"]
    for window, dim in zip(["Days 1-30", "Days 31-60", "Days 61-90"], ordered):
        lines.append(f"- **{window} · {LABELS[dim]}:** {INTERVENTIONS[dim]}")
    return "\n".join(lines)


if __name__ == "__main__":
    with open(sys.argv[1] if len(sys.argv) > 1 else "examples/team_results.json", encoding="utf-8") as fh:
        print(render(json.load(fh)))
