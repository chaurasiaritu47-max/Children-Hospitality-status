import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("HHS_Unaccompanied_Alien_Children_Program.csv")
df= df.rename(columns={"Children apprehended and placed in CBP custody*": "CBP_Intake","Children in CBP custody":"CBP_Custody","Children transferred out of CBP custody":"CBP_to_HHS","Children in HHS Care":"HHS_custody","Children discharged from HHS Care":"HHS_Discharged"})
df['HHS_custody'] = df['HHS_custody'].str.replace(',', '').astype(float)
df['Date'] = pd.to_datetime(df['Date'])
sns.heatmap(df.corr(), annot=True, cmap='coolwarm')
plt.title("Correlation Heatmap", fontsize=14, color='brown')
plt.xticks(rotation=0)
plt.show()

df.boxplot(figsize=(12,6), color='brown')
plt.xticks(rotation=0)
plt.show()


print("Data\n:",df.head(10))

print("data type of the data\n:",df.info())

print("statistical summary:\n",df.describe())

print("shape of the data:\n",df.shape)

#pipeline flow analysis
df = df.sort_values('Date')
pipeline_cols = ['CBP_Intake', 'CBP_to_HHS', 'HHS_Discharged']
print('pipeline flow:\n', df[pipeline_cols].head())


plt.figure(figsize=(12,6))
plt.plot(df['Date'], df['CBP_Intake'], label='Intake (Entry)')
plt.plot(df['Date'], df['CBP_to_HHS'], label='Transfer to HHS')
plt.plot(df['Date'], df['HHS_Discharged'], label='Discharge (Exit)')

plt.legend()
plt.title("Care Pipeline Flow", fontsize=14, color='brown')
plt.xlabel("Date", fontsize=12, color='brown')
plt.ylabel("Children Count", fontsize=12, color='brown')
plt.show()


# Transfer Efficiency Metrics
Transfer_Efficiency= df['CBP_to_HHS'] / df['CBP_Intake']
Discharge_Effectiveness = df['HHS_Discharged'] / df['HHS_custody']
Throughput_Rate= df['HHS_Discharged'] / df['CBP_Intake']

plt.figure(figsize=(12,6))
plt.plot(df['Date'],Transfer_Efficiency, label='Transfer Efficiency')
plt.plot(df['Date'],Discharge_Effectiveness, label='Discharge Effectiveness')
plt.legend()
plt.title("Efficiency Metrics Over Time", fontsize=14, color='brown')
plt.xlabel("Date", fontsize=12, color='brown')
plt.ylabel("Efficiency",fontsize=12, color='brown')
plt.show()

#Delay and Backlog Analysis
Net_Flow = df['CBP_Intake'] - df['HHS_Discharged']
Backlog = df['CBP_Custody'] + df['HHS_custody']

plt.figure(figsize=(12,6))
plt.plot(df['Date'], Net_Flow, label='Net Flow')
plt.axhline(0, linestyle='--', color='red')
plt.title("Backlog / Imbalance Detection", fontsize=14, color='brown')
plt.xlabel("Date", fontsize=12, color='brown')
plt.ylabel("Net Flow (Intake - Discharged)", fontsize=12, color='brown')
plt.legend()
plt.show()



#Seasonal and Temporal Patterns
df['Day'] = df['Date'].dt.day_name()
weekday_avg = df.groupby('Day').apply(lambda x: (x['CBP_to_HHS'] / x['CBP_Intake']).mean())
weekday_avg.plot(kind='bar', figsize=(10,5))
plt.title("Weekday vs Weekend Efficiency", fontsize=14, color='brown')
plt.xlabel("Day of Week", fontsize=12, color='brown')
plt.ylabel("Average Transfer Efficiency", fontsize=12, color='brown')
plt.xticks(rotation=0)
plt.show()

df['Month'] = df['Date'].dt.to_period('M')
monthly_trend = df.groupby('Month')['HHS_Discharged'].sum()
monthly_trend.plot(figsize=(12,5))
plt.title("Monthly Discharge Trend", fontsize=14, color='brown')
plt.xlabel("Month", fontsize=12, color='brown')
plt.ylabel("Total Discharges", fontsize=12, color='brown')
plt.show()

#Stagnation Detection
Rolling_Discharge = df['HHS_Discharged'].rolling(7).mean()
plt.figure(figsize=(12,6))
plt.plot(df['Date'], df['HHS_Discharged'], label='Daily')
plt.plot(df['Date'], Rolling_Discharge, label='7-day Avg')
plt.legend()
plt.title("Stagnation Detection", fontsize=14, color='brown')
plt.xlabel("Date", fontsize=12, color='brown')
plt.ylabel("Discharges", fontsize=12, color='brown')
plt.show()

# sudden drop detection
Drop_Flag = df['HHS_Discharged'] < (Rolling_Discharge * 0.5)
print("drop\n",Drop_Flag.head())


plt.figure(figsize=(12,6))
plt.plot(df['Date'], df['HHS_Discharged'], label='Discharge')
plt.scatter(df['Date'], df['HHS_Discharged'], c= Drop_Flag, label='Drops')
plt.legend()
plt.title("Outcome Stability & Sudden Drops", fontsize=14, color='brown')
plt.xlabel("Date", fontsize=12, color='brown')
plt.ylabel("Discharges", fontsize=12, color='brown')
plt.show()

df.drop(columns=['Day', 'Month'], inplace=True)

df.info()
df.to_csv("HHS_Analysis_Output.csv", index=False)


