# chatlogic.py
# Contains the conversation nodes, routing, and helpers.

import re
from copy import deepcopy

# Fixed UI quote & bot name (used for personalization in messages)
BOT_NAME = "FlaskChat Bot"
TOP_QUOTE = "Small steps daily beat motivation."

# A compact tree of nodes. Each node has:
# "text": message (can include {name}, {goal}, {habit})
# "options": list of (option_id, option_text)
# "tags": optional keywords to match typed input to route
#
# Node ids are strings. "start" is initial node.

_nodes = {
    "start": {
        "text": "Welcome sir/ma’am! How can I help you today?",
        "options": [
            ("habits_start", "I need motivation to start daily habits."),
            ("confidence_start", "I want to build confidence / stop overthinking."),
            ("career_start", "I need career / future planning help.")
        ],
        "tags": ["habit", "habits", "motivate", "motivation", "confidence", "career", "future"]
    },

    # HABITS FLOW
    "habits_start": {
        "text": "Great — clarity first. Do you want a short habit plan or tips to regain momentum?",
        "options": [
            ("habit_choose", "Help me choose a small habit."),
            ("habit_tips", "Give me quick tips to stay consistent."),
            ("habit_restart", "I tried & failed — help me restart.")
        ],
        "tags": ["habit", "start", "consistency"]
    },
    "habit_choose": {
        "text": "Pick one simple habit to try for 7 days (tiny wins build momentum). Which appeals to you?",
        "options": [
            ("habit_walk", "Morning 10-minute walk"),
            ("habit_read", "Read 10 minutes / 10 pages"),
            ("habit_skill", "20-minute focused skill practice")
        ],
        "tags": ["walk", "read", "skill", "practice"]
    },
    "habit_walk": {
        "text": "A morning walk is excellent. Start Day 1 with 10 minutes after waking. Want a reminder format or a checklist?",
        "options": [
            ("habit_checklist", "Show me a simple checklist format"),
            ("habit_tips", "Give me tips to keep consistent"),
            ("back_to_habits", "Back to habit options")
        ],
    },
    "habit_read": {
        "text": "Reading daily expands focus. Start small — 10 minutes. Would you like a reading plan or tips to avoid distraction?",
        "options": [
            ("habit_plan_read", "Show reading plan"),
            ("habit_tips", "Give me tips to keep consistent"),
            ("back_to_habits", "Back to habit options")
        ],
    },
    "habit_skill": {
        "text": "Focused practice is powerful. Pick a specific skill and commit 20 minutes daily. Want a micro-plan?",
        "options": [
            ("habit_micro_skill", "Yes, give a micro-plan"),
            ("habit_tips", "Give me tips to keep consistent"),
            ("back_to_habits", "Back to habit options")
        ]
    },
    "habit_checklist": {
        "text": "Checklist: [ ] Day 1 ✓ [ ] Day 2 [ ] Day 3 ... Keep it visible. Would you like accountability tips?",
        "options": [
            ("habit_account", "Yes — accountability tips"),
            ("habit_tips", "General tips"),
            ("end_node", "Continue")
        ]
    },
    "habit_tips": {
        "text": "Tip: Start small, attach habit to a routine, track progress, and treat slip-ups as data, not failure.",
        "options": [
            ("habit_choose", "Choose a habit"),
            ("habit_account", "How to stay accountable?"),
            ("start", "Main menu")
        ]
    },
    "habit_restart": {
        "text": "Restarting is normal — focus on one tiny next step. Would you like a regret-free micro-plan or motivational strategies?",
        "options": [
            ("habit_micro_plan", "Give me a micro-plan"),
            ("motivation_boost", "I need a short motivational boost"),
            ("start", "Main menu")
        ]
    },

    # CONFIDENCE FLOW
    "confidence_start": {
        "text": "Building confidence begins with small, repeatable wins. Which area troubles you most?",
        "options": [
            ("conf_social", "Social anxiety / approaching people"),
            ("conf_selfimage", "Self-image / comparing with others"),
            ("conf_overthink", "Overthinking / decision paralysis")
        ],
        "tags": ["confidence", "overthinking", "social", "anxiety"]
    },
    "conf_social": {
        "text": "For social anxiety: start with short, low-pressure interactions. Would you like roleplay prompts or a daily micro-challenge?",
        "options": [
            ("conf_roleplay", "Roleplay prompts"),
            ("conf_micro", "Daily micro-challenge"),
            ("motivation_boost", "Motivational tip")
        ]
    },
    "conf_roleplay": {
        "text": "Roleplay: practice a friendly opener and a follow-up question. Try it now or receive examples to rehearse.",
        "options": [
            ("practice_now", "Let me practice now"),
            ("examples", "Show example openers"),
            ("conf_micro", "Try a micro-challenge")
        ]
    },
    "conf_micro": {
        "text": "Micro-challenge: start a 2-minute conversation with a familiar person this week. Small success fuels confidence.",
        "options": [
            ("confidence_progress", "How to track progress?"),
            ("conf_roleplay", "Roleplay prompts"),
            ("start", "Main menu")
        ]
    },
    "conf_selfimage": {
        "text": "Self-image improves when actions match values. Would you like concrete daily actions or coping phrases?",
        "options": [
            ("actions", "Concrete daily actions"),
            ("phrases", "Short coping phrases"),
            ("motivation_boost", "Short motivational quote")
        ]
    },
    "conf_overthink": {
        "text": "Decision paralysis reduces with time-boxing and next-action focus. Want a 3-step decision method?",
        "options": [
            ("decision_method", "Yes — 3-step decision method"),
            ("mindfulness_tip", "Give a quick mindfulness tip"),
            ("start", "Main menu")
        ]
    },

    # CAREER FLOW
    "career_start": {
        "text": "Career clarity begins with honest assessment. Do you want skill mapping, resume tips, or interview prep?",
        "options": [
            ("career_skills", "Skill mapping / learning plan"),
            ("career_resume", "Resume / CV tips"),
            ("career_interview", "Interview preparation")
        ],
        "tags": ["career", "job", "resume", "interview"]
    },
    "career_skills": {
        "text": "Identify one high-leverage skill you can start learning. Would you like a 4-week learning plan or a quick resource list?",
        "options": [
            ("learn_plan", "4-week micro learning plan"),
            ("resource_list", "Quick resource list"),
            ("career_resume", "Resume tips")
        ]
    },
    "career_resume": {
        "text": "Resume tip: keep it concise, highlight impact, list measurable results. Want a one-line achievement template?",
        "options": [
            ("achievement_template", "Show template"),
            ("career_skills", "Find skills to list"),
            ("start", "Main menu")
        ]
    },
    "career_interview": {
        "text": "Interview prep: structure answers with STAR (Situation, Task, Action, Result). Want mock interview questions or tips?",
        "options": [
            ("mock_qs", "Give mock interview questions"),
            ("interview_tips", "Quick interview tips"),
            ("resource_list", "Resource list")
        ]
    },

    # MOTIVATION BOOST / GENERIC
    "motivation_boost": {
        "text": "Remember: consistent small steps compound. What's one small step you can take today?",
        "options": [
            ("habit_choose", "Pick a small habit"),
            ("confidence_start", "Work on confidence"),
            ("career_start", "Work on career")
        ],
        "tags": ["motivate", "inspire", "boost"]
    },

    # small utility / endpoints
    "practice_now": {
        "text": "I'll simulate a brief roleplay. Say 'Hi' or type a greeting to begin practice.",
        "options": [
            ("practice_listen", "Say 'Hi'"),
            ("examples", "See example openers"),
            ("start", "Main menu")
        ]
    },
    "examples": {
        "text": "Example openers: 'Hi, how's your day?' / 'I liked your post on X — tell me more.' Try one now.",
        "options": [
            ("practice_now", "Practice now"),
            ("conf_micro", "Micro-challenge"),
            ("start", "Main menu")
        ]
    },
    "decision_method": {
        "text": "3-step method: 1) List top 2 options 2) Time-box decision 3) Commit to action for 3 days. Want an example?",
        "options": [
            ("decision_example", "Show example"),
            ("conf_overthink", "Overthinking help"),
            ("start", "Main menu")
        ]
    },
    "end_node": {
        "text": "Good. Would you like to continue or save this plan for later (session-only)?",
        "options": [
            ("start", "Main menu"),
            ("motivation_boost", "A short motivational line"),
            ("habit_tips", "More habit tips")
        ]
    },
    "habit_micro_plan": {
        "text": "Micro-plan: Day 1–3 focus on starting, Day 4–7 increase consistency. Log briefly each day.",
        "options": [
            ("habit_choose", "Choose a habit"),
            ("habit_tips", "Tips"),
            ("start", "Main menu")
        ]
    },
    "habit_micro_skill": {
        "text": "Micro-plan for skill: 1) Pick exact sub-skill 2) 20-min focused block 3) Reflect 5 min. Start today?",
        "options": [
            ("practice_now", "Start now"),
            ("habit_tips", "Tips to focus"),
            ("start", "Main menu")
        ]
    },
    "habit_account": {
        "text": "Accountability: tell a friend, set a visible tracker, or check in every 3 days. Want a sample check-in message?",
        "options": [
            ("sample_checkin", "Show sample check-in"),
            ("habit_tips", "General tips"),
            ("start", "Main menu")
        ]
    },
    "sample_checkin": {
        "text": "Sample: 'I'm starting a 7-day habit — day 1 done! I'll check in again.' Simple and clear.",
        "options": [
            ("habit_choose", "Choose a habit"),
            ("motivation_boost", "Motivational line"),
            ("start", "Main menu")
        ]
    },
    # fallback node
    "fallback": {
        "text": "I understand. Could you clarify or choose one of the options below?",
        "options": [
            ("start", "Main menu"),
            ("motivation_boost", "Give me a motivation boost"),
            ("habit_choose", "Help me choose a habit")
        ]
    }
}

