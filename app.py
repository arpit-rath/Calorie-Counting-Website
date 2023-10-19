from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import date
from sqlalchemy import insert
from sqlalchemy import create_engine
from datetime import datetime

app = Flask(__name__)

SQLALCHEMY_DATABASE_URI = 'sqlite:///F:/NIKITA/Projects/Calorie Counting Website - Arpit/blog.db'

SQLALCHEMY_BINDS = {
    'sql1': 'sqlite:///F:/NIKITA/Projects/Calorie Counting Website - Arpit/food_count.db',
    'sql2': 'sqlite:///F:/NIKITA/Projects/Calorie Counting Website - Arpit/calories.db'
}

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_BINDS'] = SQLALCHEMY_BINDS

db = SQLAlchemy(app)

class Food_item(db.Model):
    __bind_key__ = 'sql1'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(50))
    carbs = db.Column(db.Float)
    fats = db.Column(db.Float)
    protein = db.Column(db.Float)
    calorie = db.Column(db.Float)

class Caloriepost(db.Model):
    __bind_key__ = 'sql2'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(50))
    carbs = db.Column(db.Float)
    fats = db.Column(db.Float)
    protein = db.Column(db.Float)
    calorie = db.Column(db.Float)
    date_entry = db.Column(db.Date)

def calc_bmi_si(weight, height):
    return round((weight / ((height / 100) ** 2)), 2)

def calc_bmi_us(weight, height):
    return round((703 * weight / (height ** 2)), 2)

def get_color_bmi(bmi_value):
    color = ''
    print(bmi_value)
    if (bmi_value < 18.5):
        color = 'blue'
    elif (bmi_value >= 18.5 and bmi_value <=24.9):
        color = 'green'
    elif (bmi_value >= 25 and bmi_value <=29.9):
        color = 'yellow'
    elif (bmi_value >= 30 and bmi_value <=39.9):
        color = 'orange'
    elif (bmi_value >= 40):
        color = 'red'
    
    print(color)
    return color

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/view')
def view():
    calories = Caloriepost.query.order_by(Caloriepost.date_entry.desc()).all()
    
    q = db.session.query(Caloriepost.date_entry, func.sum(Caloriepost.carbs), 
                        func.sum(Caloriepost.fats), func.sum(Caloriepost.protein),
                        func.sum(Caloriepost.calorie)).group_by(Caloriepost.date_entry).order_by(Caloriepost.date_entry.desc()).all()
    
    return render_template('view.html', calories=calories, totals=q)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/bmi', methods=['GET', 'POST'])
def bmi():
    bmi_value = 0
    if request.method == 'POST' and 'weight1' in request.form:
        weight = float(request.form.get('weight1'))
        height = float(request.form.get('height1'))
        bmi_value = calc_bmi_si(weight, height)
    if request.method == 'POST' and 'weight2' in request.form:
        weight = float(request.form.get('weight2'))
        height = float(request.form.get('height2'))
        bmi_value = calc_bmi_us(weight, height)
    color = get_color_bmi(bmi_value)
    return render_template('bmi.html', bmi=bmi_value, color=color)

@app.route('/add', methods=['GET', 'POST'])
def add():
    food_list = Food_item.query.order_by(Food_item.item.asc()).all()
    get_item = ''
    if request.method == 'POST' and 'search' in request.form:
        item = request.form.get("search")
        get_item = Food_item.query.filter_by(item=item)

    return render_template('add.html', food_list=food_list, get_item=get_item)

@app.route('/addpost', methods=['POST'])
def addpost():
    food_item = request.form.get("food_item")
    print(food_item)

    q = db.session.query(Food_item.item, Food_item.carbs, Food_item.fats,
                        Food_item.protein, Food_item.calorie, func.date(date.today())).filter(Food_item.item == food_item)
    
    print(q[0])

    me = Caloriepost(item=q[0][0],carbs=float(q[0][1]),
                    fats=float(q[0][2]),protein=float(q[0][3]),calorie=float(q[0][4]),
                    date_entry=func.date(q[0][5]))

    db.session.add(me)
    db.session.commit()

    return redirect(url_for('view'))

@app.route('/delete')
def delete():
    calories = Caloriepost.query.order_by(Caloriepost.date_entry.desc()).all()

    return render_template('delete.html', calories=calories)

@app.route('/deletepost', methods=['DELETE','POST'])
def deletepost():
    food_item = request.form.get("food_item")

    post = Caloriepost.query.filter_by(item=food_item).one()
    
    db.session.delete(post)
    db.session.commit()
    
    return redirect(url_for('view'))

if __name__ == '__main__':
    app.run(debug=True)