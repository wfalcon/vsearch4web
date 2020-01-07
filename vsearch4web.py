from flask import Flask, render_template, request, redirect, escape, session
from vsearch import search4letters
from DBcm import UserDatabase
from config import dbconfig
from checker import check_logged_in

app = Flask(__name__)
app.config['dbconfig'] = dbconfig
app.secret_key='GkvIyvhuYTggritRffUTytrutYty'


@app.route('/')
@app.route('/entry')
def entry_page() -> 'html': 
	return render_template('entry.html',
		the_title='Добро пожаловать в web поиск букв в заданной фразе!')


def log_request(req: 'flask_request', res: str) -> None:
	with UserDatabase(app.config['dbconfig']) as cursor:
		_SQL = """insert into log (phrase, letters, ip, browser_string, results) values (%s, %s, %s, %s, %s) """
		cursor.execute(_SQL, (req.form['phrase'],
							req.form['letters'],
							req.remote_addr,
							req.user_agent.browser,
							res, ))
	

@app.route('/search4', methods=['POST'])
def do_search() -> str:
	title = 'Результат поиска'
	phrase = request.form['phrase']
	letters = request.form['letters']
	result = (search4letters(phrase,letters))
	if result:
		results = ' '.join(result)
	else:
		results = 'Не найдено'
	log_request(request, results)
	return render_template('result.html', the_title = title,
		the_phrase = phrase, the_letters = letters,
		the_results = results,)

@app.route('/viewlog')
@check_logged_in
def view_log() -> 'html':
	with UserDatabase(app.config['dbconfig']) as cursor:
		_SQL = """ select * from log """
		cursor.execute(_SQL)
		contents = cursor.fetchall()
	titles = ('№п.п.', 'Дата и время', 'Фраза', 'Буквы', 'Адрес источника', 'Браузер', 'Результат')	
	return render_template('viewlog.html', the_title = 'Просмотр лога',
							the_row_titles = titles,
							the_data = contents,)


@app.route('/login')
def do_login() -> str:
	session['logged_in'] = True
	return 'Вы вошли'


@app.route('/logout')
def do_logout() -> str:
	if 'logged_in' in session:
		session.pop('logged_in')
		return 'Вы вышли'
	else:
		return 'Вы не в системе'


if __name__=='__main__':
	
	app.run(port=80, debug=True)