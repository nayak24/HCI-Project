import os
import requests
from google import genai
from dotenv import load_dotenv
import time

load_dotenv()

client = genai.Client(api_key="AIzaSyC6CrdjUfF9c_u2FdRmzVGV1AWwt2Y6RFk")


def get_response(prompt):
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt,
    )
    time.sleep(0.1)
    return response.text.strip()


def extract_opinions(argument):
    prompt = (
        f"Extract the key opinions expressed in the following argument. "
        f"List each opinion as a separate bullet point:\n\n"
        f"{argument}\n\n"
        f"Opinions:"
    )
    time.sleep(0.1)
    return get_response(prompt)


def match_opinions(opinions1, opinions2):
    """
    Given two lists (or newline-joined strings) of opinions, asks the LLM to match them,
    then returns a list of (opinion1, opinion2, explanation) tuples.
    """
    prompt = (
        "You are given two sets of opinions extracted from opposing debate arguments.\n\n"
        "First argument opinions:\n"
        f"{opinions1}\n\n"
        "Second argument opinions:\n"
        f"{opinions2}\n\n"
        "Match together opinions that share significant conceptual overlap. "
        "For each matching pair, provide a brief explanation of the overlap. "
        "List each matched pair with its explanation as a separate bullet point like so:\n"
        "* 'opinion1', 'opinion2', explanation"
    )

    raw = get_response(prompt)

    matches = []
    for line in raw.splitlines():
        line = line.strip()
        # accept bullets starting *, - or •
        if not line or line[0] not in ("*", "-", "•"):
            continue
        # strip the bullet marker and any surrounding whitespace/quotes
        content = line.lstrip("*-•").strip()
        # split into exactly three parts: opinion1, opinion2, explanation
        parts = [p.strip(" '\"") for p in content.split(",", 2)]
        if len(parts) == 3:
            matches.append((parts[0], parts[1], parts[2]))
    time.sleep(0.1)
    return matches

def parse_bullets(text):
    bullets = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("-") or line.startswith("•") or line.startswith("*"):
            point = line.lstrip("-•*").strip()
            if point:
                bullets.append(point)
    return bullets


def cluster_opinions(opinions_list1, opinions_list2):
    cluster0 = opinions_list1
    cluster1 = opinions_list2

    clusters = {}
    spacing_x = 220
    spacing_y = 200
    base_x0 = 0
    base_x1 = 950

    for i, opinion in enumerate(cluster0):
        col = i % 3
        row = i // 3
        x = base_x0 + col * spacing_x
        y = row * spacing_y
        clusters[opinion] = (x, y)

    for i, opinion in enumerate(cluster1):
        col = i % 3
        row = i // 3
        x = base_x1 + col * spacing_x
        y = row * spacing_y
        clusters[opinion] = (x, y)

    return clusters

def build_graph(matches):
    """
    Turn matched (op1,op2,ex) tuples into nodes+links.
    Adds groupIndex so we can space them vertically.
    """
    nodes_map = {}
    counts = {0:0, 1:0}

    for a, b, ex in matches:
        # left‐side node = group 0
        if a not in nodes_map:
            nodes_map[a] = {
                "id": a, "group": 0,
                "groupIndex": counts[0]  # 0,1,2...
            }
            counts[0] += 1
        # right‐side node = group 1
        if b not in nodes_map:
            nodes_map[b] = {
                "id": b, "group": 1,
                "groupIndex": counts[1]
            }
            counts[1] += 1

    # convert map → list
    nodes = list(nodes_map.values())
    # one link per match
    links = [{"source": a, "target": b, "explanation": ex} for a,b,ex in matches]

    return nodes, links

