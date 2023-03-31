import telebot
import random
import phrases

from telebot import types
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

TOKEN = 'INSERT BOT TOKEN HERE'
bot = telebot.TeleBot(TOKEN)

info = eval(open(f'about\\info.txt', encoding='utf-8').read())
aboutplan = eval(open(f'about\\aboutplan.txt', encoding='utf-8').read())
aboutplan2 = eval(open(f'about\\aboutplan2.txt', encoding='utf-8').read())
aboutreport = eval(open(f'about\\aboutreport.txt', encoding='utf-8').read())
aboutlist = eval(open(f'about\\aboutlist.txt', encoding='utf-8').read())
aboutgoals = eval(open(f'about\\aboutgoals.txt', encoding='utf-8').read())
aboutrating = eval(open(f'about\\aboutrating.txt', encoding='utf-8').read())
howtouse = eval(open(f'about\\howtouse.txt', encoding='utf-8').read())

records = {}
goalslist = {}
goalsdescr = {}
goalscomp = {}
rating = {}
index = {}
from_reminder = {}
till_reminder = {}
from_local_reminder = {}
till_local_reminder = {}
scheduler = {}
current_time = {}
before_after = {}
difference = {}


class Menu:
    def __init__(self, menu='', tag='', icon='', markup=''):
        self.menu = menu
        self.tag = tag
        self.icon = icon
        self.markup = markup
        self.taskslist = {}

# creating markup
    @staticmethod
    def createmarkup(*buttons):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        markup.add(*[types.KeyboardButton(f'{i}') for i in buttons])
        return markup

# saving data
    @staticmethod
    def savedata(message, where, what):
        u = message.chat.id
        records[u] = open(f'users\\{where} {u}.txt', 'w', encoding='utf-8')
        records[u].write(str(what))
        records[u].close()

# displaying main menu
    def showmainmenu(self, message):
        bot.send_message(message.chat.id,
                         f'Hello <b>{message.from_user.first_name}</b>! What would you like to work on now?',
                         parse_mode='html', reply_markup=self.markup)

# displaying menu of tasks
    def showtasks(self, message):
        u = message.chat.id
        self.taskslist[u] = eval(open(f'users\\{self.tag} {u}.txt', encoding='utf-8').read())
        bot.send_message(u, f'<b>{self.menu}:</b>', parse_mode='html', reply_markup=self.markup)
        if len(self.taskslist[u]) == 0:
            bot.send_message(u, '\nNothing yet', parse_mode='html')
        else:
            taskslisttext = []
            for i in range(len(self.taskslist[u])):
                taskslisttext.append(f'{i+1} - {self.taskslist[u][i]} {self.icon}')
            bot.send_message(u, '\n\n'.join(taskslisttext), parse_mode='html')

# displaying menu of goals
    def showgoals(self, message):
        u = message.chat.id
        goalslist[u] = eval(open(f'users\\{self.tag} {u}.txt', encoding='utf-8').read())
        goalsdescr[u] = eval(open(f'users\\goals_descr {u}.txt', encoding='utf-8').read())
        goalscomp[u] = eval(open(f'users\\goals_comp {u}.txt', encoding='utf-8').read())
        bot.send_message(u, f'<b>{self.menu}:</b>', parse_mode='html', reply_markup=self.markup)
        if len(goalslist[u]) == 0:
            bot.send_message(u, 'Nothing yet', parse_mode='html')
        else:
            goalslisttext = []
            for i in range(len(goalslist[u])):
                goalslisttext.append(f'{i + 1} - {goalslist[u][i]}')
                if goalsdescr[u][i]:
                    goalslisttext.append(goalsdescr[u][i])
                goalslisttext.append('\nCompletion: ' + goalscomp[u][i])
                mult = int(goalscomp[u][i].strip('%'))//25
                goalslisttext.append('\U0001F7E9' * mult + '\U00002B1C' * (4 - mult)+'\n')
            bot.send_message(u, '\n'.join(goalslisttext), parse_mode='html')

# displaying menu of rating
    def showrating(self, message):
        u = message.chat.id
        rating[u] = int(open(f'users\\{self.tag} {u}.txt', encoding='utf-8').read())
        bot.send_message(u, f'\n <b>{self.menu}:</b>', parse_mode='html', reply_markup=self.markup)
        bot.send_message(u, f'\U0001F4B0 Points - <b>{rating[u] % 10}</b>\n'
                         + '\U0001F7E1' * (rating[u] % 10) + '\U000026AA' * (10 - rating[u] % 10),
                         parse_mode='html')
        bot.send_message(u, f'\U0001F3C5 Diligence level - <b>{rating[u] // 10}</b>', parse_mode='html')

