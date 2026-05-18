"""Procedural sound effects — no audio files required."""
import math
import array
import pygame

_snd = {}


def _tone(freq, ms, vol=3000, decay=8.0, rate=22050):
    n = rate * ms // 1000
    buf = array.array('h')
    for i in range(n):
        t = i / rate
        env = math.exp(-t * decay)
        v = int(vol * env * math.sin(2 * math.pi * freq * t))
        v = max(-32767, min(32767, v))
        buf.append(v)
        buf.append(v)
    return pygame.mixer.Sound(buffer=buf)


def _chord(freqs, ms, vol=1800, decay=5.0, rate=22050):
    n = rate * ms // 1000
    nf = len(freqs)
    buf = array.array('h')
    for i in range(n):
        t = i / rate
        env = math.exp(-t * decay)
        raw = sum(math.sin(2 * math.pi * f * t) for f in freqs) / nf
        v = max(-32767, min(32767, int(vol * env * raw)))
        buf.append(v)
        buf.append(v)
    return pygame.mixer.Sound(buffer=buf)


def _arpeggio(notes, ms_each, vol=2200, decay=12.0, rate=22050):
    n_each = rate * ms_each // 1000
    buf = array.array('h')
    for freq in notes:
        for i in range(n_each):
            t = i / rate
            env = math.exp(-t * decay)
            v = max(-32767, min(32767, int(vol * env * math.sin(2 * math.pi * freq * t))))
            buf.append(v)
            buf.append(v)
    return pygame.mixer.Sound(buffer=buf)


def init():
    global _snd
    try:
        if not pygame.mixer.get_init():
            return
        _snd = {
            'walk':    _tone(160, 40, 700, 60),
            'door':    _chord([330, 440, 550], 200, 1400, 5),
            'tick':    _tone(880, 35, 600, 80),
            'confirm': _chord([523, 659, 784], 220, 1700, 5),
            'event':   _chord([440, 660], 260, 1900, 4),
            'econ':    _tone(110, 80, 500, 25),
            'shoot':   _tone(220, 65, 2200, 20),
            'win':     _arpeggio([261, 330, 392, 523, 659, 784, 1046], 110, 2200, 10),
            'lose':    _arpeggio([220, 196, 165, 147, 131, 110], 130, 1800, 8),
            'mg_good': _chord([660, 880], 200, 1700, 5),
            'mg_bad':  _tone(180, 200, 1800, 8),
        }
        for s in _snd.values():
            s.set_volume(0.35)
    except Exception:
        _snd = {}


def play(name, vol=None):
    s = _snd.get(name)
    if not s:
        return
    if vol is not None:
        s.set_volume(vol)
    s.play()
