import tkinter as tk
from tkinter import filedialog, ttk
import threading
import time
import pygame
import re
import os
import math
import random
from PIL import Image, ImageTk, ImageDraw
import colorsys
try:
    import speech_recognition as sr
except Exception:
    sr = None

def start_play():
    if playing:
        return
    t = threading.Thread(target=play_thread, daemon=True)
    t.start()

def pause_play():
    global paused
    if not playing:
        return
    paused = not paused
    if paused:
        pygame.mixer.music.pause()
        status_var.set('⏸️ Paused')
    else:
        pygame.mixer.music.unpause()
        status_var.set('▶️ Playing')


def load_audio():
    global audio_path
    p = filedialog.askopenfilename(filetypes=[('Audio files', '*.mp3 *.wav *.ogg *.m4a *.flac')])
    if p:
        audio_path = p
        status_var.set('🎵 Audio loaded: ' + os.path.basename(p))
        # Update progress bar maximum
        try:
            sound = pygame.mixer.Sound(p)
            total_duration = sound.get_length()
            progress_var.set(0)
        except:
            pass

def load_lrc():
    global lrc_path, lines
    p = filedialog.askopenfilename(filetypes=[('LRC files', '*.lrc'), ('Text', '*.txt')])
    if p:
        lrc_path = p
        lines = parse_lrc(p)
        status_var.set('📝 LRC loaded: ' + os.path.basename(p))
        if lines:
            orig_label.config(text=lines[0][1])

def auto_detect_lyrics():
    global lines
    if not audio_path:
        status_var.set('❌ Please load audio first')
        return
    if not sr:
        status_var.set('❌ speech_recognition library not installed')
        return
    status_var.set('🔍 Detecting lyrics (this may take a while)...')
    
    def job():
        r = sr.Recognizer()
        try:
            with sr.AudioFile(audio_path) as source:
                audio = r.record(source)
            text = r.recognize_google(audio)
            words = text.split()
            est_dur = pygame.mixer.Sound(audio_path).get_length() if pygame.mixer.get_init() else 30
            lines = lines_from_text(words, est_dur)
            root.after(0, lambda: status_var.set('✅ Auto-detected lyrics ready!'))
            if lines:
                root.after(0, lambda: orig_label.config(text=lines[0][1]))
        except Exception as e:
            root.after(0, lambda: status_var.set(f'❌ Auto-detect failed: {str(e)}'))
    
    threading.Thread(target=job, daemon=True).start()


