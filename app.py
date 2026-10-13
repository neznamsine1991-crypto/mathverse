import os, random, sqlite3, uuid
from datetime import datetime
from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.config.update(SECRET_KEY=os.environ.get("SECRET_KEY", "change-this-before-production"), DATABASE=os.environ.get("DATABASE_PATH", "mathverse.db"))

TOPICS = {
  5: [("whole-numbers", "Whole Numbers"), ("fractions", "Fractions"), ("geometry", "Geometry"), ("measurement", "Measurement")],
  6: [("fractions", "Fraction Arithmetic"), ("ratios", "Ratios & Rates"), ("integers", "Integers"), ("equations", "Basic Equations")],
  7: [("proportions", "Proportions"), ("expressions", "Algebraic Expressions"), ("equations", "Two-step Equations"), ("geometry", "Geometry")],
  8: [("linear", "Linear Functions"), ("systems", "Systems of Equations"), ("pythagorean", "Pythagorean Theorem"), ("scientific", "Scientific Notation")],
}

def q(id, grade, topic, prompt, answer, steps, difficulty="medium"):
    return {"id": id, "grade": grade, "topic": topic, "prompt": prompt, "answer": str(answer), "steps": steps, "difficulty": difficulty}

QUESTIONS = [
q("g5-1",5,"whole-numbers","What is 4,582 + 2,739?",7321,["Add ones: 2 + 9 = 11; write 1, carry 1.","Add tens: 8 + 3 + 1 = 12; write 2, carry 1.","Continue: 4,582 + 2,739 = 7,321."]),
q("g5-2",5,"whole-numbers","Round 8,746 to the nearest hundred.",8700,["The hundreds digit is 7.","The tens digit is 4, so round down.","The result is 8,700."],"easy"),
q("g5-3",5,"fractions","What is 1/4 + 2/4?","3/4",["The denominators already match.","Add the numerators: 1 + 2 = 3.","Keep denominator 4: 3/4."],"easy"),
q("g5-4",5,"fractions","What fraction is equivalent to 3/5 with denominator 10?","6/10",["Multiply 5 by 2 to get 10.","Multiply the numerator by 2 as well: 3 × 2 = 6.","So 3/5 = 6/10."]),
q("g5-5",5,"geometry","A rectangle is 8 cm long and 5 cm wide. What is its area in cm²?",40,["Area of a rectangle is length × width.","8 × 5 = 40.","The area is 40 cm²."]),
q("g5-6",5,"geometry","What is the perimeter of a square with side length 7 cm?",28,["A square has four equal sides.","4 × 7 = 28.","The perimeter is 28 cm."],"easy"),
q("g5-7",5,"measurement","How many minutes are in 3 hours?",180,["One hour has 60 minutes.","3 × 60 = 180.","There are 180 minutes."],"easy"),
q("g5-8",5,"measurement","Convert 2.5 metres to centimetres.",250,["One metre is 100 centimetres.","2.5 × 100 = 250.","2.5 metres is 250 cm."]),
q("g6-1",6,"fractions","What is 3/4 − 1/8?","5/8",["Use denominator 8: 3/4 = 6/8.","Subtract: 6/8 − 1/8 = 5/8.","The answer is 5/8."]),
q("g6-2",6,"fractions","Calculate 2 1/2 + 1 3/4.","4 1/4",["Add whole parts: 2 + 1 = 3.","Add fractions: 1/2 + 3/4 = 2/4 + 3/4 = 5/4 = 1 1/4.","Total: 3 + 1 1/4 = 4 1/4."]),
q("g6-3",6,"ratios","A recipe uses 3 cups of flour for 2 batches. How many cups are needed for 5 batches?","7.5",["Each batch uses 3 ÷ 2 = 1.5 cups.","For 5 batches: 1.5 × 5 = 7.5.","7.5 cups are needed."]),
q("g6-4",6,"ratios","A car travels 180 km in 3 hours. What is its unit rate in km/h?",60,["Unit rate means per one hour.","180 ÷ 3 = 60.","The rate is 60 km/h."],"easy"),
q("g6-5",6,"integers","Calculate −7 + 12.",5,["Start at −7.","Moving 12 units right reaches 5.","−7 + 12 = 5."],"easy"),
q("g6-6",6,"integers","Calculate −4 × 6.",-24,["A negative times a positive is negative.","4 × 6 = 24.","So −4 × 6 = −24."]),
q("g6-7",6,"equations","Solve: x + 9 = 23.",14,["Subtract 9 from both sides.","x = 23 − 9.","x = 14."],"easy"),
q("g6-8",6,"equations","Solve: 5x = 35.",7,["Divide both sides by 5.","x = 35 ÷ 5.","x = 7."],"easy"),
q("g7-1",7,"proportions","Find x: 4/5 = x/20.",16,["Cross multiply or scale 5 to 20 by ×4.","Multiply the numerator by 4 too: 4 × 4 = 16.","x = 16."],"easy"),
q("g7-2",7,"proportions","A price rises from $80 to $100. What is the percent increase?",25,["Increase: 100 − 80 = 20.","Divide by original: 20 ÷ 80 = 0.25.","0.25 = 25%. "]),
q("g7-3",7,"expressions","Simplify: 3x + 5x − 2.","8x-2",["3x and 5x are like terms.","3x + 5x = 8x.","The simplified expression is 8x − 2."]),
q("g7-4",7,"expressions","Expand: 4(2x − 3).","8x-12",["Distribute 4 to each term.","4 × 2x = 8x and 4 × −3 = −12.","The result is 8x − 12."]),
q("g7-5",7,"equations","Solve: 3x + 4 = 19.",5,["Subtract 4: 3x = 15.","Divide by 3.","x = 5."]),
q("g7-6",7,"equations","Solve: 2x − 7 = 11.",9,["Add 7: 2x = 18.","Divide by 2.","x = 9."]),
q("g7-7",7,"geometry","The angles in a triangle are 55°, 65°, and what angle?",60,["Triangle angles total 180°.","55 + 65 = 120.","180 − 120 = 60°."]),
q("g7-8",7,"geometry","Find the area of a circle with radius 3. Use π = 3.14.",28.26,["Area = πr².","3² = 9, then 3.14 × 9 = 28.26.","The area is 28.26 square units."]),
q("g8-1",8,"linear","What is the slope between (1, 2) and (3, 8)?",3,["Slope = change in y ÷ change in x.","(8 − 2) ÷ (3 − 1) = 6 ÷ 2.","The slope is 3."]),
q("g8-2",8,"linear","For y = 2x + 1, what is y when x = 4?",9,["Substitute x = 4.","y = 2(4) + 1 = 8 + 1.","y = 9."],"easy"),
q("g8-3",8,"systems","Solve: x + y = 10 and x − y = 2. What is x?",6,["Add the equations: 2x = 12.","Divide by 2.","x = 6."]),
q("g8-4",8,"systems","Solve: x + y = 9 and x − y = 3. What is y?",3,["Add equations: 2x = 12, so x = 6.","Substitute: 6 + y = 9.","y = 3."]),
q("g8-5",8,"pythagorean","A right triangle has legs 6 and 8. Find the hypotenuse.",10,["Use a² + b² = c².","6² + 8² = 36 + 64 = 100.","c = √100 = 10."]),
q("g8-6",8,"pythagorean","Find the missing leg if c = 13 and one leg is 5.",12,["a² + 5² = 13².","a² = 169 − 25 = 144.","a = 12."]),
q("g8-7",8,"scientific","Write 4,500,000 in scientific notation.","4.5e6",["Move the decimal after 4.5.","It moved 6 places left.","4,500,000 = 4.5 × 10⁶."]),
q("g8-8",8,"scientific","Calculate (3 × 10³)(2 × 10⁴).","6e7",["Multiply coefficients: 3 × 2 = 6.","Add powers: 10³ × 10⁴ = 10⁷.","The answer is 6 × 10⁷."]),
]

