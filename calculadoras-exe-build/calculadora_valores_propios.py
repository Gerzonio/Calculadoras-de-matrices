import random
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

import numpy as np
import sympy as sp

# ── Paleta ────────────────────────────────────────────────────────────
BG_MAIN      = "#FFFDE7"
BG_RESULT    = "#FFFFF5"
COLOR_LAMBDA = "#1A237E"
COLOR_VECTOR = "#4A148C"

COMPLEXITY_THRESHOLD = 30

# ── Helpers de formato ────────────────────────────────────────────────
SEP = "=" * 70

def _fmt_complex(z, digits=6):
    z = complex(z)
    if abs(z.imag) < 1e-9 * max(1.0, abs(z.real)):
        return f"{z.real:.{digits}g}"
    sign = "+" if z.imag >= 0 else "-"
    return f"{z.real:.{digits}g} {sign} {abs(z.imag):.{digits}g}i"

def _sec(title):
    return [SEP, title, SEP]

# ── Matemática ────────────────────────────────────────────────────────
def _parse_entry(text, row, col):
    try:
        val = sp.sympify(text.strip() or "0")
        if not val.is_number:
            raise ValueError()
        return val
    except Exception:
        raise ValueError(f"Valor inválido en fila {row+1}, columna {col+1}: '{text}'")


def _group_numeric_eigenvalues(eigvals, n):
    scale = max(1.0, float(np.max(np.abs(eigvals))))
    tol, used, groups = 1e-6 * scale, [False] * n, []
    for i in range(n):
        if used[i]:
            continue
        group = [i]
        used[i] = True
        for j in range(i + 1, n):
            if not used[j] and abs(eigvals[i] - eigvals[j]) < tol:
                group.append(j); used[j] = True
        groups.append(group)
    return groups


def _numeric_eigen_report(A):
    n = A.shape[0]
    summary = {"eigens": [], "diagonalizable": None}
    eigvals, eigvecs = np.linalg.eig(np.array(A.evalf(30), dtype=complex))
    groups = _group_numeric_eigenvalues(eigvals, n)

    proc = [*_sec("PASO 3 (numérico): Valores propios ≈ raíces de p(λ)")]
    for i, g in enumerate(groups, 1):
        proc.append(f"  λ{i} ≈ {_fmt_complex(eigvals[g[0]])}   (multiplicidad ≈ {len(g)})")
    proc.append("")

    proc += _sec("PASO 4 (numérico): Vectores propios (normalizados)")
    for i, g in enumerate(groups, 1):
        lam_str = _fmt_complex(eigvals[g[0]])
        proc.append(f"\n  Para λ{i} ≈ {lam_str}:")
        vecs_str = []
        for k in g:
            comps = ", ".join(_fmt_complex(c) for c in eigvecs[:, k])
            proc.append(f"      v = ({comps})")
            vecs_str.append(f"({comps})")
        summary["eigens"].append({"lambda": f"λ{i} ≈ {lam_str}", "mult": len(g), "vectors": vecs_str})
    proc.append("")

    proc += _sec("PASO 5: ¿Es la matriz diagonalizable?")
    if len(groups) == n:
        proc.append(f"  SÍ (numéricamente): hay n = {n} valores propios distintos.")
        summary["diagonalizable"] = True
    else:
        proc.append("  No se puede determinar con certeza solo con aproximación numérica.")

    return proc, summary


