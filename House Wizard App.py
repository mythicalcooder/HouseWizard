import joblib
import numpy as np
import customtkinter as ctk
from CTkScrollableDropdown import CTkScrollableDropdown

model = joblib.load('HouseWizard.joblib')

ctk.set_default_color_theme("dark-blue")
root = ctk.CTk()
root.geometry("900x600+350+125")
root._set_appearance_mode("system")
root.title("House Wizard")

years = [str(y) for y in range(1890,2026)]

titl = ctk.CTkLabel(root, width = 200, height = 30, text = "AI House Wizard", font = ("arial",25,"bold"))
titl.place(x = 350, y = 20)

ylbl = ctk.CTkLabel(root, width = 200, height = 30, text = "Select Year Built",font = ("arial", 20, "bold"))
ylbl.place(x = 680 ,y = 110)

ycb = ctk.CTkComboBox(root, width = 200, height = 30,dropdown_hover_color = "red", state = "readonly",font = ("arial",15))
ycb.set(str(1971))
ycb.place(x = 680 ,y = 150)
ycbd =CTkScrollableDropdown(ycb,width = 200, height = 390, values = years,hover_color="dark blue",font = ("arial",15))

balbl = ctk.CTkLabel(root, width = 180, height = 30, text = "Total Basement Area",font = ("arial", 15, "bold"))
balbl.place(x = 450 ,y = 110)

baen = ctk.CTkEntry(root, width = 180, height = 30, placeholder_text= "TBA in Ft²",font = ("arial", 15))
baen.place(x = 450 ,y = 150)

grlbl = ctk.CTkLabel(root, width = 180, height = 30, text = "Total Living Area",font = ("arial", 15, "bold"))
grlbl.place(x = 250 ,y = 110)

gren = ctk.CTkEntry(root, width = 180, height = 30, placeholder_text= "TLA in Ft²",font = ("arial", 15))
gren.place(x = 250 ,y = 150)

grclbl = ctk.CTkLabel(root, width = 180, height = 30, text = "No.Garage cars",font = ("arial", 15, "bold"))
grclbl.place(x = 50 ,y = 110)

grcen = ctk.CTkEntry(root, width = 180, height = 30, placeholder_text= "(1 - 5) Cars",font = ("arial", 15))
grcen.place(x = 50 ,y = 150)

root.mainloop()


prediction = model.predict()

