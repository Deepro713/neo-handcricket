"""Commentary line templates keyed by situation, tagged by traits.

Placeholders: {batter} {bowler} {runs} {score} {wickets} {over} {target}
              {country} {opponent} {bowling_country} {batting_country}
              {extras} {extra_kind} {wicket_kind}
"""
from __future__ import annotations

LINES: dict[str, list[dict]] = {
    # --- normal balls ---
    "ball_dot": [
        {"text": "Dot ball. {batter} keeps it out.", "tags": ["serious", "dry"]},
        {"text": "Watchful from {batter}. Nothing happening there.", "tags": ["serious", "technical"]},
        {"text": "{batter} blocks that one like it owed him money.", "tags": ["hilarious", "casual"]},
        {"text": "A dot. The bowler's pleased. {batter}, less so.", "tags": ["dry"]},
        {"text": "Solid defence. The kind your dad would approve of.", "tags": ["hilarious", "casual"]},
        {"text": "{bowler} on the money. {batter} sees it through.", "tags": ["technical"]},
    ],
    "ball_run_1": [
        {"text": "Single. {runs} run, easy as you like.", "tags": ["casual"]},
        {"text": "Worked away for one. Strike rotated.", "tags": ["technical"]},
        {"text": "Just a single — but in cricket that's a small victory.", "tags": ["serious", "traditional"]},
        {"text": "Nudged for one. {batter} on {batter_runs}.", "tags": ["technical"]},
    ],
    "ball_run_2": [
        {"text": "Two runs! Sharp running.", "tags": ["extrovert", "casual"]},
        {"text": "Pushed into the gap, comes back for a comfortable two.", "tags": ["technical"]},
        {"text": "Couple of runs. Every one counts.", "tags": ["dry"]},
    ],
    "ball_run_3": [
        {"text": "Three! Now THAT was a run.", "tags": ["extrovert", "theatrical"]},
        {"text": "Three runs — the rare and majestic three.", "tags": ["hilarious", "dry"]},
        {"text": "Drilled into the gap, three completed.", "tags": ["technical"]},
    ],
    "ball_run_4": [
        {"text": "FOUR! Cracking shot from {batter}!", "tags": ["extrovert", "theatrical"]},
        {"text": "That's a boundary. Four runs to {batting_country}.", "tags": ["serious", "technical"]},
        {"text": "Beautifully timed — that's racing away for four.", "tags": ["technical", "traditional"]},
        {"text": "FOUR! {batter} just told the bowler to sit down.", "tags": ["hilarious", "extrovert"]},
        {"text": "Pinged through the covers. Bowler not happy.", "tags": ["casual"]},
    ],
    "ball_run_5": [
        {"text": "Five runs from that one — unusual.", "tags": ["dry"]},
        {"text": "Five! The kind of running you'd see in a relay.", "tags": ["hilarious"]},
    ],
    "ball_run_6": [
        {"text": "SIX! Out of the ground!", "tags": ["extrovert", "theatrical"]},
        {"text": "MAXIMUM! {batter} has gone enormous!", "tags": ["extrovert", "theatrical"]},
        {"text": "Six runs. {batter} swung — and connected.", "tags": ["technical"]},
        {"text": "He's hit it into the next post code!", "tags": ["hilarious", "extrovert"]},
        {"text": "OH. MY. WORD. That's a six and a half.", "tags": ["theatrical"]},
        {"text": "Towering hit. {batter} now on {batter_runs}.", "tags": ["serious", "technical"]},
    ],

    # --- wickets ---
    "wicket_match": [
        {"text": "MATCH! Same number from both — {batter} is GONE!", "tags": ["extrovert", "theatrical"]},
        {"text": "Wicket! Number-match dismissal. {batter} departs for {batter_runs}.", "tags": ["serious", "technical"]},
        {"text": "Read the bowler perfectly — sadly, the bowler also read him.", "tags": ["hilarious", "dry"]},
        {"text": "OUT! {bowler} pulls one out of the bag. {batter} walks back.", "tags": ["theatrical"]},
        {"text": "And that, friends, is what they call a hand-cricket dismissal.", "tags": ["hilarious", "casual"]},
    ],
    "wicket_bowled": [
        {"text": "BOWLED HIM! Stumps everywhere!", "tags": ["extrovert", "theatrical"]},
        {"text": "Castled. {batter} timed out and {bowler} cleaned him up.", "tags": ["technical"]},
        {"text": "BOWLED! Wood splintered, dignity bruised.", "tags": ["hilarious", "theatrical"]},
    ],
    "wicket_lbw": [
        {"text": "LBW! Plumb in front!", "tags": ["extrovert", "theatrical"]},
        {"text": "Adjudged LBW. The umpire didn't even need a second look.", "tags": ["serious", "technical"]},
        {"text": "Trapped! {batter} dozed off and the ball didn't.", "tags": ["hilarious", "dry"]},
    ],

    # --- extras ---
    "wide": [
        {"text": "Wide. {extras} extra to {batting_country}.", "tags": ["technical"]},
        {"text": "That was a country mile away from the stumps.", "tags": ["hilarious", "casual"]},
        {"text": "Sprayed wide. {bowler} wants that one back.", "tags": ["dry"]},
    ],
    "no_ball": [
        {"text": "No-ball! Free hit coming.", "tags": ["extrovert", "technical"]},
        {"text": "Overstepped. {bowler} owes the team an apology.", "tags": ["hilarious", "dry"]},
    ],
    "dead_ball": [
        {"text": "Dead ball. We'll go again.", "tags": ["technical"]},
        {"text": "Umpire calls dead ball. Take a breath, everyone.", "tags": ["dry"]},
        {"text": "Dead ball. Don't ask why. The umpire said so.", "tags": ["hilarious", "dry"]},
    ],
    "byes": [
        {"text": "Byes! {extras} runs sneak through.", "tags": ["casual"]},
        {"text": "The keeper waves at it as it goes past.", "tags": ["hilarious"]},
    ],
    "leg_byes": [
        {"text": "Leg byes — {extras} away.", "tags": ["technical"]},
    ],

    # --- transitions ---
    "over_start": [
        {"text": "Start of over {over_num}. {bowler} into his run-up.", "tags": ["technical"]},
        {"text": "New over. {bowler} marks his run.", "tags": ["dry"]},
        {"text": "Over {over_num}. Let's see what {bowler} has cooked up.", "tags": ["hilarious"]},
    ],
    "over_end": [
        {"text": "End of the over. {batting_country} {score}.", "tags": ["technical"]},
        {"text": "And that's drinks on the over. {batting_country} {score}.", "tags": ["traditional"]},
    ],
    "milestone_50": [
        {"text": "FIFTY! {batter} brings up the half-century.", "tags": ["extrovert", "theatrical"]},
        {"text": "Fifty for {batter} — quietly compiled.", "tags": ["serious", "technical"]},
        {"text": "Half-century! {batter} has not been having a normal one.", "tags": ["hilarious"]},
    ],
    "milestone_100": [
        {"text": "HUNDRED! {batter} reaches three figures!", "tags": ["extrovert", "theatrical"]},
        {"text": "A century. Hat off to {batter}.", "tags": ["serious", "traditional"]},
    ],
    "innings_end": [
        {"text": "End of innings. {batting_country} all out / overs done at {score}.", "tags": ["technical"]},
        {"text": "And that's that. {batting_country} sign off at {score}.", "tags": ["dry"]},
    ],
    "match_end": [
        {"text": "{result_summary}. Tip of the cap to both sides.", "tags": ["traditional", "serious"]},
        {"text": "{result_summary}. What a contest!", "tags": ["extrovert"]},
        {"text": "{result_summary}. I, for one, need a lie down.", "tags": ["hilarious", "dry"]},
    ],

    # --- Antarctica special (kicks in when penguins are on the field) ---
    "antarctica_special": [
        {"text": "{batter} waddles to the crease. There is a great deal of dignity in the wobble.", "tags": ["hilarious", "theatrical"]},
        {"text": "{bowler} into the run-up — really more of a slide, technically.", "tags": ["hilarious", "casual"]},
        {"text": "The Antarctica skipper calls a quick fielding meeting. Many penguins. Few decisions.", "tags": ["hilarious", "extrovert"]},
        {"text": "I have been told that the Antarctica players prefer their pitches at minus six.", "tags": ["hilarious", "dry"]},
        {"text": "And there's a herring on the field. We'll wait while it's removed.", "tags": ["hilarious", "theatrical"]},
        {"text": "{batter} just stared at the ball as it went past. To be fair, he's a penguin.", "tags": ["hilarious", "dry"]},
        {"text": "The Antarctica wicketkeeper is currently lying on his belly. Tactical, apparently.", "tags": ["hilarious"]},
        {"text": "{batter} attempts a single — slips, slides, and ends up safely back in the crease.", "tags": ["hilarious", "theatrical"]},
        {"text": "Tremendous form from the Antarctican tail. They've fallen over four times already.", "tags": ["hilarious", "dry"]},
        {"text": "{bowler} bowls. The ball lands. The penguin claps. We move on.", "tags": ["hilarious", "casual"]},
    ],

    # --- callbacks (filled by engine) ---
    "callback": [
        {"text": "And remember earlier in over {prev_over} when {prev_batter} did exactly the same? Pattern emerging.", "tags": ["technical", "serious"]},
        {"text": "Reminds me of {prev_event_short} a few overs back.", "tags": ["dry", "casual"]},
        {"text": "As I was saying about {prev_batter} earlier — they really do love that shot.", "tags": ["hilarious", "casual"]},
    ],
}


def situation_for_ball(runs: int, wicket_kind: str | None, extra_kind: str | None) -> str:
    if wicket_kind == "match":
        return "wicket_match"
    if wicket_kind == "bowled":
        return "wicket_bowled"
    if wicket_kind == "lbw":
        return "wicket_lbw"
    if extra_kind == "wide":
        return "wide"
    if extra_kind == "no-ball":
        return "no_ball"
    if extra_kind == "dead-ball":
        return "dead_ball"
    if extra_kind == "byes":
        return "byes"
    if extra_kind == "leg-byes":
        return "leg_byes"
    if runs == 0:
        return "ball_dot"
    return f"ball_run_{runs}"
