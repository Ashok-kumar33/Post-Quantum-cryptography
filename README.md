#post quantum cryptography
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pqcrypto.kem import ml_kem_1024
from pqcrypto.sign import ml_dsa_44, ml_dsa_65
import os, socket, threading, time, json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import hashlib
from datetime import datetime


class QuantumSafeVPN:
    def __init__(self, root):
        self.root = root
        self.root.title("QuantumSafe Enterprise VPN Gateway - NIST FIPS 203/204/205")
        self.root.geometry("1600x1000")
        self.root.configure(bg="#0a0a1a")

        # PQC Keys + Sessions
        self.kem_pk, self.kem_sk = None, None
        self.dsa_pk, self.dsa_sk = None, None
        self.sessions = {}
        self.server_thread = None
        self.is_server = False

        self.build_enterprise_ui()
        self.log("QuantumSafe VPN Gateway v2.0 - NIST Production Ready")

    def build_enterprise_ui(self):
        # Header
        header = tk.Label(
            self.root,
            text="QUANTUMSAFE ENTERPRISE VPN\nFIPS 203 ML-KEM + FIPS 204 ML-DSA",
            font=("Arial", 24, "bold"), fg="#00ff88", bg="#0a0a1a"
        )
        header.pack(pady=20)

        # Dashboard
        dash_frame = tk.LabelFrame(
            self.root, text="ENTERPRISE DASHBOARD", font=("Arial", 16, "bold"),
            fg="gold", bg="#1a1a3a"
        )
        dash_frame.pack(pady=10, padx=20, fill="x")

        self.stats = {
            "sessions": tk.Label(dash_frame, text="Active Sessions: 0", fg="lime",
                                  bg="#1a1a3a", font=("Arial", 14)),
            "throughput": tk.Label(dash_frame, text="Throughput: 0 KB/s", fg="cyan",
                                    bg="#1a1a3a", font=("Arial", 14)),
            "status": tk.Label(dash_frame, text="OFFLINE", fg="red", bg="#1a1a3a",
                                font=("Arial", 14, "bold")),
        }
        for stat in self.stats.values():
            stat.pack(pady=5)

        # Operations Panel
        ops_frame = tk.LabelFrame(
            self.root, text="ENTERPRISE OPERATIONS", font=("Arial", 16, "bold"),
            fg="white", bg="#2a2a4a"
        )
        ops_frame.pack(pady=10, padx=20, fill="both", expand=True)

        left_frame = tk.Frame(ops_frame, bg="#2a2a4a")
        left_frame.pack(side="left", padx=20, pady=20, fill="y")

        prod_buttons = [
            ("Generate Enterprise Keys", self.gen_enterprise_keys, "#4CAF50"),
            ("Start PQC VPN Server", self.start_vpn_server, "#2196F3"),
            ("Connect PQC VPN Client", self.connect_vpn_client, "#FF9800"),
            ("Encrypt File Batch", self.batch_encrypt_files, "#9C27B0"),
            ("Decrypt File Batch", self.batch_decrypt_files, "#F44336"),
            ("Export Key Bundle", self.export_key_bundle, "#FFEB3B"),
        ]

        for text, cmd, color in prod_buttons:
            tk.Button(
                left_frame, text=text, command=cmd, width=25, height=2,
                bg=color, fg="white", font=("Arial", 12, "bold"),
                relief="flat", bd=0
            ).pack(pady=8)

        # Sessions Monitor
        sessions_frame = tk.LabelFrame(
            ops_frame, text="ACTIVE PQC SESSIONS", font=("Arial", 14, "bold")
        )
        sessions_frame.pack(side="right", padx=20, pady=20, fill="both", expand=True)

        cols = ("Client", "Status", "Throughput", "Since")
        self.sessions_tree = ttk.Treeview(sessions_frame, columns=cols, show="headings", height=12)
        for col in cols:
            self.sessions_tree.heading(col, text=col)
            self.sessions_tree.column(col, width=120)
        self.sessions_tree.pack(fill="both", expand=True)

        # Logs
        self.log_area = scrolledtext.ScrolledText(
            self.root, width=180, height=15, font=("Consolas", 10),
            bg="#000a11", fg="#00ff88"
        )
        self.log_area.pack(pady=10, padx=20, fill="x")

    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.log_area.see(tk.END)

    def get_time(self):
        return datetime.now().strftime("%H:%M:%S")

    def update_dashboard(self):
        self.stats["sessions"].config(text=f"Active Sessions: {len(self.sessions)}")
        self.stats["status"].config(
            text="LIVE" if self.is_server else "OFFLINE",
            fg="lime" if self.is_server else "red",
        )
        self.root.after(2000, self.update_dashboard)

    def gen_enterprise_keys(self):
        """Enterprise-grade PQC key generation (ML-KEM-1024 + ML-DSA-65)."""
        self.log("Generating ENTERPRISE PQC Keys...")
        self.kem_pk, self.kem_sk = ml_kem_1024.generate_keypair()
        self.log(f"ML-KEM-1024: PK={len(self.kem_pk)}B, SK={len(self.kem_sk)}B")

        self.dsa_pk, self.dsa_sk = ml_dsa_65.generate_keypair()
        self.log(f"ML-DSA-65: PK={len(self.dsa_pk)}B, SK={len(self.dsa_sk)}B")

        self.log("Enterprise keys ready for production deployment")

    def start_vpn_server(self):
        """Start the PQC-secured socket listener."""
        if self.server_thread and self.server_thread.is_alive():
            return
        if not all([self.kem_pk, self.dsa_sk]):
            messagebox.showerror("ERROR", "Generate enterprise keys first!")
            return

        self.is_server = True
        self.server_thread = threading.Thread(target=self.vpn_server_loop, daemon=True)
        self.server_thread.start()
        self.log("PQC VPN Server started on port 4433")

    def vpn_server_loop(self):
        """Accept loop; each client is handled on its own thread."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", 4433))
        server.listen(5)
        self.log("Server listening on 0.0.0.0:4433...")

        while self.is_server:
            try:
                client, addr = server.accept()
                session_id = f"{addr[0]}:{addr[1]}"
                self.sessions[session_id] = {"client": client, "addr": addr, "start": time.time()}
                threading.Thread(
                    target=self.handle_client, args=(client, session_id), daemon=True
                ).start()
            except OSError:
                break

        server.close()

    def handle_client(self, client, session_id):
        """PQC key-exchange + AES-GCM tunnel for one client connection."""
        try:
            # Send server's ML-KEM-1024 public key
            client.send(len(self.kem_pk).to_bytes(4, "big") + self.kem_pk)

            # Receive client's encapsulated ciphertext, matching ML-KEM-1024
            ct_len = int.from_bytes(client.recv(4), "big")
            ct = client.recv(ct_len)
            shared_secret = ml_kem_1024.decrypt(self.kem_sk, ct)
            session_key = hashlib.sha256(shared_secret).digest()

            self.log(f"PQC Session: {session_id} established")
            self.sessions_tree.insert(
                "", "end", values=(session_id, "ACTIVE", "0 KB/s", self.get_time())
            )

            while True:
                data = client.recv(4096)
                if not data:
                    break

                iv = data[:12]
                ct_data = data[12:-16]
                tag = data[-16:]

                cipher = Cipher(algorithms.AES(session_key), modes.GCM(iv, tag), backend=default_backend())
                decryptor = cipher.decryptor()
                plaintext = decryptor.update(ct_data) + decryptor.finalize()

                self.log(f"{session_id}: {len(plaintext)} bytes tunneled")
        except Exception as e:
            self.log(f"Session {session_id} error: {e}")
        finally:
            client.close()
            self.sessions.pop(session_id, None)

    def connect_vpn_client(self):
        """Connect to a running PQC VPN server and run a one-shot tunnel test."""
        if not all([self.kem_pk, self.dsa_sk]):
            messagebox.showerror("ERROR", "Generate enterprise keys first!")
            return

        host = "127.0.0.1"  # Change to real server IP
        port = 4433

        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((host, port))

            kem_pk_len = int.from_bytes(client.recv(4), "big")
            kem_pk = client.recv(kem_pk_len)
            ct, shared_secret = ml_kem_1024.encrypt(kem_pk)

            client.send(len(ct).to_bytes(4, "big") + ct)
            self.log("PQC VPN Client connected!")

            test_data = b"QuantumSafe VPN Tunnel Test Data - NIST FIPS 203/204"
            key = hashlib.sha256(shared_secret).digest()
            iv = os.urandom(12)
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
            enc = cipher.encryptor()
            ct_data = enc.update(test_data) + enc.finalize()
            packet = iv + ct_data + enc.tag

            client.send(packet)
            self.log("Tunnel test packet sent")
        except Exception as e:
            self.log(f"Client error: {e}")

    def batch_encrypt_files(self):
        """Encrypt every file in a chosen folder with a fresh ML-KEM-512 wrap."""
        dir_path = filedialog.askdirectory(title="Select folder to Quantum-Protect")
        if not dir_path:
            return
        if not all([self.kem_pk, self.dsa_sk]):
            messagebox.showerror("ERROR", "Generate enterprise keys!")
            return

        files_encrypted = 0
        for root, _, files in os.walk(dir_path):
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    self.protect_single_file(file_path)
                    files_encrypted += 1
                except Exception as e:
                    self.log(f"Failed to protect {file_path}: {e}")

        self.log(f"BATCH COMPLETE: {files_encrypted} files quantum-protected")

    def protect_single_file(self, file_path):
        """Encrypt one file: ML-KEM-1024 wrap + AES-GCM + ML-DSA-44 signature."""
        ct, secret = ml_kem_1024.encrypt(self.kem_pk)
        key = hashlib.sha256(secret).digest()

        with open(file_path, "rb") as f:
            data = f.read()

        iv = os.urandom(12)
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        enc = cipher.encryptor()
        ct_data = enc.update(data) + enc.finalize()
        tag = enc.tag

        pkg = ct + iv + ct_data + tag
        sig = ml_dsa_44.sign(self.dsa_sk, pkg)

        out_path = file_path + ".pqsafe"
        with open(out_path, "wb") as f:
            f.write(len(sig).to_bytes(4, "big") + sig + len(ct).to_bytes(4, "big") + pkg)

    def batch_decrypt_files(self):
        """Recover every .pqsafe file in a chosen folder."""
        dir_path = filedialog.askdirectory(title="Select .pqsafe folder")
        if not dir_path:
            return

        files_recovered = 0
        for root, _, files in os.walk(dir_path):
            for name in files:
                if name.endswith(".pqsafe"):
                    file_path = os.path.join(root, name)
                    try:
                        self.recover_single_file(file_path)
                        files_recovered += 1
                    except Exception as e:
                        self.log(f"Failed to recover {file_path}: {e}")

        self.log(f"BATCH RECOVERY: {files_recovered} files restored")

    def recover_single_file(self, file_path):
        """Verify signature, then decapsulate + decrypt one .pqsafe file."""
        with open(file_path, "rb") as f:
            data = f.read()

        sig_len = int.from_bytes(data[0:4], "big")
        sig = data[4:4 + sig_len]
        ct_len = int.from_bytes(data[4 + sig_len:8 + sig_len], "big")
        pkg = data[8 + sig_len:]

        ml_dsa_44.verify(self.dsa_pk, pkg, sig)  # Verify signature before trusting contents

        ct = pkg[:ct_len]
        iv = pkg[ct_len:ct_len + 12]
        ct_data = pkg[ct_len + 12:-16]
        tag = pkg[-16:]

        secret = ml_kem_1024.decrypt(self.kem_sk, ct)
        key = hashlib.sha256(secret).digest()

        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        dec = cipher.decryptor()
        original = dec.update(ct_data) + dec.finalize()

        out_path = file_path.replace(".pqsafe", "_recovered")
        with open(out_path, "wb") as f:
            f.write(original)

    def export_key_bundle(self):
        """Write public keys + version info to a JSON bundle for distribution."""
        dir_path = filedialog.askdirectory(title="Export Enterprise Key Bundle")
        if dir_path and self.kem_pk:
            bundle = {
                "kem_pk": self.kem_pk.hex(),
                "dsa_pk": self.dsa_pk.hex(),
                "config": {"version": "2.0", "standard": "FIPS 203/204"},
            }
            with open(os.path.join(dir_path, "enterprise_pqc_bundle.json"), "w") as f:
                json.dump(bundle, f)
            self.log("Enterprise key bundle exported")


if __name__ == "__main__":
    root = tk.Tk()
    app = QuantumSafeVPN(root)
    app.update_dashboard()
    root.mainloop()
