from flask import Flask, render_template
from datetime import datetime
import requests
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
                    d[count]["amount"] = value
                    d[count]["value"] = float(value[3:])
                elif value =='-':
                    d[count] = {}
                    d[count]["amount"] = value
                    d[count]["value"] = 0
                else:
                    dt = datetime.strptime(value, '%Y-%m-%d')
                    d[count]["year"] = dt.year
                    d[count]["date"] = value
                    if dt.year not in y:
                        years.append(dt.year)
                        y[dt.year] = {}
                        y[dt.year]["value"] = d[count]["value"]
                        y[dt.year]["count"] = 1
                    else:
                        y[dt.year]["value"] += d[count]["value"]
                        y[dt.year]["count"] += 1
                    count += 1
            return d, y, years


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/stocks")
def stocks():
    dict = query()
    return render_template("stocks.html", data=dict)


@app.route("/stocks/<name>")
def views(name):
    dict = query()
    data, years, year = process(dict, name)
    return render_template("view.html", data=data, years=years, year=year, name=name)


if __name__ == "__main__":
    app.run(debug=True)