# Extended periodic table with more elements
periodic_table = {
    "H": {"name": "Hydrogen", "atomic_number": 1, "atomic_mass": 1.008, "group": 1, "period": 1, "block": "s", "category": "Nonmetal", "color": "#FF6B6B"},
    "He": {"name": "Helium", "atomic_number": 2, "atomic_mass": 4.0026, "group": 18, "period": 1, "block": "s", "category": "Noble gas", "color": "#FFD93D"},
    "Li": {"name": "Lithium", "atomic_number": 3, "atomic_mass": 6.94, "group": 1, "period": 2, "block": "s", "category": "Alkali metal", "color": "#6BCF7F"},
    "Be": {"name": "Beryllium", "atomic_number": 4, "atomic_mass": 9.0122, "group": 2, "period": 2, "block": "s", "category": "Alkaline earth metal", "color": "#4ECDC4"},
    "B": {"name": "Boron", "atomic_number": 5, "atomic_mass": 10.81, "group": 13, "period": 2, "block": "p", "category": "Metalloid", "color": "#45B7D1"},
    "C": {"name": "Carbon", "atomic_number": 6, "atomic_mass": 12.011, "group": 14, "period": 2, "block": "p", "category": "Nonmetal", "color": "#96CEB4"},
    "N": {"name": "Nitrogen", "atomic_number": 7, "atomic_mass": 14.007, "group": 15, "period": 2, "block": "p", "category": "Nonmetal", "color": "#FFEAA7"},
    "O": {"name": "Oxygen", "atomic_number": 8, "atomic_mass": 15.999, "group": 16, "period": 2, "block": "p", "category": "Nonmetal", "color": "#DDA0DD"},
    "F": {"name": "Fluorine", "atomic_number": 9, "atomic_mass": 18.998, "group": 17, "period": 2, "block": "p", "category": "Halogen", "color": "#98D8C8"},
    "Ne": {"name": "Neon", "atomic_number": 10, "atomic_mass": 20.180, "group": 18, "period": 2, "block": "p", "category": "Noble gas", "color": "#F7DC6F"},
    "Na": {"name": "Sodium", "atomic_number": 11, "atomic_mass": 22.990, "group": 1, "period": 3, "block": "s", "category": "Alkali metal", "color": "#BB8FCE"},
    "Mg": {"name": "Magnesium", "atomic_number": 12, "atomic_mass": 24.305, "group": 2, "period": 3, "block": "s", "category": "Alkaline earth metal", "color": "#85C1E9"},
    "Al": {"name": "Aluminium", "atomic_number": 13, "atomic_mass": 26.982, "group": 13, "period": 3, "block": "p", "category": "Post-transition metal", "color": "#F8C471"},
    "Si": {"name": "Silicon", "atomic_number": 14, "atomic_mass": 28.085, "group": 14, "period": 3, "block": "p", "category": "Metalloid", "color": "#82E0AA"},
    "P": {"name": "Phosphorus", "atomic_number": 15, "atomic_mass": 30.974, "group": 15, "period": 3, "block": "p", "category": "Nonmetal", "color": "#F1948A"},
    "S": {"name": "Sulfur", "atomic_number": 16, "atomic_mass": 32.06, "group": 16, "period": 3, "block": "p", "category": "Nonmetal", "color": "#F7DC6F"},
    "Cl": {"name": "Chlorine", "atomic_number": 17, "atomic_mass": 35.45, "group": 17, "period": 3, "block": "p", "category": "Halogen", "color": "#ABEBC6"},
    "Ar": {"name": "Argon", "atomic_number": 18, "atomic_mass": 39.948, "group": 18, "period": 3, "block": "p", "category": "Noble gas", "color": "#D7BDE2"},
    "K": {"name": "Potassium", "atomic_number": 19, "atomic_mass": 39.098, "group": 1, "period": 4, "block": "s", "category": "Alkali metal", "color": "#F9E79F"},
    "Ca": {"name": "Calcium", "atomic_number": 20, "atomic_mass": 40.078, "group": 2, "period": 4, "block": "s", "category": "Alkaline earth metal", "color": "#AED6F1"},
    "Sc": {"name": "Scandium", "atomic_number": 21, "atomic_mass": 44.956, "group": 3, "period": 4, "block": "d", "category": "Transition metal", "color": "#A3E4D7"},
    "Ti": {"name": "Titanium", "atomic_number": 22, "atomic_mass": 47.867, "group": 4, "period": 4, "block": "d", "category": "Transition metal", "color": "#FAD7A0"},
    "V": {"name": "Vanadium", "atomic_number": 23, "atomic_mass": 50.942, "group": 5, "period": 4, "block": "d", "category": "Transition metal", "color": "#E8DAEF"},
    "Cr": {"name": "Chromium", "atomic_number": 24, "atomic_mass": 51.996, "group": 6, "period": 4, "block": "d", "category": "Transition metal", "color": "#F5B7B1"},
    "Mn": {"name": "Manganese", "atomic_number": 25, "atomic_mass": 54.938, "group": 7, "period": 4, "block": "d", "category": "Transition metal", "color": "#D5DBDB"},
    "Fe": {"name": "Iron", "atomic_number": 26, "atomic_mass": 55.845, "group": 8, "period": 4, "block": "d", "category": "Transition metal", "color": "#FDEBD0"},
    "Co": {"name": "Cobalt", "atomic_number": 27, "atomic_mass": 58.933, "group": 9, "period": 4, "block": "d", "category": "Transition metal", "color": "#D6EAF8"},
    "Ni": {"name": "Nickel", "atomic_number": 28, "atomic_mass": 58.693, "group": 10, "period": 4, "block": "d", "category": "Transition metal", "color": "#D1F2EB"},
    "Cu": {"name": "Copper", "atomic_number": 29, "atomic_mass": 63.546, "group": 11, "period": 4, "block": "d", "category": "Transition metal", "color": "#FCF3CF"},
    "Zn": {"name": "Zinc", "atomic_number": 30, "atomic_mass": 65.38, "group": 12, "period": 4, "block": "d", "category": "Transition metal", "color": "#FDEDEC"},
    "Ga": {"name": "Gallium", "atomic_number": 31, "atomic_mass": 69.723, "group": 13, "period": 4, "block": "p", "category": "Post-transition metal", "color": "#EAECEE"},
    "Ge": {"name": "Germanium", "atomic_number": 32, "atomic_mass": 72.630, "group": 14, "period": 4, "block": "p", "category": "Metalloid", "color": "#FEF9E7"},
    "As": {"name": "Arsenic", "atomic_number": 33, "atomic_mass": 74.922, "group": 15, "period": 4, "block": "p", "category": "Metalloid", "color": "#EAF2F8"},
    "Se": {"name": "Selenium", "atomic_number": 34, "atomic_mass": 78.971, "group": 16, "period": 4, "block": "p", "category": "Nonmetal", "color": "#FDEDEC"},
    "Br": {"name": "Bromine", "atomic_number": 35, "atomic_mass": 79.904, "group": 17, "period": 4, "block": "p", "category": "Halogen", "color": "#F4ECF7"},
    "Kr": {"name": "Krypton", "atomic_number": 36, "atomic_mass": 83.798, "group": 18, "period": 4, "block": "p", "category": "Noble gas", "color": "#EBF5FB"},
    "Rb": {"name": "Rubidium", "atomic_number": 37, "atomic_mass": 85.468, "group": 1, "period": 5, "block": "s", "category": "Alkali metal", "color": "#FDEBD0"},
    "Sr": {"name": "Strontium", "atomic_number": 38, "atomic_mass": 87.62, "group": 2, "period": 5, "block": "s", "category": "Alkaline earth metal", "color": "#E8F8F5"},
    "Y": {"name": "Yttrium", "atomic_number": 39, "atomic_mass": 88.906, "group": 3, "period": 5, "block": "d", "category": "Transition metal", "color": "#FEF9E7"},
    "Zr": {"name": "Zirconium", "atomic_number": 40, "atomic_mass": 91.224, "group": 4, "period": 5, "block": "d", "category": "Transition metal", "color": "#FDEDEC"},
    "Nb": {"name": "Niobium", "atomic_number": 41, "atomic_mass": 92.906, "group": 5, "period": 5, "block": "d", "category": "Transition metal", "color": "#F4ECF7"},
    "Mo": {"name": "Molybdenum", "atomic_number": 42, "atomic_mass": 95.95, "group": 6, "period": 5, "block": "d", "category": "Transition metal", "color": "#EAF2F8"},
    "Tc": {"name": "Technetium", "atomic_number": 43, "atomic_mass": 98, "group": 7, "period": 5, "block": "d", "category": "Transition metal", "color": "#EBF5FB"},
    "Ru": {"name": "Ruthenium", "atomic_number": 44, "atomic_mass": 101.07, "group": 8, "period": 5, "block": "d", "category": "Transition metal", "color": "#D5F5E3"},
    "Rh": {"name": "Rhodium", "atomic_number": 45, "atomic_mass": 102.91, "group": 9, "period": 5, "block": "d", "category": "Transition metal", "color": "#D6EAF8"},
    "Pd": {"name": "Palladium", "atomic_number": 46, "atomic_mass": 106.42, "group": 10, "period": 5, "block": "d", "category": "Transition metal", "color": "#FADBD8"},
    "Ag": {"name": "Silver", "atomic_number": 47, "atomic_mass": 107.87, "group": 11, "period": 5, "block": "d", "category": "Transition metal", "color": "#D1F2EB"},
    "Cd": {"name": "Cadmium", "atomic_number": 48, "atomic_mass": 112.41, "group": 12, "period": 5, "block": "d", "category": "Transition metal", "color": "#E8DAEF"},
    "In": {"name": "Indium", "atomic_number": 49, "atomic_mass": 114.82, "group": 13, "period": 5, "block": "p", "category": "Post-transition metal", "color": "#FCF3CF"},
    "Sn": {"name": "Tin", "atomic_number": 50, "atomic_mass": 118.71, "group": 14, "period": 5, "block": "p", "category": "Post-transition metal", "color": "#FDEBD0"},
    "Sb": {"name": "Antimony", "atomic_number": 51, "atomic_mass": 121.76, "group": 15, "period": 5, "block": "p", "category": "Metalloid", "color": "#EAF2F8"},
    "Te": {"name": "Tellurium", "atomic_number": 52, "atomic_mass": 127.60, "group": 16, "period": 5, "block": "p", "category": "Metalloid", "color": "#FDEDEC"},
    "I": {"name": "Iodine", "atomic_number": 53, "atomic_mass": 126.90, "group": 17, "period": 5, "block": "p", "category": "Halogen", "color": "#F4ECF7"},
    "Xe": {"name": "Xenon", "atomic_number": 54, "atomic_mass": 131.29, "group": 18, "period": 5, "block": "p", "category": "Noble gas", "color": "#D5F5E3"},
    "Cs": {"name": "Caesium", "atomic_number": 55, "atomic_mass": 132.91, "group": 1, "period": 6, "block": "s", "category": "Alkali metal", "color": "#D6EAF8"},
    "Ba": {"name": "Barium", "atomic_number": 56, "atomic_mass": 137.33, "group": 2, "period": 6, "block": "s", "category": "Alkaline earth metal", "color": "#FADBD8"},
    "La": {"name": "Lanthanum", "atomic_number": 57, "atomic_mass": 138.91, "group": 3, "period": 6, "block": "f", "category": "Lanthanide", "color": "#D1F2EB"},
    "Ce": {"name": "Cerium", "atomic_number": 58, "atomic_mass": 140.12, "group": 3, "period": 6, "block": "f", "category": "Lanthanide", "color": "#E8DAEF"},
    "Pr": {"name": "Praseodymium", "atomic_number": 59, "atomic_mass": 140.91, "group": 3, "period": 6, "block": "f", "category": "Lanthanide", "color": "#FCF3CF"},
    "Nd": {"name": "Neodymium", "atomic_number": 60, "atomic_mass": 144.24, "group": 3, "period": 6, "block": "f", "category": "Lanthanide", "color": "#FDEBD0"},
    "Pm": {"name": "Promethium", "atomic_number": 61, "atomic_mass": 145, "group": 3, "period": 6, "block": "f", "category": "Lanthanide", "color": "#EAF2F8"},
    "Sm": {"name": "Samarium", "atomic_number": 62, "atomic_mass": 150.36, "group": 3, "period": 6, "block": "f", "category": "Lanthanide", "color": "#FDEDEC"},
    "Eu": {"name": "Europium", "atomic_number": 63, "atomic_mass": 151.96, "group": 3, "period": 6, "block": "f", "category": "Lanthanide", "color": "#F4ECF7"},
    "Gd": {"name": "Gadolinium", "atomic_number": 64, "atomic_mass": 157.25, "group": 3, "period": 6, "block": "f", "category": "Lanthanide", "color": "#EBF5FB"},
    "Tb": {"name": "Terbium", "atomic_number": 65, "atomic_mass": 158.93, "group": 3, "period": 6, "block": "f", "category": "Lanthanide", "color": "#D5F5E3"},
    "Dy": {"name": "Dysprosium", "atomic_number": 66, "atomic_mass": 162.50, "group": 3, "period": 6, "block": "f", "category": "Lanthanide", "color": "#D6EAF8"},
    "Ho": {"name": "Holmium", "atomic_number": 67, "atomic_mass": 164.93, "group": 3, "period": 6, "block": "f", "category": "Lanthanide", "color": "#FADBD8"},
    "Er": {"name": "Erbium", "atomic_number": 68, "atomic_mass": 167.26, "group": 3, "period": 6, "block": "f", "category": "Lanthanide", "color": "#D1F2EB"},
    "Tm": {"name": "Thulium", "atomic_number": 69, "atomic_mass": 168.93, "group": 3, "period": 6, "block": "f", "category": "Lanthanide", "color": "#E8DAEF"},
    "Yb": {"name": "Ytterbium", "atomic_number": 70, "atomic_mass": 173.05, "group": 3, "period": 6, "block": "f", "category": "Lanthanide", "color": "#FCF3CF"},
    "Lu": {"name": "Lutetium", "atomic_number": 71, "atomic_mass": 174.97, "group": 3, "period": 6, "block": "d", "category": "Lanthanide", "color": "#FDEBD0"},
    "Hf": {"name": "Hafnium", "atomic_number": 72, "atomic_mass": 178.49, "group": 4, "period": 6, "block": "d", "category": "Transition metal", "color": "#EAF2F8"},
    "Ta": {"name": "Tantalum", "atomic_number": 73, "atomic_mass": 180.95, "group": 5, "period": 6, "block": "d", "category": "Transition metal", "color": "#FDEDEC"},
    "W": {"name": "Tungsten", "atomic_number": 74, "atomic_mass": 183.84, "group": 6, "period": 6, "block": "d", "category": "Transition metal", "color": "#F4ECF7"},
    "Re": {"name": "Rhenium", "atomic_number": 75, "atomic_mass": 186.21, "group": 7, "period": 6, "block": "d", "category": "Transition metal", "color": "#EBF5FB"},
    "Os": {"name": "Osmium", "atomic_number": 76, "atomic_mass": 190.23, "group": 8, "period": 6, "block": "d", "category": "Transition metal", "color": "#D5F5E3"},
    "Ir": {"name": "Iridium", "atomic_number": 77, "atomic_mass": 192.22, "group": 9, "period": 6, "block": "d", "category": "Transition metal", "color": "#D6EAF8"},
    "Pt": {"name": "Platinum", "atomic_number": 78, "atomic_mass": 195.08, "group": 10, "period": 6, "block": "d", "category": "Transition metal", "color": "#FADBD8"},
    "Au": {"name": "Gold", "atomic_number": 79, "atomic_mass": 196.97, "group": 11, "period": 6, "block": "d", "category": "Transition metal", "color": "#D1F2EB"},
    "Hg": {"name": "Mercury", "atomic_number": 80, "atomic_mass": 200.59, "group": 12, "period": 6, "block": "d", "category": "Transition metal", "color": "#E8DAEF"},
    "Tl": {"name": "Thallium", "atomic_number": 81, "atomic_mass": 204.38, "group": 13, "period": 6, "block": "p", "category": "Post-transition metal", "color": "#FCF3CF"},
    "Pb": {"name": "Lead", "atomic_number": 82, "atomic_mass": 207.2, "group": 14, "period": 6, "block": "p", "category": "Post-transition metal", "color": "#FDEBD0"},
    "Bi": {"name": "Bismuth", "atomic_number": 83, "atomic_mass": 208.98, "group": 15, "period": 6, "block": "p", "category": "Post-transition metal", "color": "#EAF2F8"},
    "Po": {"name": "Polonium", "atomic_number": 84, "atomic_mass": 209, "group": 16, "period": 6, "block": "p", "category": "Metalloid", "color": "#FDEDEC"},
    "At": {"name": "Astatine", "atomic_number": 85, "atomic_mass": 210, "group": 17, "period": 6, "block": "p", "category": "Halogen", "color": "#F4ECF7"},
    "Rn": {"name": "Radon", "atomic_number": 86, "atomic_mass": 222, "group": 18, "period": 6, "block": "p", "category": "Noble gas", "color": "#EBF5FB"},
    "Fr": {"name": "Francium", "atomic_number": 87, "atomic_mass": 223, "group": 1, "period": 7, "block": "s", "category": "Alkali metal", "color": "#D5F5E3"},
    "Ra": {"name": "Radium", "atomic_number": 88, "atomic_mass": 226, "group": 2, "period": 7, "block": "s", "category": "Alkaline earth metal", "color": "#D6EAF8"},
    "Ac": {"name": "Actinium", "atomic_number": 89, "atomic_mass": 227, "group": 3, "period": 7, "block": "f", "category": "Actinide", "color": "#FADBD8"},
    "Th": {"name": "Thorium", "atomic_number": 90, "atomic_mass": 232.04, "group": 3, "period": 7, "block": "f", "category": "Actinide", "color": "#D1F2EB"},
    "Pa": {"name": "Protactinium", "atomic_number": 91, "atomic_mass": 231.04, "group": 3, "period": 7, "block": "f", "category": "Actinide", "color": "#E8DAEF"},
    "U": {"name": "Uranium", "atomic_number": 92, "atomic_mass": 238.03, "group": 3, "period": 7, "block": "f", "category": "Actinide", "color": "#FCF3CF"}
}

