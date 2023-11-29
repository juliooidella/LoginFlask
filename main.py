from flask import flash, render_template, request, redirect, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from app import app, db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

usuario_logado = None
print(usuario_logado)

@app.route('/')
def home():
    usuario_logado = session.get('usuario_logado')
    print(usuario_logado)
    if usuario_logado is not None: 
        return render_template('home.html', home='Página Inicial')
    else: 
        return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        pwd = request.form['password']

        user = User(name, email, pwd)
        db.session.add(user)
        db.session.commit()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = session.pop('error_message', None)  # Tente obter a mensagem de erro da sessão e removê-la

    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['password']
        session['usuario_logado'] = request.form['email']

        user = User.query.filter_by(email=email).first()

        if user and user.verify_password(pwd):
            login_user(user)
            return redirect(url_for('home'))
        else:
            error_message = "Login e/ou senha inválido(s). Tente novamente."
            flash(error_message, 'error')  # Usar flash para exibir a mensagem de erro

    return render_template('login.html', error_message=error_message)


@app.route('/logout')
def logout():
    logout_user()
    session.clear() 
    return redirect(url_for('login'))

@app.route('/change_password', methods=['POST'])
@login_required  # Use a decoradora @login_required para garantir que apenas usuários autenticados possam acessar esta rota
def change_password():
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password == confirm_password:
            # Atualize a senha do usuário
            current_user.password = generate_password_hash(new_password)
            current_user.new_password = None  # Limpe o campo de nova senha

            db.session.commit()
            flash("Senha alterada com sucesso.", 'success')
            return redirect(url_for('home'))
        else:
            flash("As senhas não coincidem. Tente novamente.", 'error')

    return render_template('home.html')

app.run(debug=True)