# displaying menu of info section
    def showinfo(self, message):
        u = message.chat.id
        msg = bot.send_message(u, info, parse_mode='html', reply_markup=self.markup)
        bot.register_next_step_handler(msg, self.selectinfo)

    def selectinfo(self, message):
        if message.text == '\U0001F4C6 About Plan':
            u = message.chat.id
            bot.send_message(u, aboutplan, parse_mode='html')
            bot.send_message(u, aboutplan2, parse_mode='html')

        elif message.text == '\U00002705 About Report':
            u = message.chat.id
            bot.send_message(u, aboutreport, parse_mode='html', reply_markup=return_info_markup)

        elif message.text == '\U0001F5C2 About List':
            u = message.chat.id
            bot.send_message(u, aboutlist, parse_mode='html', reply_markup=return_info_markup)

        elif message.text == '\U0001F9ED About Goals':
            u = message.chat.id
            bot.send_message(u, aboutgoals, parse_mode='html', reply_markup=return_info_markup)

        elif message.text == '\U0001F3C6 About Rating':
            u = message.chat.id
            bot.send_message(u, aboutrating, parse_mode='html', reply_markup=return_info_markup)

        elif message.text == '\U00002753 How to use':
            u = message.chat.id
            bot.send_message(u, howtouse, parse_mode='html', reply_markup=return_info_markup)

        elif message.text == '\U0001F3E0 Main Menu':
            main_menu.showmainmenu(message)

        else:
            self.showinfo(message)

# adding task to plan, report, list
    def addtask(self, message):
        msg = bot.reply_to(message, '<b>Enter the task.</b>'
                                    '\n<i>Suggested format:</i>[tag] Specific action - Amount/Duration - Deadline.'
                                    '\nE.g. \U0001F4DA Study textbook A - 5 chapters - by 1/1/2023', parse_mode='html')
        bot.register_next_step_handler(msg, self.processtask)

    def processtask(self, message):
        u = message.chat.id
        self.taskslist[u] = eval(open(f'users\\{self.tag} {u}.txt', encoding='utf-8').read())
        self.taskslist[u].append(message.text)
        self.savedata(message, self.tag, self.taskslist[u])
        self.showtasks(message)

# adding goal
    def addgoal(self, message):
        msg = bot.reply_to(message, '<b>Enter the goal.</b>'
                                    '\n<i>Suggested format:</i>[tag] Specific result - Amount/Duration - Deadline.'
                                    '\nE.g. \U0001F393 Pass test in X - above 90% - by 1/1/2023', parse_mode='html')
        bot.register_next_step_handler(msg, self.processgoal)

    def processgoal(self, message):
        u = message.chat.id
        goalslist[u] = eval(open(f'users\\{self.tag} {u}.txt', encoding='utf-8').read())
        goalsdescr[u] = eval(open(f'users\\goals_descr {u}.txt', encoding='utf-8').read())
        goalscomp[u] = eval(open(f'users\\goals_comp {u}.txt', encoding='utf-8').read())
        if message.text:
            goalslist[u].append(message.text)
        goalsdescr[u].append(None)
        goalscomp[u].append('0%')
        self.savedata(message, self.tag, goalslist[u])
        self.savedata(message, 'goals_descr', goalsdescr[u])
        self.savedata(message, 'goals_comp', goalscomp[u])
        self.showgoals(message)

# clearing plan, list
    def deleteall(self, message):
        msg = bot.reply_to(message, f'The whole {self.menu} will be deleted. Proceed?', parse_mode='html',
                           reply_markup=deleteall_markup)
        bot.register_next_step_handler(msg, self.processnew)

    def processnew(self, message):
        if message.text == 'Yes, let\'s start from scratch':
            u = message.chat.id
            self.taskslist[u] = eval(open(f'users\\{self.tag} {u}.txt', encoding='utf-8').read())
            self.taskslist[u].clear()
            self.savedata(message, self.tag, self.taskslist[u])
            self.showtasks(message)
        else:
            self.showtasks(message)