def solve_eigen_problem(A):
    lam = sp.symbols("lambda")
    n   = A.shape[0]
    summary = {"eigens": [], "diagonalizable": None}

    proc = [*_sec("MATRIZ A"), sp.pretty(A), "",
            *_sec("PASO 1: Matriz (A - λI)"), sp.pretty(A - lam * sp.eye(n)), ""]

    char_poly = sp.expand(A.charpoly(lam).as_expr())
    proc += [*_sec("PASO 2: Polinomio característico  p(λ) = det(A - λI)"),
             f"  p(λ) = {char_poly}",
             f"  p(λ) = {sp.factor(char_poly)}   (forma factorizada)",
             "", "  Se resuelve la ecuación característica:  p(λ) = 0", ""]

    eigen_data  = A.eigenvals()
    too_complex = any(sp.count_ops(v) > COMPLEXITY_THRESHOLD or v.has(sp.CRootOf) for v in eigen_data)

    if not too_complex:
        block = _sec("PASO 3: Valores propios (raíces de p(λ))")
        for val, mult in eigen_data.items():
            val_s = sp.nsimplify(val)
            tipo  = "real" if val_s.is_real else "complejo"
            block.append(f"  λ = {val_s}   ≈ {sp.N(val_s, 6)}   (multiplicidad algebraica = {mult}, {tipo})")
        block.append("")

        block += _sec("PASO 4: Vectores propios  →  resolver (A - λI)v = 0")
        try:
            eigen_vects = A.eigenvects()
        except Exception:
            eigen_vects = None

        if eigen_vects is not None:
            for val, mult, vects in eigen_vects:
                val_s    = sp.nsimplify(val)
                geo_mult = len(vects)
                block.append(f"\n  Para λ = {val_s}  (mult. algebraica = {mult}, mult. geométrica = {geo_mult}):")
                vecs_str = []
                for k, v in enumerate(vects, 1):
                    comps = ", ".join(str(c) for c in v.applyfunc(sp.nsimplify))
                    block.append(f"      v{k} = ({comps})")
                    vecs_str.append(f"({comps})")
                if geo_mult < mult:
                    block.append("      * Multiplicidad geométrica < algebraica.")
                summary["eigens"].append({"lambda": str(val_s), "mult": mult, "vectors": vecs_str})

        if eigen_vects is None or sum(len(l) for l in block) > 4000:
            too_complex = True
        else:
            proc += block + [""]
            proc += _sec("PASO 5: ¿Es la matriz diagonalizable?")
            try:
                P, D = A.diagonalize()
                diag_text = (f"  SÍ. A = P·D·P⁻¹, con:\n\n"
                             f"  P (columnas = vectores propios) =\n{sp.pretty(P)}\n\n"
                             f"  D (diagonal de valores propios) =\n{sp.pretty(D)}")
                proc.append(diag_text if len(diag_text) <= 3000
                            else "  SÍ, la matriz es diagonalizable (matrices P y D muy grandes para mostrar).")
                summary["diagonalizable"] = True
            except Exception:
                proc.append("  NO. La suma de las multiplicidades geométricas es menor que n.")
                summary["diagonalizable"] = False

    if too_complex:
        summary["eigens"] = []
        proc += ["NOTA: Las raíces EXACTAS requieren radicales anidados muy largos. "
                 "Se presenta solución NUMÉRICA de alta precisión.", ""]
        num_lines, num_summary = _numeric_eigen_report(A)
        proc += num_lines
        summary.update(num_summary)

    return summary, "\n".join(proc)

