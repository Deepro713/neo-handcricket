"""Commentary line templates — keyed by situation × turn.

Each ball produces 2-3 lines that flow as a conversation across commentators.
Lines are split into "turns":
  - opener   : initial reaction to the ball
  - analysis : what just happened, technical / contextual
  - quip     : optional lighter response, callback, or aside

Each turn has its own template pool, with trait tags for commentator-personality
matching. The engine picks lines turn-by-turn, ensuring different commentators
deliver successive turns when possible.

Placeholders: {batter} {bowler} {runs} {score} {wickets} {over} {target}
              {country} {opponent} {bowling_country} {batting_country}
              {extras} {extra_kind} {wicket_kind} {batter_runs} {result_summary}
"""
from __future__ import annotations

# Each situation maps to a dict of turn -> list of templates.
# A "template" is {"text": ..., "tags": [...]}

LINES: dict[str, dict[str, list[dict]]] = {

    # =========================================================================
    # ball_dot — defended / left alone / no run
    # =========================================================================
    "ball_dot": {
        "opener": [
            {"text": "Dot ball.", "tags": ["dry"]},
            {"text": "And blocked.", "tags": ["dry"]},
            {"text": "Defended into the pitch.", "tags": ["technical"]},
            {"text": "Watchful from {batter}.", "tags": ["serious", "technical"]},
            {"text": "{batter} blocks one out.", "tags": ["casual"]},
            {"text": "No run.", "tags": ["dry", "minimal"]},
            {"text": "Plays it back gently.", "tags": ["technical"]},
            {"text": "{bowler} draws him forward — defended.", "tags": ["technical"]},
        ],
        "analysis": [
            {"text": "{batter} just wanted to see one through there. Sensible cricket.", "tags": ["serious", "traditional"]},
            {"text": "That's the kind of ball you get out trying to hit.", "tags": ["technical"]},
            {"text": "Good length, on the stumps — not a bad ball at all.", "tags": ["technical"]},
            {"text": "He's keeping things simple. Score is {score}, can't take risks here.", "tags": ["serious", "technical"]},
            {"text": "{bowler} probing, {batter} respecting it.", "tags": ["technical"]},
            {"text": "Tidy from {bowler}. Building pressure ball-by-ball.", "tags": ["technical"]},
            {"text": "Patient. The fielding side will take that all day.", "tags": ["serious"]},
            {"text": "It's a chess match in the middle right now.", "tags": ["theatrical"]},
        ],
        "quip": [
            {"text": "Riveting stuff.", "tags": ["dry", "hilarious"]},
            {"text": "I've seen more excitement in a tax form, but cricket's a long game.", "tags": ["hilarious", "dry"]},
            {"text": "Solid defence. Your dad would approve.", "tags": ["hilarious", "casual"]},
            {"text": "If only someone had told the bowler that's not a plan.", "tags": ["hilarious", "dry"]},
            {"text": "{batter} treating that like a precious heirloom.", "tags": ["hilarious"]},
            {"text": "Both teams are playing as though they've forgotten who's batting.", "tags": ["hilarious", "dry"]},
        ],
    },

    # =========================================================================
    # ball_run_1 — single
    # =========================================================================
    "ball_run_1": {
        "opener": [
            {"text": "Single. {runs} run.", "tags": ["casual"]},
            {"text": "Nudged for one.", "tags": ["technical"]},
            {"text": "Worked away — single.", "tags": ["technical"]},
            {"text": "Pushed into the gap, easy single.", "tags": ["casual"]},
            {"text": "Just a single, but they'll take it.", "tags": ["dry"]},
        ],
        "analysis": [
            {"text": "Strike rotated. {batter} now on {batter_runs}.", "tags": ["technical"]},
            {"text": "Singles like this build innings. {batting_country} {score}.", "tags": ["serious", "traditional"]},
            {"text": "Smart cricket. Get off strike, give the partner a look.", "tags": ["technical"]},
            {"text": "Quick between the wickets — a single off a defensive shot.", "tags": ["technical"]},
            {"text": "{bowler} happy enough conceding singles.", "tags": ["technical"]},
        ],
        "quip": [
            {"text": "The most unsung run in cricket — and yet, the most cherished.", "tags": ["theatrical"]},
            {"text": "If you can't hit a six, run a single. {batter} agrees.", "tags": ["hilarious", "casual"]},
            {"text": "One run. The romantic in me thrills.", "tags": ["hilarious", "dry"]},
        ],
    },

    # =========================================================================
    # ball_run_2 — twos
    # =========================================================================
    "ball_run_2": {
        "opener": [
            {"text": "Two runs!", "tags": ["extrovert"]},
            {"text": "Comfortable couple.", "tags": ["technical"]},
            {"text": "Pushed into the gap, comes back for two.", "tags": ["technical"]},
            {"text": "Two!", "tags": ["casual"]},
        ],
        "analysis": [
            {"text": "Sharp running between the wickets there.", "tags": ["technical"]},
            {"text": "Couple of runs. {batting_country} {score}.", "tags": ["technical"]},
            {"text": "Found the gap perfectly. The fielder had no chance.", "tags": ["theatrical", "technical"]},
        ],
        "quip": [
            {"text": "Two! Like a one, but doubled.", "tags": ["hilarious", "dry"]},
            {"text": "More than a single, less than a three. They'll take it.", "tags": ["hilarious", "dry"]},
        ],
    },

    # =========================================================================
    # ball_run_3 — threes
    # =========================================================================
    "ball_run_3": {
        "opener": [
            {"text": "Three runs! Now THAT was a run.", "tags": ["extrovert", "theatrical"]},
            {"text": "Three! Hard running.", "tags": ["extrovert"]},
            {"text": "Drilled into the gap, three completed.", "tags": ["technical"]},
        ],
        "analysis": [
            {"text": "Beat the fielder to the rope by an inch.", "tags": ["theatrical"]},
            {"text": "Three runs and they're knackered.", "tags": ["hilarious", "casual"]},
            {"text": "{batter} on {batter_runs} now. Building.", "tags": ["technical"]},
        ],
        "quip": [
            {"text": "The rare and majestic three. Always satisfying.", "tags": ["hilarious", "dry"]},
            {"text": "I haven't seen running like that since the 90s.", "tags": ["hilarious", "traditional"]},
        ],
    },

    # =========================================================================
    # ball_run_4 — boundary four
    # =========================================================================
    "ball_run_4": {
        "opener": [
            {"text": "FOUR! Cracking shot from {batter}!", "tags": ["extrovert", "theatrical"]},
            {"text": "Boundary! Four runs!", "tags": ["extrovert"]},
            {"text": "PINGED through the covers!", "tags": ["extrovert", "theatrical"]},
            {"text": "FOUR! That's racing away!", "tags": ["extrovert"]},
            {"text": "Beautifully timed — that's four.", "tags": ["technical", "traditional"]},
            {"text": "Four runs to {batting_country}.", "tags": ["serious", "technical"]},
        ],
        "analysis": [
            {"text": "Picked the gap, beat the fielder, all class.", "tags": ["technical"]},
            {"text": "{bowler} gave him room and {batter} didn't miss out.", "tags": ["technical"]},
            {"text": "The best shot of the over. {batter} on {batter_runs}.", "tags": ["technical"]},
            {"text": "Right out of the middle. Always going.", "tags": ["theatrical", "technical"]},
            {"text": "{batting_country} {score} — and the game is shifting.", "tags": ["serious", "technical"]},
        ],
        "quip": [
            {"text": "{batter} just told the bowler to sit down.", "tags": ["hilarious", "extrovert"]},
            {"text": "{bowler} did not enjoy that. Not one bit.", "tags": ["hilarious", "dry"]},
            {"text": "If the boundary rope was a person, it would have got out of the way.", "tags": ["hilarious", "theatrical"]},
            {"text": "That's the kind of shot you put on a postcard.", "tags": ["hilarious"]},
        ],
    },

    # =========================================================================
    # ball_run_5 — fives (rare in real cricket; possible in hand cricket)
    # =========================================================================
    "ball_run_5": {
        "opener": [
            {"text": "Five runs from that one — unusual!", "tags": ["dry"]},
            {"text": "Five! Where did they come from?", "tags": ["extrovert"]},
        ],
        "analysis": [
            {"text": "Five — overthrows, presumably. Or a generous umpire.", "tags": ["hilarious", "dry"]},
            {"text": "{batter} on {batter_runs}. The five is rarer than the unicorn.", "tags": ["hilarious"]},
        ],
        "quip": [
            {"text": "I've covered a thousand matches and seen maybe four fives.", "tags": ["hilarious", "dry"]},
            {"text": "Cricket gives, cricket takes. Today it gave a five.", "tags": ["theatrical"]},
        ],
    },

    # =========================================================================
    # ball_run_6 — six
    # =========================================================================
    "ball_run_6": {
        "opener": [
            {"text": "SIX! Out of the ground!", "tags": ["extrovert", "theatrical"]},
            {"text": "MAXIMUM! {batter} has gone enormous!", "tags": ["extrovert", "theatrical"]},
            {"text": "OH. MY. WORD!", "tags": ["theatrical"]},
            {"text": "SIX RUNS! That is huge!", "tags": ["extrovert"]},
            {"text": "Towering hit. Six runs.", "tags": ["serious", "technical"]},
        ],
        "analysis": [
            {"text": "He swung from the hips and connected sweetly.", "tags": ["technical"]},
            {"text": "{batter} now on {batter_runs}. Foot to floor here.", "tags": ["technical"]},
            {"text": "Right out of the screws. Long handle, full flow.", "tags": ["technical", "theatrical"]},
            {"text": "{bowler} pitched it up and got punished.", "tags": ["technical"]},
            {"text": "{batting_country} {score} — the momentum is shifting decisively.", "tags": ["serious"]},
        ],
        "quip": [
            {"text": "He's hit it into the next post code!", "tags": ["hilarious", "extrovert"]},
            {"text": "Find that ball, send it to the museum.", "tags": ["hilarious", "theatrical"]},
            {"text": "If that hits anything taller than a fence post, it's still going up.", "tags": ["hilarious", "extrovert"]},
            {"text": "{bowler} should send the ball a postcard from wherever it lands.", "tags": ["hilarious"]},
            {"text": "That ball has plans. Big plans.", "tags": ["hilarious"]},
        ],
    },

    # =========================================================================
    # wicket_match — number-match dismissal (most common in hand cricket)
    # =========================================================================
    "wicket_match": {
        "opener": [
            {"text": "MATCH! Same number from both — {batter} is GONE!", "tags": ["extrovert", "theatrical"]},
            {"text": "WICKET! Hand-cricket classic — they read each other!", "tags": ["extrovert"]},
            {"text": "OUT! Bowler and batter tie — {batter} departs.", "tags": ["technical"]},
            {"text": "GONE! {batter} dismissed for {batter_runs}.", "tags": ["extrovert"]},
            {"text": "And that's the wicket {bowler} has been hunting.", "tags": ["serious", "technical"]},
        ],
        "analysis": [
            {"text": "Both showed the same number. {batter} walks back for {batter_runs}.", "tags": ["technical"]},
            {"text": "{bowler} read him. Or {batter} read the bowler. Either way — out.", "tags": ["technical"]},
            {"text": "{batting_country} {score} — that's a sizeable hole in the innings.", "tags": ["serious"]},
            {"text": "The wicket falls and {batting_country} need a steadier hand now.", "tags": ["serious", "traditional"]},
            {"text": "Pressure builds. {bowler} grins.", "tags": ["theatrical"]},
        ],
        "quip": [
            {"text": "Two minds, one number. That's how it always ends.", "tags": ["hilarious", "dry"]},
            {"text": "Read the bowler perfectly — sadly, the bowler also read him.", "tags": ["hilarious", "dry"]},
            {"text": "And that, friends, is what they call a hand-cricket dismissal.", "tags": ["hilarious", "casual"]},
            {"text": "Cruel game, hand cricket. Nowhere to hide.", "tags": ["hilarious", "dry"]},
        ],
    },

    # =========================================================================
    # wicket_bowled — timeout outcome bowled
    # =========================================================================
    "wicket_bowled": {
        "opener": [
            {"text": "BOWLED HIM! Stumps everywhere!", "tags": ["extrovert", "theatrical"]},
            {"text": "CASTLED!", "tags": ["extrovert"]},
            {"text": "BOWLED! Wood splintered.", "tags": ["theatrical"]},
            {"text": "Beat him all ends up. BOWLED.", "tags": ["technical"]},
        ],
        "analysis": [
            {"text": "{batter} timed out and {bowler} cleaned him up.", "tags": ["technical"]},
            {"text": "He never picked it. Stone dead.", "tags": ["technical"]},
            {"text": "{batter} departs for {batter_runs}. Big one for {bowling_country}.", "tags": ["serious"]},
        ],
        "quip": [
            {"text": "Wood splintered. Dignity bruised. Everything as it should be.", "tags": ["hilarious", "theatrical"]},
            {"text": "{batter} just heard the death rattle and felt every bit of it.", "tags": ["hilarious"]},
        ],
    },

    # =========================================================================
    # wicket_lbw
    # =========================================================================
    "wicket_lbw": {
        "opener": [
            {"text": "LBW! Plumb in front!", "tags": ["extrovert", "theatrical"]},
            {"text": "GIVEN! Leg before!", "tags": ["extrovert"]},
            {"text": "Adjudged LBW. The umpire didn't even need a second look.", "tags": ["serious", "technical"]},
        ],
        "analysis": [
            {"text": "Hit him on the pad in line, going on with the arm.", "tags": ["technical"]},
            {"text": "{batter} dozed off and the ball didn't.", "tags": ["hilarious", "dry"]},
            {"text": "Trapped. Big shout, finger up. Done.", "tags": ["technical"]},
        ],
        "quip": [
            {"text": "There are old bowlers and there are bold bowlers — but only some old, bold bowlers get LBW.", "tags": ["hilarious", "traditional"]},
            {"text": "I'm not sure {batter} even saw it. The umpire certainly did.", "tags": ["hilarious", "dry"]},
        ],
    },

    # =========================================================================
    # wide
    # =========================================================================
    "wide": {
        "opener": [
            {"text": "Wide. {extras} extra to {batting_country}.", "tags": ["technical"]},
            {"text": "Sprayed wide.", "tags": ["dry"]},
            {"text": "Wide called.", "tags": ["technical", "minimal"]},
        ],
        "analysis": [
            {"text": "{bowler} wants that one back.", "tags": ["dry"]},
            {"text": "Free run for the batting side. Pressure released.", "tags": ["technical"]},
        ],
        "quip": [
            {"text": "That was a country mile away from the stumps.", "tags": ["hilarious", "casual"]},
            {"text": "{bowler} aimed at the cones and missed the practice ground.", "tags": ["hilarious"]},
        ],
    },

    # =========================================================================
    # no_ball
    # =========================================================================
    "no_ball": {
        "opener": [
            {"text": "No-ball! Free hit coming.", "tags": ["extrovert", "technical"]},
            {"text": "Overstepped — no-ball!", "tags": ["technical"]},
        ],
        "analysis": [
            {"text": "{bowler} owes the team an apology.", "tags": ["hilarious", "dry"]},
            {"text": "And {batter} gets a freebie next ball.", "tags": ["technical"]},
        ],
        "quip": [
            {"text": "I once met a fast bowler who couldn't tell me where the line was. {bowler} would relate.", "tags": ["hilarious", "traditional"]},
        ],
    },

    # =========================================================================
    # dead_ball
    # =========================================================================
    "dead_ball": {
        "opener": [
            {"text": "Dead ball. We'll go again.", "tags": ["technical"]},
            {"text": "Umpire calls dead ball.", "tags": ["dry"]},
        ],
        "analysis": [
            {"text": "Take a breath, everyone.", "tags": ["dry"]},
            {"text": "Reset. Replay. Cricket continues.", "tags": ["traditional"]},
        ],
        "quip": [
            {"text": "Dead ball. Don't ask why. The umpire said so.", "tags": ["hilarious", "dry"]},
        ],
    },

    # =========================================================================
    # byes / leg-byes
    # =========================================================================
    "byes": {
        "opener": [
            {"text": "Byes! {extras} runs sneak through.", "tags": ["casual"]},
            {"text": "Through the keeper for {extras}.", "tags": ["technical"]},
        ],
        "analysis": [{"text": "The keeper waves at it as it goes past.", "tags": ["hilarious"]}],
        "quip":     [{"text": "If you're going to miss, miss decisively.", "tags": ["hilarious", "dry"]}],
    },
    "leg_byes": {
        "opener":   [{"text": "Leg byes — {extras} away.", "tags": ["technical"]}],
        "analysis": [{"text": "Off the pad and they run.", "tags": ["technical"]}],
        "quip":     [{"text": "Cricket's most polite form of run.", "tags": ["hilarious", "dry"]}],
    },

    # =========================================================================
    # over transitions
    # =========================================================================
    "over_start": {
        "opener": [
            {"text": "Start of over {over_num}. {bowler} into his run-up.", "tags": ["technical"]},
            {"text": "New over — {bowler} marks his run.", "tags": ["dry"]},
            {"text": "Over {over_num}. Let's see what {bowler} has cooked up.", "tags": ["hilarious"]},
        ],
        "analysis": [],
        "quip": [],
    },
    "over_end": {
        "opener": [
            {"text": "End of the over. {batting_country} {score}.", "tags": ["technical"]},
            {"text": "And that's drinks on the over.", "tags": ["traditional"]},
        ],
        "analysis": [],
        "quip": [],
    },

    # =========================================================================
    # milestones
    # =========================================================================
    "milestone_50": {
        "opener": [
            {"text": "FIFTY! {batter} brings up the half-century!", "tags": ["extrovert", "theatrical"]},
            {"text": "Fifty for {batter} — quietly compiled.", "tags": ["serious", "technical"]},
        ],
        "analysis": [
            {"text": "A serious knock from {batter}, exactly when {batting_country} needed it.", "tags": ["serious"]},
            {"text": "Half-century. {batter} acknowledges the dressing room.", "tags": ["traditional"]},
        ],
        "quip": [
            {"text": "{batter} has not been having a normal one.", "tags": ["hilarious"]},
            {"text": "Bat raised. Helmet off. The classics endure.", "tags": ["traditional", "theatrical"]},
        ],
    },
    "milestone_100": {
        "opener": [
            {"text": "HUNDRED! {batter} reaches three figures!", "tags": ["extrovert", "theatrical"]},
            {"text": "A century. Hat off to {batter}.", "tags": ["serious", "traditional"]},
        ],
        "analysis": [
            {"text": "An innings of true class. {batter} on {batter_runs} — and counting.", "tags": ["serious", "traditional"]},
        ],
        "quip": [
            {"text": "I'd buy a print of that knock.", "tags": ["hilarious"]},
        ],
    },

    # =========================================================================
    # match end
    # =========================================================================
    "innings_end": {
        "opener": [
            {"text": "End of innings. {batting_country} sign off at {score}.", "tags": ["technical"]},
            {"text": "And that's that. Innings closes at {score}.", "tags": ["dry"]},
        ],
        "analysis": [],
        "quip": [],
    },
    "match_end": {
        "opener": [
            {"text": "{result_summary}. Tip of the cap to both sides.", "tags": ["traditional", "serious"]},
            {"text": "{result_summary}. What a contest!", "tags": ["extrovert"]},
            {"text": "{result_summary}. I, for one, need a lie down.", "tags": ["hilarious", "dry"]},
        ],
        "analysis": [],
        "quip": [],
    },

    # =========================================================================
    # Antarctica special — the penguins!
    # =========================================================================
    "antarctica_special": {
        "opener": [
            {"text": "{batter} waddles to the crease. There is great dignity in the wobble.", "tags": ["hilarious", "theatrical"]},
            {"text": "{bowler} into the run-up — really more of a slide, technically.", "tags": ["hilarious", "casual"]},
            {"text": "And there's a herring on the field. We'll wait.", "tags": ["hilarious", "theatrical"]},
            {"text": "{batter} just stared at the ball. To be fair, he's a penguin.", "tags": ["hilarious", "dry"]},
            {"text": "{bowler} bowls. The ball lands. The penguin claps. We move on.", "tags": ["hilarious", "casual"]},
        ],
        "analysis": [
            {"text": "Tactical lying-down from the keeper. Very Antarctica.", "tags": ["hilarious"]},
            {"text": "The Antarctica skipper called a meeting at gully. Many penguins. Few decisions.", "tags": ["hilarious", "extrovert"]},
            {"text": "I'm told the Antarctica side prefers the pitch at minus six.", "tags": ["hilarious", "dry"]},
        ],
        "quip": [
            {"text": "Tremendous form from the Antarctican tail. Four falls already.", "tags": ["hilarious", "dry"]},
            {"text": "The crowd is mostly krill, but they're loving it.", "tags": ["hilarious"]},
            {"text": "If I am being fair, the penguins have better fielding chemistry than half the Test sides.", "tags": ["hilarious", "casual"]},
        ],
    },

    # =========================================================================
    # callbacks (engine slots these into commentary occasionally)
    # =========================================================================
    "callback": {
        "opener": [],
        "analysis": [
            {"text": "Remember earlier in over {prev_over} when {prev_batter} did exactly the same? Pattern emerging.", "tags": ["technical", "serious"]},
            {"text": "As I mentioned in over {prev_over}, {prev_batter} loves that area.", "tags": ["technical", "casual"]},
        ],
        "quip": [
            {"text": "Reminds me of {prev_event_short} a few overs back.", "tags": ["dry", "casual"]},
            {"text": "If you missed the highlight reel from over {prev_over}, this is essentially that.", "tags": ["hilarious"]},
        ],
    },
}


