import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json, os, shutil

# ── PATH SETUP ────────────────────────────────────────────────────────────────
ROOT      = os.path.dirname(os.path.abspath(__file__))
SITE_FILE = os.path.join(ROOT, "data.json")
ASSETS    = os.path.join(ROOT, "assets")

# ── THEME ─────────────────────────────────────────────────────────────────────
BG      = "#0a0a0a"
SURFACE = "#111111"
SURFACE2= "#181818"
BORDER  = "#222222"
TEXT    = "#f0f0f0"
MUTED   = "#666666"
LIME    = "#00cc33"
LIME_DIM= "#0a1a0d"
RED     = "#cc3333"
ENTRY   = "#151515"
FONT    = ("Segoe UI", 10)
FONT_SM = ("Segoe UI", 9)

# ── HELPERS ───────────────────────────────────────────────────────────────────
def load_site():
    default_data = {"meta": {}, "projects": [], "wip": [], "skills": [], "education": [], "marquee": []}
    if not os.path.exists(SITE_FILE): return default_data
    try:
        with open(SITE_FILE, encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                default_data["projects"] = data
                return default_data
            return data
    except Exception: return default_data

def save_site(data):
    with open(SITE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def copy_asset(src):
    os.makedirs(ASSETS, exist_ok=True)
    name = os.path.basename(src)
    dst  = os.path.join(ASSETS, name)
    if os.path.abspath(src) != os.path.abspath(dst): shutil.copy2(src, dst)
    return f"assets/{name}"

def make_id(title): return title.lower().strip().replace(" ", "-").replace("/", "-").replace("(","").replace(")","").replace(",","")

# ── WIDGET FACTORIES ──────────────────────────────────────────────────────────
def entry(parent, var=None, width=None, **kw):
    opts = dict(bg=ENTRY, fg=TEXT, insertbackground=LIME, relief="flat", highlightthickness=1, highlightbackground=BORDER, highlightcolor=LIME, font=FONT, textvariable=var)
    if width: opts["width"] = width
    opts.update(kw)
    return tk.Entry(parent, **opts)

def text_box(parent, h=4, **kw):
    return tk.Text(parent, bg=ENTRY, fg=TEXT, insertbackground=LIME, relief="flat", highlightthickness=1, highlightbackground=BORDER, highlightcolor=LIME, font=FONT, height=h, wrap="word", **kw)

def btn(parent, label, cmd, accent=False, danger=False, **kw):
    bg = LIME if accent else (RED if danger else SURFACE2)
    fg = "#000" if accent else TEXT
    # Safely pop out specific styles so they don't clash with defaults
    p_x = kw.pop('padx', 10)
    p_y = kw.pop('pady', 5)
    fnt = kw.pop('font', FONT_SM)
    return tk.Button(parent, text=label, command=cmd, bg=bg, fg=fg, activebackground=LIME if accent else SURFACE, activeforeground="#000" if accent else TEXT, relief="flat", bd=0, padx=p_x, pady=p_y, font=fnt, cursor="hand2", **kw)

def section_hdr(parent, txt):
    f = tk.Frame(parent, bg=BG)
    tk.Label(f, text=txt.upper(), bg=BG, fg=LIME, font=("Segoe UI", 8, "bold"), anchor="w").pack(side="left")
    tk.Frame(f, bg=BORDER, height=1).pack(side="left", fill="x", expand=True, padx=(8,0), pady=(0,1))
    return f

def scroll_frame(parent):
    outer = tk.Frame(parent, bg=BG); canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
    sb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=BG)
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0,0), window=inner, anchor="nw"); canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y"); canvas.pack(side="left", fill="both", expand=True)
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
    return outer, inner

# ── REUSABLE PANELS ───────────────────────────────────────────────────────────
class StringListPanel(tk.Frame):
    def __init__(self, parent, label_text="Items", placeholder="", **kw):
        super().__init__(parent, bg=BG, **kw)
        self.rows = []
        section_hdr(self, label_text).pack(fill="x", pady=(10,4))
        self.inner = tk.Frame(self, bg=BG); self.inner.pack(fill="x")
        btn(self, "+ Add", self._add).pack(anchor="w", pady=4)

    def _add(self, value=""):
        row = tk.Frame(self.inner, bg=BG); row.pack(fill="x", pady=2)
        var = tk.StringVar(value=value)
        entry(row, var=var).pack(side="left", fill="x", expand=True, padx=(0,6))
        btn(row, "×", lambda r=row, v=var: (r.destroy(), self.rows.remove(v)), danger=True).pack(side="left")
        self.rows.append(var)

    def load(self, items):
        for w in self.inner.winfo_children(): w.destroy()
        self.rows.clear()
        for it in (items or []): self._add(it)
    def get(self): return [v.get().strip() for v in self.rows if v.get().strip()]

