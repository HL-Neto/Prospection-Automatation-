import random
import re
import threading
import time
import tkinter as tk
import unicodedata
from tkinter import ttk, messagebox

import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

CABECALHOS = {"User-Agent": "app-prospeccao-local/1.0"}

RAIO_METROS = 15000
TAMANHO_LOTE = 5
DURACAO_MINIMA_SEGUNDOS = 8

CATEGORIAS = [
    ("amenity", "restaurant"),
    ("amenity", "cafe"),
    ("amenity", "bar"),
    ("amenity", "fast_food"),
    ("amenity", "pharmacy"),
    ("amenity", "dentist"),
    ("amenity", "doctors"),
    ("amenity", "veterinary"),
    ("leisure", "fitness_centre"),
    ("shop", "bakery"),
    ("shop", "hairdresser"),
    ("shop", "beauty"),
    ("shop", "clothes"),
    ("shop", "shoes"),
    ("shop", "jewelry"),
    ("shop", "furniture"),
    ("shop", "electronics"),
    ("shop", "hardware"),
    ("shop", "florist"),
    ("shop", "pet"),
    ("shop", "books"),
    ("shop", "gift"),
    ("shop", "sports"),
    ("shop", "houseware"),
    ("shop", "car"),
    ("shop", "car_repair"),
    ("shop", "tyres"),
    ("office", "lawyer"),
    ("office", "accountant"),
    ("office", "estate_agent"),
    ("office", "insurance"),
    ("office", "travel_agent"),
    ("craft", "electrician"),
    ("craft", "plumber"),
]

LINHAS_TERMINAL = [
    "conectando ao servidor...",
    "resolvendo coordenadas da cidade...",
    "abrindo conexao segura...",
    "consultando base de dados publica...",
    "lendo categoria de estabelecimentos...",
    "verificando presenca de site...",
    "verificando presenca de telefone...",
    "verificando presenca de endereco...",
    "removendo duplicados...",
    "ordenando por prioridade de contato...",
    "compilando lista final...",
    "gravando arquivo de saida...",
    "processando lote de dados...",
    "validando resposta do servidor...",
    "aguardando retorno da consulta...",
]


def remover_acentos(texto):
    normalizado = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in normalizado if not unicodedata.combining(c))


def slugificar(texto):
    texto = remover_acentos(texto).lower().strip()
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_")


def geocodificar_cidade(nome_cidade):
    parametros = {"q": nome_cidade, "format": "json", "limit": 1}
    resposta = requests.get(
        NOMINATIM_URL, params=parametros, headers=CABECALHOS, timeout=15
    )
    resposta.raise_for_status()
    dados = resposta.json()
    if not dados:
        return None
    return float(dados[0]["lat"]), float(dados[0]["lon"])


def montar_query_overpass(latitude, longitude, lote_categorias):
    partes = []
    for chave, valor in lote_categorias:
        filtro = f'["{chave}"="{valor}"]'
        partes.append(f"node{filtro}(around:{RAIO_METROS},{latitude},{longitude});")
        partes.append(f"way{filtro}(around:{RAIO_METROS},{latitude},{longitude});")

    corpo = "\n".join(partes)
    return f"[out:json][timeout:25];\n(\n{corpo}\n);\nout center tags;"


def buscar_lote(latitude, longitude, lote_categorias):
    query = montar_query_overpass(latitude, longitude, lote_categorias)
    try:
        resposta = requests.post(
            OVERPASS_URL, data={"data": query}, headers=CABECALHOS, timeout=40
        )
    except requests.exceptions.RequestException:
        return []

    if resposta.status_code != 200:
        return []

    try:
        dados = resposta.json()
    except ValueError:
        return []

    return dados.get("elements", [])


def tem_site(tags):
    site = tags.get("website") or tags.get("contact:website")
    if not site:
        return False
    site_lower = site.lower()
    dominios_sociais = [
        "instagram.com",
        "facebook.com",
        "linktr.ee",
        "wa.me",
        "linkedin.com",
    ]
    return not any(dominio in site_lower for dominio in dominios_sociais)