# =========================================================================
# Big-moment line banks (M007). All original / CC0 — no broadcaster catchphrases.
# Accent moments fire after the ball conversation when the event detector flags
# them. `wicket_caught` is a full ball situation; the rest are single-line accents.
# =========================================================================
LINES.update({
    "wicket_caught": {
        "opener": [
            {"text": "Caught! Picked out the fielder and {batter} has to go.", "tags": ["serious"]},
            {"text": "Straight down a throat — that's a wicket!", "tags": ["theatrical"]},
            {"text": "Up goes the catch, and it sticks. {batter} departs.", "tags": ["casual"]},
            {"text": "Skied it, and {bowler} has his man.", "tags": ["technical"]},
        ],
        "analysis": [
            {"text": "{batter} couldn't keep it down — the fielder did the rest.", "tags": ["technical"]},
            {"text": "{bowler} drew the false stroke and it's a soft dismissal.", "tags": ["serious", "technical"]},
        ],
        "quip": [
            {"text": "He hit that one right to the only person who wanted it.", "tags": ["hilarious", "dry"]},
        ],
    },
    "hat_trick": {
        "opener": [
            {"text": "HAT-TRICK! Three in a row for {bowler} — extraordinary!", "tags": ["theatrical", "extrovert"]},
            {"text": "Three wickets, three balls — {bowler} is on fire!", "tags": ["theatrical"]},
            {"text": "Did that just happen? A hat-trick for {bowler}!", "tags": ["extrovert", "casual"]},
        ],
        "analysis": [
            {"text": "You wait a career for one of those. {bowler} has it today.", "tags": ["serious"]},
        ],
    },
    "maiden": {
        "opener": [
            {"text": "A maiden over — not a run off the bat from {bowler}.", "tags": ["technical"]},
            {"text": "Six dots, nothing given. Tidy from {bowler}.", "tags": ["serious", "technical"]},
            {"text": "Pressure cranked — that's a maiden.", "tags": ["technical"]},
        ],
    },
    "last_ball_finish": {
        "opener": [
            {"text": "They've done it — sealed it right at the death! What a finish!", "tags": ["theatrical", "extrovert"]},
            {"text": "Down to the wire and over the line! Scenes here!", "tags": ["theatrical"]},
            {"text": "Off the very last they get there — heart-stopping stuff!", "tags": ["extrovert", "casual"]},
        ],
    },
    "collapse": {
        "opener": [
            {"text": "The wheels have come off — wickets tumbling in a heap.", "tags": ["serious", "theatrical"]},
            {"text": "A genuine collapse unfolding here.", "tags": ["serious"]},
            {"text": "From steady to chaos in the blink of an eye.", "tags": ["technical"]},
        ],
    },
    "partnership_50": {
        "opener": [
            {"text": "Fifty up for the stand — a real partnership building.", "tags": ["technical"]},
            {"text": "These two have put on fifty together. Steadying the ship.", "tags": ["serious"]},
        ],
    },
})


