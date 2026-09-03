import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Acesso ao sistema")
        self.geometry("900x550")
        self.resizable(False, False)

        # Fundo
        self.configure(fg_color="#f5f6f8")

        # Painel esquerdo
        left_frame = ctk.CTkFrame(
            self, width=430, height=550, corner_radius=0, fg_color="#1f2937"
        )
        left_frame.pack(side="left", fill="y")
        left_frame.pack_propagate(False)

        title = ctk.CTkLabel(
            left_frame, text="Sistema", font=("Arial", 32, "bold"), text_color="white"
        )
        title.place(x=50, y=150)

        description = ctk.CTkLabel(
            left_frame,
            text="Acesse sua conta para continuar.",
            font=("Arial", 15),
            text_color="#cbd5e1",
        )
        description.place(x=53, y=205)

        # Área de login
        login_frame = ctk.CTkFrame(
            self, width=470, height=550, corner_radius=0, fg_color="white"
        )
        login_frame.pack(side="right", fill="both")
        login_frame.pack_propagate(False)

        login_title = ctk.CTkLabel(
            login_frame, text="Entrar", font=("Arial", 28, "bold"), text_color="#111827"
        )
        login_title.place(x=75, y=105)

        subtitle = ctk.CTkLabel(
            login_frame,
            text="Informe seus dados de acesso",
            font=("Arial", 14),
            text_color="#6b7280",
        )
        subtitle.place(x=77, y=150)

        # Usuário
        user_label = ctk.CTkLabel(
            login_frame, text="Usuário", font=("Arial", 13), text_color="#374151"
        )
        user_label.place(x=77, y=205)

        self.username = ctk.CTkEntry(
            login_frame,
            width=315,
            height=42,
            placeholder_text="Digite seu usuário",
            border_width=1,
            border_color="#d1d5db",
            fg_color="white",
            text_color="#111827",
        )
        self.username.place(x=77, y=232)

        # Senha
        password_label = ctk.CTkLabel(
            login_frame, text="Senha", font=("Arial", 13), text_color="#374151"
        )
        password_label.place(x=77, y=290)

        self.password = ctk.CTkEntry(
            login_frame,
            width=315,
            height=42,
            placeholder_text="Digite sua senha",
            show="*",
            border_width=1,
            border_color="#d1d5db",
            fg_color="white",
            text_color="#111827",
        )
        self.password.place(x=77, y=317)

        # Mensagem de erro
        self.message = ctk.CTkLabel(
            login_frame, text="", font=("Arial", 12), text_color="#dc2626"
        )
        self.message.place(x=77, y=365)

        # Botão
        login_button = ctk.CTkButton(
            login_frame,
            text="Entrar",
            width=315,
            height=44,
            corner_radius=6,
            font=("Arial", 14, "bold"),
            command=self.login,
        )
        login_button.place(x=77, y=395)

        # Rodapé
        footer = ctk.CTkLabel(
            login_frame,
            text="© 2026 - Sistema interno",
            font=("Arial", 11),
            text_color="#9ca3af",
        )
        footer.place(x=77, y=470)

        self.bind("<Return>", lambda event: self.login())

    def login(self):
        username = self.username.get().strip()
        password = self.password.get()

        # Exemplo simples
        if username == "admin" and password == "1234":
            self.message.configure(
                text="Login realizado com sucesso.", text_color="#16a34a"
            )
        else:
            self.message.configure(
                text="Usuário ou senha incorretos.", text_color="#dc2626"
            )


if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()
