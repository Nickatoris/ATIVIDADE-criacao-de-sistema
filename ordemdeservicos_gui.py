import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

DISPOSITIVOS = {1: "Celular", 2: "Computador", 3: "Laptop", 4: "Outro"}
PRIORIDADES = {1: "Alta", 2: "Média", 3: "Baixa"}

ARQUIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ordens.json")


def carregar():
    try:
        with open(ARQUIVO, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def salvar(ordens):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(ordens, f, ensure_ascii=False, indent=2)


def celular_valido(valor):
    digitos = "".join(c for c in valor if c.isdigit())
    return 10 <= len(digitos) <= 13


def ordenar(ordens):
    return sorted(ordens, key=lambda o: (o["prioridade"], o["id"]))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Assistência Técnica - Ordens de Serviço")
        self.geometry("900x520")
        self.minsize(800, 480)

        self.ordens = carregar()

        estilo = ttk.Style(self)
        if "vista" in estilo.theme_names():
            estilo.theme_use("vista")
        elif "clam" in estilo.theme_names():
            estilo.theme_use("clam")
        estilo.configure("Treeview", rowheight=26)

        self._montar_formulario()
        self._montar_lista()
        self.atualizar_lista()

    # ---------- Layout ----------
    def _montar_formulario(self):
        quadro = ttk.LabelFrame(self, text=" Registrar serviço ", padding=12)
        quadro.pack(side="left", fill="y", padx=10, pady=10)

        ttk.Label(quadro, text="Nome do cliente:").pack(anchor="w")
        self.var_nome = tk.StringVar()
        ttk.Entry(quadro, textvariable=self.var_nome, width=30).pack(
            anchor="w", pady=(0, 10))

        ttk.Label(quadro, text="Tipo de dispositivo:").pack(anchor="w")
        self.cb_disp = ttk.Combobox(
            quadro, values=list(DISPOSITIVOS.values()),
            state="readonly", width=27)
        self.cb_disp.current(0)
        self.cb_disp.pack(anchor="w", pady=(0, 10))

        ttk.Label(quadro, text="Celular (DDD + número):").pack(anchor="w")
        self.var_cel = tk.StringVar()
        ttk.Entry(quadro, textvariable=self.var_cel, width=30).pack(
            anchor="w", pady=(0, 10))

        ttk.Label(quadro, text="Prioridade:").pack(anchor="w")
        self.cb_prio = ttk.Combobox(
            quadro, values=list(PRIORIDADES.values()),
            state="readonly", width=27)
        self.cb_prio.current(1)
        self.cb_prio.pack(anchor="w", pady=(0, 15))

        ttk.Button(quadro, text="Registrar serviço",
                   command=self.registrar).pack(fill="x")

    def _montar_lista(self):
        direita = ttk.Frame(self)
        direita.pack(side="left", fill="both", expand=True,
                     padx=(0, 10), pady=10)

        quadro = ttk.LabelFrame(direita, text=" Serviços registrados ",
                                padding=8)
        quadro.pack(fill="both", expand=True)

        colunas = ("num", "cliente", "dispositivo", "prioridade")
        self.tabela = ttk.Treeview(quadro, columns=colunas,
                                   show="headings", selectmode="browse")
        for col, titulo, larg in (("num", "Nº", 50),
                                  ("cliente", "Cliente", 220),
                                  ("dispositivo", "Dispositivo", 110),
                                  ("prioridade", "Prioridade", 90)):
            self.tabela.heading(col, text=titulo)
            self.tabela.column(col, width=larg,
                               anchor="center" if col != "cliente" else "w")
        self.tabela.tag_configure("Alta", foreground="#c0392b")
        self.tabela.tag_configure("Média", foreground="#b9770e")
        self.tabela.tag_configure("Baixa", foreground="#1e8449")

        barra = ttk.Scrollbar(quadro, orient="vertical",
                              command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=barra.set)
        self.tabela.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self.tabela.bind("<<TreeviewSelect>>", self.mostrar_detalhes)

        det = ttk.LabelFrame(direita, text=" Detalhes ", padding=8)
        det.pack(fill="x", pady=(10, 0))
        self.lbl_detalhes = ttk.Label(
            det, text="Selecione um serviço na lista.", justify="left")
        self.lbl_detalhes.pack(anchor="w")

        ttk.Button(direita, text="Apagar selecionado",
                   command=self.apagar).pack(anchor="e", pady=(10, 0))

    # ---------- Ações ----------
    def registrar(self):
        nome = self.var_nome.get().strip()
        celular = self.var_cel.get().strip()

        if not nome:
            messagebox.showwarning("Campo vazio",
                                   "O nome do cliente não pode ficar vazio.")
            return
        if not celular_valido(celular):
            messagebox.showwarning(
                "Número inválido",
                "Digite o DDD + número (ex.: 98 91234-5678).")
            return

        novo_id = max((o["id"] for o in self.ordens), default=0) + 1
        self.ordens.append({
            "id": novo_id,
            "nome": nome,
            "dispositivo": self.cb_disp.current() + 1,
            "celular": celular,
            "prioridade": self.cb_prio.current() + 1,
        })
        salvar(self.ordens)

        self.var_nome.set("")
        self.var_cel.set("")
        self.cb_disp.current(0)
        self.cb_prio.current(1)
        self.atualizar_lista()
        messagebox.showinfo("Pronto", "Serviço registrado.")

    def atualizar_lista(self):
        self.tabela.delete(*self.tabela.get_children())
        for i, o in enumerate(ordenar(self.ordens), start=1):
            prio = PRIORIDADES[o["prioridade"]]
            # o iid guarda o id real da ordem
            self.tabela.insert(
                "", "end", iid=str(o["id"]), tags=(prio,),
                values=(i, o["nome"], DISPOSITIVOS[o["dispositivo"]], prio))
        self.lbl_detalhes.config(text="Selecione um serviço na lista.")

    def _ordem_selecionada(self):
        sel = self.tabela.selection()
        if not sel:
            return None
        id_ = int(sel[0])
        return next((o for o in self.ordens if o["id"] == id_), None)

    def mostrar_detalhes(self, _evento=None):
        o = self._ordem_selecionada()
        if not o:
            return
        self.lbl_detalhes.config(text=(
            f"Nº:  {o['id']:03d}\n"
            f"Cliente:  {o['nome']}\n"
            f"Dispositivo:  {DISPOSITIVOS[o['dispositivo']]}\n"
            f"Celular:  {o['celular']}\n"
            f"Prioridade:  {PRIORIDADES[o['prioridade']]}"))

    def apagar(self):
        o = self._ordem_selecionada()
        if not o:
            messagebox.showinfo("Apagar", "Selecione um serviço primeiro.")
            return
        if messagebox.askyesno("Confirmar",
                               f"Apagar o serviço de '{o['nome']}'?"):
            self.ordens.remove(o)
            salvar(self.ordens)
            self.atualizar_lista()


if __name__ == "__main__":
    App().mainloop()