# get points, clear report
    def getpoints(self, message):
        msg = bot.reply_to(message,
                           'You will be given points for the completed tasks and the whole report will be deleted. '
                           'Proceed?', parse_mode='html', reply_markup=getpoints_markup)
        bot.register_next_step_handler(msg, self.process_newreport)

    def process_newreport(self, message):
        u = message.chat.id
        if message.text == 'Yes, give me the points':
            self.taskslist[u] = eval(open(f'users\\{self.tag} {u}.txt', encoding='utf-8').read())
            rating[u] = eval(open(f'users\\rating {u}.txt', encoding='utf-8').read())
            if len(self.taskslist[u]) == 1:
                word = 'point'
            else:
                word = 'points'
            bot.send_message(u,
                             f'\U0001F4B0 Congrats! You\'ve earned <b>{len(self.taskslist[u])} {word}</b>',
                             parse_mode='html')
            rating[u] += len(self.taskslist[u])
            self.taskslist[u].clear()
            self.savedata(message, self.tag, self.taskslist[u])
            self.savedata(message, rating_menu.tag, rating[u])
            self.showtasks(message)
        else:
            self.showtasks(message)

# clearing goals
    def deletegoals(self, message):
        msg = bot.reply_to(message, 'All goals will be deleted. Proceed?',
                           parse_mode='html', reply_markup=deleteall_markup)
        bot.register_next_step_handler(msg, self.process_newgoals)

    def process_newgoals(self, message):
        u = message.chat.id
        goalslist[u] = eval(open(f'users\\{self.tag} {u}.txt', encoding='utf-8').read())
        goalsdescr[u] = eval(open(f'users\\goals_descr {u}.txt', encoding='utf-8').read())
        goalscomp[u] = eval(open(f'users\\goals_comp {u}.txt', encoding='utf-8').read())
        if message.text == "Yes, let's start from scratch":
            goalslist[u].clear()
            goalsdescr[u].clear()
            goalscomp[u].clear()
            self.savedata(message, self.tag, goalslist[u])
            self.savedata(message, 'goals_descr', goalsdescr[u])
            self.savedata(message, 'goals_comp', goalscomp[u])
            self.showgoals(message)
        else:
            self.showgoals(message)

