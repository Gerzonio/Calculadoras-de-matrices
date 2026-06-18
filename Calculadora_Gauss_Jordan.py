import tkinter as tk

# ── Paleta ────────────────────────────────────────────────────────────
BG         = "#FFFDE7"
BTN_MAIN   = dict(bg="#4A90D9", fg="#FFFFFF", activebackground="#357ABD", activeforeground="#fff")
BTN_GRAY   = dict(bg="#B0B0B0", fg="#2C2C2C", activebackground="#929292", activeforeground="#000")
BTN_COMMON = dict(font=("Arial", 10, "bold"), relief="flat", cursor="hand2")

# ── Matemática ────────────────────────────────────────────────────────
def texto_a_numero(texto):
    texto = texto.strip()
    if "/" not in texto:
        return float(texto)
    num, den = texto.split("/")
    if float(den) == 0:
        raise ValueError("Denominador cero.")
    return float(num) / float(den)


def gauss_jordan(matriz, n):
    for col in range(n):
        fila_pivote = max(range(col, n), key=lambda f: abs(matriz[f][col]))
        if abs(matriz[fila_pivote][col]) < 1e-12:
            raise ValueError("El sistema no tiene solucion unica.")
        if fila_pivote != col:
            matriz[col], matriz[fila_pivote] = matriz[fila_pivote], matriz[col]

        pivote = matriz[col][col]
        matriz[col] = [x / pivote for x in matriz[col]]

        for fila in range(n):
            if fila != col:
                f = matriz[fila][col]
                matriz[fila] = [matriz[fila][k] - f * matriz[col][k] for k in range(n + 1)]

    return [matriz[i][n] for i in range(n)]

# ── UI helpers ────────────────────────────────────────────────────────
ventana    = tk.Tk()
ventana.title("Calculadora Gauss-Jordan")
ventana.geometry("520x520")
ventana.configure(bg=BG)

contenedor = tk.Frame(ventana, bg=BG)
contenedor.pack(padx=20, pady=20, expand=True, fill="both")

entradas_matriz = []

limpiar  = lambda: [w.destroy() for w in contenedor.winfo_children()]
label    = lambda texto, **kw: tk.Label(contenedor, text=texto, bg=BG, **kw)
btn_main = lambda texto, cmd, **kw: tk.Button(contenedor, text=texto, command=cmd,
                                               padx=12, pady=5, **BTN_MAIN, **BTN_COMMON, **kw)
btn_gray = lambda texto, cmd: tk.Button(contenedor, text=texto, command=cmd,
                                         padx=10, pady=4, **BTN_GRAY, **BTN_COMMON)

# ── Pantallas ─────────────────────────────────────────────────────────
def pantalla_pedir_n():
    limpiar()
    label("Calculadora Gauss-Jordan", font=("Arial", 16, "bold")).pack(pady=10)
    label("Cuantas incognitas tiene el sistema? (entre 2 y 10)").pack(pady=5)

    entrada_n = tk.Entry(contenedor, width=5, justify="center", bg="#FFFFFF")
    entrada_n.pack(pady=5)

    error = label("", fg="red")
    error.pack()

    def continuar():
        valor = entrada_n.get()
        if not valor.isdigit():
            return error.config(text="Escriba un numero entero.")
        n = int(valor)
        if not (2 <= n <= 10):
            return error.config(text="n debe estar entre 2 y 10.")
        pantalla_pedir_matriz(n)

    btn_main("Continuar", continuar).pack(pady=10)


def pantalla_pedir_matriz(n):
    global entradas_matriz
    entradas_matriz = []
    limpiar()

    label(f"Ingrese los coeficientes (sistema {n}x{n})", font=("Arial", 13, "bold")).pack(pady=10)

    grilla = tk.Frame(contenedor, bg=BG)
    grilla.pack(pady=10)

    for col in range(n):
        tk.Label(grilla, text=f"x{col+1}", font=("Arial", 10, "bold"), bg=BG).grid(row=0, column=col, padx=3)
    tk.Label(grilla, text="=", font=("Arial", 10, "bold"), bg=BG).grid(row=0, column=n, padx=3)

    for fila in range(n):
        fila_entradas = []
        for col in range(n + 1):
            caja = tk.Entry(grilla, width=6, justify="center", bg="#FFFFFF")
            caja.grid(row=fila + 1, column=col, padx=3, pady=3)
            fila_entradas.append(caja)
        entradas_matriz.append(fila_entradas)

    error = label("", fg="red")
    error.pack(pady=5)

    def resolver():
        try:
            matriz = [[texto_a_numero(entradas_matriz[f][c].get()) for c in range(n + 1)] for f in range(n)]
        except ValueError:
            return error.config(text="Use numeros o fracciones tipo 1/2.")
        try:
            pantalla_resultado(gauss_jordan(matriz, n))
        except ValueError as e:
            error.config(text=str(e))

    btn_main("Resolver", resolver).pack(pady=10)
    btn_gray("Volver", pantalla_pedir_n).pack()


def pantalla_resultado(soluciones):
    limpiar()
    label("Resultado del sistema", font=("Arial", 16, "bold")).pack(pady=15)
    for i, v in enumerate(soluciones, 1):
        label(f"x{i} = {v:.4f}", font=("Arial", 12)).pack(pady=3)
    btn_main("Resolver otro sistema", pantalla_pedir_n).pack(pady=20)


# ── Arranque ──────────────────────────────────────────────────────────
pantalla_pedir_n()
ventana.mainloop()