import streamlit as st
import plotly.express as px
from database import get_all_sessions, get_all_cycles


st.title("Nadhamni Dashboard")
sessions = get_all_sessions() 
cycles = get_all_cycles()


col1, col2, col3 = st.columns(3)
col1.metric("Sessions", len(sessions))
col2.metric("Cycles", len(cycles))
col3.metric("Score moyen", round(cycles["score"].mean(),1))


st.subheader("Category Repartitions")
category_counts= cycles["category"].value_counts().reset_index()
category_counts.columns = ["category", "count"]
fig = px.pie(category_counts, values="count", names="category")
st.plotly_chart(fig)


st.subheader("Top Apps")
top_apps = cycles["app_name"].value_counts().head(10).reset_index()
top_apps.columns = ["app_name", "count"]
fig2 = px.bar(top_apps, x="app_name", y="count")
st.plotly_chart(fig2)


st.subheader("Historique des sessions")
st.dataframe(sessions.tail(10))

