from google import genai
import os
import requests

client = genai.Client(api_key="AIzaSyC6CrdjUfF9c_u2FdRmzVGV1AWwt2Y6RFk") # get from https://aistudio.google.com/apikey
MIRO_BOARD_ID = "uXjVILQuL70"
MIRO_ACCESS_TOKEN = ""

def get_response(prompt):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response.text.strip()

def extract_opinions(argument):
    prompt = (
        f"Extract the key opinions expressed in the following argument. "
        f"List each opinion as a separate bullet point:\n\n"
        f"{argument}\n\n"
        f"Opinions:"
    )
    return get_response(prompt)

def match_opinions(opinions1, opinions2):
    prompt = (
        "You are given two sets of opinions extracted from opposing debate arguments.\n\n"
        "First argument opinions:\n"
        f"{opinions1}\n\n"
        "Second argument opinions:\n"
        f"{opinions2}\n\n"
        "Match together opinions that share significant conceptual overlap. "
        "For each matching pair, provide a brief explanation of the overlap. "
        "List each matched pair with its explanation as a separate bullet point like so: * 'opinion1', 'opinion2', explanation"
    )
    return get_response(prompt)

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

def create_miro_bubble(opinion, x, y, board_id, access_token):
    url = f"https://api.miro.com/v2/boards/{board_id}%3D/sticky_notes"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {access_token}"
    }
    payload = {
        "data": {
            "content": opinion,
            "shape": "square"
        },
        "style": {
            "fillColor": "light_yellow",
            "textAlign": "center",
            "textAlignVertical": "middle"
        },
        "position": {
            "x": x,
            "y": y
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

if __name__ == "__main__":
    print("Enter the argument for the first stance in the debate:")
    argument1 = input("> ")
    print("\nEnter the argument for the opposing stance in the debate:")
    argument2 = input("> ")
    
    print("\nExtracting opinions from the first argument...")
    opinions_text1 = extract_opinions(argument1)
    print("\nOpinions from argument 1:")
    print(opinions_text1)
    
    print("\nExtracting opinions from the second argument...")
    opinions_text2 = extract_opinions(argument2)
    print("\nOpinions from argument 2:")
    print(opinions_text2)

    print("\nMatching opinions that share conceptual overlap...")
    matched_opinions = match_opinions(opinions_text1, opinions_text2)
    matched_opinions_list = parse_bullets(matched_opinions)
    print("\nMatched Opinions:")
    for match in matched_opinions_list:
        print(match)

    opinions_list1 = parse_bullets(opinions_text1)
    opinions_list2 = parse_bullets(opinions_text2)
    opinion_positions = cluster_opinions(opinions_list1, opinions_list2)
    print("\nCreating Miro whiteboard bubbles for each opinion...")
    for opinion, (x, y) in opinion_positions.items():
        result = create_miro_bubble(opinion, x, y, MIRO_BOARD_ID, MIRO_ACCESS_TOKEN)
        # print(f"Created bubble for opinion '{opinion}' at ({x}, {y}): {result}")

    print("\nWhiteboard generation complete")