# Each listed curriculum category is expanded with ten distinct, deterministic
# questions. Keeping this generation beside the curated set makes the initial
# bank easy to audit and ensures every category is ready on first launch.
def generated_category_questions(grade, topic):
    questions = []
    for n in range(1, 11):
        ident = f"g{grade}-{topic}-generated-{n}"
        if topic == "whole-numbers":
            a, b = 1200 + n * 137, 800 + n * 83; ans = a + b
            prompt=f"Calculate {a:,} + {b:,}."; steps=[f"Add the numbers by place value.",f"{a:,} + {b:,} = {ans:,}.","Check that the sum is reasonable."]
        elif topic == "fractions":
            denom=n+2; a=n; b=1; ans=f"{a+b}/{denom}"
            prompt=f"Calculate {a}/{denom} + {b}/{denom}."; steps=["The denominators match.",f"Add numerators: {a} + {b} = {a+b}.",f"The answer is {ans}."]
        elif topic == "geometry":
            length, width=n+3,n+2; ans=length*width
            prompt=f"A rectangle is {length} cm by {width} cm. What is its area in cm²?"; steps=["Area = length × width.",f"{length} × {width} = {ans}.",f"The area is {ans} cm²."]
        elif topic == "measurement":
            hours=n+1; ans=hours*60
            prompt=f"How many minutes are in {hours} hours?"; steps=["One hour contains 60 minutes.",f"{hours} × 60 = {ans}.",f"There are {ans} minutes."]
        elif topic == "ratios":
            total=n*12; groups=n+2; ans=total/groups if total%groups else total//groups
            # use exact division values for a transparent unit-rate question
            total, groups, ans = (n+2)*6, n+2, 6
            prompt=f"{total} stickers are shared equally among {groups} students. How many does each student receive?"; steps=["Equal sharing means division.",f"{total} ÷ {groups} = {ans}.",f"Each student receives {ans} stickers."]
        elif topic == "integers":
            a=n+3; b=n+5; ans=b-a
            prompt=f"Calculate −{a} + {b}."; steps=[f"Start at −{a}.",f"Moving {b} units right reaches {ans}.",f"−{a} + {b} = {ans}."]
        elif topic == "equations":
            coefficient=(n%4)+2; answer=n+3; total=coefficient*answer; ans=answer
            prompt=f"Solve: {coefficient}x = {total}."; steps=[f"Divide both sides by {coefficient}.",f"x = {total} ÷ {coefficient}.",f"x = {answer}."]
        elif topic == "proportions":
            numerator=n+1; denominator=n+2; multiplier=3; ans=numerator*multiplier; right=denominator*multiplier
            prompt=f"Find x: {numerator}/{denominator} = x/{right}."; steps=[f"Scale {denominator} to {right} by multiplying by {multiplier}.",f"Multiply {numerator} by {multiplier} too.",f"x = {ans}."]
        elif topic == "expressions":
            a,b=n+2,n+4; ans=f"{a+b}x-{n}"
            prompt=f"Simplify: {a}x + {b}x − {n}."; steps=[f"{a}x and {b}x are like terms.",f"{a}x + {b}x = {a+b}x.",f"The simplified expression is {ans}."]
        elif topic == "linear":
            slope=n+1; intercept=n-2; x=n+3; ans=slope*x+intercept
            sign=f"+ {intercept}" if intercept>=0 else f"− {abs(intercept)}"
            prompt=f"For y = {slope}x {sign}, what is y when x = {x}?"; steps=[f"Substitute x = {x}.",f"y = {slope}({x}) {sign}.",f"y = {ans}."]
        elif topic == "systems":
            x=n+3; y=n+1; total=x+y; difference=x-y; ans=x
            prompt=f"Solve: x + y = {total} and x − y = {difference}. What is x?"; steps=["Add the equations to eliminate y.",f"2x = {total+difference}.",f"x = {x}."]
        elif topic == "pythagorean":
            # familiar scaled 3-4-5 triples
            scale=n+1; a,b,ans=3*scale,4*scale,5*scale
            prompt=f"A right triangle has legs {a} and {b}. Find its hypotenuse."; steps=["Use a² + b² = c².",f"{a}² + {b}² = {ans}².",f"The hypotenuse is {ans}."]
        elif topic == "scientific":
            base=n+1; power=n+2; ans=f"{base}e{power}"
            prompt=f"Write {base} × 10^{power} using e notation."; steps=["Keep the coefficient.",f"Use e to represent × 10 to a power.",f"The answer is {ans}."]
        else:
            # Should never occur: all TOPICS above have an explicit generator.
            continue
        questions.append(q(ident, grade, topic, prompt, ans, steps, "easy" if n < 4 else "medium"))
    return questions