# Greek letters for non-elements
greek_letters = {
    'α': 'Alpha', 'β': 'Beta', 'γ': 'Gamma', 'δ': 'Delta', 'ε': 'Epsilon',
    'ζ': 'Zeta', 'η': 'Eta', 'θ': 'Theta', 'ι': 'Iota', 'κ': 'Kappa',
    'λ': 'Lambda', 'μ': 'Mu', 'ν': 'Nu', 'ξ': 'Xi', 'ο': 'Omicron',
    'π': 'Pi', 'ρ': 'Rho', 'σ': 'Sigma', 'τ': 'Tau', 'υ': 'Upsilon',
    'φ': 'Phi', 'χ': 'Chi', 'ψ': 'Psi', 'ω': 'Omega'
}

symbols = {k.lower(): k for k in periodic_table}

# Create main window with dark theme
root = tk.Tk()
root.title('✨ Chem-Lyrics Player — The Ultimate Chemistry Experience ✨')
root.geometry('1200x800')
root.configure(bg='#1a1a2e')

# Custom styles
style = ttk.Style()
style.theme_use('clam')
style.configure('Dark.TFrame', background='#1a1a2e')
style.configure('Dark.TLabel', background='#1a1a2e', foreground='#ffffff', font=('Arial', 10))
style.configure('Title.TLabel', background='#1a1a2e', foreground='#6a11cb', font=('Arial', 18, 'bold'))
style.configure('Lyrics.TLabel', background='#1a1a2e', foreground='#e6e6e6', font=('Arial', 16, 'bold'))
style.configure('Element.TLabel', background='#162447', foreground='#ffffff', font=('Arial', 10, 'bold'))
style.configure('Dark.TButton', background='#162447', foreground='#ffffff', font=('Arial', 10))
style.map('Dark.TButton', background=[('active', '#0f3460')])