class GithubLinksPanel(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG, **kw)
        section_hdr(self, "GitHub Links").pack(fill="x", pady=(10,4))
        self.inner = tk.Frame(self, bg=BG); self.inner.pack(fill="x")
        btn(self, "+ Add Link", self._add).pack(anchor="w", pady=4)
        self.rows = []

    def _add(self, lbl="", url=""):
        row = tk.Frame(self.inner, bg=BG); row.pack(fill="x", pady=3)
        vl, vu = tk.StringVar(value=lbl), tk.StringVar(value=url)
        tk.Label(row, text="Label:", bg=BG, fg=MUTED, font=FONT_SM, width=6, anchor="w").pack(side="left")
        entry(row, var=vl, width=16).pack(side="left", padx=(0,6))
        tk.Label(row, text="URL:", bg=BG, fg=MUTED, font=FONT_SM, width=4, anchor="w").pack(side="left")
        entry(row, var=vu, width=38).pack(side="left", padx=(0,6))
        ep = {"row": row, "label": vl, "url": vu}
        btn(row, "×", lambda r=row, e=ep: (r.destroy(), self.rows.remove(e)), danger=True).pack(side="left")
        self.rows.append(ep)

    def load(self, links):
        for w in self.inner.winfo_children(): w.destroy()
        self.rows.clear()
        for l in (links or []): self._add(l.get("label",""), l.get("url",""))
    def get(self): return [{"label": e["label"].get().strip(), "url": e["url"].get().strip()} for e in self.rows if e["url"].get().strip()]

# ── TABS ──────────────────────────────────────────────────────────────────────
class GeneralTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG, padx=24, pady=16)
        self.app = app
        outer, inner = scroll_frame(self)
        outer.pack(fill="both", expand=True)

        def row(lbl, var, hint=""):
            section_hdr(inner, lbl).pack(fill="x", pady=(12,3)); entry(inner, var=var).pack(fill="x", pady=(0,2))
            if hint: tk.Label(inner, text=hint, bg=BG, fg=MUTED, font=("Segoe UI",8), anchor="w").pack(fill="x")

        self.v_name, self.v_initials, self.v_badge = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.v_location, self.v_email = tk.StringVar(), tk.StringVar()
        self.v_github, self.v_linkedin = tk.StringVar(), tk.StringVar()

        row("Full Name (use \\n for line breaks)", self.v_name)
        row("Initials (Nav logo)", self.v_initials, "e.g. HZ")
        row("Availability Badge", self.v_badge, "e.g. Available for internships — Summer 2025")
        
        section_hdr(inner, "Hero Bio").pack(fill="x", pady=(12,3))
        self.t_bio = text_box(inner, h=3); self.t_bio.pack(fill="x", pady=(0,2))

        section_hdr(inner, "Hero Meta Lines").pack(fill="x", pady=(12,3))
        self.v_meta = [tk.StringVar() for _ in range(3)]
        for v in self.v_meta: entry(inner, var=v).pack(fill="x", pady=2)

        row("Location Line", self.v_location); row("Email", self.v_email)
        row("GitHub URL", self.v_github); row("LinkedIn URL", self.v_linkedin)

        section_hdr(inner, "Marquee Skills Ticker (One per line)").pack(fill="x", pady=(12,3))
        self.t_marquee = text_box(inner, h=6); self.t_marquee.pack(fill="x", pady=4)

    def load(self, data):
        m = data.get("meta", {})
        self.v_name.set(m.get("name","")); self.v_initials.set(m.get("initials","")); self.v_badge.set(m.get("availability_badge",""))
        self.t_bio.delete("1.0","end"); self.t_bio.insert("1.0", m.get("hero_bio",""))
        self.v_location.set(m.get("location","")); self.v_email.set(m.get("email",""))
        self.v_github.set(m.get("github_url","")); self.v_linkedin.set(m.get("linkedin_url",""))
        for i, v in enumerate(self.v_meta): v.set(m.get("hero_meta", ["","",""])[i] if i < len(m.get("hero_meta", [])) else "")
        self.t_marquee.delete("1.0","end"); self.t_marquee.insert("1.0", "\n".join(data.get("marquee",[])))

    def flush(self):
        m = self.app.data.setdefault("meta", {})
        m["name"] = self.v_name.get().strip(); m["initials"] = self.v_initials.get().strip(); m["availability_badge"] = self.v_badge.get().strip()
        m["hero_bio"] = self.t_bio.get("1.0","end").strip(); m["location"] = self.v_location.get().strip(); m["email"] = self.v_email.get().strip()
        m["github_url"] = self.v_github.get().strip(); m["linkedin_url"] = self.v_linkedin.get().strip()
        m["hero_meta"] = [v.get().strip() for v in self.v_meta]
        self.app.data["marquee"] = [l.strip() for l in self.t_marquee.get("1.0","end").splitlines() if l.strip()]

