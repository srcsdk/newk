#!/usr/bin/env python3
"""tab-based feed reader gui with personalized recommendations"""

import json
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrape import load_cache, scrape_all, save_cache, load_categories
from preview import generate_preview, strip_html
from preferences import (
    load_preferences, save_preferences, add_interest, remove_interest,
    pin_category, unpin_category, mark_read, is_read,
    score_relevance, rank_by_relevance,
)

DARK_BG = "#1e1e1e"
DARK_FG = "#d4d4d4"
DARK_BG2 = "#252526"
DARK_BG3 = "#2d2d30"
DARK_ACCENT = "#3c8dbc"
DARK_READ = "#666666"
DARK_BORDER = "#3e3e42"


class FeedListFrame(tk.Frame):
    """scrollable list of feed items with click handling"""

    def __init__(self, parent, on_select=None, **kwargs):
        super().__init__(parent, bg=DARK_BG2, **kwargs)
        self.on_select = on_select
        self.items = []
        self.item_frames = []

        self.canvas = tk.Canvas(self, bg=DARK_BG2, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=DARK_BG2)

        self.inner.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        ))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self._bind_mousewheel(self.canvas)

    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _bind_mousewheel(self, widget):
        widget.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-3, "units"))
        widget.bind("<Button-5>", lambda e: self.canvas.yview_scroll(3, "units"))
        widget.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(
            -1 * (e.delta // 120), "units"
        ))

    def load_items(self, items):
        """populate the list with feed items"""
        self.items = items
        for widget in self.inner.winfo_children():
            widget.destroy()
        self.item_frames = []

        for i, item in enumerate(items):
            frame = tk.Frame(self.inner, bg=DARK_BG2, cursor="hand2")
            frame.pack(fill="x", padx=6, pady=2)

            read = is_read(item)
            fg = DARK_READ if read else DARK_FG
            title_fg = DARK_READ if read else "#ffffff"

            date_str = item.get("date", "")[:10]
            source = item.get("source", "")
            source_short = source.split("/")[2] if source.count("/") >= 2 else source[:30]
            cat = item.get("category", "")

            title_label = tk.Label(
                frame, text=item.get("title", "")[:120],
                fg=title_fg, bg=DARK_BG2, anchor="w",
                font=("sans-serif", 10, "bold" if not read else "normal"),
                wraplength=500,
            )
            title_label.pack(fill="x", padx=4, pady=(4, 0))

            meta_text = f"{date_str}  |  {source_short}"
            if cat:
                meta_text += f"  |  {cat}"
            meta_label = tk.Label(
                frame, text=meta_text,
                fg=fg, bg=DARK_BG2, anchor="w",
                font=("sans-serif", 8),
            )
            meta_label.pack(fill="x", padx=4, pady=(0, 4))

            sep = tk.Frame(frame, bg=DARK_BORDER, height=1)
            sep.pack(fill="x")

            idx = i
            for widget in [frame, title_label, meta_label]:
                widget.bind("<Button-1>", lambda e, ii=idx: self._on_click(ii))
                self._bind_mousewheel(widget)

            self.item_frames.append(frame)

    def _on_click(self, index):
        if self.on_select and index < len(self.items):
            self.on_select(self.items[index])