# Breadth expansion (M013) — extra original/CC0 lines appended to thinner pools.
_EXTRA: dict[str, dict[str, list[dict]]] = {
    "ball_run_2": {
        "opener": [
            {"text": "Two more, well run.", "tags": ["technical"]},
            {"text": "Pushed into the gap, back for the second.", "tags": ["casual"]},
            {"text": "Good running between the wickets — two.", "tags": ["technical"]},
        ],
        "analysis": [{"text": "They're turning ones into twos — pressure on the field.", "tags": ["serious"]}],
    },
    "ball_run_3": {
        "opener": [
            {"text": "Three! Into the deep and they scamper back.", "tags": ["casual"]},
            {"text": "Driven hard, three to the rope-rider.", "tags": ["technical"]},
        ],
        "quip": [{"text": "Three is the new four if you run hard enough.", "tags": ["hilarious", "dry"]}],
    },
    "ball_run_5": {
        "opener": [
            {"text": "Five — boundary overthrows tagged on.", "tags": ["casual"]},
            {"text": "Misfield! They cash in for five.", "tags": ["technical"]},
        ],
    },
    "milestone_100": {
        "opener": [
            {"text": "A hundred! Bat aloft, helmet off — take it in.", "tags": ["theatrical", "extrovert"]},
            {"text": "Three figures, and richly deserved.", "tags": ["serious"]},
        ],
    },
    "partnership_50": {
        "opener": [
            {"text": "Fifty for the stand and the momentum has shifted.", "tags": ["serious"]},
            {"text": "They've dug in together — half-century partnership.", "tags": ["technical"]},
        ],
    },
    "hat_trick": {
        "opener": [{"text": "THREE IN THREE! File this one in the memory bank.", "tags": ["theatrical"]}],
    },
    "collapse": {
        "opener": [{"text": "One brings two, two brings three — it's unravelling.", "tags": ["serious"]}],
    },
    "maiden": {
        "opener": [{"text": "Maiden over. Dot, dot, dot — relentless.", "tags": ["technical"]}],
    },
    "last_ball_finish": {
        "opener": [{"text": "Last delivery, and they nick it! Absolute scenes.", "tags": ["theatrical", "extrovert"]}],
    },
    "wicket_caught": {
        "opener": [{"text": "Held! Safe hands, and the batter trudges off.", "tags": ["serious"]}],
    },
    "over_start": {
        "opener": [{"text": "Fresh over, fresh plans. Here we go again.", "tags": ["casual"]}],
    },
    "innings_end": {
        "opener": [{"text": "And that's the innings — a total to bowl at.", "tags": ["serious"]}],
    },
    "match_end": {
        "opener": [{"text": "Stumps. What a contest that turned out to be.", "tags": ["serious"]}],
    },
}
for _sit, _turns in _EXTRA.items():
    _bucket = LINES.setdefault(_sit, {})
    for _turn, _lines in _turns.items():
        _bucket.setdefault(_turn, []).extend(_lines)