# Gradient background function
def create_gradient_bg():
    width, height = 1200, 800
    image = Image.new('RGB', (width, height), color='#1a1a2e')
    draw = ImageDraw.Draw(image)
    
    for y in range(height):
        # Create gradient from dark blue to purple
        r = int(26 + (y / height) * 100)
        g = int(26 + (y / height) * 30)
        b = int(46 + (y / height) * 100)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    return ImageTk.PhotoImage(image)

# Create animated background
class AnimatedBackground:
    def __init__(self, canvas):
        self.canvas = canvas
        self.particles = []
        self.colors = ['#6a11cb', '#2575fc', '#ff6b6b', '#4ecdc4', '#f7dc6f']
        self.create_particles()
        self.animate()
    
    def create_particles(self):
        for _ in range(50):
            x = random.randint(0, 1200)
            y = random.randint(0, 800)
            size = random.randint(1, 3)
            color = self.colors[random.randint(0, len(self.colors)-1)]
            dx = random.uniform(-0.5, 0.5)
            dy = random.uniform(-0.5, 0.5)
            particle = self.canvas.create_oval(x, y, x+size, y+size, fill=color, outline='')
            self.particles.append((particle, dx, dy))
    
    def animate(self):
        for particle, dx, dy in self.particles:
            self.canvas.move(particle, dx, dy)
            coords = self.canvas.coords(particle)
            if coords[0] <= 0 or coords[2] >= 1200:
                dx = -dx
            if coords[1] <= 0 or coords[3] >= 800:
                dy = -dy
        root.after(50, self.animate)

