import os
from typing import TypedDict
import time
import psutil
from dotenv import load_dotenv
from groq import Groq
from langgraph.graph import StateGraph
import cv2
from plyer import notification


# JOUR2 Classification 
categories = {
    "cursor": "productif",
    "code": "productif",
    "firefox": "neutre",
    "spotify": "neutre",
    "instagram": "distraction",
    "tiktok": "distraction",
    
}

historique_global = []
class CurrentApp (TypedDict) :
    current_app : str
    iteration : int 
    category : str 
    score : int 
    presence : str 
    distraction_streak : int 
    historique : list [str]


def capture_app(state: CurrentApp) -> dict:
    # Récupère les process qui utilisent le plus de CPU
    procs = []
    for proc in psutil.process_iter(['name', 'cpu_percent']):
        try:
            info = proc.info
            if info['cpu_percent'] and info['cpu_percent'] > 0:
                procs.append(info)
        except:
            pass
    
    # Trie par CPU et prend le top
    procs.sort(key=lambda x: x['cpu_percent'], reverse=True)
    app_name = procs[0]['name'] if procs else "unknown"


    state["current_app"]= app_name
    state["iteration"]+= 1
    return {"current_app": state["current_app"], "iteration": state["iteration"]}  # retourne SEULEMENT ce qui change

def log_and_wait (state : CurrentApp) -> dict :
    current_app = state["current_app"]
    iteration = state["iteration"]
    category = state["category"]
    score = state ["score"]
    presence = state["presence"]

    resultat_log = f"[iter{ iteration }   ] APP : { current_app } | {category} | {score} | {presence}"
    print (resultat_log)
    
    time.sleep(3)
    
    historique = state["historique"].copy()
    historique.append(resultat_log)
    historique_global.append(resultat_log)
    return{"historique":historique}

def router (state: CurrentApp) -> dict : 
    return "capture"


#Part 2 : classifying used software 
def classify (state : CurrentApp) :
    current_app = state["current_app"]
    state["category"]= categories.get(current_app,"neutre")
    return {"category" : state["category"]}

def update_score ( state : CurrentApp) : 
    category = state["category"]
    presence = state ["presence"]
    if ( presence =="present" and category == "productif"): 
        state["score"]+= 2
    if ( presence =="present" and category == "distraction"): 
        state["score"]-= 3
    if (presence =="distracted" and category == "productif"): 
        state["score"]+= 1
    if (presence =="distracted" and category == "distraction"): 
        state["score"]-= 3
    return {"score": state["score"]}

#part3 webcam 
def check_presence (state : CurrentApp) :
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_eye.xml')

    video = cv2.VideoCapture(0)
    ok, image = video.read()
    video.release()

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    visage = face_cascade.detectMultiScale(gray)
    yeux = eye_cascade.detectMultiScale(gray)

    # print(f"Visages: {len(visage)}, Yeux: {len(yeux)}")
    presence ="absent"
    if (len(visage) > 0 and len(yeux) > 0 ) :
        presence = "present"
    elif ( len(visage) > 0 or len(yeux) >0 ):
        presence = "distracted"
    
    return {"presence" : presence}

#step 4 desktop alert when too much distracted 
def update_distraction (state : CurrentApp ) : 
    if (state["category"]=="distraction" or state["presence"]=='distracted') :
        return {"distraction_streak":state["distraction_streak"]+1}
    return {"distraction_streak":0}

def send_alert (state : CurrentApp) : 
    if ( state["distraction_streak"]>=3) : 
        notification.notify(
            title="Nadhamni — Alerte",
            message=f"Tu es en distraction depuis {state['distraction_streak']} cycles !",
            timeout=5
        )
    return {}


#step5 integrating LLM
def LLM_answer (system_prompt: str, user_prompt : str) :
    load_dotenv()

    groq_key = os.getenv("GROQ_API_KEY")

    client = Groq(api_key=groq_key)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content

def generate_report () :
    if not historique_global:
        print("Pas assez de données pour générer un rapport.")
        return

    system_prompt = """Tu es un coach de productivité. Analyse les logs d'activité et génère un rapport en français.
Structure ton rapport ainsi :
- Résumé global (1-2 phrases)
- Stats clés (% productif, % distrait, % absent, score final)
- Top apps utilisées
- Conseil personnalisé pour demain"""

    logs_text = "\n".join(historique_global)
    user_prompt = f"Voici mes logs de session ({len(historique_global)} cycles) :\n{logs_text}"

    print("\n📊 === RAPPORT DE PRODUCTIVITÉ === 📊\n")
    summary = LLM_answer(system_prompt, user_prompt)
    print(summary)

graph = StateGraph(CurrentApp) # ou peut etre StateGraph({})
graph.add_node ("capturer_app",capture_app)
graph.add_node ("check_presence",check_presence)
graph.add_node ("classify", classify)
graph.add_node ("update_score",update_score)
graph.add_node("update_distraction",update_distraction)
graph.add_node ("send_alert", send_alert)
graph.add_node ("attente",log_and_wait)

graph.add_conditional_edges("attente", router, {"capture": "capturer_app"}) #for the loop

graph.add_edge("capturer_app","check_presence")
graph.add_edge("check_presence","classify")
graph.add_edge("classify","update_score")
graph.add_edge("update_score","update_distraction")
graph.add_edge("update_distraction","send_alert")
graph.add_edge("send_alert","attente")
graph.set_entry_point("capturer_app")
app = graph.compile()

try :
    app.invoke({"current_app": "Premiere Pro", "iteration": 1, "category":"neutre", "score" : 0, "presence":"absent", "distraction_streak":0 , "historique":[]}) # les premiers states sont obligatoires
except KeyboardInterrupt : 
    generate_report()


