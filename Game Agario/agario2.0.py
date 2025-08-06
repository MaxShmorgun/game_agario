from pygame import *
import random
import math
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from menu import ConnectWindow

class Food:
    def __init__(self, x, y, r, c):
        self.x = x
        self.y = y
        self.radius = r
        self.color = c


win = ConnectWindow()
win.mainloop()

name = win.name or f"Гравець{random.randint(1000, 9999)}"
host = win.host 
port = win.port 


sock = socket(AF_INET, SOCK_STREAM)
try:
    sock.connect((host, port))
except Exception as e:
    print(f"Не вдалося підключитися до сервера: {e}")
    exit()

try:
    data = sock.recv(64).decode().strip()
    my_id, start_x, start_y, start_r = map(int, data.split(','))
    my_player = [start_x, start_y, start_r]  # [x, y, radius]
    print(f"Підключено як ID: {my_id}, Початок: {my_player}")
except Exception as e:
    print(f"Помилка отримання даних: {e}")
    sock.close()
    exit()

sock.setblocking(False)


lose = False
all_players = []  
received_player_ids = set()  



random.seed(1234)
eats = []
for _ in range(300):
    x = random.randint(-2000, 2000)
    y = random.randint(-2000, 2000)
    r = random.randint(5, 15)
    c = [random.randint(100, 255) for _ in range(3)]
    eats.append(Food(x, y, r, c))



init()
window = display.set_mode((1000, 1000))
display.set_caption("Agario")
clock = time.Clock()

font1 = font.SysFont("Arial", 16)  
font2 = font.SysFont("Arial", 48)  



def receive_data():
    global all_players, lose, received_player_ids
    buffer = ""
    while True:
        try:
            data = sock.recv(4096).decode()
            if not data:
                print("Сервер розірвав з'єднання.")
                break

            buffer += data

            if "LOSE" in buffer:
                buffer = buffer.replace("LOSE", "", 1)
                lose = True
                continue

            
            received_player_ids.clear()

            while '|' in buffer:
                packet, buffer = buffer.split('|', 1)
                packet = packet.strip()
                if not packet or packet == "LOSE":
                    continue

                parts = packet.split(',')
                if len(parts) == 5:
                    try:
                        pid, x, y, r = map(int, parts[:4])
                        pname = parts[4]

                        
                        received_player_ids.add(pid)

                        if pid == my_id:
                            my_player[0], my_player[1], my_player[2] = x, y, r
                        else:
                            
                            updated = False
                            for i, p in enumerate(all_players):
                                if p[0] == pid:
                                    all_players[i] = [pid, x, y, r, pname]
                                    updated = True
                                    break
                            if not updated:
                                all_players.append([pid, x, y, r, pname])
                    except (ValueError, IndexError):
                        print(f"Некоректний пакет: {packet}")
                        continue

            
            all_players[:] = [p for p in all_players if p[0] in received_player_ids]

        except BlockingIOError:
            pass
        except Exception as e:
            print(f"Помилка прийому даних: {e}")
            break

    global running
    running = False



Thread(target=receive_data, daemon=True).start()



running = True
while running:
    dt = clock.tick(60) / 1000.0

    
    for e in event.get():
        if e.type == QUIT:
            running = False

    
    keys = key.get_pressed()
    dx, dy = 0, 0
    if keys[K_w]: dy -= 15
    if keys[K_s]: dy += 15
    if keys[K_a]: dx -= 15
    if keys[K_d]: dx += 15

    if dx != 0 and dy != 0:
        dx *= 0.7071
        dy *= 0.7071

    my_player[0] += dx
    my_player[1] += dy

    
    to_remove = []
    for eat in eats:
        dist = math.hypot(eat.x - my_player[0], eat.y - my_player[1])
        if dist < my_player[2]:
            my_player[2] += eat.radius * 0.1
            to_remove.append(eat)
    for eat in to_remove:
        eats.remove(eat)

    
    if not lose:
        try:
            msg = f"{my_id},{int(my_player[0])},{int(my_player[1])},{int(my_player[2])},{name}|"
            sock.send(msg.encode())
        except (OSError, ConnectionError):
            print("Не вдалося відправити дані. Втрачено з'єднання.")
            running = False

    
    window.fill((10, 10, 30))

    
    scale = max(0.3, min(50 / my_player[2], 0.5))

    
    draw.circle(window, (0, 255, 0), (500, 500), int(my_player[2] * scale))

    
    for eat in eats:
        sx = int((eat.x - my_player[0]) * scale + 500)
        sy = int((eat.y - my_player[1]) * scale + 500)
        draw.circle(window, eat.color, (sx, sy), int(eat.radius * scale))

    
    for p in all_players:
        px, py, pr = p[1], p[2], p[3]
        sx = int((px - my_player[0]) * scale + 500)
        sy = int((py - my_player[1]) * scale + 500)
        draw.circle(window, (0, 100, 255), (sx, sy), int(pr * scale))
        text = font1.render(p[4], True, (255, 255, 255))
        window.blit(text, (sx - text.get_width() // 2, sy - int(pr * scale) - 20))

    
    if lose:
        text = font2.render("ТИ ПРОГРАВ!", True, (255, 50, 50))
        window.blit(text, (500 - text.get_width() // 2, 500 - text.get_height() // 2))

    display.update()


sock.close()
quit()