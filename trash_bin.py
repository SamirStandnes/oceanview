
@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():

    # To be built later maybe: provde the option to change categories and difficulty.
    # Quiz Start
    if request.method == "POST":

        # Make API call, get random category and difficulty, but keep as multiple choice. 10 new at a time.
        API_ENDPOINT = ('https://opentdb.com/api.php?amount=10&type=multiple')
        response = requests.get(API_ENDPOINT)

        # Check the status code to make sure the request was successful
        if response.status_code == 200:

            # Parse the response data
            print(response)
            data = response.json()
            print(data)

            # Clean data and insert into DB
            for question in data['results']:
                quiz_question = clean(question['question'])
                category = question['category']
                difficulty = question['difficulty']
                alternative_1 = clean(question['incorrect_answers'][0])
                alternative_2 = clean(question['incorrect_answers'][1])
                alternative_3 = clean(question['incorrect_answers'][2])
                correct_answer = clean(question['correct_answer'])
                # Insert into Questions DB
                db.execute("INSERT INTO questions (category, difficulty, question, alternative_1, alternative_2, alternative_3, correct_answer) VALUES (?, ?, ?, ?, ?, ?, ?);",
                            category, difficulty, quiz_question, alternative_1, alternative_2, alternative_3, correct_answer)

            # Send user to questions
            return redirect("/question")

        else:
            # There was an error making the request
            print('An error occurred: {}'.format(response.status_code))
            return apology("An error occured, please go back to start", 400)

    else:
        return render_template("quiz.html")


@app.route("/question", methods=["GET", "POST"])
def question():

    if request.method == "POST":
        if not request.form.get("answer"):
            return apology("You did not submit an answer and thus got 0 points, remember pick an answer. Go back to start", 400)

        # Get the answer
        answer = request.form.get("answer")
        # Get the question_id from question displayed
        question_id = request.form.get('id')

        # Query the question data using question_id
        query =  db.execute("SELECT correct_answer, question FROM questions WHERE id = ?;", question_id)[0]

        # Define the correct answer and question
        correct_answer = query['correct_answer']
        question = query['question']

        # Return a True or False result based on answer to question
        result = (answer == correct_answer)

        # INSERT the answer into the answer db with question in question...pun intended
        db.execute("INSERT INTO answers (user_id, question_id, question, answer, correct_answer, results) VALUES (?, ?, ?, ?, ?, ?);", session["user_id"], question_id, question, answer, correct_answer, result)

        # Prompt a new question
        return redirect("/question")

    else:

        # Define question from random query of question "row" from 'questions' db.
        question = db.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 1;")[0]

        # Define the alternative answers from query and shuffle the order randomly each time
        alternatives = [question['alternative_1'], question['alternative_2'], question['alternative_3'], question['correct_answer']]
        random.shuffle(alternatives)

        #Define question_id from query
        question_id = question['id']

        return render_template("question.html", question=question['question'], category=question['category'], difficulty=question['difficulty'], alternatives=alternatives, id=question_id, correct_answer = question['correct_answer'], script=True)


@app.route("/history")
@login_required
def history():
    user_id = session["user_id"]

    #Query answer history of user
    query = db.execute("SELECT * from answers WHERE user_id = ?;", user_id)

    return render_template("history.html", history=query)

@app.route("/leaderboards")
@login_required
def leaderboards():

    # Query a result of leaderboar based on most correct answers
    query = db.execute("SELECT u.username, COUNT(a.results) as num_trues FROM answers AS a JOIN users AS u ON a.user_id = u.id WHERE a.results = 1 AND u.id = a.user_id  GROUP BY u.id ORDER BY num_trues DESC;")

    return render_template("leaderboards.html", leaderboards=query)




CREATE TABLE messages (
  message_id INTEGER PRIMARY KEY,
  sender_id INTEGER NOT NULL,
  recipient_id INTEGER NOT NULL,
  message_text TEXT NOT NULL,
  timestamp DATETIME NOT NULL,
  FOREIGN KEY (sender_id) REFERENCES users(user_id),
  FOREIGN KEY (recipient_id) REFERENCES users(user_id)
);