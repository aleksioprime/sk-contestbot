from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, SelectMultipleField, widgets, DateField
from wtforms.validators import DataRequired, Length, EqualTo, Optional

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class LoginForm(FlaskForm):
    username = StringField(label=('Логин'),
                           validators=[DataRequired(), Length(min=5)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField(label=('Войти'))

class CreateUserForm(FlaskForm):
    username = StringField(label=('Логин'), validators=[DataRequired(), Length(max=64)])
    password = PasswordField(label=('Пароль'),
                             validators=[DataRequired(),
                                         Length(min=8, message='Password should be at least %(min)d characters long')])
    confirm_password = PasswordField(
        label=('Повторите пароль'),
        validators=[DataRequired(message='*Required'),
                    EqualTo('password', message='Both password fields must be equal!')])
    first_name = StringField(label=('Имя'), validators=[DataRequired(), Length(max=64)])
    last_name = StringField(label=('Фамилия'), validators=[DataRequired(), Length(max=64)])
    submit = SubmitField(label=('Зарегистрировать'))

class ContestForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[Optional()])
    link = StringField('Ссылка', validators=[DataRequired()])
    level = SelectField('Уровень',
                        choices=[('1', '1 уровень'), ('2', '2 уровень'), ('3', '3 уровень'), ('-', 'Без уровня')])
    type = SelectField('Тип мероприятия',
                        choices=[('Олимпиада', 'Олимпиада'), ('Конкурс', 'Конкурс'), ('Соревнование', 'Соревнование'), ('Конференция', 'Конференция'), ('Другое', 'Другое')])
    group = SelectField('Кафедра', coerce=int)
    grade = StringField('Классы', validators=[Optional()])
    year = SelectField('Учебный год', coerce=int)
    subjects = MultiCheckboxField('Предметы', validators=[Optional()], coerce=int)
    submit = SubmitField(label=('Сохранить'))

class StageForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    link = StringField('Ссылка', validators=[DataRequired()])
    deadline = DateField('Дедлайн', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField(label=(''))