# helper to ensure every node has 3 options: if fewer, fill with sensible choices
def _ensure_three_options(node):
    opts = node.get("options", [])
    # If any options are strings (legacy), convert; expect tuples (id,text)
    normalized = []
    for o in opts:
        if isinstance(o, tuple) and len(o) == 2:
            normalized.append({"id": o[0], "text": o[1]})
        elif isinstance(o, dict) and "id" in o and "text" in o:
            normalized.append(o)
    # fill if less than 3
    defaults = [{"id": "start", "text": "Main menu"}, {"id": "motivation_boost", "text": "Motivation boost"}, {"id": "habit_choose", "text": "Choose a habit"}]
    i = 0
    while len(normalized) < 3:
        normalized.append(defaults[i % len(defaults)])
        i += 1
    return normalized[:3]

# Precompute options for nodes
_nodes_prepared = {}
for nid, node in _nodes.items():
    n = deepcopy(node)
    n["options"] = _ensure_three_options(n)
    _nodes_prepared[nid] = n

# Basic tokenizer/normalizer for matching
def _normalize_text(t: str) -> str:
    return re.sub(r"[^\w\s]", "", t.lower()).strip()

# Try to match user input to one of the node's option text or tags or common keywords
def _match_option_by_text(user_text: str, node_id: str):
    norm = _normalize_text(user_text)
    node = _nodes_prepared.get(node_id, {})
    # 1) exact option text match
    for opt in node.get("options", []):
        if _normalize_text(opt["text"]) == norm:
            return opt["id"]
    # 2) partial match (option keyword appears)
    for opt in node.get("options", []):
        opt_norm = _normalize_text(opt["text"])
        # check if any word overlaps
        user_words = set(norm.split())
        opt_words = set(opt_norm.split())
        if user_words & opt_words:
            return opt["id"]
    # 3) match tags
    tags = node.get("tags", []) + _nodes_prepared.get("start", {}).get("tags", [])
    for tag in tags:
        if tag and tag in norm:
            # try to map tag to a candidate option
            for opt in node.get("options", []):
                if tag in _normalize_text(opt["text"]):
                    return opt["id"]
    return None

