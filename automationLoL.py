import psutil
import requests
import urllib3
import time
import base64
import json
import os
urllib3.disable_warnings()

def get_config_path():
    if getattr(sys, 'frozen', False):
        # Si c'est un .exe (pyinstaller)
        script_dir = os.path.dirname(sys.executable)
    else:
        # Si c'est un .py
        script_dir = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(script_dir, "config.json")

def load_config():
    config_path = get_config_path()
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erreur: {config_path} non trouvé")
        return {"pick_id": [38], "ban_id": [238]}

def get_lcu_credentials():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['name'] == 'LeagueClientUx.exe':
            cmdline = proc.info['cmdline']
            port = None
            token = None
            for arg in cmdline:
                if '--app-port=' in arg:
                    port = arg.split('=')[1]
                if '--remoting-auth-token=' in arg:
                    token = arg.split('=')[1]
            return port, token
    return None, None

def get_gameflow_phase(port, token):
    url = f"https://127.0.0.1:{port}/lol-gameflow/v1/gameflow-phase"
    response = requests.get(url, auth=('riot', token), verify=False)
    return response.json()

def accept_match(port, token):
    url = f"https://127.0.0.1:{port}/lol-matchmaking/v1/ready-check/accept"
    response = requests.post(url, auth=("riot", token), verify=False)
    if response.status_code == 200:
        print("Match accepté !")
    else:
        print(f"Erreur : {response.status_code}")

def monitor_gameflow(port, token):
    last_phase = None
    while True:
        phase = get_gameflow_phase(port, token)

        if phase != last_phase:
            last_phase = phase
            print(f"Phase actuelle : {phase}")
        
        if phase == "ReadyCheck":
            accept_match(port, token)
        elif phase == "ChampSelect":
            print("Champion select !")
            return

        time.sleep(1)
    
def get_session(port, token): 
    url = f"https://127.0.0.1:{port}/lol-champ-select/v1/session"
    response = requests.get(url, auth=("riot", token), verify=False)
    return response.json()

def hover_champion(port, headers, champion_id, action_id):
    url = f"https://127.0.0.1:{port}/lol-champ-select/v1/session/actions/{action_id}"
    data = {
        "championId": champion_id,
        "actionId": action_id,
        "completed": False
    }
    response = requests.patch(url, headers=headers, json=data, verify=False)
    return response.status_code

def ban_champion(port, headers, champion_id, action_id):
    url = f"https://127.0.0.1:{port}/lol-champ-select/v1/session/actions/{action_id}"
    data = {
        "championId": champion_id,
        "completed": True
    }
    response = requests.patch(url, headers=headers, json=data, verify=False)
    print(f"Ban response: {response.status_code} | {response.text}")
    return response.status_code

def lock_champion(port, headers, champion_id, action_id):
    url = f"https://127.0.0.1:{port}/lol-champ-select/v1/session/actions/{action_id}"
    data = {
        "championId": champion_id,
        "actionId": action_id,
        "completed": True
    }
    response = requests.patch(url, headers=headers, json=data, verify=False)
    return response.status_code

def get_champ_select_session(port, headers):
    url = f"https://127.0.0.1:{port}/lol-champ-select/v1/session"
    response = requests.get(url, headers=headers, verify=False)
    if response.text == "" or response.status_code != 200:
        return None
    return response.json()

def get_available_pick(port, headers, pick_ids):
    session = get_champ_select_session(port, headers)
    banned = []
    for action_group in session["actions"]:
        for action in action_group:
            if action["type"] == "ban" and action["completed"]:
                banned.append(action["championId"])
    
    for champ_id in pick_ids:
        if champ_id not in banned:
            return champ_id
    return pick_ids[0]

def get_available_ban(port, headers, ban_ids):
    session = get_champ_select_session(port, headers)
    already_banned = []
    for action_group in session["actions"]:
        for action in action_group:
            if action["type"] == "ban" and action["completed"]:
                already_banned.append(action["championId"])

    for champ_id in ban_ids:
        if champ_id not in already_banned:
            return champ_id
    return ban_ids[0]

def main():
    # Charge la config depuis config.json
    config = load_config()
    pick_ids = config.get("pick_id", [38])
    ban_ids = config.get("ban_id", [238])
    
    # Récupère les credentials League Client
    port, token = get_lcu_credentials()
    if port is None or token is None:
        print("League Client non trouvé")
        return
    
    # Encode le token en base64 pour l'authentification
    token_b64 = base64.b64encode(f"riot:{token}".encode()).decode()
    headers = {
        "Authorization": f"Basic {token_b64}",
        "Content-Type": "application/json"
    }

    while True:
        monitor_gameflow(port, token)

        # Gère pick/ban
        ban_done = False
        pick_done = False
        hover_done = False
        last_states = {}
        dernier_etat = None

        while not ban_done or not pick_done:
            session = get_champ_select_session(port, headers)
            if session is None:
                hover_done = False
                ban_done = False
                pick_done = False
                time.sleep(1)
                continue

            local_cell_id = session["localPlayerCellId"]

            # Savoir dans quelle phase on est 
            timer = session.get("timer", {})
            phase = timer.get("phase", "")
            etat_actuel = timer
            if etat_actuel != dernier_etat:
                dernier_etat = etat_actuel
                print(f"Phase timer: {phase}")

            for action_group in session["actions"]:
                for action in action_group:
                    if action["actorCellId"] == local_cell_id:
                        current_state = f"{action['type']}|{action['isInProgress']}|{action['completed']}"
                        action_id = action["id"]
                        if current_state != last_states.get(action_id):
                            print(f"TYPE: {action['type']} | isInProgress: {action['isInProgress']} | completed: {action['completed']}")
                            last_states[action_id] = current_state

                        # BAN
                        if action["type"] == "ban" and action['isInProgress'] and not ban_done and phase == "BAN_PICK":
                            actual_ban_id = get_available_ban(port, headers, ban_ids)
                            ban_champion(port, headers, actual_ban_id, action["id"])
                            ban_done = True
                            print(f"Champion {actual_ban_id} banni !")

                        # PICK HOVER
                        if action["type"] == "pick" and not hover_done:
                            actual_pick_id = get_available_pick(port, headers, pick_ids)
                            hover_champion(port, headers, actual_pick_id, action["id"])
                            hover_done = True

                        # PICK LOCK
                        if action["type"] == "pick" and action["isInProgress"] and not pick_done:
                            actual_pick_id = get_available_pick(port, headers, pick_ids)
                            lock_champion(port, headers, actual_pick_id, action["id"])
                            pick_done = True
                            print(f"Champion {actual_pick_id} sélectionné !")

            time.sleep(1)

if __name__ == "__main__":
    import sys
    main()
