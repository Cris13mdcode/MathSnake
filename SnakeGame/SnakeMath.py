import pygame, random, sys, os, math, json

pygame.init()

# Eliminăm apple_pulse deoarece merele nu mai pulsează
gold_apple = None
gold_timer = 0
gold_chance_counter = 0
badges = {
    "1games": False,
    "10games": False,
    "25games": False,
    "badge5win": False,
    "badge15win": False,
    "badge25win": False
}
games_played = 0
wins = 0
bucket_mode = False
coins = 0  # Sistem de coins
current_skin = "default"  # Sistem de skins
unlocked_skins = {"default": True}  # Sistem de deblocare skins
skin_prices = {"lime": 50, "poison": 300}  # Prețuri skins

# ─── Sistem XP și Autosave ───────────────────────────────────────────────
xp = 0  # Sistem de experiență
level = 1  # Nivelul jucătorului
xp_to_next_level = 100  # XP necesar pentru următorul nivel
autosave_timer = 0  # Timer pentru autosave
AUTOSAVE_INTERVAL = 300  # Autosave la fiecare 15 secunde (300 frames la 20 FPS)

# ─── Sistem Power-ups ────────────────────────────────────────────────────
power_ups = []  # Lista de power-ups: [(x, y, type, timer)]
power_up_types = {
    "speed": {"name": "⚡ Speed Boost", "duration": 300, "color": (255, 255, 0)},  # 15 sec la 20 FPS
    "magnet": {"name": "🧲 Magnet Apple", "duration": 300, "color": (255, 100, 100)},
    "shield": {"name": "🛡️ Shield", "duration": 1, "color": (100, 100, 255)},  # O singură coliziune
    "ghost": {"name": "🌀 Ghost", "duration": 180, "color": (200, 200, 200)},  # 9 sec la 20 FPS
    "coins": {"name": "💰 Coin Storm", "duration": 600, "color": (255, 215, 0)}  # 30 sec la 20 FPS
}

# Stări active power-ups
active_power_ups = {
    "speed": 0,
    "magnet": 0,
    "shield": 0,
    "ghost": 0,
    "coins": 0
}

# ─── Cufere: control apariție ───────────────────────────────────────────
apples_since_last_chest = 0
chest_apples_required = 5

# Dicționar cu titlu și descriere pentru fiecare badge
BADGE_INFO = {
    "1games": ("Primul joc!", "Joacă primul tău joc."),
    "10games": ("10 jocuri", "Joacă 10 jocuri complete."),
    "25games": ("25 jocuri", "Joacă 25 de jocuri complete."),
    "badge5win": ("5 victorii", "Câștigă 5 jocuri (scor > 0)."),
    "badge15win": ("15 victorii", "Câștigă 15 jocuri (scor > 0)."),
    "badge25win": ("25 victorii", "Câștigă 25 de jocuri (scor > 0)."),
}

# ─── Dimensiuni și grilă ────────────────────────────────────────────────
WIDTH, HEIGHT = 960, 960
CELL = 40 # dimensiune celulă pentru grila șarpelui (80x80 pixeli)
APPLE_SIZE = 40  # dimensiune măr (80x80 pixeli)

# ─── Fereastră ─────────────────────────────────────────────────────────
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SnakyMath")
clock = pygame.time.Clock()

# ─── Verificare fișiere imagine ─────────────────────────────────────────
required_files = [
    "snake_head.png", "snake_body.png", "Corner.png", "snake_tail.png", "snake_toung.png",
    "snake_head_lime.png", "snake_body_lime.png", "Corner_lime.png", "snake_tail_lime.png", "snake_toung_lime.png",
    "snake_head_poison.png", "snake_body_poison.png", "Corner_poison.png", "snake_tail_poison.png", "snake_toung_poison.png",
    "apple.png", "apple2.png", "game_background.png", "main-menu.png",
    "question.png", "button.png", "button2.png", "button_left.png", "button_right.png", "wall.png", "wall_metal.png", "applegold.png", "snake_bucket.png",
    "spike1.png", "spike2.png", "spike3.png", "spike4.png",
    "spikewood1.png", "spikewood2.png", "spikewood3.png", "spikewood4.png",
    "coins.png",
    "Nr.0.png", "Nr.1.png", "Nr.2.png", "Nr.3.png", "Nr.4.png",
    "Nr.5.png", "Nr.6.png", "Nr.7.png", "Nr.8.png", "Nr.9.png",
    "chest_closed.png", "chest_open.png"
]

# Verificăm dacă toate fișierele imagine există în directorul curent
font = pygame.font.Font(None, 36)  # Pentru mesaje de eroare
for file in required_files:
    file_path = os.path.join(file)
    if not os.path.exists(file_path):
        error_msg = f"Eroare: Fișierul {os.path.abspath(file_path)} lipsește! Asigură-te că toate imaginile sunt în directorul 'K:\\Users\\Cristi\\Desktop\\SnakeGame': {', '.join(required_files)}."
        print(error_msg)
        screen.fill((0, 0, 0))
        error_text = font.render(error_msg, True, (255, 0, 0))
        error_rect = error_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(error_text, error_rect)
        pygame.display.flip()
        pygame.time.wait(5000)
        pygame.quit()
        sys.exit()

# ─── Încărcare sprite-uri (cap, corp, colț, coadă, măr, fundal) ───────────────
try:
    head_img = pygame.transform.scale(pygame.image.load("snake_head.png"), (CELL, CELL))
    body_img = pygame.transform.scale(pygame.image.load("snake_body.png"), (CELL, CELL))
    corner_img = pygame.transform.scale(pygame.image.load("Corner.png"), (CELL, CELL))
    snake_tail_img = pygame.transform.scale(pygame.image.load("snake_tail.png"), (CELL, CELL))
    snake_tongue_img = pygame.transform.scale(pygame.image.load("snake_toung.png"), (CELL, CELL))
    apple_img = pygame.transform.scale(pygame.image.load("apple.png"), (APPLE_SIZE, APPLE_SIZE))
    apple2_img = pygame.transform.scale(pygame.image.load("apple2.png"), (APPLE_SIZE, APPLE_SIZE))
    gold_apple_img = pygame.transform.scale(pygame.image.load("applegold.png"), (APPLE_SIZE, APPLE_SIZE))
    bucket_head_img = pygame.transform.scale(pygame.image.load("snake_bucket.png"), (CELL, CELL))
    background_img = pygame.transform.scale(pygame.image.load("game_background.png"), (WIDTH, HEIGHT))
    menu_background_img = pygame.transform.scale(pygame.image.load("main-menu.png"), (WIDTH, HEIGHT))
    question_background_img = pygame.transform.scale(pygame.image.load("question.png"), (WIDTH, HEIGHT))
    button_base_img = pygame.image.load("button.png").convert_alpha()
    button2_base_img = pygame.image.load("button2.png").convert_alpha()
    wall_img = pygame.transform.scale(pygame.image.load("wall.png"), (CELL, CELL))
    wall_metal_img = pygame.transform.scale(pygame.image.load("wall_metal.png"), (CELL, CELL))
    # Încărcare skinuri
    head_lime_img = pygame.transform.scale(pygame.image.load("snake_head_lime.png"), (CELL, CELL))
    body_lime_img = pygame.transform.scale(pygame.image.load("snake_body_lime.png"), (CELL, CELL))
    corner_lime_img = pygame.transform.scale(pygame.image.load("Corner_lime.png"), (CELL, CELL))
    snake_tail_lime_img = pygame.transform.scale(pygame.image.load("snake_tail_lime.png"), (CELL, CELL))
    snake_tongue_lime_img = pygame.transform.scale(pygame.image.load("snake_toung_lime.png"), (CELL, CELL))
    # Încărcare skinuri poison
    head_poison_img = pygame.transform.scale(pygame.image.load("snake_head_poison.png"), (CELL, CELL))
    body_poison_img = pygame.transform.scale(pygame.image.load("snake_body_poison.png"), (CELL, CELL))
    corner_poison_img = pygame.transform.scale(pygame.image.load("Corner_poison.png"), (CELL, CELL))
    snake_tail_poison_img = pygame.transform.scale(pygame.image.load("snake_tail_poison.png"), (CELL, CELL))
    snake_tongue_poison_img = pygame.transform.scale(pygame.image.load("snake_toung_poison.png"), (CELL, CELL))
    # Încărcare butoane
    button_left_img = pygame.image.load("button_left.png").convert_alpha()
    button_right_img = pygame.image.load("button_right.png").convert_alpha()
    # Încărcare imagine coins
    coins_img = pygame.image.load("coins.png").convert_alpha()
    # Încărcare imagini cifre
    digit_imgs = {}
    for i in range(10):
        digit_imgs[i] = pygame.image.load(f"Nr.{i}.png").convert_alpha()
    # Încărcare cufere
    chest_closed_img = pygame.transform.scale(pygame.image.load("chest_closed.png"), (CELL, CELL))
    chest_open_img = pygame.transform.scale(pygame.image.load("chest_open.png"), (CELL, CELL))
    # Încărcare spike-uri
    spike_imgs = []
    spikewood_imgs = []
    for i in range(1, 5):
        try:
            spike_imgs.append(pygame.transform.scale(pygame.image.load(f"spike{i}.png"), (CELL, CELL)))
        except:
            spike_surface = pygame.Surface((CELL, CELL))
            spike_surface.fill((255, 0, 0))  # Roșu pentru spike simplu
            spike_imgs.append(spike_surface)
        try:
            spikewood_imgs.append(pygame.transform.scale(pygame.image.load(f"spikewood{i}.png"), (CELL, CELL)))
        except:
            spikewood_surface = pygame.Surface((CELL, CELL))
            spikewood_surface.fill((139, 69, 19))  # Maro pentru spike de lemn
            spikewood_imgs.append(spikewood_surface)
    print(f"Succes: Toate imaginile ({', '.join(required_files)}) au fost încărcate din directorul '{os.path.abspath('.')}'!")
