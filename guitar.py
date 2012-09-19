#!/usr/bin/python

import gtk, gobject
from playnote import play_note
import random

strings = "ebgdaE"
current_fret = 0
current_note = 0
buttons = {}
status = gtk.Label()
status.set_markup('<span size="x-large"> </span>')

right = 0
total = 0

def play(*args):
    global current_note
    play_note(current_note)

def new_question():
    global current_note

    current_note = random.randint(-29, -5+12)
    play()

def note_name(note):
    note_names = [" a ","ais"," b "," c" ,"cis"," d ","dis"," e "," f ","fis"," g ","gis"]

    while note<0: note += 12
    return note_names[note % 12]

def note(string, fret):
    tunings = [-5, -10, -14, -19, -24, -29]
    return tunings[string] + fret

def select(widget, data):
    global buttons, current_note, right, total

    string, fret = data
    try:
        buttons[string, fret].grab_focus()
    except KeyError: pass

    guess = note(string, fret)

    play_note(guess)

    total += 1
    if guess==current_note:
        right += 1
        status.set_markup('<span foreground="dark green" size="x-large">RIGHT</span> %d%%' % int(100.0*right/total))
        gobject.timeout_add(1500, new_question)
    else:
        status.set_markup('<span foreground="red" size="x-large">FALSE</span> %d%%' % int(100.0*right/total))
        gobject.timeout_add(400, play)

def key_callback(window, event):
    global current_fret, strings

    key = gtk.gdk.keyval_name(event.keyval)
    if key=="Escape":
        current_fret = 0
        play()

    if key.isdigit():
        current_fret *= 10
        current_fret += int(key)

    if key in strings:
        string = strings.index(key)
        fret = current_fret
        current_fret = 0
        select(None, (string, fret))

w = gtk.Window()
table = gtk.Table(7, 15, False)

for string in xrange(6):
    label = gtk.Label(" %s " % strings[string])
    table.attach(label, 0, 1, string+1, string+2)

circle = "\xe2\x97\x8f"
for fret in [5,7,9,12]:
    label = gtk.Label(circle)
    table.attach(label, fret+2, fret+3, 0, 1)

for string in xrange(6):
    #button = gtk.Button("%d/%d" % (string+1, 0))
    button = gtk.Button(note_name(note(string, 0)))
    button.connect("clicked", select, (string, 0))
    table.attach(button, 1, 2, string+1, string+2)
    buttons[string, 0] = button

    label = gtk.Label("|")
    table.attach(label, 2, 3, string+1, string+2)

    for fret in xrange(12):
        #button = gtk.Button("%d/%d" % (string+1, fret+1))
        button = gtk.Button(note_name(note(string, fret+1)))
        button.connect("clicked", select, (string, fret+1))
        table.attach(button, fret+3, fret+4, string+1, string+2)
        buttons[string, fret+1] = button

#status.connect("clicked", play)

vbox = gtk.VBox()
w.add(vbox)

vbox.add(status)
vbox.add(table)

w.set_events(gtk.gdk.KEY_PRESS_MASK)
w.connect("key_press_event", key_callback)

w.show_all()

w.connect("destroy", lambda *args: gtk.main_quit())
w.connect("delete_event", lambda *args: gtk.main_quit())

new_question()

gtk.main()