# Event kind → commentary situation key, in descending priority. Used to pick the
# single most newsworthy accent line when the event detector flags big moments.
_EVENT_SITUATION_PRIORITY: list[tuple[str, str, str]] = [
    # (event.kind, event.subtype or "", situation_key)
    ("last_ball_finish", "", "last_ball_finish"),
    ("hat_trick", "", "hat_trick"),
    ("milestone", "hundred", "milestone_100"),
    ("milestone", "fifty", "milestone_50"),
    ("collapse", "", "collapse"),
    ("partnership", "fifty", "partnership_50"),
    ("maiden", "", "maiden"),
]


def event_situation(events: list) -> str | None:
    """Pick the highest-priority *accent* situation key from detected events, or
    None if none of them warrant an extra escalation line (wickets/boundaries are
    already covered by the ball conversation)."""
    kinds = {(e.kind, e.subtype) for e in events}
    for kind, subtype, key in _EVENT_SITUATION_PRIORITY:
        if (kind, subtype) in kinds:
            return key
    return None


def situation_for_ball(runs: int, wicket_kind: str | None, extra_kind: str | None) -> str:
    if wicket_kind == "match":
        return "wicket_match"
    if wicket_kind == "bowled":
        return "wicket_bowled"
    if wicket_kind == "lbw":
        return "wicket_lbw"
    if wicket_kind == "caught":
        return "wicket_caught"
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