except pygame.error as e:
    error_msg = f"Eroare la încărcarea imaginilor: {str(e)}. Folosesc sprite-uri de rezervă (colorate)."
    print(error_msg)
    head_img = pygame.Surface((CELL, CELL))
    head_img.fill((0,255,0))  # Verde pentru cap
    body_img = pygame.Surface((CELL, CELL))
    body_img.fill((0,200,0))  # Verde închis pentru corp
    corner_img = pygame.Surface((CELL, CELL))
    corner_img.fill((0, 150, 0))  # Verde mediu pentru colțuri
    snake_tail_img = pygame.Surface((CELL, CELL))  # Fallback pentru coadă
    snake_tail_img.fill((0, 180, 0))  # Verde distinct pentru coadă
    snake_tongue_img = pygame.Surface((CELL, CELL))  # Fallback pentru limbă
    snake_tongue_img.fill((255, 100, 100))  # Roz pentru limbă
    apple_img = pygame.Surface((APPLE_SIZE, APPLE_SIZE))
    apple_img.fill((255, 0, 0))  # Roșu pentru măr
    apple2_img = pygame.Surface((APPLE_SIZE, APPLE_SIZE))
    apple2_img.fill((0, 0, 255))  # Albastru pentru mărul negativ
    gold_apple_img = pygame.Surface((APPLE_SIZE, APPLE_SIZE))
    gold_apple_img.fill((255, 215, 0))  # Auriu pentru mărul de aur
    bucket_head_img = pygame.Surface((CELL, CELL))
    bucket_head_img.fill((0, 0, 255))  # Albastru pentru bucket head
    menu_background_img = pygame.Surface((WIDTH, HEIGHT))
    menu_background_img.fill((0, 0, 50))  # Albastru închis pentru meniu
    question_background_img = pygame.Surface((WIDTH, HEIGHT))
    question_background_img.fill((20, 20, 20))
    button_base_img = pygame.Surface((400, 100), pygame.SRCALPHA)
    button_base_img.fill((80, 80, 80, 230))
    button2_base_img = pygame.Surface((200, 80), pygame.SRCALPHA)
    button2_base_img.fill((100, 100, 100, 230))
    wall_img = pygame.Surface((CELL, CELL))
    wall_img.fill((100, 100, 100))  # Gri pentru perete
    wall_metal_img = pygame.Surface((CELL, CELL))
    wall_metal_img.fill((150, 150, 150))  # Gri mai deschis pentru perete metalic
    # Sprite-uri de rezervă pentru skinuri
    head_lime_img = pygame.Surface((CELL, CELL))
    head_lime_img.fill((0, 255, 0))  # Verde lime pentru cap
    body_lime_img = pygame.Surface((CELL, CELL))
    body_lime_img.fill((0, 200, 0))  # Verde lime închis pentru corp
    corner_lime_img = pygame.Surface((CELL, CELL))
    corner_lime_img.fill((0, 150, 0))  # Verde lime mediu pentru colțuri
    snake_tail_lime_img = pygame.Surface((CELL, CELL))
    snake_tail_lime_img.fill((0, 180, 0))  # Verde lime distinct pentru coadă
    snake_tongue_lime_img = pygame.Surface((CELL, CELL))
    snake_tongue_lime_img.fill((255, 150, 150))  # Roz deschis pentru limbă lime
    # Sprite-uri de rezervă pentru skinuri poison
    head_poison_img = pygame.Surface((CELL, CELL))
    head_poison_img.fill((128, 0, 128))  # Mov pentru cap poison
    body_poison_img = pygame.Surface((CELL, CELL))
    body_poison_img.fill((100, 0, 100))  # Mov închis pentru corp poison
    corner_poison_img = pygame.Surface((CELL, CELL))
    corner_poison_img.fill((120, 0, 120))  # Mov mediu pentru colțuri poison
    snake_tail_poison_img = pygame.Surface((CELL, CELL))
    snake_tail_poison_img.fill((140, 0, 140))  # Mov distinct pentru coadă poison
    snake_tongue_poison_img = pygame.Surface((CELL, CELL))
    snake_tongue_poison_img.fill((255, 100, 255))  # Roz mov pentru limbă poison
    # Sprite-uri de rezervă pentru butoane
    button_left_img = pygame.Surface((50, 50), pygame.SRCALPHA)
    button_left_img.fill((100, 100, 100, 230))
    button_right_img = pygame.Surface((50, 50), pygame.SRCALPHA)
    button_right_img.fill((100, 100, 100, 230))
    # Sprite de rezervă pentru coins
    coins_img = pygame.Surface((50, 50), pygame.SRCALPHA)
    coins_img.fill((255, 215, 0, 255))  # Auriu pentru coins
    # Sprite-uri de rezervă pentru cifre
    digit_imgs = {}
    for i in range(10):
        digit_surface = pygame.Surface((30, 40), pygame.SRCALPHA)
        digit_surface.fill((255, 255, 255, 255))
        font_digit = pygame.font.Font(None, 36)
        digit_text = font_digit.render(str(i), True, (0, 0, 0))
        digit_rect = digit_text.get_rect(center=(15, 20))
        digit_surface.blit(digit_text, digit_rect)
        digit_imgs[i] = digit_surface
    # Sprite-uri de rezervă pentru cufere
    chest_closed_img = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
    chest_closed_img.fill((160, 82, 45, 255))
    chest_open_img = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
    chest_open_img.fill((205, 133, 63, 255))
    # Sprite-uri de rezervă pentru spike-uri
    spike_imgs = []
    spikewood_imgs = []
    for i in range(4):
        spike_surface = pygame.Surface((CELL, CELL))
        spike_surface.fill((255, 0, 0))  # Roșu pentru spike simplu
        spike_imgs.append(spike_surface)
        spikewood_surface = pygame.Surface((CELL, CELL))
        spikewood_surface.fill((139, 69, 19))  # Maro pentru spike de lemn
        spikewood_imgs.append(spikewood_surface)
    print("Avertisment: Imaginile nu au fost găsite. Folosesc sprite-uri de rezervă colorate.")

# ─── Fonturi ───────────────────────────────────────────────────────────
font = pygame.font.Font(None, 28)  # Pentru scor și mesaje
math_font = pygame.font.Font(None, 36)  # Pentru cifre pe șarpe/măr și întrebări
option_font = pygame.font.Font(None, 38)  # Pentru opțiuni de răspuns și meniu

# ─── UI Helpers ─────────────────────────────────────────────────────────
BUTTON_SIZE = (400, 100)
button_img_scaled = pygame.transform.scale(button_base_img, BUTTON_SIZE)
BUTTON2_SIZE = (200, 80)
button2_img_scaled = pygame.transform.scale(button2_base_img, BUTTON2_SIZE)
LIGHT_GREEN = (140, 255, 140)
DARK_GREEN = (0, 140, 0)

# ─── Efecte vizuale ─────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.life = 60  # 3 secunde la 20 FPS
        self.color = random.choice([
            (255,0,0), (0,200,255), (255,200,0), (255,100,180), (100,255,120), (180,120,255)
        ])
        self.size0 = random.randint(3,8)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.vy += 0.1  # gravitație
    
    def draw(self, screen):
        if self.life > 0:
            s = pygame.Surface((self.size0*2, self.size0*2), pygame.SRCALPHA)
            alpha = int(255 * (self.life / 60))
            pygame.draw.circle(s, (*self.color, alpha), (self.size0, self.size0), self.size0)
            screen.blit(s, (int(self.x)-self.size0, int(self.y)-self.size0))

particles = []
particle_timer = 0
snake_red_timer = 0  # Timer pentru șarpe roșu
bug_pos = None
bug_timer = 0
bug_counter = 0
bug_heads = 0

# ─── Variabile pentru spike-uri ─────────────────────────────────────────
spikes = []  # Lista de spike-uri: [(x, y, type, animation_frame, timer)]
# type: 'spike' (ucide) sau 'spikewood' (scade 3 din lungime)
SPIKE_ANIMATION_SPEED = 3 # Frames între schimbarea animației (2 secunde la 20 FPS)

