import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import numpy as np
import time
import plotly.graph_objects as go

st.set_page_config(page_title="Children Hospitality Analysis Dashboard", page_icon="👶", layout="wide")

st.markdown("""
<style>
.stApp {
    background-color: #121212;     /* black background */
}
h1 {   
    color: #3F7BD6 !important;     \* purple title color */
    font-weight: 700;
    font-size: 36px;
    text-align: center;        
}

[data-testid="stSidebar"] {
    background-color: #0A192F; 
}

[data-testid="stMetricValue"] {
    color: #1a237e !important;   \* purple kpi values */
    font-size: 20px;
    white-space: normal !important;
}

[data-testid="stMetricLabel"] {
    color: #5E195E !important;            /* indigo kpi labels */
    font-size: 20px !important;
    
    
}

div[data-testid="stMetric"] {
    background-color: #f0f8ff;
    border: 2px solid #4B2E2B;   /* kpi border */
    padding: 12px;
    border-radius: 5px;
    text-align: center;
    
}

label[data-testid="stWidgetLabel"] {
    color: #00FFFF !important;   
    font-weight: bold;
}


</style>
""", unsafe_allow_html=True)

df= pd.read_csv("HHS_Analysis_Output.csv")
filtered_df = df.copy()
filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])
st.title("💊 Care Transition Efficiency & Placement Outcome Analytics")

#filters
st.sidebar.markdown("<h2 style='color:#568DCB; font-weight: 700; font-size: 24px;'>📋 Filters</h2>", unsafe_allow_html=True) 

start_date = st.sidebar.date_input("Start Date", filtered_df['Date'].min())
end_date = st.sidebar.date_input("End Date", filtered_df['Date'].max())

# i. date filtering from start and end date
filtered_df = filtered_df[(filtered_df['Date'] >= pd.to_datetime(start_date)) & (filtered_df['Date'] <= pd.to_datetime(end_date))]


st.sidebar.markdown("""<div style='color:#69D177; font-size:15px;margin-top:30px;'><p>This Analytics project focuses on analyzing the operational effectiveness of the UAC (Unaccompanied Children) Program.</p><b>📌 Care Pipeline:</b><br><br>• CBP(Customs and Border Protection) apprehension & custody<br>• Transfer to HHS(Health and Human Services) care<br>• Medical screening & case management<br> • Discharge & reunification</div>""",unsafe_allow_html=True)  

# KPIs
transfer_efficiency = filtered_df['CBP_to_HHS'] / filtered_df['CBP_Custody']
discharge_effectiveness = filtered_df['HHS_Discharged'] / filtered_df['HHS_custody']
pipeline_throughput = filtered_df['HHS_Discharged'] / filtered_df['CBP_Intake'].replace(0, np.nan)
backlog = filtered_df['CBP_Custody'] + filtered_df['HHS_custody']


Rolling_Discharge = filtered_df['HHS_Discharged'].rolling(7).mean()  
Rolling_Std = filtered_df['HHS_Discharged'].rolling(7).std()
Outcome_Stability_Score = 1 / (1 + Rolling_Std)

transfer_eff = transfer_efficiency.mean()
discharge_eff = discharge_effectiveness.mean()
throughput = pipeline_throughput.mean()
backlog_rate = backlog.mean()
stability_score = Outcome_Stability_Score.mean()

col1, col2, col3, col4, col5 = st.columns(5)

# Display KPIs
with col1:
    st.metric("Transfer Efficiency", f"{transfer_eff*100:.1f}%")

with col2:
    st.metric("Discharge Effectiveness", f"{discharge_eff*100:.1f}%")

with col3:
    st.metric("Throughput Rate", f"{throughput*100:.1f}%")

with col4:
    st.metric("Backlog Rate", f"{backlog_rate*100:.1f}%")

with col5:
    st.metric("Stability Score", f"{stability_score:.2f}")

# alerts 
alert_placeholder = st.empty()
high_backlog = backlog.iloc[-1] 
low_transfer_eff = transfer_efficiency.iloc[-1]

if high_backlog > 0.5:
    alert_placeholder.warning(f"⚠️ High backlog detected in selected period: {high_backlog:.2f}")
    time.sleep(3)  # show for 3 seconds
    alert_placeholder.empty()  # remove alert

if low_transfer_eff < 0.5:
    alert_placeholder.warning(f"⚠️ Low transfer efficiency detected: {low_transfer_eff:.2f}")
    time.sleep(3)  # show for 3 seconds
    alert_placeholder.empty()  # remove alert

# metric selection

metric = st.selectbox("Select Metric (Over Time)",["transfer_efficiency", "discharge_effectiveness", "pipeline_throughput"])

fig,ax=plt.subplots(figsize=(12,5))

if metric == "transfer_efficiency":
    plt.plot(filtered_df['Date'], transfer_efficiency, color="#0C82BC")
elif metric == "discharge_effectiveness":
    plt.plot(filtered_df['Date'], discharge_effectiveness, color='#0C82BC')
else:
    plt.plot(filtered_df['Date'], pipeline_throughput, color="#0C82BC")