class ListEditorTab(tk.Frame):
    def __init__(self, parent, app, data_key, title_key, edit_ui_builder):
        super().__init__(parent, bg=BG)
        self.app = app; self.data_key = data_key; self.title_key = title_key; self.sel = None

        left = tk.Frame(self, bg=SURFACE, width=220); left.pack(side="left", fill="y"); left.pack_propagate(False)
        tk.Label(left, text=data_key.upper(), bg=SURFACE, fg=MUTED, font=("Segoe UI",8,"bold"), anchor="w", padx=12, pady=8).pack(fill="x")
        tk.Frame(left, bg=BORDER, height=1).pack(fill="x")
        self.lb = tk.Listbox(left, bg=SURFACE, fg=TEXT, selectbackground=LIME_DIM, selectforeground=LIME, relief="flat", bd=0, font=FONT, activestyle="none", highlightthickness=0)
        self.lb.pack(fill="both", expand=True)
        self.lb.bind("<<ListboxSelect>>", self._on_sel)
        
        btns = tk.Frame(left, bg=SURFACE, pady=6, padx=6); btns.pack(fill="x")
        btn(btns, "↑", self._move_up).pack(side="left")
        btn(btns, "↓", self._move_down).pack(side="left", padx=4)
        btn(btns, "＋ New", self._new).pack(side="left", padx=4)
        btn(btns, "Delete", self._delete, danger=True).pack(side="right")

        right_outer, self.right = scroll_frame(self)
        right_outer.pack(side="left", fill="both", expand=True); self.right.configure(padx=24, pady=16)

        self.no_sel = tk.Label(self.right, text="Select an item or click + New", bg=BG, fg=MUTED, font=FONT); self.no_sel.pack(pady=40)
        self.editor = tk.Frame(self.right, bg=BG)
        self.ui_vars = edit_ui_builder(self.editor, self)

    def flush(self):
        if self.sel is not None:
            self.ui_vars['save'](self.app.data[self.data_key][self.sel])
            title = self.app.data[self.data_key][self.sel].get(self.title_key, 'Unnamed')
            self.lb.delete(self.sel)
            self.lb.insert(self.sel, f"  {title}")

    def _refresh(self):
        self.lb.delete(0,"end")
        for item in self.app.data.get(self.data_key, []): self.lb.insert("end", f"  {item.get(self.title_key, 'Unnamed')}")

    def _on_sel(self, _=None):
        self.flush() 
        s = self.lb.curselection()
        if not s: return
        self.sel = s[0]
        self.ui_vars['load'](self.app.data[self.data_key][self.sel])
        self.no_sel.pack_forget(); self.editor.pack(fill="both", expand=True)

    def _new(self):
        self.flush()
        self.app.data.setdefault(self.data_key, []).append({self.title_key: "New Entry"})
        self._refresh(); self.lb.selection_clear(0,"end"); self.lb.selection_set(len(self.app.data[self.data_key])-1); self._on_sel()

    def _delete(self):
        if self.sel is None: return
        if messagebox.askyesno("Delete", "Delete this entry?"):
            self.app.data[self.data_key].pop(self.sel)
            self.sel = None; self.editor.pack_forget(); self.no_sel.pack(pady=40); self._refresh()

    def _move_up(self):
        self.flush()
        if self.sel is None or self.sel == 0: return
        lst = self.app.data[self.data_key]
        lst[self.sel], lst[self.sel-1] = lst[self.sel-1], lst[self.sel]
        self.sel -= 1; self._refresh(); self.lb.selection_set(self.sel)

    def _move_down(self):
        self.flush()
        lst = self.app.data[self.data_key]
        if self.sel is None or self.sel >= len(lst)-1: return
        lst[self.sel], lst[self.sel+1] = lst[self.sel+1], lst[self.sel]
        self.sel += 1; self._refresh(); self.lb.selection_set(self.sel)

    def load(self, data): self._refresh()