# working with specific task
    def specifictask(self, message):
        u = message.chat.id
        self.taskslist[u] = eval(open(f'users\\{self.tag} {u}.txt', encoding='utf-8').read())
        if len(self.taskslist[u]) == 0:
            bot.send_message(u,
                             f'There are no tasks in the {self.tag}. '
                             f'Add the first one by clicking on <b>Add task</b>',
                             parse_mode='html', reply_markup=self.markup)
        else:
            msg = bot.reply_to(message, 'Work on which task?', parse_mode='html',
                               reply_markup=self.createmarkup(*range(1, len(self.taskslist[u])+1)))
            bot.register_next_step_handler(msg, self.processsequence)

    def processsequence(self, message):
        u = message.chat.id
        if message.text.isdigit():
            if (int(message.text) - 1) in range(len(self.taskslist[u])):
                index[u] = int(message.text) - 1
                bot.send_message(u, f'\U0001F447 What would you like to do with this task?', parse_mode='html',
                                 reply_markup=self.task_markup)
                msg = bot.send_message(u, f'<b>{self.taskslist[u][index[u]]}</b>', parse_mode='html')
                bot.register_next_step_handler(msg, self.getinput)
            else:
                self.showtasks(message)
        else:
            self.showtasks(message)

    def getinput(self, message):
        u = message.chat.id
        if message.text == '\U00002705 Mark as completed':
            fulfilled_menu.taskslist[u] = eval(open(f'users\\{fulfilled_menu.tag} {u}.txt', encoding='utf-8').read())
            fulfilled_menu.taskslist[u].append(str(self.taskslist[u][index[u]]))
            self.taskslist[u].pop(index[u])
            self.savedata(message, self.tag, self.taskslist[u])
            self.savedata(message, fulfilled_menu.tag, fulfilled_menu.taskslist[u])
            bot.send_message(u, f'\U0001F389 {random.choice(phrases.praise)}, {message.from_user.first_name}! '
                                f'\U0001F389', parse_mode='html')
            self.showtasks(message)

        elif message.text == '\U0001F5C2 Transfer to General List':
            list_menu.taskslist[u] = eval(open(f'users\\{list_menu.tag} {u}.txt', encoding='utf-8').read())
            list_menu.taskslist[u].append(str(self.taskslist[u][index[u]]))
            self.taskslist[u].pop(index[u])
            self.savedata(message, self.tag, self.taskslist[u])
            self.savedata(message, list_menu.tag, list_menu.taskslist[u])
            self.showtasks(message)

        elif message.text == '\U0001F5C2 Copy to General List':
            list_menu.taskslist[u] = eval(open(f'users\\{list_menu.tag} {u}.txt', encoding='utf-8').read())
            list_menu.taskslist[u].append(str(self.taskslist[u][index[u]]))
            self.savedata(message, self.tag, self.taskslist[u])
            self.savedata(message, list_menu.tag, list_menu.taskslist[u])
            self.showtasks(message)

        elif message.text == '\U0001F4C6 Transfer to Plan for the day':
            plan_menu.taskslist[u] = eval(open(f'users\\{plan_menu.tag} {u}.txt', encoding='utf-8').read())
            plan_menu.taskslist[u].append(str(self.taskslist[u][index[u]]))
            self.taskslist[u].pop(index[u])
            self.savedata(message, self.tag, self.taskslist[u])
            self.savedata(message, plan_menu.tag, plan_menu.taskslist[u])
            self.showtasks(message)

        elif message.text == '\U0001F4C6 Copy to Plan for the day':
            plan_menu.taskslist[u] = eval(open(f'users\\{plan_menu.tag} {u}.txt', encoding='utf-8').read())
            plan_menu.taskslist[u].append(str(self.taskslist[u][index[u]]))
            self.savedata(message, self.tag, self.taskslist[u])
            self.savedata(message, plan_menu.tag, plan_menu.taskslist[u])
            self.showtasks(message)

        elif message.text == '\U0001F5D1 Delete the task':
            self.taskslist[u].pop(index[u])
            self.savedata(message, self.tag, self.taskslist[u])
            self.showtasks(message)

        elif message.text == '\U0001F58A Edit the task':
            msg = bot.send_message(u, f'Enter edited task', parse_mode='html')
            bot.register_next_step_handler(msg, self.edittask)

        elif message.text == '\U00002195 Change position':
            msg = bot.reply_to(message, 'Put at which number?', parse_mode='html',
                               reply_markup=self.createmarkup(*range(1, len(self.taskslist[u])+1)))
            bot.register_next_step_handler(msg, self.edittaskposition)

        elif message.text == '\U000027162  Duplicate the task':
            insert = self.taskslist[u][index[u]]
            self.taskslist[u].insert(len(self.taskslist[u]), insert)
            self.savedata(message, self.tag, self.taskslist[u])
            self.showtasks(message)
        else:
            self.showtasks(message)

    def edittask(self, message):
        u = message.chat.id
        self.taskslist[u][index[u]] = message.text
        self.savedata(message, self.tag, self.taskslist[u])
        self.showtasks(message)

    def edittaskposition(self, message):
        u = message.chat.id
        if message.text.isdigit():
            if int(message.text) in range(len(self.taskslist[u])):
                sequence = int(message.text) - 1
                insert = self.taskslist[u][index[u]]
                self.taskslist[u].pop(index[u])
                self.taskslist[u].insert(sequence, insert)
                self.savedata(message, self.tag, self.taskslist[u])
                self.showtasks(message)
            else:
                self.showtasks(message)
        else:
            self.showtasks(message)