# ─── Funcții pentru salvarea și încărcarea datelor ─────────────────────
def save_game_data():
    """Salvează datele jocului în fișierul save.json"""
    data = {
        "coins": coins,
        "unlocked_skins": unlocked_skins,
        "current_skin": current_skin,
        "badges": badges,
        "games_played": games_played,
        "wins": wins,
        "xp": xp,
        "level": level,
        "xp_to_next_level": xp_to_next_level
    }
    try:
        with open("save.json", "w") as f:
            json.dump(data, f)
        print("Date salvate cu succes!")
    except Exception as e:
        print(f"Eroare la salvarea datelor: {e}")

def load_game_data():
    """Încarcă datele jocului din fișierul save.json"""
    global coins, unlocked_skins, current_skin, badges, games_played, wins, xp, level, xp_to_next_level
    try:
        if os.path.exists("save.json"):
            with open("save.json", "r") as f:
                data = json.load(f)
                coins = data.get("coins", 0)
                unlocked_skins = data.get("unlocked_skins", {"default": True})
                current_skin = data.get("current_skin", "default")
                badges = data.get("badges", {
                    "1games": False, "10games": False, "25games": False,
                    "badge5win": False, "badge15win": False, "badge25win": False
                })
                games_played = data.get("games_played", 0)
                wins = data.get("wins", 0)
                xp = data.get("xp", 0)
                level = data.get("level", 1)
                xp_to_next_level = data.get("xp_to_next_level", 100)
            print("Date încărcate cu succes!")
        else:
            print("Fișierul de salvare nu există. Folosesc valorile implicite.")
    except Exception as e:
        print(f"Eroare la încărcarea datelor: {e}")
        # Folosește valorile implicite dacă încărcarea eșuează
        coins = 0
        unlocked_skins = {"default": True}
        current_skin = "default"
        badges = {
            "1games": False, "10games": False, "25games": False,
            "badge5win": False, "badge15win": False, "badge25win": False
        }
        games_played = 0
        wins = 0
        xp = 0
        level = 1
        xp_to_next_level = 100

def add_xp(amount):
    """Adaugă XP și verifică dacă jucătorul a avansat la următorul nivel"""
    global xp, level, xp_to_next_level, coins
    xp += amount
    
    # Verifică dacă jucătorul a avansat la următorul nivel
    level_up = False
    while xp >= xp_to_next_level:
        xp -= xp_to_next_level
        level += 1
        xp_to_next_level = int(100 * (1.2 ** (level - 1)))  # Creștere exponențială
        print(f"Felicitări! Ai ajuns la nivelul {level}!")
        
        # Bonus pentru nivel nou
        coins += level * 5  # 5 coins per nivel
        level_up = True
    
    # Salvează doar dacă s-a avansat la un nivel nou
    # Autosave-ul din joc se va ocupa de rest
    if level_up:
        save_game_data()

def get_xp_progress():
    """Returnează progresul XP pentru următorul nivel (0-100%)"""
    if xp_to_next_level == 0:
        return 100
    return (xp / xp_to_next_level) * 100

def draw_button(label_text, center_pos, is_selected=False):
    # Adaugă paranteze rotunde în jurul textului
    formatted_text = f"( {label_text} )"
    
    # Mărește butonul când este selectat
    if is_selected:
        scaled_button = pygame.transform.scale(button_base_img, (int(BUTTON_SIZE[0] * 1.1), int(BUTTON_SIZE[1] * 1.1)))
    else:
        scaled_button = button_img_scaled
    
    btn_rect = scaled_button.get_rect(center=center_pos)
    screen.blit(scaled_button, btn_rect)
    
    # Two-tone green text (light top, dark bottom)
    text_light = option_font.render(formatted_text, True, LIGHT_GREEN)
    text_dark = option_font.render(formatted_text, True, DARK_GREEN)
    text_rect = text_light.get_rect(center=btn_rect.center)
    half_h = text_rect.height // 2
    
    # Adaugă umbră pentru toate butoanele
    shadow = option_font.render(formatted_text, True, (0, 0, 0))
    shadow_rect = shadow.get_rect(center=(text_rect.centerx + 2, text_rect.centery + 2))
    screen.blit(shadow, shadow_rect)
    
    screen.blit(text_light, text_rect, area=pygame.Rect(0, 0, text_rect.width, half_h))
    screen.blit(text_dark, (text_rect.x, text_rect.y + half_h), area=pygame.Rect(0, half_h, text_rect.width, text_rect.height - half_h))

def draw_button_resizable(label_text, center_pos, size, is_selected=False):
    btn_img = pygame.transform.scale(button_base_img, size)
    btn_rect = btn_img.get_rect(center=center_pos)
    screen.blit(btn_img, btn_rect)
    text_light = option_font.render(label_text, True, LIGHT_GREEN)
    text_dark = option_font.render(label_text, True, DARK_GREEN)
    text_rect = text_light.get_rect(center=btn_rect.center)
    half_h = text_rect.height // 2
    if is_selected:
        shadow = option_font.render(label_text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(text_rect.centerx + 2, text_rect.centery + 2))
        screen.blit(shadow, shadow_rect)
    screen.blit(text_light, text_rect, area=pygame.Rect(0, 0, text_rect.width, half_h))
    screen.blit(text_dark, (text_rect.x, text_rect.y + half_h), area=pygame.Rect(0, half_h, text_rect.width, text_rect.height - half_h))

def draw_button_resizable_singlecolor(label_text, center_pos, size, color, is_selected=False):
    btn_img = pygame.transform.scale(button_base_img, size)
    btn_rect = btn_img.get_rect(center=center_pos)
    screen.blit(btn_img, btn_rect)
    text = option_font.render(label_text, True, color)
    text_rect = text.get_rect(center=btn_rect.center)
    if is_selected:
        shadow = option_font.render(label_text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(text_rect.centerx + 2, text_rect.centery + 2))
        screen.blit(shadow, shadow_rect)
    screen.blit(text, text_rect)

def draw_button2(label_text, center_pos, is_selected=False):
    btn_rect = button2_img_scaled.get_rect(center=center_pos)
    screen.blit(button2_img_scaled, btn_rect)
    text_light = option_font.render(label_text, True, LIGHT_GREEN)
    text_dark = option_font.render(label_text, True, DARK_GREEN)
    text_rect = text_light.get_rect(center=btn_rect.center)
    half_h = text_rect.height // 2
    if is_selected:
        shadow = option_font.render(label_text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(text_rect.centerx + 2, text_rect.centery + 2))
        screen.blit(shadow, shadow_rect)
    screen.blit(text_light, text_rect, area=pygame.Rect(0, 0, text_rect.width, half_h))
    screen.blit(text_dark, (text_rect.x, text_rect.y + half_h), area=pygame.Rect(0, half_h, text_rect.width, text_rect.height - half_h))

# ─── Dificultăți ───────────────────────────────────────────────────────
DIFFICULTIES = {
    "Ușoară": {"max_num": 10, "operations": ["+", "-"]},
    "Medie": {"max_num": 20, "operations": ["+", "-"]},
    "Greu": {"max_num": 30, "operations": ["+", "-"]}
}
current_difficulty = "Ușoară"

# ─── Funcții desen ─────────────────────────────────────────────────────
def draw_background():
    screen.blit(background_img, (0, 0))
    grid_color = (50, 50, 50)  # Gri închis
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, grid_color, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, grid_color, (0, y), (WIDTH, y), 1)

def draw_menu_background():
    screen.blit(menu_background_img, (0, 0))

