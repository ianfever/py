import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import zipfile
import imaplib
import email
from email.header import decode_header

class AntBankApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Ant Bank Manager')
        self.geometry('600x400')
        self.statement_dir = tk.StringVar()
        self.decrypt_pwd = tk.StringVar()

        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True)

        self.history_frame = ttk.Frame(notebook)
        self.email_frame = ttk.Frame(notebook)
        notebook.add(self.history_frame, text='交易記錄')
        notebook.add(self.email_frame, text='獲取日結單')

        self.build_history_tab()
        self.build_email_tab()

    def build_history_tab(self):
        path_frame = ttk.Frame(self.history_frame)
        path_frame.pack(fill='x', pady=5)
        ttk.Label(path_frame, text='日結單路徑:').pack(side='left')
        ttk.Entry(path_frame, textvariable=self.statement_dir, width=40).pack(side='left', padx=5)
        ttk.Button(path_frame, text='瀏覽', command=self.browse_dir).pack(side='left')
        ttk.Button(path_frame, text='載入', command=self.load_history).pack(side='left')

        self.history_list = tk.Text(self.history_frame)
        self.history_list.pack(fill='both', expand=True, padx=5, pady=5)

    def build_email_tab(self):
        frame = ttk.Frame(self.email_frame)
        frame.pack(pady=10, fill='x')

        ttk.Label(frame, text='郵件日結單密碼:').grid(row=0, column=0, sticky='e')
        ttk.Entry(frame, textvariable=self.decrypt_pwd, show='*').grid(row=0, column=1, padx=5)
        ttk.Button(frame, text='檢查郵件', command=self.fetch_email).grid(row=0, column=2, padx=5)

        self.email_status = tk.Text(self.email_frame, height=10)
        self.email_status.pack(fill='both', expand=True, padx=5, pady=5)

    def browse_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.statement_dir.set(directory)

    def load_history(self):
        self.history_list.delete(1.0, tk.END)
        directory = self.statement_dir.get()
        pwd = self.decrypt_pwd.get().encode()
        if not directory:
            messagebox.showerror('錯誤', '請選擇日結單路徑')
            return
        for fname in sorted(os.listdir(directory)):
            if fname.endswith('.zip'):
                path = os.path.join(directory, fname)
                try:
                    with zipfile.ZipFile(path) as zf:
                        for csv_name in zf.namelist():
                            with zf.open(csv_name, pwd=pwd) as f:
                                reader = csv.reader(line.decode('utf-8') for line in f)
                                for row in reader:
                                    self.history_list.insert(tk.END, ','.join(row) + '\n')
                except RuntimeError:
                    messagebox.showerror('錯誤', '無法解密，請提供正確金鑰')
                    return

    def fetch_email(self):
        self.email_status.delete(1.0, tk.END)
        self.email_status.insert(tk.END, '連線郵件伺服器...\n')
        # TODO: 根據實際郵件帳戶資訊配置以下代碼
        host = os.environ.get('IMAP_HOST')
        user = os.environ.get('IMAP_USER')
        password = os.environ.get('IMAP_PASS')
        if not all([host, user, password]):
            self.email_status.insert(tk.END, '缺少郵件帳戶配置\n')
            return
        try:
            mail = imaplib.IMAP4_SSL(host)
            mail.login(user, password)
            mail.select('INBOX')
            status, messages = mail.search(None, 'UNSEEN')
            if status != 'OK' or not messages[0]:
                messagebox.showinfo('提示', '沒有新日結單')
                return
            for num in messages[0].split():
                status, msg_data = mail.fetch(num, '(RFC822)')
                if status == 'OK':
                    msg = email.message_from_bytes(msg_data[0][1])
                    subject, encoding = decode_header(msg['Subject'])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or 'utf-8')
                    if '日結單' in subject:
                        for part in msg.walk():
                            if part.get_content_maintype() == 'multipart':
                                continue
                            if part.get('Content-Disposition') is None:
                                continue
                            filename = part.get_filename()
                            if filename:
                                filepath = os.path.join(self.statement_dir.get(), filename)
                                with open(filepath, 'wb') as f:
                                    f.write(part.get_payload(decode=True))
                                self.email_status.insert(tk.END, f'下載: {filename}\n')
            mail.close()
            mail.logout()
        except Exception as e:
            self.email_status.insert(tk.END, f'郵件取得失敗: {e}\n')

if __name__ == '__main__':
    app = AntBankApp()
    app.mainloop()
