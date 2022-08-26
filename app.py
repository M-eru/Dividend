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
            yields = []
            dates = []
            years = []
            data = requests.get(f"https://www.dividends.sg{dict[key]}")
            soup = BeautifulSoup(data.text, "html.parser")
            for data in soup.find_all('td', {'class': None, 'rowspan': None, 'vertical-align': None}):
                value = data.text.strip()
                if 'SGD' in value or value == '-':
                    yields.append(value)
                else:
                    dt = datetime.strptime(value, '%Y-%m-%d')
                    years.append(dt.year)
                    dates.append(value)
            return yields, dates, years


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
    yields, dates, years = process(dict, name)
    return render_template("view.html", yields=yields, dates=dates, years=years, name=name)


if __name__ == "__main__":
    app.run(debug=True)
