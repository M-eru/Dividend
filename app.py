from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta, date
import requests
import pandas
from bs4 import BeautifulSoup

app = Flask(__name__, template_folder="templates")


def query():
    dict = {}
    data = requests.get("https://www.dividends.sg/")
    soup = BeautifulSoup(data.text, "html.parser")
    for link in soup.find_all('a', {'target': '_blank'}):
        title = link.get('title')
        stats = link.get('href')
        if title != "" and title != None:
            dict[title] = stats
    return dict


def process(dict, name):
    for key in dict:
        if key == name:
            d = {}
            y = {}
            years = []
            count = 0
            data = requests.get(f"https://www.dividends.sg{dict[key]}")
            soup = BeautifulSoup(data.text, "html.parser")
            for data in soup.find_all('td', {'class': None, 'rowspan': None, 'vertical-align': None}):
                value = data.text.strip()
                if 'SGD' in value:
                    d[count] = {}
                    d[count]["status"] = "False"
                    d[count]["amount"] = value
                    d[count]["value"] = float(value[3:])
                elif value == '-':
                    d[count] = {}
                    d[count]["status"] = "False"
                    d[count]["amount"] = value
                    d[count]["value"] = 0
                else:
                    dt = datetime.strptime(value, '%Y-%m-%d')
                    d[count]["year"] = dt.year
                    d[count]["date"] = value
                    if dt.year not in y:
                        years.append(dt.year)
                        y[dt.year] = {}
                        y[dt.year]["status"] = "False"
                        y[dt.year]["value"] = d[count]["value"]
                        y[dt.year]["count"] = 1
                    else:
                        y[dt.year]["value"] += d[count]["value"]
                        y[dt.year]["count"] += 1
                    count += 1
            return d, y, years


def getDates(buyDate, sellDate):
    dates = pandas.date_range(
        start=buyDate, end=sellDate, freq='d').strftime('%Y-%m-%d').tolist()
    return dates


def status(dict, ydict, d):
    total = 0
    for key in dict:
        if dict[key]["date"] in d:
            dict[key]["status"] = "True"
            total += dict[key]["value"]
            ydict[dict[key]["year"]]["status"] = "True"
    total = round(total, 3)
    return dict, ydict, total


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/stocks")
def stocks():
    dict = query()
    return render_template("stocks.html", data=dict)


@app.route("/stocks/<name>")
def views(name):
    buyDate = request.args.get('buyDate', default=None)
    sellDate = request.args.get('sellDate', default=None)
    if buyDate == None and sellDate == None:
        dict = query()
        data, years, year = process(dict, name)
        return render_template("view.html", data=data, years=years, year=year, name=name)
    else:
        dates = getDates(buyDate, sellDate)
        dict = query()
        d, y, year = process(dict, name)
        data, years, total = status(d, y, dates)
        return render_template("view.html", data=data, years=years, year=year, total=total, name=name)


@app.route("/submitFilter", methods=['POST'])
def submitFilter():
    if request.method == "POST":
        name = request.form["companyName"]
        buyDate = request.form['buyDate']
        sellDate = request.form['sellDate']
        if sellDate == '':
            sellDate = datetime.today().strftime('%Y-%m-%d')
        return redirect(url_for("views", name=name, buyDate=buyDate, sellDate=sellDate))
    else:
        return render_template("view.html")


if __name__ == "__main__":
    app.run(debug=True)