# working on specific goal
    def specificgoal(self, message):
        u = message.chat.id
        goalslist[u] = eval(open(f'users\\{self.tag} {u}.txt', encoding='utf-8').read())
        goalsdescr[u] = eval(open(f'users\\goals_descr {u}.txt', encoding='utf-8').read())
        goalscomp[u] = eval(open(f'users\\goals_comp {u}.txt', encoding='utf-8').read())
        if len(goalslist[u]) == 0:
            bot.send_message(u, 'There are no goals currently. Add the first one by clicking on <b>Add goal</b>',
                             parse_mode='html', reply_markup=self.markup)
        else:
            msg = bot.reply_to(message, 'Work on which goal?', parse_mode='html',
                               reply_markup=self.createmarkup(*range(1, len(goalslist[u])+1)))
            bot.register_next_step_handler(msg, self.processgoalsequence)

    def processgoalsequence(self, message):
        u = message.chat.id
        if message.text.isdigit():
            if (int(message.text) - 1) in range(len(goalslist[u])):
                index[u] = int(message.text) - 1
                bot.send_message(u, f'\U0001F447 What would you like to do with this goal?', parse_mode='html',
                                 reply_markup=goals_specific_markup)
                msg = bot.send_message(u, f'<b>{goalslist[u][index[u]]}</b>', parse_mode='html')
                bot.register_next_step_handler(msg, self.get_goals_input)
            else:
                self.showgoals(message)
        else:
            self.showgoals(message)

    def get_goals_input(self, message):
        u = message.chat.id
        if message.text == '\U00002705 Select completion level':
            msg = bot.reply_to(message, 'What is the level of completion?',
                               parse_mode='html', reply_markup=completion_markup)
            bot.register_next_step_handler(msg, self.edit_goals_completion)

        elif message.text == '\U0001F5D1 Delete the goal':
            goalslist[u].pop(index[u])
            goalsdescr[u].pop(index[u])
            goalscomp[u].pop(index[u])
            self.savedata(message, self.tag, goalslist[u])
            self.savedata(message, 'goals_descr', goalsdescr[u])
            self.savedata(message, 'goals_comp', goalscomp[u])
            self.showgoals(message)

        elif message.text == '\U0001F58A Edit the goal':
            msg = bot.send_message(u, f'Enter edited goal', parse_mode='html')
            bot.register_next_step_handler(msg, self.edit_goals_task)

        elif message.text == '\U0001F4DD Add/edit description':
            bot.send_message(u, f'\U0001F447 This is current goal description.  Enter new goal description.',
                             parse_mode='html')
            msg = bot.send_message(u, f'<b>{goalsdescr[u][index[u]]}</b>', parse_mode='html')
            bot.register_next_step_handler(msg, self.edit_goals_description)

        elif message.text == '\U00002195 Change position':
            msg = bot.reply_to(message, 'Put at which number?', parse_mode='html',
                               reply_markup=self.createmarkup(*range(1, len(goalslist[u])+1)))
            bot.register_next_step_handler(msg, self.edit_goals_position)

        elif message.text == '\U000027162  Duplicate the goal':
            goalslist[u].insert(len(goalslist[u]), goalslist[u][index[u]])
            goalsdescr[u].insert(len(goalslist[u]), goalsdescr[u][index[u]])
            goalscomp[u].insert(len(goalslist[u]), goalscomp[u][index[u]])
            self.savedata(message, self.tag, goalslist[u])
            self.savedata(message, 'goals_descr', goalsdescr[u])
            self.savedata(message, 'goals_comp', goalscomp[u])
            self.showgoals(message)

        else:
            self.showgoals(message)

    def edit_goals_completion(self, message):
        u = message.chat.id
        goalscomp[u][index[u]] = message.text
        self.savedata(message, 'goals_comp', goalscomp[u])
        self.showgoals(message)

    def edit_goals_task(self, message):
        u = message.chat.id
        goalslist[u][index[u]] = message.text
        self.savedata(message, self.tag, goalslist[u])
        self.showgoals(message)

    def edit_goals_description(self, message):
        u = message.chat.id
        goalsdescr[u][index[u]] = message.text
        self.savedata(message, 'goals_descr', goalsdescr[u])
        self.showgoals(message)

    def edit_goals_position(self, message):
        u = message.chat.id
        if message.text.isdigit():
            if int(message.text) in range(len(goalslist[u])):
                sequence = int(message.text) - 1
                insert = goalslist[u][index[u]]
                insert_descr = goalsdescr[u][index[u]]
                insert_comp = goalscomp[u][index[u]]
                goalslist[u].pop(index[u])
                goalsdescr[u].pop(index[u])
                goalscomp[u].pop(index[u])
                goalslist[u].insert(sequence, insert)
                goalsdescr[u].insert(sequence, insert_descr)
                goalscomp[u].insert(sequence, insert_comp)
                self.savedata(message, self.tag, goalslist[u])
                self.savedata(message, 'goals_descr', goalsdescr[u])
                self.savedata(message, 'goals_comp', goalscomp[u])
                self.showgoals(message)
            else:
                self.showgoals(message)
        else:
            self.showgoals(message)

