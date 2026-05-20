# lol-auto-accept
A program written in Python that auto accepts a match, hovers a champion, bans a champion and picks a champion for you

---

## Requirements
- Python 3.X downloaded on your system

## 1. Installation
Clone the repo
```bash
git clone https://github.com/yzaals/lol-auto-accept.git
```
## 2. Dependencies
Extract the folder, open it and type "cmd" in the search bar

![screenshot](https://media.discordapp.net/attachments/1506492998677168128/1506493033204547755/A165040D-DE8C-4372-BD70-93D0A80215D1.webp?ex=6a0e7678&is=6a0d24f8&hm=d451a63c2c824c8f714a7afed681fc6e3fd5bd3582bb5a63e9ef3fa487e40a62&=&format=webp)

A command prompt window will open, type 
```bash
pip install -r requirements.txt"
```
and it'll install all libraries

![screenshot](https://media.discordapp.net/attachments/1506492998677168128/1506493488772939796/B3244EC6-556A-4A15-ADF2-49F1DE8F590B.png?ex=6a0e76e5&is=6a0d2565&hm=807b8e9e6a5ff677baf82404d1e0450408228f64456cfd8777619715e0846356&=&format=webp&quality=lossless)

## 3. Configuration
There's two files :
```markdown
- config.json
- champions.txt  -> displays all the champions in the games with their ID.
```
Open `config.json` and changes whatever champion you'd like the program to pick for you using its ID or whatever champion you'd like to ban.

The program will automatically select the first ID from the list; if the character is already selected or banned, the program will select the next ID in the list.

## 4. Usage
Launch League of Legends

Launch the program :
`python automationLoL.py`

# ⚠️ Disclaimer
### This program uses local client API (LCU API) use it at your own risk.

# Enjoy !