ax.grid(True, linestyle='--', alpha=0.5)
ax.set_facecolor('#121212')
fig.patch.set_facecolor('#121212')
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
st.pyplot(fig)


col1, col2 = st.columns([1,2])
with col1:
    # Take total values (or use latest: .iloc[-1])
    intake = filtered_df['CBP_Intake'].sum()
    discharged = filtered_df['HHS_Discharged'].sum()

    values = [intake, discharged]
    labels = ['Intake', 'Discharged']
    total = sum(values)
    intake_pct = values[0] / total * 100
    discharge_pct = values[1] / total * 100
    
    fig = go.Figure(data=[go.Pie(labels=labels,values=values,hole=0.6,textinfo='label',hoverinfo='label+percent',marker=dict(colors=["#3388c5", "#d555e4"]))])
    fig.update_layout(paper_bgcolor="#121212",font=dict(color='white'),legend=dict(font=dict(color='white')))
    st.plotly_chart(fig, use_container_width=True)

    
with col2:
    fig, ax = plt.subplots(figsize=(20,10)) #stackplot used to show stacked area
    ax.stackplot(filtered_df['Date'],filtered_df['CBP_Custody'],filtered_df['HHS_custody'],labels=['CBP Custody', 'HHS Custody'], colors=["#1E22FF", '#4BDE3E'], alpha=0.8)
    ax.set_title("CBP vs HHS Custody Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Children Count")

    ax.legend(facecolor='#121212', labelcolor='white', edgecolor='#121212',fontsize=20)
    ax.tick_params(axis='x', rotation=45, colors='white', labelsize=20)
    ax.tick_params(axis='y', colors='white', labelsize=20)
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#121212')
    st.pyplot(fig)


col1 = st.columns(1)
with col1[0]:
    #st.subheader("Outcome Stability Trend")

    fig, ax = plt.subplots(figsize=(12,5))
    ax.bar(filtered_df['Date'],filtered_df['HHS_Discharged'],label='Daily Discharge',color="#CB3E25")

    ax.bar(filtered_df['Date'],Rolling_Discharge,bottom=filtered_df['HHS_Discharged'],label='7-day Avg Discharge', color="#E357E5")

    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_facecolor('#121212')
    fig.patch.set_facecolor('#121212')
    ax.set_xlabel("Date", color='white')
    ax.set_ylabel("Discharge Count", color='white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.legend(facecolor='#121212', labelcolor='white', edgecolor='#121212') 
    st.pyplot(fig)


col1 = st.columns(1)
with col1[0]:
    #st.subheader("Care Pipeline Flow")

    fig, ax = plt.subplots(figsize=(12,5))

    ax.plot(filtered_df['Date'], filtered_df['CBP_Intake'], label='Intake', color="#2a8e88")
    ax.plot(filtered_df['Date'], filtered_df['CBP_to_HHS'], label='Transfer', color="#3697F7")
    ax.plot(filtered_df['Date'], filtered_df['HHS_Discharged'], label='Discharge', color="#F36B53")
    ax.set_title("Care Pipeline Flow")        
    ax.set_xlabel("Date", color="white")
    ax.set_ylabel("Children Count", color="white")
    ax.legend(facecolor='#121212', labelcolor='white', edgecolor='#121212')
    ax.tick_params(axis='x', rotation=45, colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.grid(True, linestyle='--', alpha=0.5)
    fig.patch.set_facecolor('#121212')     # chart background
    ax.set_facecolor('#121212')
    st.pyplot(fig)


col1 = st.columns(1)
with col1[0]:
    #st.subheader("Bottleneck Detection")
    net_flow = filtered_df['CBP_Intake'] - filtered_df['HHS_Discharged']
    fig,ax=plt.subplots(figsize=(12,5))
    ax.scatter(filtered_df['Date'], net_flow, label='Net Flow',color="#65B41B")
    ax.set_xlabel("Date", color='white')
    ax.set_ylabel("Net Flow", color='white')
    ax.axhline(0, linestyle='--', color='deeppink', label='Zero Net Flow')
    ax.legend(facecolor='#121212', labelcolor='white', edgecolor="#121212")
    ax.set_facecolor('#121212')
    fig.patch.set_facecolor('#121212')
    ax.tick_params(axis='x', rotation=45, colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig)


col1 = st.columns(1)
with col1[0]:
   # st.subheader("Efficiency Trends")

    fig,ax =plt.subplots(figsize=(12,5))
    ax.plot(filtered_df['Date'], transfer_efficiency, label='Transfer Efficiency', color="#5E87E1")
    ax.plot(filtered_df['Date'], discharge_effectiveness, label='Discharge Effectiveness', color="#D940DC")
    ax.set_title("Efficiency Trends Over Time")    
    ax.set_xlabel("Date", color='white')
    ax.set_ylabel("Efficiency", color='white')
    ax.legend(facecolor='#121212', labelcolor='white', edgecolor='#121212')
    ax.tick_params(axis='x', rotation=45, colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_facecolor('#121212')
    fig.patch.set_facecolor('#121212')
    st.pyplot(fig)




