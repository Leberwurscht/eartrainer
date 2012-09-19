#!/usr/bin/env python

import gobject
gobject.threads_init()

import pygst
pygst.require('0.10')
import gst

import binascii, StringIO

class MidiNoteSource(gst.BaseSrc):
    __gsttemplates__ = (
        gst.PadTemplate("src",
                        gst.PAD_SRC,
                        gst.PAD_ALWAYS,
                        gst.caps_new_any()),
        )

    blocksize = 4096
    fd = None

    def __init__(self, name=None, note=None):
        self.__gobject_init__()
        self.curoffset = 0
        if name is not None: self.set_name(name)
        if note is not None: self.set_note(note)

    def set_note(self, note):
        self.fd = StringIO.StringIO(binascii.unhexlify("4d546864000000060000000101e04d54726b0000002600ff510307a12000ff5902000000ff58040402300800c0180090%x69816f80%x00820aff2f00" % (note+69, note+69)))

    def set_property(self, name, value):
        if name == 'note':
            self.set_note(value)

    def do_create(self, offset, size):
        if offset != self.curoffset:
            self.fd.seek(offset, 0)
        data = self.fd.read(self.blocksize)
        if data:
            self.curoffset += len(data)
            return gst.FLOW_OK, gst.Buffer(data)
        else:
            return gst.FLOW_UNEXPECTED, None
gobject.type_register(MidiNoteSource)

class NotePlayer:
    def __init__(self, note):
        self.pipeline = gst.Pipeline()

        self.midinotesrc = MidiNoteSource('midinotesrc', note)
        self.wildmidi = gst.element_factory_make('wildmidi')
        self.sink = gst.element_factory_make('gconfaudiosink')

        self.pipeline.add(self.midinotesrc, self.wildmidi, self.sink)
        gst.element_link_many(self.midinotesrc, self.wildmidi, self.sink)

        self.pipeline.get_bus().add_watch(self.bus_event)

    def play(self):
        self.pipeline.set_state(gst.STATE_PLAYING)

    def bus_event(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.pipeline.set_state(gst.STATE_NULL)
        elif t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "Error: %s" % err, debug

        return True

def play_note(note):
    player = NotePlayer(note)
    player.play()