# ── Aplicación ────────────────────────────────────────────────────────
class EigenCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Valores y Vectores Propios")
        self.root.geometry("980x760")
        self.root.minsize(820, 650)
        self.root.configure(bg=BG_MAIN)
        self.entries = []
        self.n = 3
        self._proc_visible = False
        self._build_ui()

    def _build_ui(self):
        style = ttk.Style()
        try: style.theme_use("clam")
        except tk.TclError: pass

        for widget, opts in [
            ("TFrame",            {"background": BG_MAIN}),
            ("TLabelframe",       {"background": BG_MAIN}),
            ("TLabelframe.Label", {"background": BG_MAIN, "font": ("Arial", 10, "bold"), "foreground": "#333"}),
            ("TRadiobutton",      {"background": BG_MAIN, "font": ("Arial", 10)}),
            ("TLabel",            {"background": BG_MAIN}),
            ("TEntry",            {"fieldbackground": "#FFFFFF"}),
        ]:
            style.configure(widget, **opts)

        # Barra superior
        top = ttk.Frame(self.root, padding=(12, 8))
        top.pack(fill="x")
        ttk.Label(top, text="Orden de la matriz (n):", font=("Arial", 11, "bold")).pack(side="left", padx=(0, 10))
        self.n_var = tk.IntVar(value=3)
        for v in range(2, 6):
            ttk.Radiobutton(top, text=str(v), variable=self.n_var, value=v,
                            command=self.build_matrix_grid).pack(side="left", padx=4)

        # Zona central: matriz + botones laterales
        center = tk.Frame(self.root, bg=BG_MAIN)
        center.pack(fill="x", padx=12, pady=4)

        self.matrix_frame = ttk.LabelFrame(center, text="Matriz A", padding=12)
        self.matrix_frame.pack(side="left", fill="both")

        side = tk.Frame(center, bg=BG_MAIN)
        side.pack(side="left", padx=12, anchor="n", pady=8)
        self._gray_btn(side, "Llenar ejemplo\naleatorio", self.fill_example).pack(fill="x", pady=(0, 8))
        self._gray_btn(side, "Limpiar", self.clear_matrix).pack(fill="x")

        # Botón calcular
        action = tk.Frame(self.root, bg=BG_MAIN)
        action.pack(fill="x", padx=12, pady=(6, 0))
        tk.Button(action, text="⟹  Calcular valores y vectores propios", command=self.calculate,
                  bg="#4A90D9", fg="#fff", font=("Arial", 11, "bold"), relief="flat",
                  padx=14, pady=7, cursor="hand2",
                  activebackground="#357ABD", activeforeground="#fff").pack(side="left")

        # Resultados
        result_outer = ttk.LabelFrame(self.root, text="Resultados", padding=10)
        result_outer.pack(fill="both", expand=True, padx=12, pady=8)

        self.summary_frame = tk.Frame(result_outer, bg=BG_RESULT, relief="flat", bd=1)
        self.summary_frame.pack(fill="x", pady=(0, 6))
        self._placeholder()

        self.proc_btn = tk.Button(result_outer, text="▶  Mostrar procedimiento paso a paso",
                                  command=self._toggle_procedure,
                                  bg="#7CB87C", fg="#fff", font=("Arial", 10, "bold"),
                                  relief="flat", padx=10, pady=5, cursor="hand2",
                                  activebackground="#5C9E5C", activeforeground="#fff")

        self.result_text = scrolledtext.ScrolledText(result_outer, wrap="word",
                                                     font=("Consolas", 9),
                                                     bg="#F9F9F0", fg="#222", state="disabled")
        self.build_matrix_grid()

    def _gray_btn(self, parent, text, cmd):
        return tk.Button(parent, text=text, command=cmd,
                         bg="#B0B0B0", fg="#2C2C2C", font=("Arial", 10),
                         relief="flat", padx=10, pady=6, cursor="hand2",
                         activebackground="#929292", activeforeground="#000", width=16)

    def _placeholder(self):
        tk.Label(self.summary_frame, text="Los resultados aparecerán aquí después de calcular.",
                 font=("Arial", 10, "italic"), bg=BG_RESULT, fg="#888", pady=8).pack()

    def build_matrix_grid(self):
        for w in self.matrix_frame.winfo_children(): w.destroy()
        self.n = self.n_var.get()
        self.entries = []
        for i in range(self.n):
            row = []
            for j in range(self.n):
                e = ttk.Entry(self.matrix_frame, width=8, justify="center", font=("Arial", 11))
                e.grid(row=i, column=j, padx=4, pady=4)
                e.insert(0, "1" if i == j else "0")
                row.append(e)
            self.entries.append(row)

    def clear_matrix(self):
        for row in self.entries:
            for e in row: e.delete(0, tk.END); e.insert(0, "0")
        for w in self.summary_frame.winfo_children(): w.destroy()
        self._placeholder()
        self.proc_btn.pack_forget()
        self.result_text.pack_forget()
        self._proc_visible = False

    def fill_example(self):
        for row in self.entries:
            for e in row: e.delete(0, tk.END); e.insert(0, str(random.randint(-5, 5)))

    def read_matrix(self):
        return sp.Matrix([[_parse_entry(self.entries[i][j].get(), i, j)
                           for j in range(self.n)] for i in range(self.n)])

    def calculate(self):
        try:
            A = self.read_matrix()
        except ValueError as e:
            return messagebox.showerror("Error de entrada", str(e))
        try:
            summary_data, procedure_text = solve_eigen_problem(A)
        except Exception as e:
            return messagebox.showerror("Error en el cálculo", str(e))

        self._show_summary(summary_data)

        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, procedure_text)
        self.result_text.config(state="disabled")

        self.proc_btn.pack(anchor="w", pady=(0, 4))
        if self._proc_visible:
            self.result_text.pack(fill="both", expand=True)

    def _show_summary(self, data):
        for w in self.summary_frame.winfo_children(): w.destroy()

        tk.Label(self.summary_frame, text="Valores y Vectores Propios",
                 font=("Arial", 12, "bold"), bg=BG_RESULT, fg="#1A237E", pady=6).pack(anchor="w", padx=10)

        is_diag = data.get("diagonalizable")
        diag_map = {
            True:  ("✔  La matriz ES diagonalizable",      "#2E7D32"),
            False: ("✘  La matriz NO es diagonalizable",   "#B71C1C"),
            None:  ("ℹ  Diagonalizabilidad: ver procedimiento", "#555"),
        }
        txt, color = diag_map[is_diag]
        tk.Label(self.summary_frame, text=txt, font=("Arial", 10, "bold"),
                 bg=BG_RESULT, fg=color, pady=2).pack(anchor="w", padx=10)

        tk.Frame(self.summary_frame, bg="#C8C8A0", height=1).pack(fill="x", padx=10, pady=4)

        for item in data.get("eigens", []):
            row = tk.Frame(self.summary_frame, bg=BG_RESULT)
            row.pack(fill="x", padx=10, pady=3)
            tk.Label(row, text=f"λ = {item['lambda']}", font=("Consolas", 11, "bold"),
                     bg=BG_RESULT, fg=COLOR_LAMBDA, width=34, anchor="w").pack(side="left")
            tk.Label(row, text=f"(mult. {item['mult']})", font=("Arial", 9),
                     bg=BG_RESULT, fg="#666").pack(side="left", padx=(0, 16))
            for vstr in item["vectors"]:
                tk.Label(row, text=f"v = {vstr}", font=("Consolas", 10),
                         bg=BG_RESULT, fg=COLOR_VECTOR).pack(side="left", padx=6)

        tk.Frame(self.summary_frame, bg=BG_RESULT, height=6).pack()

    def _toggle_procedure(self):
        if self._proc_visible:
            self.result_text.pack_forget()
            self._proc_visible = False
            self.proc_btn.config(text="▶  Mostrar procedimiento paso a paso")
        else:
            self.result_text.pack(fill="both", expand=True)
            self._proc_visible = True
            self.proc_btn.config(text="▼  Ocultar procedimiento")


if __name__ == "__main__":
    root = tk.Tk()
    EigenCalculatorApp(root)
    root.mainloop()
