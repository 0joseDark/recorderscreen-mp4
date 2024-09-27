import cv2
import numpy as np
import pygetwindow as gw
import pyautogui
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time

# Variáveis globais para controle de gravação e arquivo de saída
recording = False
paused = False
out = None
file_path = None
fps = 30  # FPS inicial (definido pelo slider)
start_time = 0  # Tempo inicial da gravação
elapsed_time = 0  # Tempo decorrido da gravação (considerando pausas)

def select_window():
    """
    Seleciona a janela com base no título escolhido pelo usuário.
    """
    windows = gw.getAllTitles()
    selected_window = selected_window_var.get()
    if selected_window in windows:
        return gw.getWindowsWithTitle(selected_window)[0]
    else:
        return None

def update_timer():
    """
    Atualiza o tempo na interface enquanto a gravação está em andamento.
    """
    global start_time, elapsed_time
    while recording:
        if not paused:
            elapsed_time = time.time() - start_time
            timer_label.config(text=format_time(elapsed_time))
        time.sleep(1)  # Atualiza o tempo a cada segundo

def format_time(seconds):
    """
    Converte o tempo de segundos para o formato HH:MM:SS.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def record_screen():
    """
    Função de gravação da tela da janela selecionada.
    """
    global recording, paused, out, file_path, fps, start_time, elapsed_time
    selected_window = select_window()
    if not selected_window:
        messagebox.showerror("Erro", "Janela não encontrada!")
        return

    recording = True
    paused = False
    start_time = time.time() - elapsed_time  # Ajusta o tempo para retomar de onde parou

    # Iniciar a thread para atualizar o timer
    threading.Thread(target=update_timer, daemon=True).start()

    # Configurações do vídeo
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(file_path, fourcc, fps, (selected_window.width, selected_window.height))

    # Melhorando a captura de frames com buffer e captura mais direta
    while recording:
        if not paused:
            img = pyautogui.screenshot(region=(selected_window.left, selected_window.top, selected_window.width, selected_window.height))
            frame = np.array(img)  # Conversão direta
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Conversão para BGR
            out.write(frame)  # Escrevendo o frame no arquivo de saída
        cv2.waitKey(int(1000 / fps))  # Controle da taxa de frames

def start_recording():
    """
    Inicia a gravação em uma thread separada.
    """
    global elapsed_time
    if not file_path:
        messagebox.showerror("Erro", "Selecione o caminho e nome do arquivo primeiro!")
        return
    elapsed_time = 0  # Reseta o tempo quando uma nova gravação começa
    threading.Thread(target=record_screen).start()

def pause_recording():
    """
    Pausa ou retoma a gravação e o timer.
    """
    global paused, start_time
    paused = not paused
    pause_button.config(text="Pausar" if not paused else "Continuar")
    if not paused:
        start_time = time.time() - elapsed_time  # Ajusta o tempo para continuar de onde parou

def stop_recording():
    """
    Para a gravação e salva o arquivo.
    """
    global recording, out, elapsed_time
    recording = False
    if out:
        out.release()
    out = None
    elapsed_time = 0  # Reseta o tempo ao parar a gravação
    timer_label.config(text="00:00:00")  # Reseta o contador na interface
    messagebox.showinfo("Informação", f"Gravação finalizada e salva como {file_path}")

def on_closing():
    """
    Trata o fechamento da aplicação, garantindo que a gravação seja parada.
    """
    global recording
    if recording:
        messagebox.showwarning("Aviso", "Pare a gravação antes de sair.")
    else:
        root.destroy()

def select_file_path():
    """
    Abre um diálogo para selecionar o caminho e o nome do arquivo MP4.
    """
    global file_path
    file_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
    file_path_label.config(text=file_path if file_path else "Nenhum arquivo selecionado")

def adjust_fps(value):
    """
    Ajusta a taxa de frames por segundo de acordo com o slider.
    """
    global fps
    fps = int(value)
    fps_label.config(text=f"FPS: {fps}")

def increase_fps(event):
    """
    Aumenta o FPS quando a tecla "+" é pressionada.
    """
    global fps
    if fps < 200:
        fps += 10
        fps_slider.set(fps)
        fps_label.config(text=f"FPS: {fps}")

def decrease_fps(event):
    """
    Diminui o FPS quando a tecla "-" é pressionada.
    """
    global fps
    if fps > 10:
        fps -= 10
        fps_slider.set(fps)
        fps_label.config(text=f"FPS: {fps}")

# Configuração da interface gráfica
root = tk.Tk()
root.title("Gravador de Tela")

selected_window_var = tk.StringVar()

# Menu de seleção de janela
windows = gw.getAllTitles()
window_label = tk.Label(root, text="Selecione a janela para gravar:")
window_label.pack(pady=5)
window_menu = ttk.Combobox(root, textvariable=selected_window_var)
window_menu['values'] = windows
window_menu.pack(pady=5)

# Botão para selecionar o caminho do arquivo
file_button = tk.Button(root, text="Selecionar Caminho e Nome do Arquivo", command=select_file_path)
file_button.pack(pady=5)

# Label para mostrar o caminho do arquivo selecionado
file_path_label = tk.Label(root, text="Nenhum arquivo selecionado")
file_path_label.pack(pady=5)

# Slider para ajustar o FPS
fps_slider = tk.Scale(root, from_=10, to=200, orient='horizontal', length=300, command=adjust_fps, label="FPS (10-200)")
fps_slider.set(30)  # Valor inicial do FPS
fps_slider.pack(pady=5)

fps_label = tk.Label(root, text=f"FPS: {fps}")
fps_label.pack(pady=5)

# Timer para mostrar o tempo de gravação
timer_label = tk.Label(root, text="00:00:00", font=("Helvetica", 16))
timer_label.pack(pady=5)

# Botões de controle de gravação
start_button = tk.Button(root, text="Gravar", command=start_recording)
start_button.pack(pady=5)

pause_button = tk.Button(root, text="Pausar", command=pause_recording)
pause_button.pack(pady=5)

stop_button = tk.Button(root, text="Parar", command=stop_recording)
stop_button.pack(pady=5)

exit_button = tk.Button(root, text="Sair", command=on_closing)
exit_button.pack(pady=5)

# Bind para as teclas "+" e "-" controlarem o FPS
root.bind("<Key-plus>", increase_fps)
root.bind("<Key-minus>", decrease_fps)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
