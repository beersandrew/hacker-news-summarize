import os

import openai
import requests

from operator import itemgetter
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")




@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        animal = request.form["animal"]
        url = 'https://hacker-news.firebaseio.com/v0/topstories.json'  # to obtain list of top story ids
        r = requests.get(url)

        article_ids = r.json()  # author used submission as variable name, but articles made more sense to me
        five_articles_dicts = []  # this dict will contain all of our articles

        for article_id in article_ids[:6]:
            url = 'https://hacker-news.firebaseio.com/v0/item/' + str(article_id) + '.json'  # plug in looped id
            article_r = requests.get(url)  # get response for each individual article

            # author prints out article status code to ensure no failures with requests
            print(article_r.status_code)

            one_article = article_r.json()

            # Now let's add our info to our main dictionary

            prompt = generate_prompt(one_article['url'])
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                temperature=0,
                max_tokens=500,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            query = "Summarize this for a second-grade student: {0}".format(response['choices'][0]['text'])
            summary = openai.Completion.create(
                model="text-davinci-003",
                prompt=query,
                temperature=0,
                max_tokens=500,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            five_articles_dict = {
                'Title': one_article['title'],
                'Discussion link': one_article['url'],
                'Comments': one_article['descendants'],
                'LongSummary': response['choices'][0]['text'],
                'Summary': summary['choices'][0]['text']
            }

            five_articles_dicts.append(five_articles_dict)
        return render_template("index.html", len=len(five_articles_dicts), articles=five_articles_dicts)

    result = request.args.get("result")
    return render_template("index.html", result=result)


def generate_prompt(website):
    return "Q: what is this about? {0}".format(website)