for _grade, _topics in TOPICS.items():
    for _topic, _name in _topics:
        QUESTIONS.extend(generated_category_questions(_grade, _topic))

def db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"]); g.db.row_factory = sqlite3.Row
        g.db.execute("CREATE TABLE IF NOT EXISTS attempts (id TEXT PRIMARY KEY, created_at TEXT, grade INTEGER, topic TEXT, score INTEGER, total INTEGER, answers TEXT)")
    return g.db
@app.teardown_appcontext
def close_db(_):
    if "db" in g: g.db.close()
def guest():
    if "guest" not in session: session["guest"] = str(uuid.uuid4())
    return session["guest"]
def normalize(v): return str(v).lower().replace(" ", "").replace("−", "-").replace("×", "*")
def numeric_value(value):
    """Parse normal numbers, simple fractions, and mixed numbers without eval."""
    value = str(value).strip().lower().replace("−", "-").replace("×", "*")
    if "/" in value:
        whole, fraction = ("0", value) if value.count("/") == 1 and value[0] in "-0123456789" else value.split(" ", 1)
        numerator, denominator = fraction.split("/", 1)
        if float(denominator) == 0: raise ZeroDivisionError
        result = float(numerator) / float(denominator)
        return float(whole) + result if float(whole) >= 0 else float(whole) - abs(result)
    return float(value)
def correct(question, answer):
    try: return abs(numeric_value(answer)-numeric_value(question["answer"])) < 0.0001
    except (ValueError, ZeroDivisionError): pass
    a, b = normalize(answer), normalize(question["answer"])
    if a == b: return True
    return False
def get_question(qid): return next((x for x in QUESTIONS if x["id"] == qid), None)

