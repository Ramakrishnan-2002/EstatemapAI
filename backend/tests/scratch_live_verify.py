from __future__ import annotations

import httpx

base_url = "http://localhost:8000/api/v1/ai/ask-map"


def run_turn(turn_num: int, msg: str, state: dict) -> dict:
    payload = {"message": msg, "current_state": state, "session_id": "live-verify-14"}
    resp = httpx.post(base_url, json=payload, timeout=30.0)
    if resp.status_code != 200:
        print(f"=== TURN {turn_num} ERROR {resp.status_code}: {resp.text}")
        return state
    data = resp.json()
    print(f"=== TURN {turn_num}: '{msg}' ===")
    print(
        f"Provider: {data.get('provider')} ({data.get('model')}) | Latency: {data.get('latency_ms')}ms | Action: {data.get('action')}"
    )
    s = data["state"]
    print(
        f"State: BHK={s.get('bedrooms')}, MaxPrice={s.get('max_price')}, Locality={s.get('locality')}, Dest={s.get('commute_destination')}, MaxCommute={s.get('max_commute_minutes')}, POIs={s.get('preferred_poi_categories')}, Preset={s.get('ranking_preset')}"
    )
    fb = data["feedback"]
    print(
        f"Feedback: Added={fb.get('added')}, Modified={fb.get('modified')}, Removed={fb.get('removed')}, Preserved={fb.get('preserved')}"
    )
    print(
        f"Total Matches: {data.get('total_matches')}, Items returned: {len(data.get('items', []))}"
    )
    if data.get("items"):
        for itm in data["items"][:3]:
            print(
                f"  - Prop #{itm['property']['id']} ({itm['property']['title']}) | Price={itm['property']['price']} | Score={itm['final_score']} | CommuteDuration={itm.get('commute_duration_minutes')}"
            )
    if data.get("comparison_result"):
        print(f"Comparison: {len(data['comparison_result']['properties'])} properties compared.")
    if data.get("needs_clarification"):
        print(f"Clarification: {data.get('clarification_prompt')}")
    print()
    return data["state"]


def main():
    state: dict = {}
    # Turn 1
    state = run_turn(1, "2 BHK in HSR Layout under 80 lakh", state)
    # Turn 2
    state = run_turn(2, "Only near parks", state)
    # Turn 3
    state = run_turn(3, "Within 30 minutes of Electronic City", state)
    # Turn 4
    state = run_turn(4, "Actually make it 3 BHK", state)
    # Turn 5
    state = run_turn(5, "Remove the budget limit", state)
    # Turn 6
    state = run_turn(6, "Prioritize commute", state)
    # Turn 7
    state = run_turn(7, "Compare the top two", state)
    # Turn 8
    state = run_turn(8, "Start over", state)


if __name__ == "__main__":
    main()
