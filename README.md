# Ant Bank UI Demo

This repository includes a small Python GUI application `ant_bank_ui.py` demonstrating how to load local statement files and fetch new statements from email.

## Requirements
- Python 3.x
- A desktop environment capable of running Tkinter

## Running

```bash
python3 ant_bank_ui.py
```

The application allows you to specify the directory where your encrypted statement zip files reside, provide the decryption password, and load your transaction history. The email tab contains a button to check for new statements using IMAP credentials provided via the environment variables `IMAP_HOST`, `IMAP_USER`, and `IMAP_PASS`.

Please note that email fetching is only a simple example and may require additional configuration for real-world use.