# ── UI BUILDERS ───────────────────────────────────────────────────────────────
def build_projects_ui(parent, tab):
    v_title, v_cat, v_status, v_slabel, v_tags, v_thumb, v_try = [tk.StringVar() for _ in range(7)]
    section_hdr(parent, "Title").pack(fill="x", pady=(12,3)); entry(parent, var=v_title).pack(fill="x")
    cat_row = tk.Frame(parent, bg=BG); cat_row.pack(fill="x", pady=(12,0))
    cf = tk.Frame(cat_row, bg=BG); cf.pack(side="left", fill="x", expand=True, padx=(0,12))
    section_hdr(cf, "Category").pack(fill="x", pady=(0,3)); ttk.Combobox(cf, textvariable=v_cat, values=["web","ai","game"], state="readonly").pack(fill="x")
    sf = tk.Frame(cat_row, bg=BG); sf.pack(side="left", fill="x", expand=True, padx=(0,12))
    section_hdr(sf, "Status Key").pack(fill="x", pady=(0,3)); ttk.Combobox(sf, textvariable=v_status, values=["live","wip","exe"], state="readonly").pack(fill="x")
    slabf = tk.Frame(cat_row, bg=BG); slabf.pack(side="left", fill="x", expand=True)
    section_hdr(slabf, "Status Label").pack(fill="x", pady=(0,3)); entry(slabf, var=v_slabel).pack(fill="x")

    section_hdr(parent, "Description").pack(fill="x", pady=(12,3)); t_desc = text_box(parent, h=4); t_desc.pack(fill="x")
    section_hdr(parent, "Tags (comma separated)").pack(fill="x", pady=(12,3)); entry(parent, var=v_tags).pack(fill="x")
    
    section_hdr(parent, "Thumbnail").pack(fill="x", pady=(12,3))
    trow = tk.Frame(parent, bg=BG); trow.pack(fill="x")
    entry(trow, var=v_thumb).pack(side="left", fill="x", expand=True, padx=(0,6))
    btn(trow, "Browse", lambda: v_thumb.set(copy_asset(p)) if (p := filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg *.jpeg *.gif *.webp")])) else None).pack(side="left")
    
    section_hdr(parent, "Live / Try URL").pack(fill="x", pady=(12,3)); entry(parent, var=v_try).pack(fill="x")
    gh_panel = GithubLinksPanel(parent); gh_panel.pack(fill="x")

    def load_data(d):
        v_title.set(d.get("title","")); v_cat.set(d.get("category","web")); v_status.set(d.get("status","exe")); v_slabel.set(d.get("status_label",""))
        v_tags.set(", ".join(d.get("tags",[]))); v_thumb.set(d.get("thumbnail","")); v_try.set(d.get("try_url",""))
        t_desc.delete("1.0","end"); t_desc.insert("1.0", d.get("description","")); gh_panel.load(d.get("github_links",[]))
        
    def save_data(d):
        d.update({"title": v_title.get().strip(), "id": make_id(v_title.get()), "category": v_cat.get(), "status": v_status.get(), "status_label": v_slabel.get().strip(),
                  "description": t_desc.get("1.0","end").strip(), "tags": [x.strip() for x in v_tags.get().split(",") if x.strip()],
                  "thumbnail": v_thumb.get().strip(), "try_url": v_try.get().strip(), "github_links": gh_panel.get()})
    return {'load': load_data, 'save': save_data}

def build_wip_ui(parent, tab):
    v_title = tk.StringVar()
    section_hdr(parent,"Title").pack(fill="x",pady=(12,3)); entry(parent, var=v_title).pack(fill="x")
    section_hdr(parent,"Description").pack(fill="x",pady=(12,3)); t_desc = text_box(parent, h=4); t_desc.pack(fill="x")
    return {'load': lambda d: (v_title.set(d.get("title","")), t_desc.delete("1.0","end"), t_desc.insert("1.0", d.get("description",""))),
            'save': lambda d: d.update({"title": v_title.get().strip(), "description": t_desc.get("1.0","end").strip()})}

def build_skills_ui(parent, tab):
    v_grp = tk.StringVar()
    section_hdr(parent,"Group Name").pack(fill="x",pady=(12,3)); entry(parent, var=v_grp).pack(fill="x", pady=(0,8))
    items_frame = tk.Frame(parent, bg=BG); items_frame.pack(fill="x")
    item_rows = []
    
    def add_row(name="", used=""):
        row = tk.Frame(items_frame, bg=BG); row.pack(fill="x", pady=2)
        vn, vu = tk.StringVar(value=name), tk.StringVar(value=used)
        tk.Label(row, text="Skill:", bg=BG, fg=MUTED, font=FONT_SM, width=5, anchor="w").pack(side="left"); entry(row, var=vn, width=18).pack(side="left", padx=(0,6))
        tk.Label(row, text="Used in:", bg=BG, fg=MUTED, font=FONT_SM, width=7, anchor="w").pack(side="left"); entry(row, var=vu, width=28).pack(side="left", padx=(0,6))
        ep = {"row":row,"name":vn,"used":vu}
        btn(row,"×",lambda r=row,e=ep: (r.destroy(), item_rows.remove(e)), danger=True).pack(side="left"); item_rows.append(ep)

    btn(parent, "+ Add Skill", add_row).pack(anchor="w", pady=6)
    return {'load': lambda d: (v_grp.set(d.get("group","")), [r["row"].destroy() for r in item_rows], item_rows.clear(), [add_row(it.get("name",""), it.get("used_in","")) for it in d.get("items",[])]),
            'save': lambda d: d.update({"group": v_grp.get().strip(), "items": [{"name": r["name"].get().strip(), "used_in": r["used"].get().strip()} for r in item_rows if r["name"].get().strip()]})}

def build_edu_ui(parent, tab):
    v_deg, v_sch, v_yr, v_gpa = [tk.StringVar() for _ in range(4)]
    for lbl, var in [("Degree", v_deg), ("School", v_sch), ("Year Range", v_yr), ("CGPA (Optional)", v_gpa)]:
        section_hdr(parent, lbl).pack(fill="x", pady=(12,3)); entry(parent, var=var).pack(fill="x")
    c_panel = StringListPanel(parent, "Courses", "e.g. Artificial Intelligence"); c_panel.pack(fill="x")
    return {'load': lambda d: (v_deg.set(d.get("degree","")), v_sch.set(d.get("school","")), v_yr.set(d.get("year","")), v_gpa.set(d.get("cgpa","")), c_panel.load(d.get("courses",[]))),
            'save': lambda d: d.update({"degree": v_deg.get().strip(), "school": v_sch.get().strip(), "year": v_yr.get().strip(), "cgpa": v_gpa.get().strip(), "courses": c_panel.get()})}

# ── MAIN APP ──────────────────────────────────────────────────────────────────
class App:
    def __init__(self, root):
        self.root = root; self.root.title("Portfolio Editor")
        self.root.configure(bg=BG); self.root.geometry("1100x720"); self.root.minsize(900, 600)
        self.data = load_site()

        tb = tk.Frame(root, bg=SURFACE, pady=10, padx=16); tb.pack(fill="x")
        tk.Label(tb, text="Portfolio Editor", bg=SURFACE, fg=TEXT, font=("Segoe UI",13,"bold")).pack(side="left")
        
        btn(tb, "💾 SAVE ALL CHANGES TO WEBSITE", self.save_all, accent=True, font=("Segoe UI", 10, "bold"), padx=20).pack(side="right")
        
        style = ttk.Style(); style.theme_use("clam")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=SURFACE2, foreground=MUTED, padding=[14,6], font=("Segoe UI",9))
        style.map("TNotebook.Tab", background=[("selected",BG)], foreground=[("selected",LIME)])
        
        nb = ttk.Notebook(root); nb.pack(fill="both", expand=True)
        self.tabs = {
            "General": GeneralTab(nb, self),
            "Projects": ListEditorTab(nb, self, "projects", "title", build_projects_ui),
            "In Progress": ListEditorTab(nb, self, "wip", "title", build_wip_ui),
            "Skills": ListEditorTab(nb, self, "skills", "group", build_skills_ui),
            "Education": ListEditorTab(nb, self, "education", "degree", build_edu_ui),
        }
        for name, tab in self.tabs.items(): nb.add(tab, text=f"  {name}  ")
        for tab in self.tabs.values(): tab.load(self.data)
        
        nb.bind("<<NotebookTabChanged>>", lambda e: self.flush_all())

    def flush_all(self):
        for tab in self.tabs.values(): tab.flush()

    def save_all(self):
        self.flush_all()
        save_site(self.data)
        messagebox.showinfo("Success", "All changes have been saved!\n\nRefresh your local browser to see them, or commit and push to update your live Vercel site.")

if __name__ == "__main__":
    root = tk.Tk(); App(root); root.mainloop()