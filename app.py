#This part is to get data from Google BigQuery

import pandas as pd
from google.cloud import bigquery

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './Labor Statistics Project-27f747351078.json'
client = bigquery.Client()

query_job = client.query("""
    select
    value,predicted_value,date
    from `labor-statistics-project.export_evaluated_examples_bls_sample_data_20190803020030_2019_08_03T13_12_34_235Z.evaluated_examples`""")

result = query_job.result()  # Waits for job to complete.

#Define a sample_data data frame
sample_data=pd.DataFrame(columns=['date','value','predicted_value'],index=range(0,1000))

#Create a counter
i=0

#Load source data into sample_data DataFrame
for row in result:
    sample_data.date[i]=row.date
    sample_data.value[i]=row.value
    sample_data.predicted_value[i]=row.predicted_value
    i=i+1


#Get Row Count of the Data Frame
row_count=sample_data.date.count()

#Review the predicted value JSON format
sample_data.predicted_value[1]

#Function to extract the predicted value from the JSON format
def between(value, a, b):
    # Find and validate before-part.
    pos_a = value.find(a)
    if pos_a == -1: return ""
    # Find and validate after part.
    pos_b = value.rfind(b)
    if pos_b == -1: return ""
    # Return middle part.
    adjusted_pos_a = pos_a + len(a)
    if adjusted_pos_a >= pos_b: return ""
    return value[adjusted_pos_a:pos_b]

#To make sure that the function works
between(str(sample_data.predicted_value[1]),"value': ", "}}")

#Define a Dataframe
df=pd.DataFrame(columns=['Date','Value','Predict_Value'],index=range(0,row_count))

#Load the Date, Actual Value and the Predicted Value into the new dataframe df
for i in range(row_count):
    pv=str(sample_data.predicted_value[i])
    df.Date[i]=sample_data.date[i].strftime('%Y-%m-%d')
    df.Value[i]=sample_data.value[i]
    df.Predict_Value[i]=float(between(pv,"value': ", "}}"))

#Sort DataFrame by date
df =df.sort_values(by=['Date'])

#group the values by Date
df=df.groupby(['Date'], as_index=False)['Value','Predict_Value'].sum()


#Prepare for creating the visualization through flask & chartjs
from flask import Flask, Markup, render_template

app = Flask(__name__)

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

labels = df.Date
value1 = df.Value
value2 = df.Predict_Value

@app.route('/ActualvsPredicted')
def ActualvsPredicted():
        line_labels=labels
        line_value1=value1
        line_value2=value2
        return render_template('ActualvsPredicted.html', title='ActualvsPredicted', labels=line_labels, value1=line_value1, value2=line_value2)

@app.route('/')
def hello():
        return render_template('hello.html', title="Weclome to Leo Song's Project Page")

if __name__ == '__main__':
    app.run(host='localhost', port=8081)