def montar_endereco(tags):
    partes = []
    if tags.get("addr:street"):
        rua = tags["addr:street"]
        if tags.get("addr:housenumber"):
            rua += ", " + tags["addr:housenumber"]
        partes.append(rua)
    if tags.get("addr:suburb"):
        partes.append(tags["addr:suburb"])
    if tags.get("addr:city"):
        partes.append(tags["addr:city"])
    return " - ".join(partes)


def salvar_txt(cidade, resultados):
    nome_arquivo = f"estabelecimentos_{slugificar(cidade)}.txt"
    with open(nome_arquivo, "w", encoding="utf8") as arquivo:
        for item in resultados:
            arquivo.write(
                "Nome: "
                + item["nome"]
                + " | Endereco: "
                + (item["endereco"] or "nao informado")
                + " | Telefone: "
                + (item["telefone"] or "nao informado")
                + "\n"
            )
    return nome_arquivo


def buscar_estabelecimentos(nome_cidade, quantidade, callback_status):
    callback_status("localizando cidade...")
    coordenadas = geocodificar_cidade(nome_cidade)
    if coordenadas is None:
        return None, None

    latitude, longitude = coordenadas

    elementos = []
    total_lotes = (len(CATEGORIAS) + TAMANHO_LOTE - 1) // TAMANHO_LOTE

    for indice in range(0, len(CATEGORIAS), TAMANHO_LOTE):
        lote = CATEGORIAS[indice : indice + TAMANHO_LOTE]
        numero_lote = indice // TAMANHO_LOTE + 1
        callback_status(f"lote {numero_lote} de {total_lotes}...")
        elementos.extend(buscar_lote(latitude, longitude, lote))

    encontrados = {}

    for elemento in elementos:
        tags = elemento.get("tags", {})

        nome = tags.get("name")
        if not nome:
            continue

        if tem_site(tags):
            continue

        chave_dedup = nome.strip().lower()
        if chave_dedup in encontrados:
            continue

        endereco = montar_endereco(tags)
        telefone = tags.get("phone") or tags.get("contact:phone") or ""

        pontuacao = (1 if telefone else 0) + (1 if endereco else 0)

        encontrados[chave_dedup] = {
            "nome": nome,
            "endereco": endereco,
            "telefone": telefone,
            "pontuacao": pontuacao,
        }

    lista = list(encontrados.values())
    lista.sort(key=lambda item: item["pontuacao"], reverse=True)
    lista = lista[:quantidade]

    nome_arquivo = None
    if lista:
        nome_arquivo = salvar_txt(nome_cidade, lista)

    return lista, nome_arquivo


class JanelaTerminal(tk.Toplevel):
    def __init__(self, master, x, y, largura, altura):
        super().__init__(master)
        self.overrideredirect(True)
        self.geometry(f"{largura}x{altura}+{x}+{y}")
        self.configure(bg="black")

        self.texto = tk.Text(
            self,
            bg="black",
            fg="#00ff00",
            insertbackground="#00ff00",
            font=("Courier", 10),
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#00ff00",
        )
        self.texto.pack(fill="both", expand=True)

    def adicionar_linha(self, linha):
        self.texto.insert("end", linha + "\n")
        self.texto.see("end")


class JanelaResultados(tk.Toplevel):
    def __init__(self, master, resultados, nome_arquivo):
        super().__init__(master)
        self.title("Estabelecimentos sem site")
        self.geometry("750x500")

        colunas = ("nome", "endereco", "telefone")
        titulos = ("Nome", "Endereço", "Telefone")

        tabela = ttk.Treeview(self, columns=colunas, show="headings")
        for col, titulo in zip(colunas, titulos):
            tabela.heading(col, text=titulo)
            tabela.column(col, width=230, anchor="w")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=tabela.yview)
        tabela.configure(yscrollcommand=scrollbar.set)

        tabela.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for item in resultados:
            tabela.insert(
                "",
                "end",
                values=(
                    item["nome"],
                    item["endereco"] or "-",
                    item["telefone"] or "-",
                ),
            )

        texto_rodape = f"Total: {len(resultados)}"
        if nome_arquivo:
            texto_rodape += f"  |  Arquivo salvo: {nome_arquivo}"

        rodape = ttk.Label(self, text=texto_rodape)
        rodape.pack(side="bottom", pady=5)


class JanelaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Prospecção de Estabelecimentos")
        self.geometry("340x220")

        ttk.Label(self, text="Cidade").pack(pady=(20, 0))
        self.campo_cidade = ttk.Entry(self)
        self.campo_cidade.insert(0, "João Pessoa")
        self.campo_cidade.pack()

        ttk.Label(self, text="Quantidade").pack(pady=(10, 0))
        self.campo_quantidade = ttk.Entry(self)
        self.campo_quantidade.insert(0, "20")
        self.campo_quantidade.pack()

        self.botao_buscar = ttk.Button(self, text="Buscar", command=self.iniciar_busca)
        self.botao_buscar.pack(pady=15)

        self.label_status = ttk.Label(self, text="")
        self.label_status.pack()

        self.janelas_terminal = []
        self.animacao_ativa = False
        self.resultado_pronto = None

    def atualizar_status(self, texto):
        self.after(0, lambda: self.label_status.config(text=texto))

    def iniciar_busca(self):
        cidade = self.campo_cidade.get().strip()
        if not cidade:
            messagebox.showerror("Erro", "Digite o nome da cidade")
            return

        try:
            quantidade = int(self.campo_quantidade.get())
        except ValueError:
            messagebox.showerror("Erro", "Quantidade precisa ser um número")
            return

        self.botao_buscar.config(state="disabled")
        self.resultado_pronto = None

        self.abrir_janelas_terminal()
        self.animacao_ativa = True
        self.rodar_animacao_terminal()

        tempo_inicio = time.time()

        def rodar_busca():
            resultados, nome_arquivo = buscar_estabelecimentos(
                cidade, quantidade, self.atualizar_status
            )
            self.resultado_pronto = (resultados, nome_arquivo)

        threading.Thread(target=rodar_busca, daemon=True).start()

        self.verificar_conclusao(tempo_inicio)

    def abrir_janelas_terminal(self):
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()

        posicoes = [
            (30, 30, 320, 180),
            (largura_tela - 350, 30, 320, 180),
            (30, altura_tela - 250, 320, 180),
            (largura_tela - 350, altura_tela - 250, 320, 180),
        ]

        self.janelas_terminal = []
        for x, y, largura, altura in posicoes:
            janela = JanelaTerminal(self, x, y, largura, altura)
            self.janelas_terminal.append(janela)

    def rodar_animacao_terminal(self):
        if not self.animacao_ativa:
            return

        janela = random.choice(self.janelas_terminal)
        linha = random.choice(LINHAS_TERMINAL)
        janela.adicionar_linha(linha)

        self.after(180, self.rodar_animacao_terminal)

    def verificar_conclusao(self, tempo_inicio):
        if self.resultado_pronto is None:
            self.after(200, lambda: self.verificar_conclusao(tempo_inicio))
            return

        decorrido = time.time() - tempo_inicio
        restante = DURACAO_MINIMA_SEGUNDOS - decorrido

        if restante > 0:
            self.after(int(restante * 1000), self.finalizar_busca)
        else:
            self.finalizar_busca()

    def finalizar_busca(self):
        self.animacao_ativa = False

        for janela in self.janelas_terminal:
            janela.destroy()
        self.janelas_terminal = []

        self.botao_buscar.config(state="normal")

        resultados, nome_arquivo = self.resultado_pronto

        if resultados is None:
            self.label_status.config(text="Cidade não encontrada")
            return

        self.label_status.config(text=f"Concluído. {len(resultados)} encontrados.")
        JanelaResultados(self, resultados, nome_arquivo)


if __name__ == "__main__":
    app = JanelaPrincipal()
    app.mainloop()
