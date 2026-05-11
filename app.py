import customtkinter as ctk
from tkinter import messagebox
import joblib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.pdfgen import canvas
from datetime import datetime
import os
import sys
import arabic_reshaper
from bidi.algorithm import get_display

def reshape_arabic_text(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

ARABIC_FONT = ("Tahoma", 14)
ENGLISH_FONT = ("Segoe UI", 14)
TITLE_FONT = ("Tahoma", 28, "bold")
BUTTON_FONT = ("Tahoma", 14, "bold")

TEXTS = {
    "ar": {
        "app_title": "🏡 House Wizard - تقدير أسعار العقارات",
        "sidebar_title": "🏡 House Wizard",
        "theme_btn": "🌓 تغيير الوضع",
        "language_btn": "🌐 English",
        "header": "🤖 التنبؤ بأسعار العقارات",
        "overall": "الجودة الإجمالية (1-10)",
        "year": "سنة البناء (1800-2026)",
        "bsmt": "مساحة الطابق السفلي (قدم²)",
        "living": "مساحة المعيشة (قدم²)",
        "garage": "عدد السيارات في المرآب",
        "exter": "جودة الواجهة الخارجية",
        "bsmt_qual": "جودة الطابق السفلي",
        "result": "💰 السعر المتوقع: --",
        "result_prefix": "💰 السعر المتوقع",
        "predict": "🔮 توقع السعر",
        "reset": "🔄 إعادة تعيين",
        "pdf": "📄 تصدير PDF",
        "chart": "📊 رسم بياني",
        "login_title": "🔐 تسجيل الدخول",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "login_btn": "دخول",
        "error_empty": "الرجاء إدخال قيمة لـ {}",
        "error_qual": "الجودة الإجمالية يجب أن تكون بين 1 و 10",
        "error_year": "سنة البناء يجب أن تكون بين 1800 و {}",
        "error_bsmt": "مساحة الطابق السفلي لا يمكن أن تكون سالبة",
        "error_area": "مساحة المعيشة يجب أن تكون أكبر من صفر",
        "error_cars": "عدد السيارات يجب أن يكون بين 0 و 10",
        "error_num": "يرجى إدخال أرقام صحيحة",
        "warning_no_pred": "قم بعمل توقع أولاً",
        "warning_two_preds": "اعمل توقعين على الأقل",
        "pdf_saved": "تم حفظ التقرير:\n{}",
        "chart_title": "رسم بياني للتوقعات",
        "price": "السعر ($)",
        "pred_num": "رقم التوقع"
    },
    "en": {
        "app_title": "🏡 House Wizard - Real Estate Price Prediction",
        "sidebar_title": "🏡 House Wizard",
        "theme_btn": "🌓 Dark/Light",
        "language_btn": "🌐 العربية",
        "header": "🤖 AI Price Predictor",
        "overall": "Overall Quality (1-10)",
        "year": "Year Built (1800-2026)",
        "bsmt": "Basement Area (sq ft)",
        "living": "Living Area (sq ft)",
        "garage": "Garage Cars",
        "exter": "Exterior Quality",
        "bsmt_qual": "Basement Quality",
        "result": "💰 Predicted Price: --",
        "result_prefix": "💰 Predicted Price",
        "predict": "🔮 Predict Price",
        "reset": "🔄 Reset",
        "pdf": "📄 Export PDF",
        "chart": "📊 Show Chart",
        "login_title": "🔐 Login",
        "username": "Username",
        "password": "Password",
        "login_btn": "Login",
        "error_empty": "Please enter a value for {}",
        "error_qual": "Overall Quality must be between 1 and 10",
        "error_year": "Year Built must be between 1800 and {}",
        "error_bsmt": "Basement area cannot be negative",
        "error_area": "Living area must be greater than zero",
        "error_cars": "Garage cars must be between 0 and 10",
        "error_num": "Please enter valid numbers",
        "warning_no_pred": "Make a prediction first",
        "warning_two_preds": "Make at least two predictions",
        "pdf_saved": "Report saved:\n{}",
        "chart_title": "Prediction History",
        "price": "Price ($)",
        "pred_num": "Prediction Number"
    }
}

current_lang = "ar"
QUALITY_MAP = {"Po": 1, "Fa": 2, "TA": 3, "Gd": 4, "Ex": 5}

try:
    model = joblib.load("model.pkl")
    feature_names = model.feature_names_in_ if hasattr(model, 'feature_names_in_') else None
except Exception as e:
    messagebox.showerror("Error", f"Model not found:\n{e}")
    sys.exit(1)

class HouseWizardApp:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("House Wizard")
        self.app.geometry("1300x850")
        self.app.minsize(1000, 700)
        if os.path.exists("icon.ico"):
            self.app.iconbitmap("icon.ico")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.prediction_history = []
        self.current_lang = "ar"

        self.show_splash()
        self.app.after(2000, self.show_login_frame)
        self.app.mainloop()

    def show_splash(self):
        self.splash_frame = ctk.CTkFrame(self.app, fg_color="#1f6aa5", corner_radius=0)
        self.splash_frame.pack(fill="both", expand=True)
        label = ctk.CTkLabel(self.splash_frame, text="🏡 House Wizard\nجاري التحميل...",
                             font=("Tahoma", 28, "bold"), text_color="white")
        label.pack(expand=True)
        progress = ctk.CTkProgressBar(self.splash_frame, width=300)
        progress.pack(pady=20)
        progress.set(1.0)
        self.app.after(2000, self.hide_splash)

    def hide_splash(self):
        if hasattr(self, 'splash_frame'):
            self.splash_frame.destroy()

    def show_login_frame(self):
        if hasattr(self, 'main_panel'):
            return

        self.login_frame = ctk.CTkFrame(self.app, corner_radius=20)
        self.login_frame.pack(expand=True, fill="both", padx=50, pady=50)

        title = ctk.CTkLabel(self.login_frame, text=TEXTS[self.current_lang]["login_title"],
                             font=("Tahoma", 30, "bold"))
        title.pack(pady=30)

        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text=TEXTS[self.current_lang]["username"],
                                           width=260)
        self.username_entry.pack(pady=15)
        self.password_entry = ctk.CTkEntry(self.login_frame, placeholder_text=TEXTS[self.current_lang]["password"],
                                           show="*", width=260)
        self.password_entry.pack(pady=15)

        login_btn = ctk.CTkButton(self.login_frame, text=TEXTS[self.current_lang]["login_btn"],
                                  command=self.login_action, width=220, height=45, font=BUTTON_FONT)
        login_btn.pack(pady=30)

        self.app.bind('<Return>', lambda e: self.login_action())

    def login_action(self):
        if self.username_entry.get() == "admin" and self.password_entry.get() == "1234":
            self.login_frame.destroy()
            self.build_main_ui()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def build_main_ui(self):
        self.sidebar = ctk.CTkFrame(self.app, width=280, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        sidebar_title = ctk.CTkLabel(self.sidebar, text=TEXTS[self.current_lang]["sidebar_title"],
                                     font=("Tahoma", 28, "bold"), text_color="#2b7a62")
        sidebar_title.pack(pady=40)

        def switch_theme():
            ctk.set_appearance_mode("light" if ctk.get_appearance_mode() == "Dark" else "dark")
        theme_btn = ctk.CTkButton(self.sidebar, text=TEXTS[self.current_lang]["theme_btn"],
                                  command=switch_theme, width=220, height=45, font=BUTTON_FONT)
        theme_btn.pack(pady=10)

        lang_btn = ctk.CTkButton(self.sidebar, text=TEXTS[self.current_lang]["language_btn"],
                                 command=self.toggle_language, width=220, height=45,
                                 font=BUTTON_FONT, fg_color="#555")
        lang_btn.pack(pady=10)

        self.main_frame = ctk.CTkFrame(self.app, corner_radius=20)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.header = ctk.CTkLabel(self.main_frame, text=TEXTS[self.current_lang]["header"],
                                   font=TITLE_FONT, text_color="#2b7a62")
        self.header.pack(pady=20)

        input_frame = ctk.CTkFrame(self.main_frame)
        input_frame.pack(pady=20, padx=30, fill="both")

        fields_keys = [
            ("overall", "Overall Qual"),
            ("year", "Year Built"),
            ("bsmt", "Total Bsmt SF"),
            ("living", "Gr Liv Area"),
            ("garage", "Garage Cars")
        ]
        self.entries = {}
        self.labels_dict = {}
        for key, col in fields_keys:
            frame = ctk.CTkFrame(input_frame)
            frame.pack(fill="x", pady=6, padx=10)
            label = ctk.CTkLabel(frame, text=TEXTS[self.current_lang][key], width=250, anchor="w", font=ARABIC_FONT)
            label.pack(side="left", padx=10)
            self.labels_dict[key] = label
            entry = ctk.CTkEntry(frame, width=300, font=ARABIC_FONT)
            entry.pack(side="right", padx=10)
            self.entries[col] = entry

        quality_frame = ctk.CTkFrame(input_frame)
        quality_frame.pack(fill="x", pady=15, padx=10)
        exter_label = ctk.CTkLabel(quality_frame, text=TEXTS[self.current_lang]["exter"], width=250, anchor="w", font=ARABIC_FONT)
        exter_label.grid(row=0, column=0, padx=10, pady=6, sticky="w")
        self.exter_option = ctk.CTkOptionMenu(quality_frame, values=list(QUALITY_MAP.keys()), width=200)
        self.exter_option.grid(row=0, column=1, padx=10, pady=6)
        self.exter_option.set("TA")

        bsmt_label = ctk.CTkLabel(quality_frame, text=TEXTS[self.current_lang]["bsmt_qual"], width=250, anchor="w", font=ARABIC_FONT)
        bsmt_label.grid(row=1, column=0, padx=10, pady=6, sticky="w")
        self.bsmt_option = ctk.CTkOptionMenu(quality_frame, values=list(QUALITY_MAP.keys()), width=200)
        self.bsmt_option.grid(row=1, column=1, padx=10, pady=6)
        self.bsmt_option.set("TA")

        self.result_label = ctk.CTkLabel(self.main_frame, text=TEXTS[self.current_lang]["result"],
                                         font=TITLE_FONT, text_color="#e67e22")
        self.result_label.pack(pady=25)

        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(pady=30)
        self.predict_btn = ctk.CTkButton(button_frame, text=TEXTS[self.current_lang]["predict"],
                                         command=self.predict_price, width=180, height=50,
                                         font=BUTTON_FONT, fg_color="#2b7a62")
        self.predict_btn.grid(row=0, column=0, padx=10)
        self.reset_btn = ctk.CTkButton(button_frame, text=TEXTS[self.current_lang]["reset"],
                                       command=self.reset_fields, width=180, height=50,
                                       font=BUTTON_FONT, fg_color="#e67e22")
        self.reset_btn.grid(row=0, column=1, padx=10)
        self.pdf_btn = ctk.CTkButton(button_frame, text=TEXTS[self.current_lang]["pdf"],
                                     command=self.export_pdf, width=180, height=50,
                                     font=BUTTON_FONT, fg_color="#2980b9")
        self.pdf_btn.grid(row=0, column=2, padx=10)
        self.chart_btn = ctk.CTkButton(button_frame, text=TEXTS[self.current_lang]["chart"],
                                       command=self.show_chart, width=180, height=50,
                                       font=BUTTON_FONT, fg_color="#8e44ad")
        self.chart_btn.grid(row=0, column=3, padx=10)

        self.sidebar_title = sidebar_title
        self.theme_btn = theme_btn
        self.lang_btn = lang_btn
        self.exter_label = exter_label
        self.bsmt_label = bsmt_label

    def validate_inputs(self, vals):
        try:
            qual = float(vals["Overall Qual"])
            if not (1 <= qual <= 10):
                return False, TEXTS[self.current_lang]["error_qual"]
            year = float(vals["Year Built"])
            current_year = datetime.now().year
            if not (1800 <= year <= current_year+1):
                return False, TEXTS[self.current_lang]["error_year"].format(current_year+1)
            bsmt = float(vals["Total Bsmt SF"])
            if bsmt < 0:
                return False, TEXTS[self.current_lang]["error_bsmt"]
            area = float(vals["Gr Liv Area"])
            if area <= 0:
                return False, TEXTS[self.current_lang]["error_area"]
            cars = float(vals["Garage Cars"])
            return True, ""
        except ValueError:
            return False, TEXTS[self.current_lang]["error_num"]

    def predict_price(self):
        for key, entry in self.entries.items():
            if entry.get().strip() == "":
                messagebox.showerror("Error", TEXTS[self.current_lang]["error_empty"].format(key))
                return
        raw = {key: entry.get() for key, entry in self.entries.items()}
        valid, msg = self.validate_inputs(raw)
        if not valid:
            messagebox.showerror("Error", msg)
            return
        values = [
            float(self.entries["Overall Qual"].get()),
            float(self.entries["Year Built"].get()),
            float(self.entries["Total Bsmt SF"].get()),
            float(self.entries["Gr Liv Area"].get()),
            float(self.entries["Garage Cars"].get()),
            QUALITY_MAP[self.exter_option.get()],
            QUALITY_MAP[self.bsmt_option.get()]
        ]
        import pandas as pd
        feature_names = ['Overall Qual', 'Year Built', 'Total Bsmt SF', 'Gr Liv Area', 'Garage Cars', 'Exter Qual', 'Bsmt Qual']
        X_input = pd.DataFrame([values], columns=feature_names)
        pred = model.predict(X_input)[0]
        self.prediction_history.append(pred)
        self.result_label.configure(text=f"{TEXTS[self.current_lang]['result_prefix']}: ${pred:,.2f}")

    def reset_fields(self):
        for entry in self.entries.values():
            entry.delete(0, 'end')
        self.exter_option.set("TA")
        self.bsmt_option.set("TA")
        self.result_label.configure(text=TEXTS[self.current_lang]["result"])

    def export_pdf(self):
        if not self.prediction_history:
            messagebox.showwarning("Warning", TEXTS[self.current_lang]["warning_no_pred"])
            return
        os.makedirs("exports", exist_ok=True)
        filename = f"exports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf = canvas.Canvas(filename)
        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawString(100, 800, "House Wizard Report")
        pdf.setFont("Helvetica", 14)
        pdf.drawString(100, 750, f"Last Prediction: ${self.prediction_history[-1]:,.2f}")
        pdf.drawString(100, 720, f"Total Predictions: {len(self.prediction_history)}")
        pdf.save()
        messagebox.showinfo("Done", TEXTS[self.current_lang]["pdf_saved"].format(filename))

    def show_chart(self):
        if len(self.prediction_history) < 2:
            messagebox.showwarning("Warning", TEXTS[self.current_lang]["warning_two_preds"])
            return

        plt.rcParams['font.family'] = 'Arial'
        plt.rcParams['axes.unicode_minus'] = False

        win = ctk.CTkToplevel(self.app)
        win.geometry("800x600")
        win.title(TEXTS[self.current_lang]["chart_title"])
        win.lift()
        win.focus_force()

        fig, ax = plt.subplots(figsize=(7, 5))
        ax.plot(self.prediction_history, marker='o', linestyle='-', linewidth=2, color='#2b7a62', markersize=6)
        ax.fill_between(range(len(self.prediction_history)), self.prediction_history, alpha=0.1, color='#2b7a62')
        ax.grid(True, linestyle='--', alpha=0.6)

        if self.current_lang == "ar":
            ax.set_title(reshape_arabic_text("رسم بياني للتوقعات"), fontsize=14, fontweight='bold')
            ax.set_ylabel(reshape_arabic_text("السعر ($)"), fontsize=12)
            ax.set_xlabel(reshape_arabic_text("رقم التوقع"), fontsize=12)
        else:
            ax.set_title("Prediction History", fontsize=14, fontweight='bold')
            ax.set_ylabel("Price ($)", fontsize=12)
            ax.set_xlabel("Prediction Number", fontsize=12)

        for i, val in enumerate(self.prediction_history):
            ax.annotate(f"${val:,.0f}", (i, val), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=8)

        canvas_chart = FigureCanvasTkAgg(fig, master=win)
        canvas_chart.draw()
        canvas_chart.get_tk_widget().pack(fill="both", expand=True)

    def toggle_language(self):
        self.current_lang = "en" if self.current_lang == "ar" else "ar"
        if hasattr(self, 'sidebar_title'):
            self.sidebar_title.configure(text=TEXTS[self.current_lang]["sidebar_title"])
            self.theme_btn.configure(text=TEXTS[self.current_lang]["theme_btn"])
            self.lang_btn.configure(text=TEXTS[self.current_lang]["language_btn"])
            self.header.configure(text=TEXTS[self.current_lang]["header"])
            for key, label in self.labels_dict.items():
                label.configure(text=TEXTS[self.current_lang][key])
            self.exter_label.configure(text=TEXTS[self.current_lang]["exter"])
            self.bsmt_label.configure(text=TEXTS[self.current_lang]["bsmt_qual"])
            self.predict_btn.configure(text=TEXTS[self.current_lang]["predict"])
            self.reset_btn.configure(text=TEXTS[self.current_lang]["reset"])
            self.pdf_btn.configure(text=TEXTS[self.current_lang]["pdf"])
            self.chart_btn.configure(text=TEXTS[self.current_lang]["chart"])
            if self.prediction_history:
                self.result_label.configure(text=f"{TEXTS[self.current_lang]['result_prefix']}: ${self.prediction_history[-1]:,.2f}")
            else:
                self.result_label.configure(text=TEXTS[self.current_lang]["result"])

if __name__ == "__main__":
    app = HouseWizardApp()