# setting reminder
    def setreminder(self, message):
        msg = bot.send_message(message.chat.id, 'What would you like to to do with <b>reminders settings</b>?',
                               parse_mode='html', reply_markup=reminder_markup)
        bot.register_next_step_handler(msg, self.selectreminder)

    def selectreminder(self, message):
        u = message.chat.id
        if message.text == '\U0001F515 Switch off FOCUS regime':
            try:
                scheduler[u].remove_job('job1')
            except KeyError:
                pass
            try:
                scheduler[u].remove_job('job2')
            except KeyError:
                pass
            try:
                scheduler[u].remove_job('job3')
            except KeyError:
                pass
            bot.send_message(u, f'FOCUS regime is <b>OFF</b>', parse_mode='html', reply_markup=self.markup)
        elif message.text == '\U0001F514 Switch on / Adjust FOCUS regime':
            try:
                scheduler[u].remove_job('job1')
            except KeyError:
                pass
            try:
                scheduler[u].remove_job('job2')
            except KeyError:
                pass
            try:
                scheduler[u].remove_job('job3')
            except KeyError:
                pass
            msg = bot.reply_to(message, f'What is your <b>current local time</b>?'
                                        f'(24h format, e.g. 14:00)', parse_mode='html')
            bot.register_next_step_handler(msg, self.process_user_time)
        else:
            self.showtasks(message)

    def process_user_time(self, message):
        u = message.chat.id
        isvaliddate = True
        try:
            current_time[u] = datetime.strptime(message.text, '%H:%M')
        except IndexError:
            isvaliddate = False
        except ValueError:
            isvaliddate = False
        if isvaliddate:
            utc_date = datetime.utcnow().strftime('%H:%M')
            utc_date = datetime.strptime(utc_date, '%H:%M')
            if current_time[u] >= utc_date:
                before_after[u] = True
                diff = current_time[u] - utc_date
            else:
                before_after[u] = False
                diff = utc_date - current_time[u]
            minutes_number = round((int(str(diff).split(':')[0]) * 60 + int(str(diff).split(':')[1]) + 1) / 10) * 10
            self.savedata(message, 'difference for', minutes_number)
            msg = bot.reply_to(message, f'<b>From which hour</b> would you like to get reminder?'
                                        f'\nE.g. 8', parse_mode='html')
            bot.register_next_step_handler(msg, self.process_from_reminder)
        else:
            msg = bot.reply_to(message, f'What is your <b>current local time</b>?'
                                        f'(24h format, e.g. 14:00)', parse_mode='html')
            bot.register_next_step_handler(msg, self.process_user_time)

    def process_from_reminder(self, message):
        u = message.chat.id
        isvaliddate = True
        try:
            from_reminder[u] = datetime(2022, 1, 1, int(message.text), 0)
        except IndexError:
            isvaliddate = False
        except ValueError:
            isvaliddate = False
        if isvaliddate:
            difference[u] = eval(open(f'users\\difference for {u}.txt', encoding='utf-8').read())
            from_local_reminder[u] = message.text
            if before_after[u]:
                from_reminder[u] -= timedelta(minutes=int(difference[u]))
            else:
                from_reminder[u] += timedelta(minutes=int(difference[u]))
            from_reminder[u] = [from_reminder[u].strftime('%H'), from_reminder[u].strftime('%M')]
            msg = bot.reply_to(message, f'<b>Till which hour</b> would you like to get reminder?'
                                        f'\nE.g. 23', parse_mode='html')
            bot.register_next_step_handler(msg, self.process_till_reminder)
        else:
            msg = bot.reply_to(message, f'<b>From which hour</b> would you like to get reminder?'
                                        f'\nE.g. 8', parse_mode='html')
            bot.register_next_step_handler(msg, self.process_from_reminder)

    def process_till_reminder(self, message):
        u = message.chat.id
        isvaliddate = True
        try:
            till_reminder[u] = datetime(2022, 1, 1, int(message.text), 0)
        except IndexError:
            isvaliddate = False
        except ValueError:
            isvaliddate = False
        if isvaliddate:
            till_local_reminder[u] = message.text
            if before_after[u]:
                till_reminder[u] -= timedelta(minutes=int(difference[u]))
            else:
                till_reminder[u] += timedelta(minutes=int(difference[u]))
            till_reminder[u] = [till_reminder[u].strftime('%H'), till_reminder[u].strftime('%M')]
            self.savedata(message, 'from_reminder', from_reminder[u])
            self.savedata(message, 'till_reminder', till_reminder[u])
            bot.reply_to(message, f'<b>FOCUS regime is ON.</b> \nReminder has been set '
                                  f'\n<b>from {from_local_reminder[u]}:00 till {till_local_reminder[u]}:00</b>',
                         parse_mode='html', reply_markup=self.markup)
            scheduler[u] = BackgroundScheduler({'apscheduler.timezone': 'UTC'}, job_defaults={'misfire_grace_time': 60})
            if from_reminder[u][0] <= till_reminder[u][0]:
                scheduler[u].add_job(self.reminder, 'cron', hour=f'{from_reminder[u][0]}-{till_reminder[u][0]}',
                                     minute=from_reminder[u][1], id='job1', args=[message])
            else:
                scheduler[u].add_job(self.reminder, 'cron', hour=f'{from_reminder[u][0]}-23',
                                     minute=from_reminder[u][1], id='job2', args=[message])
                scheduler[u].add_job(self.reminder, 'cron', hour=f'0-{till_reminder[u][0]}',
                                     minute=from_reminder[u][1], id='job3', args=[message])
            scheduler[u].start()
        else:
            msg = bot.reply_to(message, f'<b>Till which hour</b> would you like to get reminder?'
                                        f'\nE.g. 23',
                               parse_mode='html')
            bot.register_next_step_handler(msg, self.process_till_reminder)

    @staticmethod
    def reminder(message):
        u = message.chat.id
        from_reminder[u] = eval(open(f'users\\from_reminder {u}.txt', encoding='utf-8').read())
        till_reminder[u] = eval(open(f'users\\till_reminder {u}.txt', encoding='utf-8').read())
        current_time_hr = datetime.utcnow().strftime("%H")
        if int(current_time_hr) == int(from_reminder[u][0]) or int(current_time_hr) == int(till_reminder[u][0]):
            bot.send_message(u, f'\U000023F0  FOCUS on <b>what you need to do now</b>'
                                f'\nRemember to create your <b>Plan for the day</b> and get points in '
                                f'<b>Completed tasks report</b>', parse_mode='html')
        else:
            bot.send_message(u, f'\U000023F0  FOCUS on <b>what you need to do now</b>', parse_mode='html')


