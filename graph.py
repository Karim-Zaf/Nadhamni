from langgraph.graph import StateGraph
from nodes import CurrentApp, capture_app, check_presence, classify, update_score, update_distraction, send_alert, log_and_wait, router


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