# High-level router invoked from Flask
def handle_message(user_message: str, memory: dict):
    # ensure memory keys
    mem = memory or {}
    mem = dict(mem)  # shallow copy
    current_node = mem.get("node", "start")
    mem.setdefault("steps", 0)
    # store name if user says "my name is X" or "call me X"
    name_match = re.search(r"\b(?:my name is|i am|i'm|call me)\s+([A-Za-z]{2,40})\b", user_message, re.IGNORECASE)
    if name_match:
        mem["name"] = name_match.group(1).strip().capitalize()

    # store goal/habit if user explicitly says "my goal is ..." or "i want to ..."
    goal_match = re.search(r"\b(?:my goal is|i want to|i'm aiming to|i want)\s+(.*)", user_message, re.IGNORECASE)
    if goal_match:
        mem["goal"] = goal_match.group(1).strip()

    # If user typed "restart" or "main menu" or "start", go to start
    if re.search(r"\b(main menu|start over|restart|home|menu)\b", user_message, re.IGNORECASE):
        current_node = "start"

    # If user typed a direct option text that matches any option for current node
    matched = _match_option_by_text(user_message, current_node)
    if matched:
        current_node = matched
    else:
        # attempt to map by scanning all nodes for a tag match for free-typed inputs
        norm = _normalize_text(user_message)
        # quick heuristic: if user mentions "career" or "job" map to career_start
        if re.search(r"\b(career|job|resume|interview|skills)\b", norm):
            current_node = "career_start"
        elif re.search(r"\b(habit|habit|daily|routine|start|consistency|walk|read)\b", norm):
            current_node = "habits_start"
        elif re.search(r"\b(confidence|overthink|anxiety|social|shy|confidence)\b", norm):
            current_node = "confidence_start"
        elif re.search(r"\b(motivate|motivation|inspire|boost)\b", norm):
            current_node = "motivation_boost"
        else:
            # if nothing maps, fallback to a gentle fallback node but still accept message
            current_node = "fallback"

    # build reply
    node = _nodes_prepared.get(current_node, _nodes_prepared["fallback"])
    # personalize text
    text = node.get("text", "")
    if "{name}" in text and mem.get("name"):
        text = text.replace("{name}", mem["name"])
    # small personalization insertion
    if "{goal}" in text and mem.get("goal"):
        text = text.replace("{goal}", mem["goal"])
    # increment steps
    mem["steps"] = mem.get("steps", 0) + 1
    mem["node"] = current_node

    # prepare options to send to frontend
    options_out = node.get("options", [])[:3]

    # final reply object
    reply_obj = {
        "reply": text,
        "options": options_out,
        "node": current_node,
        "memory": mem
    }
    return reply_obj