# Create main canvas for background
main_canvas = tk.Canvas(root, width=1200, height=800, highlightthickness=0)
main_canvas.pack(fill='both', expand=True)
bg_image = create_gradient_bg()
main_canvas.create_image(0, 0, image=bg_image, anchor='nw')

# Add title with glow effect
title_label = tk.Label(root, text='✨ Chem-Lyrics Player ✨', 
                      font=('Arial', 28, 'bold'), 
                      fg='#ffffff', 
                      bg='#1a1a2e',
                      bd=0)
title_window = main_canvas.create_window(600, 30, window=title_label)

# Top frame for controls
top_frame = ttk.Frame(root, style='Dark.TFrame')
main_canvas.create_window(600, 80, window=top_frame, width=1100)

# Controls
controls_frame = ttk.Frame(top_frame, style='Dark.TFrame')
controls_frame.pack(side='left', padx=10)

# Create beautiful gradient buttons
def create_gradient_button(parent, text, command, color1, color2):
    btn_frame = tk.Frame(parent, bg='#1a1a2e')
    btn = tk.Button(btn_frame, text=text, command=command, 
                   font=('Arial', 10, 'bold'),
                   bg=color1, fg='white',
                   activebackground=color2,
                   activeforeground='white',
                   bd=0, relief='flat',
                   padx=15, pady=8)
    btn.pack(padx=2, pady=2)
    return btn_frame

