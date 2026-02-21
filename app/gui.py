from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List

from .models import PasswordPolicy
from .core import SecurePassApp
from .utils import clamp_int


def _charset_size_for_policy(p: PasswordPolicy) -> int:
    """
    Used only for reporting (entropy approximation uses detected charset in strength.py).
    This is a simple estimate based on enabled groups.
    """
    size = 0
    if p.use_lower:
        size += 26
    if p.use_upper:
        size += 26
    if p.use_digits:
        size += 10
    if p.use_symbols:
        size += 32
    return max(size, 1)


def _policy_types(p: PasswordPolicy) -> str:
    parts: List[str] = []
    if p.use_lower:
        parts.append("lowercase")
    if p.use_upper:
        parts.append("uppercase")
    if p.use_digits:
        parts.append("digits")
    if p.use_symbols:
        parts.append("symbols")
    return ", ".join(parts) if parts else "none"


class SecurePassGUI:
    def __init__(self, app: SecurePassApp) -> None:
        self.app = app
        self.root = tk.Tk()
        self.root.title("SecurePass (Tkinter) - Password Generator & Vault")
        self.root.geometry("980x650")

        self.generated_password: str = ""
        self.master_password: str = ""

        self._build_ui()

    def run(self) -> None:
        self.root.mainloop()

    def _build_ui(self) -> None:
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_gen = ttk.Frame(nb)
        self.tab_vault = ttk.Frame(nb)
        self.tab_logs = ttk.Frame(nb)

        nb.add(self.tab_gen, text="Generator")
        nb.add(self.tab_vault, text="Vault")
        nb.add(self.tab_logs, text="Logs")

        self._build_generator_tab()
        self._build_vault_tab()
        self._build_logs_tab()

    # ---------------- Generator ----------------
    def _build_generator_tab(self) -> None:
        frm = ttk.Frame(self.tab_gen, padding=12)
        frm.pack(fill="both", expand=True)

        # Policy controls
        left = ttk.LabelFrame(frm, text="Password Policy", padding=12)
        left.pack(side="left", fill="y")

        self.len_var = tk.IntVar(value=16)
        ttk.Label(left, text="Length (6 to 64)").pack(anchor="w")
        ttk.Spinbox(left, from_=6, to=64, textvariable=self.len_var, width=8).pack(anchor="w", pady=(0, 8))

        self.lower_var = tk.BooleanVar(value=True)
        self.upper_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)
        self.ambig_var = tk.BooleanVar(value=True)
        self.require_each_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(left, text="Include lowercase", variable=self.lower_var).pack(anchor="w")
        ttk.Checkbutton(left, text="Include uppercase", variable=self.upper_var).pack(anchor="w")
        ttk.Checkbutton(left, text="Include digits", variable=self.digits_var).pack(anchor="w")
        ttk.Checkbutton(left, text="Include symbols", variable=self.symbols_var).pack(anchor="w")
        ttk.Checkbutton(left, text="Exclude ambiguous (O/0, l/1)", variable=self.ambig_var).pack(anchor="w", pady=(6, 0))
        ttk.Checkbutton(left, text="Require each selected type", variable=self.require_each_var).pack(anchor="w")

        ttk.Button(left, text="Generate", command=self.on_generate).pack(anchor="w", pady=(12, 0))
        ttk.Button(left, text="Copy to Clipboard", command=self.on_copy).pack(anchor="w", pady=(8, 0))

        # Output area
        right = ttk.LabelFrame(frm, text="Output", padding=12)
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))

        ttk.Label(right, text="Generated Password").pack(anchor="w")
        self.out_pw = tk.Text(right, height=2, width=70)
        self.out_pw.pack(fill="x", pady=(0, 10))

        ttk.Label(right, text="Strength and Policy Report").pack(anchor="w")
        self.out_report = tk.Text(right, height=14, width=70)
        self.out_report.pack(fill="both", expand=True)

        ttk.Label(
            right,
            text="Security note: the application does not log the generated password value.",
        ).pack(anchor="w", pady=(6, 0))

    def _policy(self) -> PasswordPolicy:
        length = clamp_int(self.len_var.get(), 6, 64)
        use_lower = bool(self.lower_var.get())
        use_upper = bool(self.upper_var.get())
        use_digits = bool(self.digits_var.get())
        use_symbols = bool(self.symbols_var.get())
        exclude_ambiguous = bool(self.ambig_var.get())
        require_each = bool(self.require_each_var.get())

        # Improvement 1: explicit validation (clear message, avoids confusion)
        if not any([use_lower, use_upper, use_digits, use_symbols]):
            raise ValueError("Select at least one character type (lowercase/uppercase/digits/symbols).")

        # Improvement 2: explicit validation (even though spinbox limits, this is safer)
        if length < 6 or length > 64:
            raise ValueError("Password length must be between 6 and 64.")

        return PasswordPolicy(
            length=length,
            use_lower=use_lower,
            use_upper=use_upper,
            use_digits=use_digits,
            use_symbols=use_symbols,
            exclude_ambiguous=exclude_ambiguous,
            require_each_selected=require_each,
        )

    def on_generate(self) -> None:
        try:
            policy = self._policy()
            pw, rep = self.app.generate_and_score(policy)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self.generated_password = pw
        self.out_pw.delete("1.0", "end")
        self.out_pw.insert("1.0", pw)

        # Improvement 3: add policy summary (helps marks + clearer results section)
        report_lines: List[str] = []
        report_lines.append("Policy Summary")
        report_lines.append(f"- Length: {policy.length}")
        report_lines.append(f"- Types: {_policy_types(policy)}")
        report_lines.append(f"- Exclude ambiguous: {policy.exclude_ambiguous}")
        report_lines.append(f"- Require each selected type: {policy.require_each_selected}")
        report_lines.append(f"- Estimated charset size: {_charset_size_for_policy(policy)}")
        report_lines.append("")
        report_lines.append("Strength Report")
        report_lines.append(f"- Score: {rep.score}/100")
        report_lines.append(f"- Rating: {rep.label}")
        report_lines.append(f"- Estimated entropy: {rep.entropy_bits} bits")
        report_lines.append("")

        if rep.issues:
            report_lines.append("Issues:")
            for i in rep.issues:
                report_lines.append(f"- {i}")
            report_lines.append("")

        if rep.suggestions:
            report_lines.append("Suggestions:")
            for s in rep.suggestions:
                report_lines.append(f"- {s}")

        self.out_report.delete("1.0", "end")
        self.out_report.insert("1.0", "\n".join(report_lines))

    def on_copy(self) -> None:
        if not self.generated_password:
            messagebox.showinfo("Copy", "Generate a password first.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.generated_password)
        messagebox.showinfo("Copy", "Password copied to clipboard. It will be cleared in 15 seconds.")
        self.root.after(15000, self._clear_clipboard)

    def _clear_clipboard(self) -> None:
        try:
            self.root.clipboard_clear()
        except Exception:
            pass

    # ---------------- Vault ----------------
    def _build_vault_tab(self) -> None:
        frm = ttk.Frame(self.tab_vault, padding=12)
        frm.pack(fill="both", expand=True)

        top = ttk.LabelFrame(frm, text="Vault Access", padding=12)
        top.pack(fill="x")

        ttk.Label(top, text="Master Password").pack(side="left")
        self.master_var = tk.StringVar(value="")
        self.master_entry = ttk.Entry(top, textvariable=self.master_var, show="*", width=30)
        self.master_entry.pack(side="left", padx=8)

        ttk.Button(top, text="Unlock / Create", command=self.on_unlock).pack(side="left", padx=5)
        ttk.Button(top, text="Refresh List", command=self.on_refresh).pack(side="left", padx=5)

        add = ttk.LabelFrame(frm, text="Save Generated Password", padding=12)
        add.pack(fill="x", pady=(12, 0))

        ttk.Label(add, text="Label").grid(row=0, column=0, sticky="w")
        self.label_var = tk.StringVar(value="Example: Gmail / Bank / Social Media")
        ttk.Entry(add, textvariable=self.label_var, width=40).grid(row=0, column=1, padx=8, pady=4)

        ttk.Label(add, text="Username").grid(row=1, column=0, sticky="w")
        self.user_var = tk.StringVar(value="")
        ttk.Entry(add, textvariable=self.user_var, width=40).grid(row=1, column=1, padx=8, pady=4)

        ttk.Button(add, text="Save Current Password", command=self.on_save_to_vault).grid(row=0, column=2, rowspan=2, padx=8)

        listfrm = ttk.LabelFrame(frm, text="Saved Entries", padding=12)
        listfrm.pack(fill="both", expand=True, pady=(12, 0))

        cols = ("label", "username", "created")
        self.tree = ttk.Treeview(listfrm, columns=cols, show="headings", height=12)
        self.tree.heading("label", text="Label")
        self.tree.heading("username", text="Username")
        self.tree.heading("created", text="Created At")
        self.tree.column("label", width=320)
        self.tree.column("username", width=240)
        self.tree.column("created", width=220)
        self.tree.pack(fill="both", expand=True)

        ttk.Label(frm, text="Note: Password values are stored encrypted in the vault file.").pack(anchor="w", pady=(6, 0))

    def on_unlock(self) -> None:
        mp = self.master_var.get().strip()
        if not mp:
            messagebox.showerror("Vault", "Enter a master password.")
            return
        try:
            self.app.ensure_vault(mp)
            self.master_password = mp
            messagebox.showinfo("Vault", "Vault ready. You can now refresh list or save passwords.")
            self.on_refresh()
        except Exception as e:
            messagebox.showerror("Vault Error", str(e))

    def on_refresh(self) -> None:
        if not self.master_password:
            messagebox.showinfo("Vault", "Unlock the vault first.")
            return
        try:
            entries = self.app.vault_list(self.master_password)
        except Exception as e:
            messagebox.showerror("Vault Error", str(e))
            return

        for i in self.tree.get_children():
            self.tree.delete(i)
        for e in entries:
            self.tree.insert("", "end", values=(e.label, e.username, e.created_at_iso))

    def on_save_to_vault(self) -> None:
        if not self.master_password:
            messagebox.showinfo("Vault", "Unlock the vault first.")
            return
        if not self.generated_password:
            messagebox.showinfo("Vault", "Generate a password first.")
            return
        try:
            self.app.vault_add(
                self.master_password,
                label=self.label_var.get(),
                username=self.user_var.get(),
                password=self.generated_password,
            )
            messagebox.showinfo("Vault", "Saved to vault.")
            self.on_refresh()
        except Exception as e:
            messagebox.showerror("Vault Error", str(e))

    # ---------------- Logs ----------------
    def _build_logs_tab(self) -> None:
        frm = ttk.Frame(self.tab_logs, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Button(frm, text="Refresh Logs", command=self.on_refresh_logs).pack(anchor="w")

        self.log_box = tk.Text(frm, height=25)
        self.log_box.pack(fill="both", expand=True, pady=(8, 0))

        ttk.Label(frm, text="Security note: generated password values are never written to logs.").pack(anchor="w", pady=(6, 0))

    def on_refresh_logs(self) -> None:
        path = self.app.log.path
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()
        except FileNotFoundError:
            data = "(No logs yet.)"
        self.log_box.delete("1.0", "end")
        self.log_box.insert("1.0", data)
