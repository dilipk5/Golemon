# 🧠 Golemon – A Minimal Python C2 Server

Golemon is a simple Command and Control (C2) server written in Python, designed for learning and research purposes. It allows you to manage multiple agents (or "zombies"), execute remote shell commands, and maintain control over victims in a local or tunneled environment (e.g., via Ngrok or port forwarding).

> ⚠️ **For educational and authorized testing use only. Do not deploy on networks or systems you do not own or have permission to test.**

---

## 💡 Features

- Multi-agent support using `threading`
- Agent identification with `uname -r`
- Interactive remote shell per zombie
- Simple CLI for listing and selecting agents
- Designed for socket-based raw TCP communication

---

## 🚀 Getting Started

### 🔧 Requirements

- Python 3.x
- Linux (or modify agent for Windows)
- Optional: [Ngrok](https://ngrok.com/) for remote tunneling

---

## 📂 Folder Structure

golemon/

├── server.py # The main Golemon C2 server

├── agent.py # Example agent (reverse shell)

└── README.md

---

## 🖥️ How to Run

### 1. Start the C2 server

```bash
attacker$ python3 server.py
```
### 2. Run the agent.py on victim machine
```bash
victim$ python agent.py
```