load_audio_btn = create_gradient_button(controls_frame, '🎵 Load Audio', load_audio, '#6a11cb', '#2575fc')
load_audio_btn.grid(row=0, column=0, padx=4, pady=4)

load_lrc_btn = create_gradient_button(controls_frame, '📝 Load LRC', load_lrc, '#ff6b6b', '#ff8e8e')
load_lrc_btn.grid(row=0, column=1, padx=4, pady=4)

auto_detect_btn = create_gradient_button(controls_frame, '🔍 Auto-detect Lyrics', auto_detect_lyrics, '#4ecdc4', '#67e6dc')
auto_detect_btn.grid(row=0, column=2, padx=4, pady=4)

play_btn = create_gradient_button(controls_frame, '▶️ Play', start_play, '#00b894', '#55efc4')
play_btn.grid(row=0, column=3, padx=4, pady=4)

pause_btn = create_gradient_button(controls_frame, '⏸️ Pause', pause_play, '#fdcb6e', '#ffeaa7')
pause_btn.grid(row=0, column=4, padx=4, pady=4)

# Status
status_var = tk.StringVar(value='🎯 Ready to explore chemistry through music!')
status_label = tk.Label(top_frame, textvariable=status_var, 
                       font=('Arial', 11, 'italic'),
                       fg='#4ecdc4', bg='#1a1a2e')
status_label.pack(side='left', padx=20)

# Center area for lyrics and elements
center_frame = ttk.Frame(root, style='Dark.TFrame')
main_canvas.create_window(600, 300, window=center_frame, width=1100, height=400)

# Original lyrics display
orig_label = tk.Label(center_frame, text='', 
                     font=('Arial', 18, 'bold'),
                     fg='#ffffff', bg='#1a1a2e',
                     wraplength=1000, justify='center')
orig_label.pack(pady=15)

# Chemistry elements display with enhanced styling
chem_frame = tk.Frame(center_frame, bg='#1a1a2e')
chem_frame.pack(fill='both', expand=True, pady=10)

# Create a canvas for chemistry elements with scrollbar
chem_canvas = tk.Canvas(chem_frame, bg='#1a1a2e', highlightthickness=0)
chem_scroll = ttk.Scrollbar(chem_frame, orient='vertical', command=chem_canvas.yview)
chem_inner = tk.Frame(chem_canvas, bg='#1a1a2e')

chem_inner.bind('<Configure>', lambda e: chem_canvas.configure(scrollregion=chem_canvas.bbox('all')))
chem_canvas.create_window((0, 0), window=chem_inner, anchor='nw')
chem_canvas.configure(yscrollcommand=chem_scroll.set, height=250)

chem_canvas.pack(side='left', fill='both', expand=True)
chem_scroll.pack(side='right', fill='y')

# Detail frame for element information
detail_frame = ttk.Frame(root, style='Dark.TFrame')
main_canvas.create_window(600, 650, window=detail_frame, width=1100, height=100)

detail_label = tk.Label(detail_frame, text='🔬 Hover over any element to see its details!', 
                       font=('Arial', 12),
                       fg='#f7dc6f', bg='#1a1a2e',
                       justify='left', wraplength=1000)
detail_label.pack(fill='x', padx=20, pady=10)

# Progress bar
progress_frame = ttk.Frame(root, style='Dark.TFrame')
main_canvas.create_window(600, 720, window=progress_frame, width=1100)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100, 
                              style='Horizontal.TProgressbar')
progress_bar.pack(fill='x', padx=20, pady=5)

time_label = tk.Label(progress_frame, text='00:00 / 00:00', 
                     font=('Arial', 10),
                     fg='#ffffff', bg='#1a1a2e')
time_label.pack()

# Initialize pygame
pygame.mixer.init()
audio_path = None
lrc_path = None
lines = []
playing = False
paused = False
current_index = 0
start_time = 0

# Enhanced Tooltip with styling
class Tooltip:
    def __init__(self, widget, textfunc, is_element=True):
        self.widget = widget
        self.textfunc = textfunc
        self.is_element = is_element
        self.top = None
        widget.bind('<Enter>', self.show)
        widget.bind('<Leave>', self.hide)
        widget.bind('<Button-1>', self.show_permanent)
    
    def show(self, event=None):
        if self.top:
            return
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        self.top = tk.Toplevel(self.widget)
        self.top.wm_overrideredirect(True)
        self.top.wm_geometry(f'+{x}+{y}')
        
        text = self.textfunc()
        bg_color = '#2d3436' if self.is_element else '#6c5ce7'
        
        label = tk.Label(self.top, text=text, justify='left', 
                        bg=bg_color, fg='white',
                        font=('Arial', 9),
                        bd=1, relief='solid', padx=8, pady=6)
        label.pack()
    
    def hide(self, event=None):
        if self.top:
            self.top.destroy()
            self.top = None
    
    def show_permanent(self, event=None):
        # Show details in the main detail area
        text = self.textfunc()
        detail_label.config(text=text)