mainmenu_markup = Menu.createmarkup('\U0001F4C6 Plan for the day', '\U00002705 Completed tasks Report',
                                    '\U0001F5C2 General tasks List', '\U0001F9ED Strategic goals',
                                    '\U0001F3C6 My Rating', '\U00002139 About bot')

plan_markup = Menu.createmarkup('\U00002795 Add task to the Plan', '\U0001F50D Specific task in the Plan',
                                '\U0001F5D1 Delete the whole Plan', '\U000023F0 Reminders settings',
                                '\U0001F3E0 Main Menu')

plantask_markup = Menu.createmarkup('\U0001F58A Edit the task', '\U00002705 Mark as completed',
                                    '\U0001F5C2 Transfer to General List', '\U00002195 Change position',
                                    '\U000027162  Duplicate the task', '\U0001F5D1 Delete the task',
                                    '\U00002B05 Return to current Plan')

fulfilled_markup = Menu.createmarkup('\U00002795 Add task to the Report', '\U0001F50D Specific task in the Report',
                                     '\U0001F4B0 Get points', '\U0001F3E0 Main Menu')

fulfilledtask_markup = Menu.createmarkup('\U0001F58A Edit the task', '\U0001F4C6 Transfer to Plan for the day',
                                         '\U0001F5C2 Transfer to General List', '\U0001F5C2 Copy to General List',
                                         '\U00002195 Change position', '\U000027162  Duplicate the task',
                                         '\U0001F5D1 Delete the task', '\U00002B05 Return to current Report')

list_markup = Menu.createmarkup('\U00002795 Add task to the List', '\U0001F50D Specific task in the List',
                                '\U0001F5D1 Delete the whole List', '\U0001F3E0 Main Menu')

listtask_markup = Menu.createmarkup('\U0001F58A Edit the task', '\U00002705 Mark as completed',
                                    '\U0001F4C6 Transfer to Plan for the day', '\U0001F4C6 Copy to Plan for the day',
                                    '\U00002195 Change position', '\U000027162  Duplicate the task',
                                    '\U0001F5D1 Delete the task', '\U00002B05 Return to current List')

rating_markup = Menu.createmarkup('Main menu')

deleteall_markup = Menu.createmarkup('Yes, let\'s start from scratch', 'No, return back')

getpoints_markup = Menu.createmarkup('Yes, give me the points', 'No, return back')

reminder_markup = Menu.createmarkup('\U0001F514 Switch on / Adjust FOCUS regime', '\U0001F515 Switch off FOCUS regime',
                                    '\U00002B05 Return to current Plan')

info_markup = Menu.createmarkup('\U0001F4C6 About Plan', '\U00002705 About Report',
                                '\U0001F5C2 About List', '\U0001F9ED About Goals',
                                '\U0001F3C6 About Rating', '\U00002753 How to use',
                                '\U0001F3E0 Main Menu')

return_info_markup = Menu.createmarkup('\U00002B05 Return to About bot section')

goals_markup = Menu.createmarkup('\U00002795 Add goal', '\U0001F50D Specific goal',
                                 '\U0001F5D1 Delete all goals', '\U0001F3E0 Main Menu')

goals_specific_markup = Menu.createmarkup('\U0001F58A Edit the goal', '\U0001F4DD Add/edit description',
                                          '\U00002705 Select completion level', '\U00002195 Change position',
                                          '\U000027162  Duplicate the goal', '\U0001F5D1 Delete the goal',
                                          '\U00002B05 Return to Strategic Goals')