@app.route("/")
def home(): return render_template("home.html")
@app.route("/dashboard")
def dashboard():
    guest(); rows=db().execute("SELECT * FROM attempts ORDER BY created_at DESC").fetchall(); answered=sum(r["total"] for r in rows); right=sum(r["score"] for r in rows)
    return render_template("dashboard.html", rows=rows[:5], total_tests=len(rows), answered=answered, accuracy=round(right/answered*100) if answered else 0)
@app.route("/grades")
def grades(): return render_template("grades.html", topics=TOPICS)
@app.route("/grades/<int:grade>")
def grade(grade):
    if grade not in TOPICS: abort(404)
    qs=[x for x in QUESTIONS if x["grade"]==grade]
    return render_template("grade.html", grade=grade, topics=TOPICS[grade], question_count=len(qs))
@app.route("/practice", methods=["GET","POST"])
def practice():
    if request.method == "POST":
        grade=int(request.form["grade"]); topic=request.form.get("topic", "all"); count=min(max(int(request.form.get("count",5)),1),10)
        pool=[x for x in QUESTIONS if x["grade"]==grade and (topic=="all" or x["topic"]==topic)]
        if not pool: flash("No questions are available for that selection."); return redirect(url_for("practice"))
        picked=random.sample(pool, min(count,len(pool))); session["test"]={"title":"Practice session", "questions":[x["id"] for x in picked], "answers":{}, "practice":True}; return redirect(url_for("test", index=0))
    return render_template("practice.html", topics=TOPICS)
@app.route("/tests/create", methods=["GET","POST"])
def create_test():
    if request.method == "POST":
        grade=int(request.form["grade"]); topic=request.form.get("topic", "all"); count=min(max(int(request.form.get("count",5)),1),10)
        pool=[x for x in QUESTIONS if x["grade"]==grade and (topic=="all" or x["topic"]==topic)]
        if len(pool)<count: flash(f"Only {len(pool)} eligible questions are available. Choose a smaller test."); return redirect(url_for("create_test"))
        session["test"]={"title":"Custom assessment", "questions":[x["id"] for x in random.sample(pool,count)], "answers":{}, "practice":False}; return redirect(url_for("test", index=0))
    return render_template("create_test.html", topics=TOPICS)
@app.route("/tests/current/<int:index>", methods=["GET","POST"])
def test(index):
    t=session.get("test");
    if not t or index<0 or index>=len(t["questions"]): return redirect(url_for("practice"))
    if request.method=="POST":
        t["answers"][t["questions"][index]]=request.form.get("answer",""); session["test"]=t
        if request.form.get("submit"): return redirect(url_for("submit_test"))
        return redirect(url_for("test", index=min(index+1,len(t["questions"])-1)))
    question=get_question(t["questions"][index]); return render_template("test.html", t=t, question=question, index=index)
@app.route("/tests/submit", methods=["POST","GET"])
def submit_test():
    t=session.get("test")
    if not t: return redirect(url_for("dashboard"))
    answers=[]; score=0
    for qid in t["questions"]:
        question=get_question(qid); answer=t["answers"].get(qid,""); ok=correct(question,answer); score+=ok; answers.append({"qid":qid,"answer":answer,"correct":ok})
    aid=str(uuid.uuid4()); db().execute("INSERT INTO attempts VALUES (?,?,?,?,?,?,?)",(aid,datetime.utcnow().isoformat(),get_question(t["questions"][0])["grade"],"mixed" if len(set(get_question(x)["topic"] for x in t["questions"]))>1 else get_question(t["questions"][0])["topic"],score,len(answers),__import__('json').dumps(answers))); db().commit(); session.pop("test",None)
    return redirect(url_for("results", aid=aid))
@app.route("/tests/<aid>/results")
def results(aid):
    row=db().execute("SELECT * FROM attempts WHERE id=?",(aid,)).fetchone()
    if not row: abort(404)
    data=__import__('json').loads(row["answers"]); items=[{**a,"q":get_question(a["qid"])} for a in data]; pct=round(row["score"]/row["total"]*100); letter="A" if pct>=90 else "B" if pct>=80 else "C" if pct>=70 else "D" if pct>=60 else "F"
    return render_template("results.html", row=row, items=items, pct=pct, letter=letter)
@app.route("/history")
def history(): return render_template("history.html", rows=db().execute("SELECT * FROM attempts ORDER BY created_at DESC").fetchall())
@app.route("/mistakes")
def mistakes():
    rows=db().execute("SELECT * FROM attempts ORDER BY created_at DESC").fetchall(); items=[]
    for r in rows:
      for a in __import__('json').loads(r["answers"]):
       if not a["correct"]: items.append({**a,"q":get_question(a["qid"])})
    return render_template("mistakes.html", items=items)

if __name__ == "__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)), debug=True)
