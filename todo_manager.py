import os
import datetime
from collections import OrderedDict
from peewee import *

db = SqliteDatabase('todo_list.db')

class ToDo(Model):
    """Model for creating to-do items. 'done' indicates that has been completed."""
    task = CharField(max_length=255)
    timestamp = DateTimeField(default=datetime.datetime.now)
    done = BooleanField(default=False)

    class Meta:
        database = db


def initialize():
    """Connect to database, build tables if they don't exist"""
    db.connect()
    db.create_tables([ToDo], safe=True)


def view_entries(index, entries, single_entry, search_query=None):
    """"View to-do list"""
    index = index % len(entries)  
    if single_entry: 
        entries = [entries[index]]
        index = 0
    else:
        print('\nMY TO-DO LIST')
        print('=' * 40)
    prev_timestamp = None

    entries = ToDo.select().order_by(ToDo.timestamp.desc())
    if search_query:
        entries = entries.where(ToDo.task.contains(search_query))

    for ind, entry in enumerate(entries):
        timestamp = entry.timestamp.strftime('%d/%B/%Y')

        if timestamp != prev_timestamp:  
            print('\n')
            print(timestamp)
            print('=' * len(timestamp))
            prev_timestamp = timestamp

        if ind == index:  
            tick = '> '
        else:
            tick = '  '

        print('{}{}'.format(tick, entry.task), end='')
        if entry.done:
            print('\t(DONE)', end='')
        print('')

    return entries


def search_entries(index, entries):
    """Search entries"""
    view_entries(input('Search: '))


def add_entry(index, entries):
    """Add a new task"""
    new_task = input('\nTo do: ')
    while len(new_task) < 5:
        print("It seems too short to be a proper task... Try again!")
        new_task = input('\nTo do: ')
    ToDo.create(task=new_task)


def modify_entry(index, entries):
    """Modify selected entry"""
    entry = view_entries(index, entries, True)[0]
    print('\n\n')

    for key, value in sub_menu.items():
        print('{}) {}'.format(key, sub_menu[key].__doc__))
    print('q) Back to Main')
    next_action = input('Action: ')

    if next_action.lower().strip() in sub_menu:
        sub_menu[next_action](entry)
    else:
        return


def edit_task(entry):
    """Edit task"""
    new_task = input('> ')
    while len(new_task) < 5:
        print("It seems too short to be a proper task... Try again!")
        new_task = input('> ')
    entry.task = new_task
    entry.save()


def delete_entry(entry):
    """Delete entry"""
    if (input('Are you sure [yN]? ').lower().strip() == 'y'):
        entry.delete_instance()


def toggle_done(entry):
    """Toggle 'DONE'"""
    entry.done = not entry.done
    entry.save()


def menu_loop():
    choice = None
    index = 0
    entries = ToDo.select().order_by(ToDo.timestamp.desc())
    while choice != 'q':
        if len(entries) != 0:
            view_entries(index, entries, False)

            print('\n' + '=' * 40 + '\n')
            print('Previous/Next: p/n \n')
        for key, value in main_menu.items():
            print('{}) {}'.format(key, value.__doc__))
        print('q) Quit')

        choice = input('\nAction: ')
        if choice in main_menu:
            try:
                main_menu[choice](index, entries)
            except ZeroDivisionError:
                continue
            entries = ToDo.select().order_by(ToDo.timestamp.desc())

        elif choice == 'n':
            index += 1
        elif choice == 'p':
            index -= 1


main_menu = OrderedDict([
    ('a', add_entry),
    ('m', modify_entry),
    ('s', search_entries)
])

sub_menu = OrderedDict([
    ('e', edit_task),
    ('t', toggle_done),
    ('d', delete_entry)
])

if __name__ == '__main__':
    initialize()
    menu_loop()
    db.close()