def draw_snake(coords, direction, current_sum):
    global snake_red_timer, current_skin, unlocked_skins
    is_red = snake_red_timer > 0
    
    # Verifică dacă skin-ul este deblocat, altfel folosește default
    # Dacă skin-ul este "tiger" (eliminat), folosește "default"
    actual_skin = current_skin
    if current_skin == "tiger":
        actual_skin = "default"
    elif current_skin != "default" and not unlocked_skins.get(current_skin, False):
        actual_skin = "default"
    
    # Selectează skinurile în funcție de actual_skin
    if actual_skin == "lime":
        head_img_skin = head_lime_img
        body_img_skin = body_lime_img
        corner_img_skin = corner_lime_img
        snake_tail_img_skin = snake_tail_lime_img
        snake_tongue_img_skin = snake_tongue_lime_img
    elif actual_skin == "poison":
        head_img_skin = head_poison_img
        body_img_skin = body_poison_img
        corner_img_skin = corner_poison_img
        snake_tail_img_skin = snake_tail_poison_img
        snake_tongue_img_skin = snake_tongue_poison_img
    else:  # default
        head_img_skin = head_img
        body_img_skin = body_img
        corner_img_skin = corner_img
        snake_tail_img_skin = snake_tail_img
        snake_tongue_img_skin = snake_tongue_img
    
    for i, (x, y) in enumerate(coords):
        if i == 0:  # Capul șarpelui
            head_to_use = bucket_head_img if bucket_mode else head_img_skin
            if direction == (0, CELL):  # Jos
                rotated_head = head_to_use
            elif direction == (0, -CELL):  # Sus
                rotated_head = pygame.transform.rotate(head_to_use, 180)
            elif direction == (CELL, 0):  # Dreapta
                rotated_head = pygame.transform.rotate(head_to_use, 90)
            elif direction == (-CELL, 0):  # Stânga
                rotated_head = pygame.transform.rotate(head_to_use, -90)
            if is_red:
                red_head = rotated_head.copy()
                red_head.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)
                head_rect = red_head.get_rect(center=(x + CELL // 2, y + CELL // 2))
                screen.blit(red_head, head_rect)
            else:
                head_rect = rotated_head.get_rect(center=(x + CELL // 2, y + CELL // 2))
                screen.blit(rotated_head, head_rect)
            # Desenează suma folosind imagini de cifre (mai mari pentru șarpe)
            draw_number_with_digits(current_sum, (x + CELL // 2, y - CELL // 2), 1.8)
            
            # Desenează limba șarpelui în fața capului
            tongue_x = x + direction[0]
            tongue_y = y + direction[1]
            if direction == (0, CELL):  # Jos
                rotated_tongue = snake_tongue_img_skin
            elif direction == (0, -CELL):  # Sus
                rotated_tongue = pygame.transform.rotate(snake_tongue_img_skin, 180)
            elif direction == (CELL, 0):  # Dreapta
                rotated_tongue = pygame.transform.rotate(snake_tongue_img_skin, 90)
            elif direction == (-CELL, 0):  # Stânga
                rotated_tongue = pygame.transform.rotate(snake_tongue_img_skin, -90)
            tongue_rect = rotated_tongue.get_rect(center=(tongue_x + CELL // 2, tongue_y + CELL // 2))
            screen.blit(rotated_tongue, tongue_rect)
        else:
            next_pos = coords[i - 1]
            prev_pos = coords[i + 1] if i + 1 < len(coords) else None
            dx_next, dy_next = next_pos[0] - x, next_pos[1] - y
            if prev_pos:  # Segmentele din mijloc (corp sau colțuri)
                dx_prev, dy_prev = x - prev_pos[0], y - prev_pos[1]
                if (dx_next != 0 and dy_prev != 0) or (dy_next != 0 and dx_prev != 0):  # Colț
                    if dx_next > 0 and dy_prev > 0:  # Dreapta -> Jos
                        rotated_corner = pygame.transform.rotate(corner_img_skin, 0)
                    elif dx_next > 0 and dy_prev < 0:  # Dreapta -> Sus
                        rotated_corner = pygame.transform.rotate(corner_img_skin, 270)
                    elif dx_next < 0 and dy_prev > 0:  # Stânga -> Jos
                        rotated_corner = pygame.transform.rotate(corner_img_skin, 90)
                    elif dx_next < 0 and dy_prev < 0:  # Stânga -> Sus
                        rotated_corner = pygame.transform.rotate(corner_img_skin, 180)
                    elif dy_next > 0 and dx_prev > 0:  # Jos -> Dreapta
                        rotated_corner = pygame.transform.rotate(corner_img_skin, 180)
                    elif dy_next > 0 and dx_prev < 0:  # Jos -> Stânga
                        rotated_corner = pygame.transform.rotate(corner_img_skin, 270)
                    elif dy_next < 0 and dx_prev > 0:  # Sus -> Dreapta
                        rotated_corner = pygame.transform.rotate(corner_img_skin, 90)
                    elif dy_next < 0 and dx_prev < 0:  # Sus -> Stânga
                        rotated_corner = pygame.transform.rotate(corner_img_skin, 0)
                    corner_rect = rotated_corner.get_rect(center=(x + CELL // 2, y + CELL // 2))
                    if is_red:
                        red_corner = rotated_corner.copy()
                        red_corner.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)
                        screen.blit(red_corner, corner_rect)
                    else:
                        screen.blit(rotated_corner, corner_rect)
                else:  # Segment drept
                    if dy_next != 0:  # Vertical
                        rotated_body = pygame.transform.rotate(body_img_skin, 90)
                        body_rect = rotated_body.get_rect(center=(x + CELL // 2, y + CELL // 2))
                        if is_red:
                            red_body = rotated_body.copy()
                            red_body.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)
                            screen.blit(red_body, body_rect)
                        else:
                            screen.blit(rotated_body, body_rect)
                    else:  # Orizontal
                        body_rect = body_img_skin.get_rect(center=(x + CELL // 2, y + CELL // 2))
                        if is_red:
                            red_body = body_img_skin.copy()
                            red_body.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)
                            screen.blit(red_body, body_rect)
                        else:
                            screen.blit(body_img_skin, body_rect)
            else:  # Ultimul segment (coada)
                dx_next, dy_next = next_pos[0] - x, next_pos[1] - y
                if dy_next != 0:  # Vertical (coada orientată sus sau jos)
                    rotated_tail = pygame.transform.rotate(snake_tail_img_skin, 270) if dy_next > 0 else pygame.transform.rotate(snake_tail_img_skin, 90)
                else:  # Orizontal (coada orientată stânga sau dreapta)
                    rotated_tail = snake_tail_img_skin if dx_next > 0 else pygame.transform.rotate(snake_tail_img_skin, 180)
                tail_rect = rotated_tail.get_rect(center=(x + CELL // 2, y + CELL // 2))
                if is_red:
                    red_tail = rotated_tail.copy()
                    red_tail.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)
                    screen.blit(red_tail, tail_rect)
                else:
                    screen.blit(rotated_tail, tail_rect)

def draw_apple(pos, apple_number):
    offset = (CELL - APPLE_SIZE) // 2
    img = apple2_img if apple_number < 0 else apple_img
    screen.blit(img, (pos[0] + offset, pos[1] + offset))
    # Desenează numărul mărului folosind imagini de cifre
    draw_number_with_digits(apple_number, (pos[0] + CELL // 2, pos[1] + CELL // 2), 0.9)

def draw_gold_apple(pos):
    offset = (CELL - APPLE_SIZE) // 2
    screen.blit(gold_apple_img, (pos[0] + offset, pos[1] + offset))
    # Poți adăuga text dacă vrei, ex. num_text = math_font.render("?", True, (255, 255, 255))
    # screen.blit(num_text, (pos[0] + CELL // 2 - 10, pos[1] + CELL // 2 - 18))

def draw_walls(walls):
    for x, y in walls:
        wall_rect = wall_img.get_rect(center=(x + CELL // 2, y + CELL // 2))
        screen.blit(wall_img, wall_rect)

def draw_metal_walls(metal_walls):
    for x, y in metal_walls:
        wall_rect = wall_metal_img.get_rect(center=(x + CELL // 2, y + CELL // 2))
        screen.blit(wall_metal_img, wall_rect)

def draw_spikes():
    global spikes
    for spike in spikes:
        x, y, spike_type, frame, timer = spike
        if spike_type == 'spike':
            img = spike_imgs[frame]
        else:  # spikewood
            img = spikewood_imgs[frame]
        spike_rect = img.get_rect(center=(x + CELL // 2, y + CELL // 2))
        screen.blit(img, spike_rect)

def draw_number_with_digits(number, center_pos, scale=1.0):
    """Desenează un număr folosind imagini de cifre"""
    if number < 0:
        # Pentru numere negative, desenează semnul minus
        number_str = str(abs(number))
        start_x = center_pos[0] - (len(number_str) + 1) * 15 * scale
    else:
        number_str = str(number)
        start_x = center_pos[0] - len(number_str) * 15 * scale
    
    # Desenează fiecare cifră
    for i, digit_char in enumerate(number_str):
        digit = int(digit_char)
        digit_img = digit_imgs[digit]
        scaled_digit = pygame.transform.scale(digit_img, (int(30 * scale), int(40 * scale)))
        digit_rect = scaled_digit.get_rect(center=(start_x + i * 30 * scale, center_pos[1]))
        screen.blit(scaled_digit, digit_rect)
    
    # Desenează semnul minus dacă este necesar
    if number < 0:
        minus_img = pygame.Surface((int(20 * scale), int(4 * scale)))
        minus_img.fill((255, 255, 255))
        minus_rect = minus_img.get_rect(center=(start_x - 15 * scale, center_pos[1]))
        screen.blit(minus_img, minus_rect)

def draw_coins():
    global coins
    # Redimensionează imaginea coins pentru a fi mult mai mică
    small_coins_img = pygame.transform.scale(coins_img, (30, 30))
    # Afișează imaginea coins în colțul dreapta sus
    coins_rect = small_coins_img.get_rect(topright=(WIDTH - 10, 10))
    screen.blit(small_coins_img, coins_rect)
    # Afișează numărul de coins folosind imagini de cifre
    coins_pos = (WIDTH - 10, 10 + small_coins_img.get_height() + 20)
    draw_number_with_digits(coins, coins_pos, 1.2)

def draw_xp_bar():
    """Desenează bara de XP în colțul stânga sus"""
    global xp, level, xp_to_next_level
    
    # Desenează fundalul barei de XP
    bar_width = 200
    bar_height = 20
    bar_x = 10
    bar_y = 10
    
    # Fundal
    pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 2)
    
    # Progresul XP
    progress = get_xp_progress()
    fill_width = int((bar_width - 4) * (progress / 100))
    pygame.draw.rect(screen, (0, 255, 0), (bar_x + 2, bar_y + 2, fill_width, bar_height - 4))
    
    # Textul nivelului
    level_text = font.render(f"Level {level}", True, (255, 255, 255))
    screen.blit(level_text, (bar_x, bar_y - 25))
    
    # Textul XP
    xp_text = font.render(f"XP: {xp}/{xp_to_next_level}", True, (255, 255, 255))
    screen.blit(xp_text, (bar_x, bar_y + bar_height + 5))

def update_spikes():
    global spikes
    for i, spike in enumerate(spikes):
        x, y, spike_type, frame, timer = spike
        timer -= 1
        if timer <= 0:
            frame = (frame + 1) % 4  # Ciclu 0->1->2->3->0
            timer = SPIKE_ANIMATION_SPEED
        spikes[i] = (x, y, spike_type, frame, timer)

# ─── Cufere (Chests) ─────────────────────────────────────────────────────
chests = []  # Lista de cufere: [(x, y)]

def spawn_chest(exclude_positions):
    """Generează un cufăr la o poziție liberă (stare: închis)."""
    pos = random_cell(exclude_positions)
    # (x, y, opened, timer_open_frames)
    chests.append((pos[0], pos[1], False, 0))

def draw_chests():
    for cx, cy, opened, _ in chests:
        img = chest_open_img if opened else chest_closed_img
        rect = img.get_rect(center=(cx + CELL // 2, cy + CELL // 2))
        screen.blit(img, rect)

def update_chests():
    # Elimină cuferele deschise după scurt timp pentru аfișare
    for i in range(len(chests) - 1, -1, -1):
        cx, cy, opened, timer = chests[i]
        if opened:
            timer -= 1
            if timer <= 0:
                chests.pop(i)
            else:
                chests[i] = (cx, cy, opened, timer)

def spawn_power_up(exclude_positions):
    """Generează un power-up aleatoriu"""
    global power_ups
    power_up_type = random.choice(list(power_up_types.keys()))
    pos = random_cell(exclude_positions)
    power_ups.append((pos[0], pos[1], power_up_type, 0))

def draw_power_ups():
    """Desenează power-ups-urile pe ecran"""
    global power_ups
    for power_up in power_ups:
        x, y, power_type, timer = power_up
        # Creează o suprafață pentru power-up
        power_up_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
        color = power_up_types[power_type]["color"]
        
        # Desenează un cerc colorat cu text
        pygame.draw.circle(power_up_surface, color, (20, 20), 18)
        pygame.draw.circle(power_up_surface, (255, 255, 255), (20, 20), 18, 3)
        
        # Adaugă textul power-up-ului
        font_power = pygame.font.Font(None, 24)
        text = font_power.render(power_up_types[power_type]["name"][0], True, (0, 0, 0))
        text_rect = text.get_rect(center=(20, 20))
        power_up_surface.blit(text, text_rect)
        
        # Desenează power-up-ul
        power_rect = power_up_surface.get_rect(center=(x + CELL // 2, y + CELL // 2))
        screen.blit(power_up_surface, power_rect)

def update_power_ups():
    """Actualizează power-ups-urile"""
    global power_ups, active_power_ups
    # Actualizează timer-urile power-ups-urilor active
    for power_type in active_power_ups:
        if active_power_ups[power_type] > 0:
            active_power_ups[power_type] -= 1

def activate_power_up(power_type):
    """Activează un power-up"""
    global active_power_ups
    duration = power_up_types[power_type]["duration"]
    active_power_ups[power_type] = duration
    print(f"Power-up activat: {power_up_types[power_type]['name']}")

def is_power_up_active(power_type):
    """Verifică dacă un power-up este activ"""
    return active_power_ups[power_type] > 0

# ─── Funcție pentru popup cu întrebare matematică ──────────────────────
def show_math_question(current_sum, apple_number, operation):
    if operation == "+":
        correct_answer = current_sum + apple_number
    else:  # "-"
        correct_answer = current_sum - apple_number
    
    wrong1 = correct_answer + random.randint(-2, -1) if random.choice([True, False]) else correct_answer + random.randint(1, 2)
    wrong2 = correct_answer + random.randint(-2, -1) if wrong1 > correct_answer else correct_answer + random.randint(1, 2)
    options = [correct_answer, wrong1, wrong2]
    random.shuffle(options)
    selected = 1  # Începe cu opțiunea din mijloc selectată
    
    while True:
        screen.blit(question_background_img, (0, 0))
        
        # Desenează întrebarea folosind imagini de cifre
        question_x = WIDTH // 2
        question_y = HEIGHT // 2 - 100
        
        # Desenează primul număr
        draw_number_with_digits(current_sum, (question_x - 80, question_y), 1.8)
        
        # Desenează semnul operației
        op_text = math_font.render(operation, True, (255, 255, 255))
        op_rect = op_text.get_rect(center=(question_x - 20, question_y))
        screen.blit(op_text, op_rect)
        
        # Desenează al doilea număr
        draw_number_with_digits(apple_number, (question_x + 40, question_y), 1.8)
        
        # Desenează semnul egal
        equal_text = math_font.render("=", True, (255, 255, 255))
        equal_rect = equal_text.get_rect(center=(question_x + 100, question_y))
        screen.blit(equal_text, equal_rect)
        
        # Desenează semnul întrebării
        question_text = math_font.render("?", True, (255, 255, 255))
        question_rect = question_text.get_rect(center=(question_x + 140, question_y))
        screen.blit(question_text, question_rect)
        
        # Desenează opțiunile de răspuns folosind imagini de cifre
        option_width = WIDTH // 4
        for i, opt in enumerate(options):
            center_pos = (option_width * (i + 1), HEIGHT - 100)
            # Desenează butonul
            btn_rect = button2_img_scaled.get_rect(center=center_pos)
            screen.blit(button2_img_scaled, btn_rect)
            
            # Desenează numărul pe buton
            draw_number_with_digits(opt, center_pos, 1.2)
            
            # Desenează selecția
            if i == selected:
                pygame.draw.rect(screen, (255, 255, 0), btn_rect, 3)
        
        pygame.display.flip()
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_a:
                    selected = max(0, selected - 1)
                if e.key == pygame.K_d:
                    selected = min(2, selected + 1)
                if e.key == pygame.K_RETURN:
                    chosen = options[selected]
                    return chosen == correct_answer

def show_badges_screen():
    options = ["Exit"]
    selected = 0
    badge_images = {
        "1games": "1game.png",
        "10games": "10games.png",
        "25games": "25games.png",
        "badge5win": "badge5win.png",
        "badge15win": "badge15win.png",
        "badge25win": "badge25win.png",
    }
    loaded_badge_imgs = {}
    for k, imgfile in badge_images.items():
        try:
            loaded_badge_imgs[k] = pygame.image.load(imgfile).convert_alpha()
        except:
            loaded_badge_imgs[k] = None
    
    while True:
        draw_menu_background()
        title_text = option_font.render("Badges", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 260))
        screen.blit(title_text, title_rect)
        chenar_rect = pygame.Rect(WIDTH//2-250, HEIGHT//2-120, 500, 240)
        pygame.draw.rect(screen, (60,60,80), chenar_rect, border_radius=30)
        pygame.draw.rect(screen, (200,255,200), chenar_rect, 4, border_radius=30)
        badge_keys = [k for k,v in badges.items() if v and loaded_badge_imgs[k]]
        n = len(badge_keys)
        if n > 0:
            img_w = 80
            spacing = 30
            total_w = n*img_w + (n-1)*spacing
            x0 = WIDTH//2 - total_w//2
            y_img = HEIGHT//2
            for i, k in enumerate(badge_keys):
                img = pygame.transform.smoothscale(loaded_badge_imgs[k], (img_w, img_w))
                img_rect = img.get_rect(left=x0 + i*(img_w+spacing), centery=y_img)
                screen.blit(img, img_rect)
        btn_y = HEIGHT - 15 - 50//2
        draw_button(options[0], (WIDTH//2, btn_y), is_selected=(selected == 0))
        pygame.display.flip()
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_c, pygame.K_RETURN):
                    return

def show_menu():
    global current_difficulty
    # Butoanele în format 2x2 (două rânduri, două coloane)
    options = [
        ["Dificultate", "Start"],
        ["Skins", "Ieșire"]
    ]
    selected_row = 0
    selected_col = 0
    
    while True:
        draw_menu_background()
        # Afișează textul "TheMathSnake" (fără imaginea name.png)
        title_font = pygame.font.Font(None, 72)  # Font mai mare pentru titlu
        title_text = title_font.render("TheMathSnake", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 300))
        screen.blit(title_text, title_rect)
        
        # Afișează coins-urile în colțul dreapta sus
        draw_coins()
        # Afișează bara de XP în colțul stânga sus
        draw_xp_bar()
        
        # Desenează butoanele în format 2x2
        btn_width = 300
        btn_height = 100
        btn_spacing_h = 120  # Spațiu orizontal între butoane (mărit)
        btn_spacing_v = 80  # Spațiu vertical între rânduri (redus)
        
        # Calculează pozițiile pentru centrul grilei
        total_width = 2 * btn_width + btn_spacing_h
        total_height = 2 * btn_height + btn_spacing_v
        start_x = (WIDTH - total_width) // 2 + btn_width // 2
        start_y = HEIGHT - 280  # Ajustat pentru a vedea toate butoanele
        
        for row in range(2):
            for col in range(2):
                center_x = start_x + col * (btn_width + btn_spacing_h)
                center_y = start_y + row * (btn_height + btn_spacing_v)
                center = (center_x, center_y)
                draw_button(options[row][col], center, is_selected=(row == selected_row and col == selected_col))
        
        pygame.display.flip()
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_w:  # Sus
                    selected_row = (selected_row - 1) % 2
                if e.key == pygame.K_s:  # Jos
                    selected_row = (selected_row + 1) % 2
                if e.key == pygame.K_a:  # Stânga
                    selected_col = (selected_col - 1) % 2
                if e.key == pygame.K_d:  # Dreapta
                    selected_col = (selected_col + 1) % 2
                if e.key == pygame.K_RETURN:
                    selected_option = options[selected_row][selected_col]
                    if selected_option == "Start":
                            return
                    elif selected_option == "Dificultate":
                            show_difficulty_menu()
                    elif selected_option == "Skins":
                            show_skins_menu()
                    elif selected_option == "Ieșire":
                            pygame.quit()
                            sys.exit()

def show_difficulty_menu():
    global current_difficulty
    diff_options = list(DIFFICULTIES.keys())
    selected = diff_options.index(current_difficulty)
    
    # Dicționar cu intervalele de numere pentru fiecare dificultate
    difficulty_ranges = {
        "Ușoară": "1-10",
        "Medie": "1-20",
        "Greu": "1-30"
    }
    
    while True:
        draw_menu_background()
        # Titlu mai mare și mai sus
        title_font = pygame.font.Font(None, 60)
        title_text = title_font.render("Alege Dificultatea", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 300))
        screen.blit(title_text, title_rect)
        
        for i, opt in enumerate(diff_options):
            # Adaugă intervalul de numere după text
            opt_with_range = f"{opt} ({difficulty_ranges[opt]})"
            center = (WIDTH // 2, HEIGHT // 2 - 50 + i * 120)
            draw_button(opt_with_range, center, is_selected=(i == selected))
        draw_button("Înapoi (Esc)", (WIDTH // 2, HEIGHT // 2 + 250))
        pygame.display.flip()
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_w:  # Sus
                    selected = max(0, selected - 1)
                if e.key == pygame.K_s:  # Jos
                    selected = min(len(diff_options) - 1, selected + 1)
                if e.key == pygame.K_RETURN:
                    current_difficulty = diff_options[selected]
                    return
                if e.key == pygame.K_ESCAPE:
                    return

def show_skins_menu():
    global current_skin, coins, unlocked_skins
    # Dacă skin-ul curent este "tiger" (eliminat), resetează la "default"
    if current_skin == "tiger":
        current_skin = "default"
    skins = ["default", "lime", "poison"]
    # Asigură-te că current_skin_index este valid
    if current_skin not in skins:
        current_skin = "default"
    current_skin_index = skins.index(current_skin)
    
    while True:
        draw_menu_background()
        title_text = option_font.render("Selectează Skin", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 300))
        screen.blit(title_text, title_rect)
        
        # Afișează coins-urile în colțul dreapta sus
        draw_coins()
        
        # Desenează preview-ul șarpelui
        preview_x = WIDTH // 2
        preview_y = HEIGHT // 2 - 100
        
        # Selectează skinurile pentru preview
        if current_skin == "lime":
            head_img_preview = head_lime_img
            body_img_preview = body_lime_img
            snake_tail_img_preview = snake_tail_lime_img
            snake_tongue_img_preview = snake_tongue_lime_img
        elif current_skin == "poison":
            head_img_preview = head_poison_img
            body_img_preview = body_poison_img
            snake_tail_img_preview = snake_tail_poison_img
            snake_tongue_img_preview = snake_tongue_poison_img
        else:  # default
            head_img_preview = head_img
            body_img_preview = body_img
            snake_tail_img_preview = snake_tail_img
            snake_tongue_img_preview = snake_tongue_img
        
        # Mărește imaginile pentru preview (2x mai mari)
        scale_factor = 2
        large_tail = pygame.transform.scale(snake_tail_img_preview, (CELL * scale_factor, CELL * scale_factor))
        large_body = pygame.transform.scale(body_img_preview, (CELL * scale_factor, CELL * scale_factor))
        large_head = pygame.transform.scale(head_img_preview, (CELL * scale_factor, CELL * scale_factor))
        large_tongue = pygame.transform.scale(snake_tongue_img_preview, (CELL * scale_factor, CELL * scale_factor))
        
        # Desenează șarpele: 1(tail) -> 2(body) -> 3(head) -> 4(tongue) cu distanțe de 80px
        # 1 - Coada (la început)
        tail_rect = large_tail.get_rect(center=(preview_x - 120, preview_y))  # 1 la început
        screen.blit(large_tail, tail_rect)
        
        # 2 - Corpul (80px de la 1)
        body_rect = large_body.get_rect(center=(preview_x - 40, preview_y))  # 80px de la 1
        screen.blit(large_body, body_rect)
        
        # 3 - Capul (80px de la 2)
        rotated_head = pygame.transform.rotate(large_head, 90)  # 90 grade pentru dreapta
        head_rect = rotated_head.get_rect(center=(preview_x + 40, preview_y))  # 80px de la 2
        screen.blit(rotated_head, head_rect)
        
        # 4 - Limba (80px de la 3)
        rotated_tongue = pygame.transform.rotate(large_tongue, 90)  # 90 grade pentru dreapta
        tongue_rect = rotated_tongue.get_rect(center=(preview_x + 120, preview_y))  # 80px de la 3
        screen.blit(rotated_tongue, tongue_rect)
        
        # Numele skin-ului deasupra imaginii
        if current_skin == "default":
            skin_name = "Original Snake"
        elif current_skin == "lime":
            skin_name = "Lime Snake"
        elif current_skin == "poison":
            skin_name = "Poison Snake"
        else:
            skin_name = "Unknown Snake"
        
        skin_text = option_font.render(skin_name, True, (255, 255, 255))
        skin_rect = skin_text.get_rect(center=(preview_x, preview_y - 80))  # Deasupra imaginii
        screen.blit(skin_text, skin_rect)
        
        # Afișează prețul sau statusul skin-ului
        if current_skin == "default":
            status_text = "GRATUIT"
            status_color = (0, 255, 0)
        elif unlocked_skins.get(current_skin, False):
            status_text = "DEBLOCAT"
            status_color = (0, 255, 0)
        else:
            price = skin_prices.get(current_skin, 0)
            status_text = f"{price} COINS"
            status_color = (255, 215, 0)  # Auriu
        
        status_display = option_font.render(status_text, True, status_color)
        status_rect = status_display.get_rect(center=(preview_x, preview_y + 80))  # Sub imagine
        screen.blit(status_display, status_rect)
        
        # Butoanele de navigare
        left_btn_rect = button_left_img.get_rect(center=(preview_x - 200, preview_y))
        right_btn_rect = button_right_img.get_rect(center=(preview_x + 200, preview_y))
        screen.blit(button_left_img, left_btn_rect)
        screen.blit(button_right_img, right_btn_rect)
        
        # Butonul de înapoi
        draw_button("Back", (WIDTH // 2, HEIGHT // 2 + 200))
        
        pygame.display.flip()
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_a:
                    current_skin_index = (current_skin_index - 1) % len(skins)
                    current_skin = skins[current_skin_index]
                    save_game_data()  # Salvează când schimbi skin-ul
                if e.key == pygame.K_d:
                    current_skin_index = (current_skin_index + 1) % len(skins)
                    current_skin = skins[current_skin_index]
                    save_game_data()  # Salvează când schimbi skin-ul
                if e.key == pygame.K_RETURN:
                    # Încearcă să cumpere skin-ul dacă nu este deblocat
                    if current_skin != "default" and not unlocked_skins.get(current_skin, False):
                        price = skin_prices.get(current_skin, 0)
                        if coins >= price:
                            coins -= price
                            unlocked_skins[current_skin] = True
                            save_game_data()  # Salvează datele după cumpărare
                if e.key == pygame.K_ESCAPE:
                    return

def game_over(score):
    global wins
    if score > 0:
        wins += 1
        # Adaugă XP pentru victorie
        add_xp(score * 5)  # 5 XP per punct câștigat
        
        if wins >= 5 and not badges["badge5win"]:
            badges["badge5win"] = True
            add_xp(50)  # Bonus XP pentru badge nou
        if wins >= 15 and not badges["badge15win"]:
            badges["badge15win"] = True
            add_xp(100)  # Bonus XP pentru badge nou
        if wins >= 25 and not badges["badge25win"]:
            badges["badge25win"] = True
            add_xp(200)  # Bonus XP pentru badge nou
    selected = 0
    options = ["Restart", "Enter"]
    pygame.time.wait(300)
    
    while True:
        draw_background()
        draw_button_resizable_singlecolor("GAME OVER", (WIDTH//2, HEIGHT//2 - 180), (600, 110), (255, 60, 60))
        draw_button(options[0], (WIDTH//2 - 240, HEIGHT//2 - 20), is_selected=(selected == 0))
        draw_button(options[1], (WIDTH//2 + 240, HEIGHT//2 - 20), is_selected=(selected == 1))
        
        # Desenează "Score:" text
        score_label = option_font.render("Score:", True, (80, 160, 255))
        score_label_rect = score_label.get_rect(center=(WIDTH//2 - 50, HEIGHT//2 + 120))
        screen.blit(score_label, score_label_rect)
        # Desenează scorul folosind imagini de cifre
        draw_number_with_digits(score, (WIDTH//2 + 50, HEIGHT//2 + 120), 1.5)
        pygame.display.flip()
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_a:
                    selected = max(0, selected - 1)
                if e.key == pygame.K_d:
                    selected = min(1, selected + 1)
                if e.key == pygame.K_RETURN:
                    if selected == 0:
                        return start_game()
                    else:
                        return main()
                if e.key == pygame.K_r:
                    return start_game()
                if e.key in (pygame.K_ESCAPE, pygame.K_m):
                    return main()

def random_cell(exclude, walls=None):
    exclude = exclude + (walls or [])
    while True:
        x = random.randrange(CELL, WIDTH - CELL, CELL)
        y = random.randrange(CELL, HEIGHT - CELL, CELL)
        if x == CELL or x == WIDTH-2*CELL or y == CELL or y == HEIGHT-2*CELL:
            continue
        if (x, y) not in exclude:
            return (x, y)

def init_spikes(snake, walls, apple):
    global spikes
    spikes = []
    exclude = snake + walls + [apple]
    if gold_apple:
        exclude.append(gold_apple)
    
    # Adaugă spike-uri simple (ucide șarpele)
    num_spikes = {"Ușoară": 2, "Medie": 3, "Greu": 4}[current_difficulty]
    for _ in range(num_spikes):
        spike_pos = random_cell(exclude)
        spikes.append((spike_pos[0], spike_pos[1], 'spike', 0, SPIKE_ANIMATION_SPEED))
        exclude.append(spike_pos)
    
    # Adaugă spike-uri de lemn (scade 3 din lungime)
    num_wood_spikes = {"Ușoară": 1, "Medie": 2, "Greu": 3}[current_difficulty]
    for _ in range(num_wood_spikes):
        spike_pos = random_cell(exclude)
        spikes.append((spike_pos[0], spike_pos[1], 'spikewood', 0, SPIKE_ANIMATION_SPEED))
        exclude.append(spike_pos)

def start_game():
    global particle_timer, particles, snake_red_timer, gold_apple, gold_timer, games_played, bug_pos, bug_timer, bug_counter, bug_heads, bucket_mode, coins, power_ups, active_power_ups, autosave_timer, apples_since_last_chest, chest_apples_required
    games_played += 1
    if games_played >= 1 and not badges["1games"]:
        badges["1games"] = True
    if games_played >= 10 and not badges["10games"]:
        badges["10games"] = True
    if games_played >= 25 and not badges["25games"]:
        badges["25games"] = True
    
    snake = [(CELL * 2, CELL * 2), (CELL * 1, CELL * 2)]  # Cap și coadă la început
    direction = (CELL, 0)
    current_sum = 0
    score = 0
    max_num = DIFFICULTIES[current_difficulty]["max_num"]
    operations = DIFFICULTIES[current_difficulty]["operations"]
    apple_number = random.randint(1, max_num)
    operation = "+"
    apple = random_cell(snake)
    num_walls = {"Ușoară": 10, "Medie": 10, "Greu": 10}[current_difficulty]
    walls = []
    metal_walls = []  # Pereți metalici indestructibili
    exclude = snake + [apple]
    for _ in range(num_walls):
        wall_pos = random_cell(exclude, walls)
        walls.append(wall_pos)
        exclude.append(wall_pos)
    
    # Adaugă 5 pereți metalici indestructibili
    for _ in range(5):
        metal_wall_pos = random_cell(exclude, walls + metal_walls)
        metal_walls.append(metal_wall_pos)
        exclude.append(metal_wall_pos)
    
    paused = False
    particles.clear()
    particle_timer = 0
    snake_red_timer = 0
    gold_apple = None
    gold_timer = 0
    bug_pos = None
    bug_timer = 0
    bug_counter = 0
    bug_heads = 0
    bucket_mode = False
    
    # Inițializează power-ups-urile
    power_ups = []
    active_power_ups = {"speed": 0, "magnet": 0, "shield": 0, "ghost": 0, "coins": 0}
    
    # Inițializează autosave-ul
    autosave_timer = 0
    # Reset cufere și progres
    chests.clear()
    apples_since_last_chest = 0
    chest_apples_required = 5
    # Inițializează cuferele
    chests.clear()
    
    # Inițializează spike-urile după ce toate celelalte obiecte sunt plasate
    init_spikes(snake, walls, apple)
    
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_p:
                    paused = not paused
                if not paused:
                    if e.key == pygame.K_w and direction != (0, CELL):
                        direction = (0, -CELL)
                    if e.key == pygame.K_s and direction != (0, -CELL):
                        direction = (0, CELL)
                    if e.key == pygame.K_a and direction != (CELL, 0):
                        direction = (-CELL, 0)
                    if e.key == pygame.K_d and direction != (-CELL, 0):
                        direction = (CELL, 0)
        if paused:
            continue
        
        proposed_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        atinge_marginea = (
            proposed_head[0] < 0 or proposed_head[0] >= WIDTH or
            proposed_head[1] < 0 or proposed_head[1] >= HEIGHT or
            proposed_head[0] == 0 or proposed_head[0] == WIDTH-CELL or
            proposed_head[1] == 0 or proposed_head[1] == HEIGHT-CELL
        )
        hits_wall = proposed_head in walls
        hits_metal_wall = proposed_head in metal_walls
        hits_self = proposed_head in snake
        
        # Verifică coliziunea cu spike-urile
        hits_spike = False
        spike_type = None
        for spike in spikes:
            spike_x, spike_y, spike_type, frame, timer = spike
            if proposed_head == (spike_x, spike_y):
                hits_spike = True
                break

        ate_apple = proposed_head == apple
        ate_gold = gold_apple is not None and proposed_head == gold_apple
        
        # Verifică coliziunea cu power-ups-urile
        ate_power_up = False
        power_up_type = None
        for i, power_up in enumerate(power_ups):
            power_x, power_y, power_type, timer = power_up
            if proposed_head == (power_x, power_y):
                ate_power_up = True
                power_up_type = power_type
                power_ups.pop(i)  # Elimină power-up-ul
                break

        # Verifică coliziunea cu cuferele
        if not ate_power_up:
            for i in range(len(chests) - 1, -1, -1):
                cx, cy, opened, timer = chests[i]
                if proposed_head == (cx, cy):
                    if not opened:
                        # Deschide cufărul: arată imaginea deschisă scurt timp, dă monede
                        coin_reward = random.choice([10,20,30,40,50,60,70,80,90])
                        coins += coin_reward
                        # Crește cerința pentru următorul cufăr
                        chest_apples_required += 5
                        # Marchează ca deschis pentru 20 cadre
                        chests[i] = (cx, cy, True, 20)
                        save_game_data()
                    break

        # Verifică coliziunea cu marginea hărții - moare instant
        if atinge_marginea:
            return game_over(score)
        
        if hits_self:
            if is_power_up_active("ghost"):
                # Ghost power-up permite trecerea prin sine
                pass
            elif len(snake) > 1:
                snake.pop()
                snake_red_timer = 20
            else:
                return game_over(score)
            continue
        elif hits_spike:
            if is_power_up_active("shield"):
                # Shield power-up protejează de o coliziune
                active_power_ups["shield"] = 0  # Consumă shield-ul
                continue
            
            # Găsește spike-ul specific pentru a determina efectul
            spike_effect = None
            for spike in spikes:
                spike_x, spike_y, spike_type, frame, timer = spike
                if proposed_head == (spike_x, spike_y):
                    if spike_type == 'spike':
                        if frame == 2:  # spike3 (frame 2 = imaginea 3)
                            spike_effect = 'kill'
                        elif frame == 3:  # spike4 (frame 3 = imaginea 4)
                            spike_effect = 'kill'
                        # spike1-2 (frame 0-1) - trece prin ele
                    else:  # spikewood
                        if frame == 2:  # spikewood3 (frame 2 = imaginea 3)
                            spike_effect = 'damage_3'
                        elif frame == 3:  # spikewood4 (frame 3 = imaginea 4)
                            spike_effect = 'damage_5'
                        # spikewood1-2 (frame 0-1) - trece prin ele
                    break
            
            if spike_effect == 'kill':
                # Spike3-4 ucide șarpele
                return game_over(score)
            elif spike_effect == 'damage_3':
                # Spikewood3 scade 3 din lungime
                for _ in range(min(3, len(snake) - 1)):
                    if len(snake) > 1:
                        snake.pop()
                snake_red_timer = 20
            elif spike_effect == 'damage_5':
                # Spikewood4 scade 5 din lungime
                for _ in range(min(5, len(snake) - 1)):
                    if len(snake) > 1:
                        snake.pop()
                snake_red_timer = 20
            # Dacă spike_effect este None, șarpele trece prin spike-urile 1-2
            continue
        elif hits_metal_wall:
            # Pereții metalici ucid șarpele și nu pot fi distruși
            return game_over(score)
        elif hits_wall:
            if bucket_mode and not atinge_marginea and proposed_head in walls:
                # Când folosește snake_bucket, poate să distrugă peretele
                walls.remove(proposed_head)
                bucket_mode = False
                snake.insert(0, proposed_head)
                if not ate_apple and not ate_gold:
                    snake.pop()
            else:
                # Pereții ucid șarpele (exceptie când folosește snake_bucket)
                return game_over(score)
            continue
        else:
            snake.insert(0, proposed_head)
            if ate_gold:
                gold_apple = None
            if not ate_apple and not ate_gold:
                snake.pop()
        
        # Удалена дублированная проверка коллизий - уже проверяется выше
        
        if ate_apple:
            correct = show_math_question(current_sum, abs(apple_number), operation)
            if correct:
                if operation == "+":
                    current_sum += abs(apple_number)
                else:
                    current_sum -= abs(apple_number)
                current_sum = min(current_sum, max_num)
                current_sum = max(current_sum, 0)
                score += 1
                coins += 10  # Adaugă 10 coins pentru răspunsul corect
                add_xp(15)  # Adaugă 15 XP pentru răspunsul corect
                for _ in range(50):
                    particles.append(Particle(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
                particle_timer = 60
                # Apariție gold apple cu 10% șansă
                if random.random() < 0.1:
                    gold_apple = random_cell(snake + walls + [apple])
                    gold_timer = 300  # Aproximativ 30 secunde la viteza jocului
                
                # Increment progres pentru cufăr și spawnează când pragul este atins
                apples_since_last_chest += 1
                if apples_since_last_chest >= chest_apples_required and not any(not opened for _, _, opened, _ in chests):
                    exclude_chest = snake + walls + [apple]
                    if gold_apple:
                        exclude_chest.append(gold_apple)
                    exclude_chest += [(px, py) for (px, py, _, _) in power_ups]
                    spawn_chest(exclude_chest)
                    apples_since_last_chest = 0
                operation = random.choice(operations)
                if operation == "+":
                    apple_number = random.randint(1, max_num - current_sum) if current_sum < max_num else 1
                else:
                    apple_number = -random.randint(1, current_sum) if current_sum > 0 else 1
                apple = random_cell(snake, walls)
            else:
                snake.pop()  # Nu crește dacă răspuns greșit
        
        if ate_gold:
            max_hard = max_num + 5
            operation_gold = random.choice(operations)
            if operation_gold == "+":
                apple_number_gold = random.randint(1, max_hard - current_sum) if current_sum < max_hard else 1
            else:
                apple_number_gold = -random.randint(1, current_sum) if current_sum > 0 else 1
            correct = show_math_question(current_sum, abs(apple_number_gold), operation_gold)
            if correct:
                if operation_gold == "+":
                    current_sum += abs(apple_number_gold)
                else:
                    current_sum -= abs(apple_number_gold)
                current_sum = min(current_sum, max_hard)
                current_sum = max(current_sum, 0)
                score += 1
                coins += 10  # Adaugă 10 coins pentru răspunsul corect la mărul de aur
                add_xp(25)  # Adaugă 25 XP pentru mărul de aur (mai mult decât normal)
                bucket_mode = True
                for _ in range(50):
                    particles.append(Particle(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
                particle_timer = 60
            else:
                snake.pop()  # Nu crește dacă răspuns greșit
        
        if ate_power_up:
            # Activează power-up-ul
            activate_power_up(power_up_type)
            
            # Efecte speciale pentru fiecare power-up
            if power_up_type == "coins":
                # Coin Storm - adaugă monede extra
                coins += 20
                save_game_data()
            elif power_up_type == "magnet":
                # Magnet - atrage mărul către șarpe
                if apple:
                    # Calculează direcția către șarpe
                    dx = snake[0][0] - apple[0]
                    dy = snake[0][1] - apple[1]
                    if dx != 0:
                        apple = (apple[0] + CELL if dx > 0 else apple[0] - CELL, apple[1])
                    if dy != 0:
                        apple = (apple[0], apple[1] + CELL if dy > 0 else apple[1] - CELL)
        
        draw_background()
        draw_walls(walls)
        draw_metal_walls(metal_walls)  # Desenează pereții metalici
        draw_spikes()  # Desenează spike-urile
        draw_chests()  # Desenează cuferele
        draw_power_ups()  # Desenează power-ups-urile
        if gold_apple:
            draw_gold_apple(gold_apple)
            gold_timer -= 1
            if gold_timer <= 0:
                gold_apple = None
        draw_apple(apple, apple_number)
        draw_snake(snake, direction, current_sum)
        # Afișează coins-urile în colțul dreapta sus
        draw_coins()
        # Afișează bara de XP în colțul stânga sus
        draw_xp_bar()
        
        # Actualizează power-ups-urile și cuferele
        update_power_ups()
        update_chests()
        
        # Autosave la fiecare 15 secunde
        autosave_timer += 1
        if autosave_timer >= AUTOSAVE_INTERVAL:
            save_game_data()
            autosave_timer = 0
        
        if particle_timer > 0:
            particle_timer -= 1
        for particle in particles[:]:
            particle.update()
            particle.draw(screen)
            if particle.life <= 0:
                particles.remove(particle)
        
        if snake_red_timer > 0:
            snake_red_timer -= 1
        
        # Actualizează animația spike-urilor
        update_spikes()
        
        display_length = max(1, len(snake) - 1)  # Coada apare oricum, chiar dacă șarpele are 0 puncte
        
        # Desenează "Sum:" text
        sum_label = font.render("Sum:", True, (0, 0, 0))
        screen.blit(sum_label, (10, 10))
        # Desenează suma folosind imagini de cifre
        draw_number_with_digits(current_sum, (10 + sum_label.get_width() + 20, 10 + 15), 0.9)
        
        # Desenează "Length:" text
        length_label = font.render("Length:", True, (0, 0, 0))
        screen.blit(length_label, (10, 40))
        # Desenează lungimea folosind imagini de cifre
        draw_number_with_digits(display_length, (10 + length_label.get_width() + 20, 40 + 15), 0.9)
        
        # Desenează "Score:" text
        score_label = font.render("Score:", True, (0, 0, 0))
        score_label_rect = score_label.get_rect(topright=(WIDTH - 10, 10))
        screen.blit(score_label, score_label_rect)
        # Desenează scorul folosind imagini de cifre
        draw_number_with_digits(score, (WIDTH - 10, 10 + 15), 0.9)
        
        # Desenează power-ups-urile active
        y_offset = 50
        for power_type, timer in active_power_ups.items():
            if timer > 0:
                power_name = power_up_types[power_type]["name"]
                power_color = power_up_types[power_type]["color"]
                power_text = font.render(f"{power_name} ({timer//20}s)", True, power_color)
                power_rect = power_text.get_rect(topright=(WIDTH - 10, y_offset))
                screen.blit(power_text, power_rect)
                y_offset += 25
        
        if paused:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(160)
            screen.blit(overlay, (0, 0))
            pause_text = option_font.render("PAUZĂ", True, (255, 255, 255))
            pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
            screen.blit(pause_text, pause_rect)
            draw_button("Continuă (P)", (WIDTH // 2, HEIGHT // 2))
        
        pygame.display.flip()
        base_speed = min(12, 6 + len(snake) // 4)  # Viteza puțin mai încet
        if snake_red_timer > 0:
            base_speed = max(6, base_speed - 1)  # Viteza puțin mai încet chiar și când este roșu
        
        # Speed Boost power-up
        if is_power_up_active("speed"):
            base_speed = min(20, base_speed + 8)  # Viteza mult mai rapidă
        
        clock.tick(max(1, int(base_speed * 1.0)))  # Multiplicator normal pentru viteză

def main():
    load_game_data()  # Încarcă datele salvate la începutul jocului
    show_menu()
    return start_game()

if __name__ == "__main__":
    main()