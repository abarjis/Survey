from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey

# key names will use to store some things in the session;
# put here as constants so we're guaranteed to be consistent in
# our spelling of these

# here we set a variable that will be used as key later for our session
# we use a constant RESPONSES_KEY that has a value of 'responses' (which actually does not really matter, it could be called "anwers", "res" or whatever)
RESPONSES_KEY = "responses" 

app = Flask(__name__)
app.config['SECRET_KEY'] = "abcde!"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


@app.route("/")
def show_survey_start():
    """Select a survey."""

    return render_template("survey_start.html", survey=survey)


@app.route("/begin", methods=["POST"])
def start_survey():
    """Clear the session of responses."""

    # Here we set a specific key for our session using the constant we defined line 11. 
    # In Flask, the session is directly accessible (as a global variable in our controllers).
    # It will be used to store the answers of our user in an array directly in the server's memory (no persistence, if the server shut down for any reason, this is lost)
    session[RESPONSES_KEY] = []

    return redirect("/questions/0")


@app.route("/answer", methods=["POST"])
def handle_question():
    """Save response and redirect to next question."""

    # get the response choice
    choice = request.form['answer']

    # add this response to the session
        # we get the array of our user's previous answers from the session using the dedicated key
    responses = session[RESPONSES_KEY]
        # we add the answer he just sent from the form to the array for answers
    responses.append(choice)
        # we store the array including the newest answer back into the session by resetting the key
    session[RESPONSES_KEY] = responses

    if (len(responses) == len(survey.questions)):
        # They've answered all the questions! Thank them.
        return redirect("/complete")

    else:
        return redirect(f"/questions/{len(responses)}")


@app.route("/questions/<int:qid>")
def show_question(qid):
    """Display current question."""
    # here that's another way to get the array of answers stored in the session
    responses = session.get(RESPONSES_KEY)

    if (responses is None):
        # trying to access question page too soon
        return redirect("/")

    if (len(responses) == len(survey.questions)):
        # They've answered all the questions! Thank them.
        return redirect("/complete")

    if (len(responses) != qid):
        # Trying to access questions out of order.
        flash(f"Invalid question id: {qid}.")
        return redirect(f"/questions/{len(responses)}")

    question = survey.questions[qid]
    return render_template(
        "question.html", question_num=qid, question=question)


@app.route("/complete")
def complete():
    """Survey complete. Show completion page."""

    return render_template("completion.html")