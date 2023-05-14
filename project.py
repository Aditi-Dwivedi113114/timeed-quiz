from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from datetime import datetime 

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Aditi@123'
app.config['MYSQL_DB'] = 'quizzes_db'

mysql = MySQL(app)

@app.route('/quizzes', methods=['POST'])
def create_quiz():
    question = request.json['question']
    options = request.json['options']
    right_answer = request.json['right_answer']
    start_date = datetime.strptime(request.json['start_date'], '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(request.json['end_date'], '%Y-%m-%d %H:%M:%S')

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO quizzes (question, options, right_answer, start_date, end_date) VALUES (%s, %s, %s, %s, %s)", 
        (question, options, right_answer, start_date, end_date))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Quiz created successfully'})

@app.route('/quizzes/active', methods=['GET'])
def get_active_quiz():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM quizzes WHERE start_date <= NOW() AND end_date >= NOW()")
    quiz = cur.fetchone()
    cur.close()

    if quiz:
        return jsonify({'quiz_id': quiz[0], 'question': quiz[1], 'options': quiz[2]})
    else:
        return jsonify({'message': 'No active quiz found'})

@app.route('/quizzes/<int:quiz_id>/result', methods=['GET'])
def get_quiz_result(quiz_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT right_answer FROM quizzes WHERE quiz_id = %s", (quiz_id,))
    right_answer = cur.fetchone()[0]
    cur.close()

    return jsonify({'quiz_id': quiz_id, 'right_answer': right_answer})

@app.route('/quizzes/all', methods=['GET'])
def get_all_quizzes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM quizzes")
    quizzes = cur.fetchall()
    cur.close()

    quiz_list = []
    for quiz in quizzes:
        if quiz[4] < datetime.now():
            status = 'finished'
        elif quiz[3] > datetime.now():
            status = 'inactive'
        else:
            status = 'active'
        quiz_dict = {'quiz_id': quiz[0], 'question': quiz[1], 'options': quiz[2]}
        quiz_list.append(quiz_dict)

    return jsonify({'quizzes': quiz_list})

if __name__ == '__main__':
    app.run(debug=True)