def parse_lrc(path):
    with open(path, encoding='utf-8') as f:
        raw = f.read()
    parts = re.findall(r"\[(\d+):(\d+\.?\d*)\](.*)", raw)
    arr = []
    for m in parts:
        mm = int(m[0])
        ss = float(m[1])
        t = mm * 60 + ss
        txt = m[2].strip()
        arr.append((t, txt))
    arr.sort()
    return arr

def word_to_elements(word):
    w = re.sub('[^a-zA-Z]', '', word).lower()
    if not w:
        return []
    res = []
    i = 0
    while i < len(w):
        taken = False
        for l in (2, 1):
            if i + l <= len(w):
                chunk = w[i:i+l]
                if chunk in symbols:
                    res.append(symbols[chunk])
                    i += l
                    taken = True
                    break
        if not taken:
            ch = w[i]
            # Map non-element letters to Greek symbols
            if ch in 'qxzj':
                res.append('α')  # Alpha
            elif ch in 'wv':
                res.append('β')  # Beta
            elif ch in 'yk':
                res.append('γ')  # Gamma
            elif ch in 'mp':
                res.append('δ')  # Delta
            else:
                res.append('ε')  # Epsilon for others
            i += 1
    return res

def line_to_tokens(line):
    parts = line.split()
    tokens = []
    for p in parts:
        els = word_to_elements(p)
        tokens.append((p, els))
    return tokens

def lines_from_text(words, total_dur):
    if total_dur <= 0:
        return []
    avg = total_dur / max(1, len(words))
    arr = []
    t = 0.0
    buf = []
    for i, w in enumerate(words):
        buf.append(w)
        if len(buf) >= 4 or i == len(words)-1:
            arr.append((t, ' '.join(buf)))
            t += avg * len(buf)
            buf = []
    return arr

def clear_chem_frame():
    for c in chem_inner.winfo_children():
        c.destroy()

def create_element_box(parent, element, is_greek=False):
    if is_greek:
        # Greek letter display
        frame = tk.Frame(parent, bg='#6c5ce7', bd=1, relief='raised', padx=8, pady=6)
        symbol_label = tk.Label(frame, text=element, font=('Arial', 14, 'bold'), 
                               bg='#6c5ce7', fg='white')
        symbol_label.pack()
        name_label = tk.Label(frame, text=greek_letters.get(element, 'Greek'), 
                             font=('Arial', 8), bg='#6c5ce7', fg='white')
        name_label.pack()
        
        def tooltip_text():
            return f"Greek Letter: {greek_letters.get(element, 'Unknown')}\nUsed for non-element characters"
        
        Tooltip(frame, tooltip_text, is_element=False)
        return frame
    else:
        # Regular element display
        element_data = periodic_table.get(element, {})
        color = element_data.get('color', '#95a5a6')
        
        frame = tk.Frame(parent, bg=color, bd=1, relief='raised', padx=8, pady=6)
        
        # Atomic number (small, top left)
        atomic_num = element_data.get('atomic_number', '')
        num_label = tk.Label(frame, text=str(atomic_num), font=('Arial', 7), 
                            bg=color, fg='white')
        num_label.place(x=2, y=2)
        
        # Element symbol (big, center)
        symbol_label = tk.Label(frame, text=element, font=('Arial', 16, 'bold'), 
                               bg=color, fg='white')
        symbol_label.pack(pady=2)
        
        # Element name (small, bottom)
        name = element_data.get('name', 'Unknown')
        name_label = tk.Label(frame, text=name, font=('Arial', 7), 
                             bg=color, fg='white', wraplength=80)
        name_label.pack()
        
        # Atomic mass (small, bottom right)
        mass = element_data.get('atomic_mass', '')
        mass_label = tk.Label(frame, text=str(mass), font=('Arial', 7), 
                             bg=color, fg='white')
        mass_label.place(x=45, y=45)
        
        def tooltip_text():
            if element in periodic_table:
                d = periodic_table[element]
                return (f"🏷️  {d['name']} ({element})\n"
                       f"🔢 Atomic Number: {d['atomic_number']}\n"
                       f"⚖️  Atomic Mass: {d['atomic_mass']}\n"
                       f"📊 Group: {d.get('group', '-')}\n"
                       f"📈 Period: {d.get('period', '-')}\n"
                       f"🧩 Block: {d.get('block', '-')}\n"
                       f"📂 Category: {d.get('category', '-')}")
            return f"Element: {element}"
        
        Tooltip(frame, tooltip_text, is_element=True)
        return frame

