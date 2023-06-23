from bs4 import BeautifulSoup
import requests
import re
import webbrowser
import time
import tkinter as tk
from tkinter import filedialog, ttk

def search_products(event=None):
    search_term = search_entry.get()
    url = f"https://www.newegg.ca/p/pl?d={search_term}&N=4131"
    page = requests.get(url).text
    doc = BeautifulSoup(page, "html.parser")
    page_text = doc.find(class_="list-tool-pagination-text").strong
    pages = int(str(page_text).split("/")[-2].split(">")[-1][:-1])

    items_found = {}

    for page in range(1, pages + 1):
        url = f"https://www.newegg.ca/p/pl?d={search_term}&N=4131&page={page}"
        page = requests.get(url).text
        doc = BeautifulSoup(page, "html.parser")
        div = doc.find(class_="item-cells-wrap border-cells items-grid-view four-cells expulsion-one-cell")
        items = div.find_all(text=re.compile(search_term))

        for item in items:
            parent = item.parent
            if parent.name != "a":
                continue
            link = parent['href']
            next_parent = item.find_parent(class_="item-container")
            try:
                price = next_parent.find(class_="price-current").find("strong").string
                items_found[item] = {"price": int(price.replace(",", "")), "link": link}
            except:
                pass

    sorted_items = sorted(items_found.items(), key=lambda x: x[1]['price'])

    # Clear previous results
    for child in results_tree.get_children():
        results_tree.delete(child)

    # Display search results in the treeview
    for item in sorted_items:
        name = str(item[0])
        price = f"${item[1]['price']}"
        link = item[1]['link']
        results_tree.insert("", tk.END, values=(name, price, link))

# Create the GUI window
window = tk.Tk()
window.title("PC Part Search")
window.geometry("1000x800")

# Create a style for the GUI elements
style = ttk.Style()
style.configure("Treeview", font=("Arial", 12))
style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

# Search term input
search_frame = tk.Frame(window)
search_frame.pack(pady=10)

search_label = tk.Label(search_frame, text="Search term:", font=("Arial", 14))
search_label.pack(side=tk.LEFT)

search_entry = tk.Entry(search_frame, font=("Arial", 14), width=30)
search_entry.pack(side=tk.LEFT)

# Bind Enter key to search_products function
search_entry.bind("<Return>", search_products)

# Search button
search_button = tk.Button(window, text="Search", command=search_products, font=("Arial", 14))
search_button.pack(pady=10)

# Results treeview
results_tree = ttk.Treeview(window, columns=("Name", "Price", "Link"), show="headings")
results_tree.heading("Name", text="Name")
results_tree.heading("Price", text="Price")
results_tree.heading("Link", text="Link")

# Center align the text in the "Price" column
results_tree.column("Price", anchor=tk.CENTER)

# Adjust column widths to fit the content
results_tree.column("Name", width=400)
results_tree.column("Price", width=100)
results_tree.column("Link", width=500)

results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Results scrollbar
results_scrollbar = ttk.Scrollbar(window, orient=tk.VERTICAL, command=results_tree.yview)
results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
results_tree.configure(yscroll=results_scrollbar.set)

# Enable text highlighting, right-click, copy, and paste
def copy_text():
    selected_item = results_tree.selection()
    if selected_item:
        selected_text = results_tree.item(selected_item)['values'][2]
        window.clipboard_clear()
        window.clipboard_append(selected_text)

def paste_text():
    text = window.clipboard_get()
    search_entry.insert(tk.END, text)

results_tree.bind("<Button-3>", lambda e: results_tree.focus_set())
results_tree.bind("<Control-c>", lambda e: copy_text())
results_tree.bind("<Control-v>", lambda e: paste_text())

# Define a callback function for opening the link in a browser
def open_link(event):
    selected_item = results_tree.selection()
    if selected_item:
        link = results_tree.item(selected_item, "values")[2]
        webbrowser.open(link)

# Bind the callback function to the double-click event on the results_tree
results_tree.bind("<Double-1>", open_link)


# Run the GUI event loop
window.mainloop()