completion_markup = Menu.createmarkup('0%', '25%', '50%', '75%', '100%')


main_menu = Menu(menu='Main Menu', markup=mainmenu_markup)
plan_menu = Menu(menu='Plan for the day', tag='plan', icon='\U00002611', markup=plan_markup)
plan_menu.task_markup = plantask_markup
fulfilled_menu = Menu(menu='Completed tasks Report', tag='fulfilled', icon='\U00002705', markup=fulfilled_markup)
fulfilled_menu.task_markup = fulfilledtask_markup
list_menu = Menu(menu='General tasks List', tag='generallist', icon='\U00002611', markup=list_markup)
list_menu.task_markup = listtask_markup
goals_menu = Menu(menu='Strategic goals', tag='goals', markup=goals_markup)
rating_menu = Menu(menu='My Rating', tag='rating', markup=rating_markup)
info_menu = Menu(menu='About bot', markup=info_markup)


@bot.message_handler(commands=['start'])
def kickstart(message):
    u = message.chat.id
    Menu.savedata(message, plan_menu.tag, '[]')
    Menu.savedata(message, fulfilled_menu.tag, '[]')
    Menu.savedata(message, list_menu.tag, '[]')
    Menu.savedata(message, rating_menu.tag, '0')
    Menu.savedata(message, 'from_reminder', '8')
    Menu.savedata(message, 'till_reminder', '23')
    Menu.savedata(message, goals_menu.tag, '[]')
    Menu.savedata(message, 'goals_descr', '[]')
    Menu.savedata(message, 'goals_comp', '[]')
    bot.send_message(u, f'Hello <b>{message.from_user.first_name}</b>!'
                     '\n<b>Welcome to Goal Achiever!</b> '
                     '\nThis bot will help you achieve your goals, stay focused on tasks and track your progress.'
                     '\nType /start - if you want to <b>reset</b> all your data and start from scratch'
                     '\nClick on respective button in the bottom menu to proceed to respective section.'
                     '\nWhat would you like to work on now?', parse_mode='html', reply_markup=mainmenu_markup)


@bot.message_handler(regexp='Main Menu')
def welcome(message):
    main_menu.showmainmenu(message)


@bot.message_handler(regexp='Plan for the day')
def welcome(message):
    plan_menu.showtasks(message)


@bot.message_handler(regexp='Add task to the Plan')
def welcome(message):
    plan_menu.addtask(message)


@bot.message_handler(regexp='Delete the whole Plan')
def welcome(message):
    plan_menu.deleteall(message)


@bot.message_handler(regexp='Specific task in the Plan')
def welcome(message):
    plan_menu.specifictask(message)


@bot.message_handler(regexp='Reminders settings')
def welcome(message):
    plan_menu.setreminder(message)


@bot.message_handler(regexp='Completed tasks Report')
def welcome(message):
    fulfilled_menu.showtasks(message)


@bot.message_handler(regexp='Add task to the Report')
def welcome(message):
    fulfilled_menu.addtask(message)


@bot.message_handler(regexp='Get points')
def welcome(message):
    fulfilled_menu.getpoints(message)


@bot.message_handler(regexp='Specific task in the Report')
def welcome(message):
    fulfilled_menu.specifictask(message)


@bot.message_handler(regexp='General tasks List')
def welcome(message):
    list_menu.showtasks(message)


@bot.message_handler(regexp='Add task to the List')
def welcome(message):
    list_menu.addtask(message)


@bot.message_handler(regexp='Delete the whole List')
def welcome(message):
    list_menu.deleteall(message)


@bot.message_handler(regexp='Specific task in the List')
def welcome(message):
    list_menu.specifictask(message)


@bot.message_handler(regexp='My rating')
def welcome(message):
    rating_menu.showrating(message)


@bot.message_handler(regexp='About bot')
def welcome(message):
    info_menu.showinfo(message)


@bot.message_handler(regexp='Return to About bot section')
def welcome(message):
    info_menu.showinfo(message)


@bot.message_handler(regexp='Strategic goals')
def welcome(message):
    goals_menu.showgoals(message)


@bot.message_handler(regexp='Add goal')
def welcome(message):
    goals_menu.addgoal(message)


@bot.message_handler(regexp='Delete all goals')
def welcome(message):
    goals_menu.deletegoals(message)


@bot.message_handler(regexp='Specific goal')
def welcome(message):
    goals_menu.specificgoal(message)


# --------------------------------------
bot.enable_save_next_step_handlers(delay=1)
bot.load_next_step_handlers()
bot.infinity_polling()
