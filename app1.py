from flask import Flask,render_template,request,Markup
import pickle
import numpy as np
import pandas as pd
from static.fertilizer_data import fertilizer_dict
import requests,json

def find_weather(city):
    api_key = "3c1cc89ee899fb2f93b2407c36cdf0a8"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    city_name = city
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    print("bfr res")
    response = requests.get(complete_url)
    print("hey after res")
    x = response.json()
    if x["cod"] != "404":
        y = x["main"]
        curr_temperature = y["temp"]-273
        curr_humidity = y["humidity"]
        print("val returned")
        return (curr_temperature,curr_humidity)
    else:
        return None



app = Flask(__name__)



@app.route("/")
def HomePage():
    #return render_template("fertilizer_recommend.html")
    #return render_template("crop_recommend2.html")
    return render_template("HomePage.html")

@app.route("/fertilizer")
def fertilizer_search():
    return render_template('fertilizer_recommend.html')

@app.route("/crop")
def crop_search():
    return render_template('crop_recommend2.html')


@app.route("/crop_predict",methods=["POST"])
def crop_prediction():
    if request.method=='POST':
        n = int(request.form["N"])
        print(n)
        p=int(request.form["P"])
        k=int(request.form["K"])
        city=str(request.form['city'])
        #temp=float(request.form["temp"])
        #humidity=float(request.form["humidity"])
        ph=float(request.form["ph"])
        rainfall=float(request.form["rainfall"])
        print(city)
        weather = find_weather(city)
        if weather:
            print("hiiiii")
            temp = weather[0]
            humidity = weather[1]
        else:
            print("shittt")
            return "Enter valid city name"
    param_list=[]
    input_params=[n,p,k,temp,humidity,ph,rainfall]
    param_list.append(input_params)
    np_params = np.array(param_list)
    crop_model = pickle.load(open("model.pkl", "rb"))
    crop=crop_model.predict(np_params)
    predict_crop=Markup(crop[0])
    return predict_crop
    #return render_template("crop_recommend2.html",return_crop=predict_crop)

@app.route("/fertilizer_predict", methods=["POST"])
def fertilizer_recommend1():
    df = pd.read_csv("static/mydata.csv")
    crop = str(request.form['crop'])
    n_req = df[df['Crop'] == crop]['N'][0]
    p_req = df[df['Crop'] == crop]['P'][0]
    k_req = df[df['Crop'] == crop]['K'][0]
    n = int(request.form["N"])
    p = int(request.form["P"])
    k = int(request.form["K"])
    n_diff,p_diff,k_diff = abs(n_req-n),abs(p_req-p),abs(k_req-k)
    maximum = max([n_diff,p_diff,k_diff])
    key = ''
    if maximum == n_diff:
        key = 'NHigh' if n_req<n else 'NLow'
    elif maximum==p_diff:
        key = 'PHigh' if p_req<p else 'PLow'
    else:
        key = 'KHigh' if k_req<k else 'KLow'
    desc=Markup(fertilizer_dict[key])
    return render_template("fertilizer_suggestion.html",description=desc)


if __name__ == "__main__":
    app.run()