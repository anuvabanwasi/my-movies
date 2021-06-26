from flask import Flask
from flask import Flask, flash, jsonify, redirect, render_template, request, session
import requests
from flask_paginate import Pagination, get_page_args
import math
import os

app = Flask(__name__)

api_key = "b26a4c28"
per_page = 20
title = ""
filter = False
page = 1
total = 0
start_year = 0
end_year = 0

class movie:
    def __init__(self, obj_title, obj_year, obj_imdbID):
        self.obj_title = obj_title
        self.obj_year = obj_year
        self.obj_imdbID = obj_imdbID

@app.route('/')
def search():
    """Search for movie title."""
    return render_template("search.html")

@app.route('/search_results.html', methods = ['POST', 'GET'])
def search_results():
    global title
    global api_key
    global per_page
    global filter
    global page
    global total
    global start_year
    global end_year

    print("1. Inside search_results")

    page = int(request.args.get("page", 1))
    offset = (page - 1) * per_page

    print("\n\n 2. THE PAGE IS %s" % page)

    if request.method == "POST":
        print("3. Inside POST")
        if "movie" in request.form:
            title = request.form["movie"]
            total = get_total_records()
            filter = False
        if "num_per_page" in request.form:
            per_page = int(request.form["num_per_page"])
        if "submit_years" in request.form:
            start_year = request.form["start_year"]
            end_year = request.form["end_year"]
            filter = True
        if "filter" in request.form:
            print("\n\n INSIDE FILTER IF")
            toggle_val = request.form["filter"]
            if toggle_val == "true":
                filter = True
            else:
                filter = False
        # return render_template("layout.html")

    if filter == True:
        movieList = get_results_for_page()
        movieList = get_filtered_results_for_page(movieList, start_year, end_year)
    else:
        print("4")
        movieList = get_results_for_page()

    print("total inside search_results is %s" % total)

    pagination = Pagination(page = page, per_page = per_page, total = total,
                                    css_framework="bootstrap4")

    return render_template("search_results.html",
                            movieList = movieList,
                            title = title,
                            offset = offset,
                            pagination = pagination,
                            filter = filter
                            )

def get_results_for_page():
    global per_page
    global api_key
    global title
    global page

    print("5")
    movieList = []

    total_results = get_total_records()
    page = int(request.args.get("page", 1))
    offset = (page - 1) * per_page
    numCalls = int(math.ceil(per_page / 10))

    firstMovie = ((page - 1) * per_page) + 1
    OMDBPage = int(firstMovie / 10)

    if OMDBPage == 0 and firstMovie > 0:
        OMDBPage = 1

    print("OMDBPage is %s" % OMDBPage)
    print("numCalls is %s" % numCalls)

    for i in range(OMDBPage, OMDBPage + numCalls):
        pageStr = str(i)
        # url = "https://www.omdbapi.com?apikey=" + api_key + "&s=" + title + "&page=" + pageStr + "&type=movie"
        url = "https://www.omdbapi.com/?apikey=b26a4c28&s=Hobbit"
        movies = requests.get(url).json().get("Search")
        print("url is: ")
        print(url)
        print("The len of movies: ")

        if movies == None:
            break

        for theMovie in movies:
            obj_title = theMovie.get("Title")
            print("The obj_title is: %s" % obj_title)
            obj_year = theMovie.get("Year")
            obj_imdbID = theMovie.get("imdbID");

            movieList.append(movie(obj_title, obj_year, obj_imdbID))

    return movieList

def get_filtered_results_for_page(movieList, start_year, end_year):
    filteredList = []

    print(start_year)
    print(end_year)

    print(type(start_year))
    print(type(end_year))

    if not start_year and not end_year:
        return movieList
    elif not start_year:
        start_year = 0
    elif not end_year:
        print("INSIDE END_YEAR = 0")
        end_year = 999999999

    for theMovie in movieList:
        if int(theMovie.obj_year) >= int(start_year) and int(theMovie.obj_year) <= int(end_year):
            filteredList.append(theMovie)

    return filteredList

def get_total_records():
    global per_page
    global api_key
    global title

    print("6")

    url = "http://www.omdbapi.com?apikey=" + api_key + "&s=" + title + "&type=movie"
    print("7")
    movies = requests.get(url).json().get("Search")
    print("8")
    total_results = requests.get(url).json().get("totalResults")
    print("9")

    print("total results in get_total_records is %s" % total_results)
    print("url in get_total_records is %s" % url)

    if total_results == None:
        total_results = 0
    else:
        print("10")
        total_results = int(total_results)

    return total_results


@app.route('/movie_details.html',  methods=["GET", "POST"])
def showResult():
    """Shows result from clicking one movie title."""
    global api_key

    if request.method == "GET":
        return render_template('details.html')
    else:
        title = request.form["title"]

        api_key = "b26a4c28"
        url = "http://www.omdbapi.com?apikey=" + api_key + "&i=" + title + "&type=movie"
        print("url %s" % url)
        result = requests.get(url).json()

        if(result["Response"] == "True"):
            name = result["Title"]
            release_date = result["Year"]
            runtime = result["Runtime"]
            genre = result["Genre"]
            director = result["Director"]
            poster = result["Poster"]

            return render_template("movie_details.html", name = name, release_date = release_date, runtime = runtime, genre = genre, director = director, poster = poster)

        else:
            return render_template("no_details.html")


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