class DetailPane(tk.Frame):
    """right-side detail view for selected article"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=DARK_BG, **kwargs)

        self.title_var = tk.StringVar(value="select an article")
        self.title_label = tk.Label(
            self, textvariable=self.title_var,
            fg="#ffffff", bg=DARK_BG, anchor="nw",
            font=("sans-serif", 12, "bold"),
            wraplength=380, justify="left",
        )
        self.title_label.pack(fill="x", padx=10, pady=(10, 4))

        self.meta_var = tk.StringVar()
        self.meta_label = tk.Label(
            self, textvariable=self.meta_var,
            fg=DARK_ACCENT, bg=DARK_BG, anchor="w",
            font=("sans-serif", 9),
        )
        self.meta_label.pack(fill="x", padx=10, pady=(0, 8))

        self.text_widget = tk.Text(
            self, bg=DARK_BG, fg=DARK_FG, wrap="word",
            font=("sans-serif", 10), relief="flat",
            padx=10, pady=5, state="disabled",
            highlightthickness=0,
        )
        self.text_widget.pack(fill="both", expand=True, padx=4, pady=4)

        self.link_var = tk.StringVar()
        self.link_label = tk.Label(
            self, textvariable=self.link_var,
            fg=DARK_ACCENT, bg=DARK_BG, anchor="w",
            font=("sans-serif", 9, "underline"), cursor="hand2",
        )
        self.link_label.pack(fill="x", padx=10, pady=(0, 10))
        self.link_label.bind("<Button-1>", self._open_link)
        self._current_link = ""

    def show_item(self, item):
        """display article details"""
        preview = generate_preview(item, summary_length=2000)
        self.title_var.set(preview["title"])

        date_str = preview.get("date", "")
        source = preview.get("source", "")
        cat = item.get("category", "")
        meta_parts = [p for p in [date_str, source, cat] if p]
        self.meta_var.set("  |  ".join(meta_parts))

        self.text_widget.configure(state="normal")
        self.text_widget.delete("1.0", "end")
        desc = strip_html(item.get("description", ""))
        self.text_widget.insert("1.0", desc if desc else "(no description available)")
        self.text_widget.configure(state="disabled")

        self._current_link = preview.get("link", "")
        if self._current_link:
            self.link_var.set(self._current_link[:80])
        else:
            self.link_var.set("")

    def _open_link(self, event):
        if self._current_link:
            try:
                import webbrowser
                webbrowser.open(self._current_link)
            except Exception:
                pass


class FeedApp(tk.Tk):
    """main application window"""

    def __init__(self):
        super().__init__()
        self.title("newk")
        self.geometry("1100x700")
        self.configure(bg=DARK_BG)
        self.minsize(800, 500)

        self.all_items = []
        self.prefs = load_preferences()
        self.categories = load_categories()
        self.category_tabs = {}

        self._setup_style()
        self._build_toolbar()
        self._build_main()
        self._build_status()
        self._load_feeds()

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=DARK_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=DARK_BG3, foreground=DARK_FG,
                        padding=[12, 4])
        style.map("TNotebook.Tab",
                  background=[("selected", DARK_BG2)],
                  foreground=[("selected", "#ffffff")])
        style.configure("TScrollbar", background=DARK_BG3, troughcolor=DARK_BG,
                        borderwidth=0, arrowsize=14)

    def _build_toolbar(self):
        toolbar = tk.Frame(self, bg=DARK_BG3, height=36)
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)

        refresh_btn = tk.Button(
            toolbar, text="refresh", bg=DARK_BG3, fg=DARK_FG,
            relief="flat", command=self._refresh_feeds,
            font=("sans-serif", 9), activebackground=DARK_ACCENT,
        )
        refresh_btn.pack(side="left", padx=8, pady=4)

        interests_btn = tk.Button(
            toolbar, text="interests", bg=DARK_BG3, fg=DARK_FG,
            relief="flat", command=self._manage_interests,
            font=("sans-serif", 9), activebackground=DARK_ACCENT,
        )
        interests_btn.pack(side="left", padx=4, pady=4)

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            toolbar, textvariable=self.search_var,
            bg=DARK_BG2, fg=DARK_FG, insertbackground=DARK_FG,
            relief="flat", font=("sans-serif", 9), width=30,
        )
        search_entry.pack(side="right", padx=8, pady=6)
        search_entry.bind("<Return>", lambda e: self._search())

        search_label = tk.Label(toolbar, text="search:", bg=DARK_BG3, fg=DARK_FG,
                                font=("sans-serif", 9))
        search_label.pack(side="right", padx=2)

    def _build_main(self):
        self.paned = tk.PanedWindow(
            self, orient="horizontal", bg=DARK_BORDER,
            sashwidth=4, sashrelief="flat",
        )
        self.paned.pack(fill="both", expand=True)

        left_frame = tk.Frame(self.paned, bg=DARK_BG2)
        self.notebook = ttk.Notebook(left_frame)
        self.notebook.pack(fill="both", expand=True)

        self.detail_pane = DetailPane(self.paned)

        self.paned.add(left_frame, minsize=400, width=650)
        self.paned.add(self.detail_pane, minsize=300)

        self._build_for_you_tab()
        self._build_new_tab()
        self._build_categories_tab()

    def _build_for_you_tab(self):
        self.for_you_list = FeedListFrame(self.notebook, on_select=self._on_item_select)
        self.notebook.add(self.for_you_list, text="for you")

    def _build_new_tab(self):
        self.new_list = FeedListFrame(self.notebook, on_select=self._on_item_select)
        self.notebook.add(self.new_list, text="new")

    def _build_categories_tab(self):
        self.cat_frame = tk.Frame(self.notebook, bg=DARK_BG2)
        self.notebook.add(self.cat_frame, text="categories")

        self.cat_canvas = tk.Canvas(self.cat_frame, bg=DARK_BG2, highlightthickness=0)
        self.cat_inner = tk.Frame(self.cat_canvas, bg=DARK_BG2)
        self.cat_canvas.create_window((0, 0), window=self.cat_inner, anchor="nw")
        self.cat_inner.bind("<Configure>", lambda e: self.cat_canvas.configure(
            scrollregion=self.cat_canvas.bbox("all")
        ))
        self.cat_canvas.pack(fill="both", expand=True)

    def _populate_categories_tab(self):
        for widget in self.cat_inner.winfo_children():
            widget.destroy()

        pinned = set(self.prefs.get("pinned_categories", []))

        header = tk.Label(
            self.cat_inner, text="click a category to add it as a tab",
            fg=DARK_FG, bg=DARK_BG2, font=("sans-serif", 10),
        )
        header.pack(pady=(10, 6))

        for cat_name, cat_data in self.categories.items():
            is_pinned = cat_name in pinned
            desc = cat_data.get("description", "")
            subcats = list(cat_data.get("subcategories", {}).keys())
            feed_count = sum(
                len(urls) for urls in cat_data.get("subcategories", {}).values()
            )

            frame = tk.Frame(self.cat_inner, bg=DARK_BG3, cursor="hand2")
            frame.pack(fill="x", padx=12, pady=4)

            name_fg = DARK_ACCENT if is_pinned else "#ffffff"
            label_text = cat_name
            if is_pinned:
                label_text += "  (pinned)"

            name_label = tk.Label(
                frame, text=label_text, fg=name_fg, bg=DARK_BG3,
                font=("sans-serif", 11, "bold"), anchor="w",
            )
            name_label.pack(fill="x", padx=8, pady=(6, 0))

            desc_label = tk.Label(
                frame, text=f"{desc}  ({feed_count} feeds: {', '.join(subcats)})",
                fg=DARK_FG, bg=DARK_BG3, font=("sans-serif", 9), anchor="w",
            )
            desc_label.pack(fill="x", padx=8, pady=(0, 6))

            cat = cat_name
            for w in [frame, name_label, desc_label]:
                w.bind("<Button-1>", lambda e, c=cat: self._toggle_category_tab(c))

    def _toggle_category_tab(self, category_name):
        """pin or unpin a category tab"""
        pinned = self.prefs.get("pinned_categories", [])
        if category_name in pinned:
            unpin_category(category_name)
            self.prefs = load_preferences()
            if category_name in self.category_tabs:
                tab_widget = self.category_tabs.pop(category_name)
                self.notebook.forget(tab_widget)
        else:
            pin_category(category_name)
            self.prefs = load_preferences()
            self._add_category_tab(category_name)

        self._populate_categories_tab()

    def _add_category_tab(self, category_name):
        """add a dynamic category tab"""
        if category_name in self.category_tabs:
            return

        feed_list = FeedListFrame(self.notebook, on_select=self._on_item_select)
        self.notebook.add(feed_list, text=category_name)
        self.category_tabs[category_name] = feed_list

        items = [it for it in self.all_items if it.get("category", "") == category_name]
        feed_list.load_items(items[:200])

    def _restore_pinned_tabs(self):
        """restore category tabs from saved preferences"""
        for cat in self.prefs.get("pinned_categories", []):
            if cat in self.categories:
                self._add_category_tab(cat)

    def _build_status(self):
        self.status_var = tk.StringVar(value="loading...")
        status_bar = tk.Label(
            self, textvariable=self.status_var,
            bg=DARK_BG3, fg=DARK_FG, anchor="w",
            font=("sans-serif", 8), padx=8,
        )
        status_bar.pack(fill="x", side="bottom")

    def _load_feeds(self):
        """load feeds from cache or scrape in background"""
        cached = load_cache()
        if cached:
            self.all_items = cached
            self._update_all_tabs()
            self.status_var.set(f"{len(cached)} items from cache")
        else:
            self.status_var.set("no cache found, refreshing...")
            self._refresh_feeds()

    def _refresh_feeds(self):
        """scrape feeds in background thread"""
        self.status_var.set("refreshing feeds...")

        def worker():
            try:
                items = scrape_all(verbose=False)
                save_cache(items)
                self.all_items = items
                self.after(0, self._update_all_tabs)
                self.after(0, lambda: self.status_var.set(
                    f"{len(items)} items loaded at {datetime.now().strftime('%H:%M')}"
                ))
            except Exception as e:
                self.after(0, lambda: self.status_var.set(f"refresh error: {e}"))

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def _update_all_tabs(self):
        """refresh content in all tabs"""
        self.prefs = load_preferences()

        ranked = rank_by_relevance(self.all_items, self.prefs)
        self.for_you_list.load_items(ranked[:300])

        sorted_new = sorted(
            self.all_items,
            key=lambda x: x.get("date", "") or "",
            reverse=True,
        )
        self.new_list.load_items(sorted_new[:300])

        self._populate_categories_tab()
        self._restore_pinned_tabs()

        for cat_name, feed_list in self.category_tabs.items():
            items = [it for it in self.all_items if it.get("category", "") == cat_name]
            feed_list.load_items(items[:200])

    def _on_item_select(self, item):
        """handle article click"""
        mark_read(item)
        self.detail_pane.show_item(item)
        self._update_all_tabs()

    def _search(self):
        """filter current tab by search term"""
        query = self.search_var.get().lower().strip()
        if not query:
            self._update_all_tabs()
            return

        filtered = [
            it for it in self.all_items
            if query in it.get("title", "").lower()
            or query in it.get("description", "").lower()
            or query in it.get("category", "").lower()
        ]
        self.status_var.set(f"{len(filtered)} results for '{query}'")

        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 0:
            ranked = rank_by_relevance(filtered, self.prefs)
            self.for_you_list.load_items(ranked[:200])
        elif current_tab == 1:
            filtered.sort(key=lambda x: x.get("date", "") or "", reverse=True)
            self.new_list.load_items(filtered[:200])
        else:
            tab_widget = self.notebook.nametowidget(self.notebook.select())
            if isinstance(tab_widget, FeedListFrame):
                tab_widget.load_items(filtered[:200])

    def _manage_interests(self):
        """open dialog to manage interest keywords"""
        dialog = tk.Toplevel(self)
        dialog.title("interests")
        dialog.geometry("400x350")
        dialog.configure(bg=DARK_BG)
        dialog.transient(self)

        tk.Label(
            dialog, text="interest keywords (used for relevance scoring)",
            fg=DARK_FG, bg=DARK_BG, font=("sans-serif", 10),
        ).pack(pady=(10, 6))

        list_frame = tk.Frame(dialog, bg=DARK_BG)
        list_frame.pack(fill="both", expand=True, padx=10)

        listbox = tk.Listbox(
            list_frame, bg=DARK_BG2, fg=DARK_FG,
            selectbackground=DARK_ACCENT, font=("sans-serif", 10),
            relief="flat", highlightthickness=0,
        )
        listbox.pack(fill="both", expand=True)

        prefs = load_preferences()
        for kw in prefs.get("interests", []):
            listbox.insert("end", kw)

        entry_frame = tk.Frame(dialog, bg=DARK_BG)
        entry_frame.pack(fill="x", padx=10, pady=6)

        entry_var = tk.StringVar()
        entry = tk.Entry(
            entry_frame, textvariable=entry_var,
            bg=DARK_BG2, fg=DARK_FG, insertbackground=DARK_FG,
            relief="flat", font=("sans-serif", 10),
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 4))

        def do_add():
            kw = entry_var.get().strip()
            if kw:
                add_interest(kw)
                listbox.insert("end", kw.lower())
                entry_var.set("")

        def do_remove():
            sel = listbox.curselection()
            if sel:
                kw = listbox.get(sel[0])
                remove_interest(kw)
                listbox.delete(sel[0])

        tk.Button(
            entry_frame, text="add", command=do_add,
            bg=DARK_BG3, fg=DARK_FG, relief="flat",
        ).pack(side="left", padx=2)

        tk.Button(
            entry_frame, text="remove selected", command=do_remove,
            bg=DARK_BG3, fg=DARK_FG, relief="flat",
        ).pack(side="left", padx=2)

        entry.bind("<Return>", lambda e: do_add())

        def on_close():
            self.prefs = load_preferences()
            self._update_all_tabs()
            dialog.destroy()

        dialog.protocol("WM_DELETE_WINDOW", on_close)


def main():
    app = FeedApp()
    app.mainloop()


if __name__ == "__main__":
    main()
