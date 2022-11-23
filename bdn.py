# charset = "UTF-8"
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from tkinter.font import families
from pynput.keyboard import Key, Controller
from PIL import Image, ImageTk
from functools import partial
import os
from sys import exit
import sqlite3

from tkinter import TclError


class Notepy:
    def __init__(self):
        super().__init__()

        self.conn = sqlite3.connect("Configurações/configurações.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS configurações(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                fonte VARCHAR(20) NOT NULL,
                tamanho INTEGER,
                bg VARCHAR(7) NOT NULL,
                fg VARCHAR(7) NOT NULL,
                idioma VARCHAR(20) NOT NULL,
                codificação VARCHAR(8) NOT NULL,
                arquivo VARCHAR(150) NOT NULL
            );
        """)

        self.cursor.execute("""
            SELECT * FROM configurações;
        """)

        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute("""
                INSERT INTO configurações(fonte, tamanho, bg, fg, idioma, codificação, arquivo) values(?,?,?,?,?,?,?)
            """, ("calibri", 25, "#ffffff", "#000000", "Português", "utf-8", "Sem titulo"))

            self.conn.commit()

        self.cursor.execute("""
            SELECT * FROM configurações;
        """)

        self.configuracoes = self.cursor.fetchall()[len(self.cursor.fetchall())]

        self.oa = False

        self.filename = self.configuracoes[7]
        if self.filename != "Sem titulo" and len(self.cursor.fetchall()) > 1:
            self.oa = True

        self.idioma = open(f"Idiomas/{self.configuracoes[5]}", 'r', encoding=self.configuracoes[6]).readlines()

        # Configura a janela 1
        self.j_1 = tk.Tk()
        self.j_1.title(f"{self.filename} - Notepy")
        self.j_1.geometry("750x500")

        try:
            self.j_1.iconbitmap("Icones/bdn.ico")
        except TclError:
            pass

        self.j_1.protocol("WM_DELETE_WINDOW", self.sair)

        fonts = list(families())
        fonts.sort()

        # Configura o menu 1
        m_1 = tk.Menu(self.j_1)
        self.j_1.config(menu=m_1)

        # Configura o sub menu 1
        self.sm_1 = tk.Menu(m_1, tearoff=False)
        m_1.add_cascade(label=self.idioma[1], menu=self.sm_1)
        self.sm_1.add_command(label=self.idioma[2], command=self.na)
        self.sm_1.add_command(label=self.idioma[3], command=self.aa)
        self.sm_1.add_separator()
        self.sm_1.add_command(label=self.idioma[4], command=self.s)
        self.sm_1.add_command(label=self.idioma[5], command=self.ca)
        self.sm_1.add_separator()
        self.sm_1.add_command(label=self.idioma[6], command=self.sair)

        # Configura o sub menu 2
        self.sm_2 = tk.Menu(m_1, tearoff=False)
        m_1.add_cascade(label=self.idioma[20], menu=self.sm_2)
        self.sm_2.add_command(label=self.idioma[14], command=self.desfazer)
        self.sm_2.add_command(label=self.idioma[15], command=self.refazer)
        self.sm_2.add_separator()
        self.sm_2.add_command(label=self.idioma[16], command=self.copiar)
        self.sm_2.add_command(label=self.idioma[17], command=self.colar)
        self.sm_2.add_command(label=self.idioma[18], command=self.recortar)
        self.sm_2.add_command(label=self.idioma[19], command=self.excluir)
        self.sm_2.add_separator()
        self.sm_2.add_command(label=self.idioma[24], command=self.selecionar_tudo)

        # Configura o sub menu 3
        sm_3 = tk.Menu(m_1, tearoff=False)
        m_1.add_cascade(label=self.idioma[7], menu=sm_3)
        smm_3 = tk.Menu(sm_3, tearoff=False)
        sm_3.add_cascade(label=self.idioma[21], menu=smm_3)
        sm_3.add_command(label=self.idioma[31])
        sm_3.add_command(label=self.idioma[41], command=partial(self.cor, "bg"))
        smm_3.add_command(label=self.idioma[40], command=partial(self.cor, "fg"))

        # Configura o sub sub menu
        smmm_3 = tk.Menu(smm_3, tearoff=False)
        smm_3.add_cascade(menu=smmm_3, label=self.idioma[22])
        for item in fonts:
            smmm_3.add_command(label=item, font=(item, 8), command=partial(self.fonte, item))

        smmm_4 = tk.Menu(self.j_1, tearoff=False)
        smm_3.add_cascade(menu=smmm_4, label=self.idioma[23])
        for c in range(100):
            smmm_4.add_command(label=c + 1, command=partial(self.tamanho, c + 1))

        # Configura o menu Sobre
        m_1.add_command(label=self.idioma[8], command=self.sobre)

        tb_1 = tk.Frame(self.j_1, relief=tk.RAISED)
        self.img = [Image.open("Icones/salvar.png"), Image.open("Icones/salvar_como.png"), Image.open("Icones/abrir.png"),
                    Image.open("Icones/desfazer.png"), Image.open("Icones/refazer.png")]
        eimg = [ImageTk.PhotoImage(self.img[0]), ImageTk.PhotoImage(self.img[1]), ImageTk.PhotoImage(self.img[2]),
                ImageTk.PhotoImage(self.img[3]), ImageTk.PhotoImage(self.img[4])]
        salvar = tk.Button(tb_1, image=eimg[0], relief=tk.FLAT, command=self.s)
        salvar.pack(side=tk.LEFT, padx=2, pady=2)
        salvar_como = tk.Button(tb_1, image=eimg[1], relief=tk.FLAT, command=self.ca)
        salvar_como.pack(side=tk.LEFT, padx=2, pady=2)
        abrir = tk.Button(tb_1, image=eimg[2], relief=tk.FLAT, command=self.aa)
        abrir.pack(side=tk.LEFT, padx=2, pady=2)
        desfazer = tk.Button(tb_1, image=eimg[3], relief=tk.FLAT, command=self.desfazer)
        desfazer.pack(side=tk.LEFT, padx=2, pady=2)
        refazer = tk.Button(tb_1, image=eimg[4], relief=tk.FLAT, command=self.refazer)
        refazer.pack(side=tk.LEFT, padx=2, pady=2)
        tb_1.pack(side=tk.TOP, fill=tk.X)

        self.pm = tk.Menu(self.j_1, tearoff=False)
        self.pm.add_command(label=self.idioma[14], command=self.desfazer)
        self.pm.add_command(label=self.idioma[15], command=self.refazer)
        self.pm.add_separator()
        self.pm.add_command(label=self.idioma[16], command=self.copiar)
        self.pm.add_command(label=self.idioma[17], command=self.colar)
        self.pm.add_command(label=self.idioma[18], command=self.recortar)
        self.pm.add_command(label=self.idioma[19], command=self.excluir)
        self.pm.add_separator()
        self.pm.add_command(label=self.idioma[24], command=self.selecionar_tudo)

        self.filename = self.idioma[0]

        self._fonte = self.configuracoes[1]

        self._tamanho = self.configuracoes[2]

        # Configura o frame 1
        f_1 = tk.Frame(self.j_1, bd=0, relief=tk.SUNKEN)

        f_1.grid_rowconfigure(0, weight=1)
        f_1.grid_columnconfigure(0, weight=1)

        # Configura a caixa de texto 1
        self.ct_1 = tk.Text(f_1, wrap=tk.NONE, bd=0, font=(self._fonte, self._tamanho))
        self.ct_1["fg"] = f"{self.configuracoes[4]}"
        self.ct_1["bg"] = f"{self.configuracoes[3]}"
        self.ct_1.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)

        # Configura a barra de rolagem 1
        br_1 = tk.Scrollbar(f_1, orient=tk.HORIZONTAL)
        br_1.grid(row=1, column=0, sticky=tk.E + tk.W)
        self.ct_1.config(xscrollcommand=br_1.set)
        br_1.config(command=self.ct_1.xview)

        # Configura a barra de rolagem 2
        br_2 = tk.Scrollbar(f_1, orient=tk.VERTICAL)
        br_2.grid(row=0, column=1, sticky=tk.N + tk.S)
        self.ct_1.config(yscrollcommand=br_2.set)
        br_2.config(command=self.ct_1.yview)

        f_1.pack(expand=tk.YES, fill=tk.BOTH)

        self.j_1.bind("<Button-3>", self.mm)
        self.j_1.bind("<Control-s>", self.s)
        self.j_1.bind("<Control-o>", self.aa)
        self.j_1.bind("<Control-n>", self.na)
        self.j_1.bind("<Control-r>", self.ca)
        self.j_1.bind("<Control-q>", self.sair)

        self.keyboard = Controller()

        while True:
            self.j_1.update()

        self.sair()

    def na(self, event = None):  # 'Novo Arquivo' Cria um arquivo não salvo
        global arq
        if self.oa:
            os.startfile("bdn.py")

    def mm(self, e):  # "Mostra Menu", Abre o popup menu
        self.pm.post(e.x_root, e.y_root)

    def sobre(self):  # "Sobre" Abre uma janela que mostra as informações do aplicativo
        messagebox.showinfo("Sobre",
                            f"{self.arq[25]}\n{self.arq[26]}{self.arq[27]}\n{self.arq[28]}{self.arq[29]}\n{self.arq[30]}")

    def traduzir(self):
        j_2 = tk.Toplevel()
        j_2.title(self.arq[8])
        j_2.geometry("200x200")
        j_2.iconbitmap('bdn.ico')
        j_2.minsize(width=200, height=200)
        j_2.maxsize(width=200, height=200)
        l_1 = tk.Label(j_2, text=self.arq[33])
        l_1.place(x=50, y=5)
        j_2.transient(self.j_1)
        j_2.focus_force()
        j_2.grab_set()
        self.filename = filedialog.askopenfile(filetypes=("Documento de texto", "*.txt"))
        filename = str(self.filename)[25:len(str(self.filename)) - 29]
        self.idioma = open(filename, "r", encoding=self.configuracoes[4]).readlines()

    def desfazer(self):
        self.keyboard.press(Key.ctrl)
        self.keyboard.press("z")
        self.keyboard.release("z")
        self.keyboard.release(Key.ctrl)

    def refazer(self):
        self.keyboard.press(Key.ctrl)
        self.keyboard.press("y")
        self.keyboard.release("y")
        self.keyboard.release(Key.ctrl)

    def copiar(self):
        self.keyboard.press(Key.ctrl)
        self.keyboard.press("c")
        self.keyboard.release("c")
        self.keyboard.release(Key.ctrl)

    def colar(self):
        self.keyboard.press(Key.ctrl)
        self.keyboard.press("v")
        self.keyboard.release("v")
        self.keyboard.release(Key.ctrl)

    def recortar(self):
        self.keyboard.press(Key.ctrl)
        self.keyboard.press("x")
        self.keyboard.release("x")
        self.keyboard.release(Key.ctrl)

    def excluir(self):
        self.keyboard.press(Key.delete)
        self.keyboard.release(Key.delete)

    def selecionar_tudo(self):
        self.keyboard.press(Key.ctrl)
        self.keyboard.press("a")
        self.keyboard.release("a")
        self.keyboard.release(Key.ctrl)

    def sair(self, event=None):  # Fecha o aplicativo
        if self.oa:
            filename = str(self.filename)[25:len(str(self.filename)) - 29]
            arq = open(filename, 'r', encoding=self.configuracoes[5])
            if arq.read() != self.ct_1.get(0.1, tk.END):
                arq.close()
                e = messagebox.askyesnocancel(title=self.idioma[10], message=self.arq[11])
                if e:
                    self.s()
                elif not e:
                    self.conn.close()
                    exit()
        else:
            if self.ct_1.get(0.1, tk.END) != "":
                e = messagebox.askyesnocancel(title=self.arq[10], message=self.arq[11])
                if e:
                    self.s()
                elif not e:
                    exit()
            else:
                e = messagebox.askyesno(title=self.arq[40], message=self.arq[41])
                if e:
                    exit()

    def s(self, event=None):  # 'Salvar' salva as alterações em um arquivo já existente
        global arq
        if self.oa:
            filename = str(self.filename)[25:len(str(self.filename)) - 29]
            arq = open(filename, 'w', encoding=arq[43])
            arq.write(self.ct_1.get(1.0, "end-1c"))
            arq.close()
        else:
            self.ca()  # Caso o arquivo ainda não tenha sido criado chama a função 'ca' para criar um arquivo

    def aa(self, event=None):  # 'Abrir arquivo' abre um arquivo salvo no computador
        global arq
        global oa
        global fn
        if self.oa:
            fn = True
            self.aa_2()
        else:
            self.filename = filedialog.askopenfile(
                filetypes=(
                    (self.idioma[34], "*.txt"), (self.idioma[35], "*.docx"), (self.idioma[36], "*.odt"),
                    (self.idioma[37], "*.html"), (self.idioma[38], "*.xml"), (self.idioma[39], "*.*")))
            filename = str(self.filename)[25:len(str(self.filename)) - 29]
            if filename != "":
                try:
                    arq = open(filename, 'r', encoding="utf-8")
                    self.ct_1.delete(tk.INSERT, tk.END)
                    self.ct_1.insert(tk.INSERT, arq.read())
                    self.j_1.title(f"{filename} - Notepy")
                    self.oa = True
                except UnicodeDecodeError:
                    messagebox.showerror(self.idioma[12], self.idioma[13])
                    print(filename, self.filename)
                except FileNotFoundError:
                    messagebox.showerror(self.idioma[12], self.idioma[13])
                    print(filename, self.filename)
            else:
                self.filename = self.idioma[0]

    def aa_2(self):
        global arq
        global fn
        global na
        fn = False
        self.filename = filedialog.askopenfile(
            filetypes=(
                (self.idioma[34], "*.txt"), (self.idioma[35], "*.docx"), (self.idioma[36], "*.odt"),
                (self.idioma[37], "*.html"), (self.idioma[38], "*.xml"), (self.idioma[39], "*.*")))
        if self.filename != "":
            na = self.filename
            try:
                na = self.filename
                Notepy()
            except FileNotFoundError:
                messagebox.showerror(self.arq[13], self.arq[14])
        else:
            self.filename = self.arq[0]

    def ca(self, event=None):  # 'Criar Arquivo' salva o texto digitado em um novo Arquivo
        global arq
        global oa
        global na
        self.filename = filedialog.asksaveasfilename(
            filetypes=(
                (self.idioma[34], "*.txt"), (self.idioma[35], "*.docx"), (self.idioma[36], "*.odt"),
                (self.idioma[37], "*.html"), (self.idioma[38], "*.xml"), (self.idioma[39], "*.*")))
        if not self.oa:
            na = self.filename
            if self.filename != "":
                arq = open(self.filename, 'w')
                arq.write(self.ct_1.get(1.0, "end-1c"))
                arq.close()
                self.j_1.title(f"{self.filename} - Notepy")
            else:
                self.filename = self.arq[0]
        else:
            self.filename = self.arq[0]

    def tamanho(self, tamanho):
        self._tamanho = tamanho
        self.ct_1["font"] = self._fonte, tamanho
        self.cursor.execute("""
        UPDATE configurações
        SET tamanho = ?,
        WHERE id = ?
        """, (tamanho, 1))

    def fonte(self, fonte):
        self._fonte = fonte
        self.ct_1["font"] = fonte, self._tamanho
        self.cursor.execute("""
        UPDATE configurações
        SET tamanho = ?,
        WHERE id = ?
        """, (fonte, 1))

    def cor(self, objeto):
        global cor
        cor = colorchooser.askcolor()
        self.ct_1[objeto] = cor[1]
        self.cursor.execute(f"""
        UPDATE configurações
        SET {objeto} = ?,
        WHERE id = ?
        """, (cor, 1))

    def mm(self, e):  # "Mostra Menu", Abre o popup menu
        self.pm.post(e.x_root, e.y_root)


if __name__ == "__main__":
    Notepy()