def show_line_tokens(tokens):
    clear_chem_frame()
    row = 0
    col = 0
    
    for word, elements in tokens:
        # Word frame
        word_frame = tk.Frame(chem_inner, bg='#1a1a2e')
        word_frame.grid(row=row, column=col, padx=10, pady=5, sticky='n')
        
        # Word label
        word_label = tk.Label(word_frame, text=word, font=('Arial', 12, 'bold'),
                             fg='#ffffff', bg='#1a1a2e')
        word_label.pack()
        
        # Elements frame
        elements_frame = tk.Frame(word_frame, bg='#1a1a2e')
        elements_frame.pack(pady=5)
        
        # Create element boxes
        el_col = 0
        for element in elements:
            is_greek = element in greek_letters
            element_box = create_element_box(elements_frame, element, is_greek)
            element_box.grid(row=0, column=el_col, padx=2)
            el_col += 1
        
        col += 1
        if col >= 6:  # 6 words per row max
            col = 0
            row += 1
    
    # Update canvas scrollregion
    chem_inner.update_idletasks()
    chem_canvas.configure(scrollregion=chem_canvas.bbox('all'))

def play_thread():
    global start_time, playing, paused, current_index
    if not audio_path or not lines:
        status_var.set('❌ Please load audio and lyrics first')
        return
    
    try:
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
    except Exception as e:
        status_var.set(f'❌ Audio playback failed: {str(e)}')
        return
    
    start_time = time.time()
    playing = True
    paused = False
    current_index = 0
    
    total_duration = pygame.mixer.Sound(audio_path).get_length() if pygame.mixer.get_init() else 0
    
    while playing and current_index < len(lines):
        if paused:
            time.sleep(0.1)
            continue
        
        now = time.time() - start_time
        current_time, current_text = lines[current_index]
        end_time = lines[current_index + 1][0] if current_index + 1 < len(lines) else current_time + 5
        
        # Update progress
        progress = min(100, (now / total_duration) * 100) if total_duration > 0 else 0
        progress_var.set(progress)
        
        # Update time display
        current_str = f"{int(now // 60):02d}:{int(now % 60):02d}"
        total_str = f"{int(total_duration // 60):02d}:{int(total_duration % 60):02d}"
        time_label.config(text=f"{current_str} / {total_str}")
        
        if now + 0.05 >= current_time:
            # Typewriter effect for lyrics
            orig_label.config(text='')
            full_text = current_text
            tokens = line_to_tokens(full_text)
            
            # Animate text appearance
            def typewriter_effect(text, index=0):
                if index <= len(text):
                    orig_label.config(text=text[:index])
                    if index < len(text):
                        root.after(50, lambda: typewriter_effect(text, index + 1))
                    else:
                        # Show chemistry elements after text is fully displayed
                        show_line_tokens(tokens)
            
            typewriter_effect(full_text)
            
            # Calculate display duration for this line
            line_duration = end_time - current_time
            
            # Wait for the duration of this line
            line_start = time.time()
            while time.time() - line_start < line_duration and playing:
                if paused:
                    time.sleep(0.1)
                    continue
                time.sleep(0.05)
            
            current_index += 1
        else:
            time.sleep(0.05)
    
    status_var.set('🎉 Finished playing!')
    playing = False

# Connect buttons to functions
load_audio_btn.winfo_children()[0].config(command=load_audio)
load_lrc_btn.winfo_children()[0].config(command=load_lrc)
auto_detect_btn.winfo_children()[0].config(command=auto_detect_lyrics)
play_btn.winfo_children()[0].config(command=start_play)
pause_btn.winfo_children()[0].config(command=pause_play)

# Sample data for demonstration
sample_lrc = '''[00:00.00]Chemistry of Love
[00:05.00]Your morning eyes tell stories untold
[00:12.00]With elements of passion and bonds of gold
[00:20.00]Hydrogen whispers and Oxygen sings
[00:28.00]Creating the chemistry that love brings
[00:35.00]Carbon foundations strong and true
[00:42.00]Nitrogen dreams in skies so blue
[00:50.00]Together we form a compound rare
[00:57.00]A molecular dance beyond compare
'''

if not os.path.exists('chemistry_demo.lrc'):
    with open('chemistry_demo.lrc', 'w', encoding='utf-8') as f:
        f.write(sample_lrc)

if not lines:
    lines = parse_lrc('chemistry_demo.lrc')
    if lines:
        orig_label.config(text=lines[0][1])

# Start background animation
bg_animation = AnimatedBackground(main_canvas)

# Add some decorative elements
def add_decorations():
    # Add some chemistry-themed decorations
    decorations = [
        (100, 100, "⚗️", 20),
        (1100, 150, "🧪", 25),
        (150, 600, "🔬", 22),
        (1000, 650, "🌡️", 18),
    ]
    
    for x, y, emoji, size in decorations:
        main_canvas.create_text(x, y, text=emoji, font=('Arial', size), fill='rgba(255,255,255,0.1)')

add_decorations()

def on_resize(event):
    pass

root.bind('<Configure>', on_resize)

root.mainloop()