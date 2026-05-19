#!/data/data/com.termux/files/usr/bin/python
# -*- coding: utf-8 -*-
"""
BUCHI FRAMEWORK – Elite AI Agent for Termux (Lock/Unlock Architecture)
GitHub Ready – No hardcoded secrets, fully configurable via .env
"""

import os
import sys
import re
import time
import json
import random
import subprocess
import shlex
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.box import HEAVY
import requests
import pytz

# =============================================
# कॉन्फ़िगरेशन लोड करें (.env फ़ाइल से)
# =============================================
load_dotenv()
console = Console()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ACTIVATION_SENTENCE = os.getenv("ACTIVATION_SENTENCE")
UNLOCK_FIXED_STRING = os.getenv("UNLOCK_FIXED_STRING")  # वैकल्पिक – फिक्स्ड स्ट्रिंग मोड के लिए
UNLOCK_MODE = os.getenv("UNLOCK_MODE", "math_concat")   # "math_concat" या "fixed_string"

if not GROQ_API_KEY:
    console.print("[red]❌ GROQ_API_KEY .env में नहीं मिला।[/]")
    sys.exit(1)
if not ACTIVATION_SENTENCE:
    console.print("[red]❌ ACTIVATION_SENTENCE .env में नहीं मिला।[/]")
    sys.exit(1)

# =============================================
# स्टेट मशीन वेरिएबल्स
# =============================================
STATE_LOCKED = "LOCKED"
STATE_UNLOCKED = "UNLOCKED"
current_state = STATE_LOCKED
pending_challenge = None   # {"question": "...", "expected": "..."}
chat_history = []           # स्थानीय चैट इतिहास (20 संदेश)

# =============================================
# सुरक्षित कमांड्स की व्हाइटलिस्ट (बिल्कुल कोई खतरनाक कमांड नहीं)
# =============================================
ALLOWED_COMMANDS = [
    "pkg", "apt", "ls", "cd", "git", "chmod", "python", "bash",
    "am start", "termux-", "clear", "echo", "sleep", "cat", "grep",
    "find", "cp", "mv", "mkdir", "rmdir", "touch", "nano", "vim",
    "zip", "unzip", "tar", "gzip", "gunzip", "less", "more", "head", "tail"
]

def is_safe_command(cmd):
    """कमांड को सुरक्षित रूप से पार्स करें – शेल मेटाकैरेक्टर्स को ब्लॉक करें"""
    # पहले जाँचें कि कमांड whitelist में किसी से शुरू होती है या नहीं
    cmd_lower = cmd.strip().lower()
    allowed = False
    for prefix in ALLOWED_COMMANDS:
        if cmd_lower.startswith(prefix):
            allowed = True
            break
    if not allowed:
        return False, "Command not in whitelist"
    
    # खतरनाक शेल मेटाकैरेक्टर्स की जाँच
    dangerous_chars = [';', '&', '|', '$', '`', '>', '<', '\\', '\n', '\r']
    for ch in dangerous_chars:
        if ch in cmd:
            return False, f"Dangerous character '{ch}' detected"
    return True, "Safe"

# =============================================
# सेंसर – बैटरी, रैम, तापमान
# =============================================
def sense_environment():
    sensors = {"battery": "N/A", "ram": "N/A", "temp": "N/A"}
    try:
        res = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=3)
        if res.returncode == 0:
            data = json.loads(res.stdout)
            sensors["battery"] = str(data.get('percentage', 'N/A'))
            sensors["temp"] = str(data.get('temperature', 'N/A'))
    except: pass
    try:
        ram_res = subprocess.run(["free", "-m"], capture_output=True, text=True, timeout=3)
        if ram_res.returncode == 0:
            ram_match = re.search(r"Mem:\s+(\d+)\s+(\d+)", ram_res.stdout)
            if ram_match:
                sensors["ram"] = ram_match.group(1)
    except: pass
    return sensors

# =============================================
# अनलॉक चैलेंज जनरेटर (यादृच्छिक गणित – बिल्कुल पुराने BUCHI जैसा)
# =============================================
def generate_challenge():
    if UNLOCK_MODE == "fixed_string" and UNLOCK_FIXED_STRING:
        return f"अनलॉक लॉजिक: {UNLOCK_FIXED_STRING} दर्ज करें", UNLOCK_FIXED_STRING
    else:
        a = random.randint(10, 99)
        b = random.randint(10, 99)
        expected = f"{a}{b}"
        question = f"अनलॉक लॉजिक: {a} + {b} = ?"
        return question, expected

# =============================================
# सेल्फ-हीलिंग (पैकेज इंस्टॉल)
# =============================================
def self_heal(cmd, error_msg):
    if "not found" in error_msg.lower() or "no such file" in error_msg.lower():
        pkg_match = re.search(r"command '(.*?)' not found", error_msg)
        if pkg_match:
            pkg = pkg_match.group(1)
            console.print(f"[cyan]🔧 स्व-सुधार: {pkg} इंस्टॉल कर रहा हूँ...[/]")
            subprocess.run(f"pkg install {pkg} -y", shell=True)
            return True
    return False

# =============================================
# कमांड निष्पादक (लाइव आउटपुट के साथ)
# =============================================
def execute_command(cmd):
    safe, reason = is_safe_command(cmd)
    if not safe:
        console.print(f"[red]❌ सुरक्षा ब्लॉक: {reason}[/]")
        return "Blocked: " + reason
    console.print(f"[bold cyan]🌀 लाइव कमांड: {cmd}[/]")
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    output_lines = []
    for line in process.stdout:
        line = line.rstrip()
        print(line)
        output_lines.append(line)
    process.wait()
    if process.returncode != 0:
        err_text = "\n".join(output_lines)
        if self_heal(cmd, err_text):
            console.print("[yellow]🔄 पुनः प्रयास...[/]")
            return execute_command(cmd)  # रीट्राई
        else:
            console.print(f"[red]❌ कमांड विफल (कोड {process.returncode})[/]")
    else:
        console.print("[green]✅ कमांड सफल[/]")
    return "\n".join(output_lines)

# =============================================
# Groq AI चैट (सामान्य बातचीत और अनलॉक के बाद भी)
# =============================================
def ask_ai(prompt, sensor_data):
    global chat_history
    # संदर्भ तैयार करें – पिछले 10 संवाद (20 संदेश)
    recent = chat_history[-20:] if len(chat_history) > 20 else chat_history
    context = ""
    for entry in recent:
        context += f"\n{entry['role']}: {entry['content']}"
    
    system_prompt = f"""तुम BUCHI हो, मास्टर माधव के वफादार AI सहायक। वर्तमान स्टेट: {current_state}.
लाइव सेंसर: बैटरी {sensor_data['battery']}%, रैम {sensor_data['ram']}MB, तापमान {sensor_data['temp']}C.
पिछली बातचीत:{context}
हमेशा 'मास्टर' कहकर संबोधित करो। कोड या कमांड माँगे जाने पर बताओ कि सिस्टम लॉक है या अनलॉक। अगर अनलॉक है और कमांड सुरक्षित है, तो मैं खुद चलाऊंगा – तुम केवल बातचीत करो।"""
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                         headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                         json=payload, timeout=25)
        reply = r.json()['choices'][0]['message']['content']
        # चैट हिस्ट्री अपडेट करें
        chat_history.append({"role": "user", "content": prompt})
        chat_history.append({"role": "assistant", "content": reply})
        if len(chat_history) > 40:
            chat_history = chat_history[-40:]
        return reply
    except Exception as e:
        return f"न्यूरल लिंक बाधित: {e}"

# =============================================
# मुख्य लूप – 3-स्टेट आर्किटेक्चर
# =============================================
def main():
    global current_state, pending_challenge
    
    console.print(Panel(Text("🤖 BUCHI FRAMEWORK ACTIVE (LOCKED)", justify="center", style="bold yellow"), box=HEAVY))
    console.print("[dim]सिस्टम LOCKED है। केवल सामान्य बातचीत होगी।[/]")
    console.print("[dim]अनलॉक करने के लिए पहले ACTIVATION_SENTENCE दर्ज करें, फिर चैलेंज उत्तर दें।[/]\n")
    
    while True:
        # सेंसर डेटा हर लूप में ताज़ा करें
        env = sense_environment()
        # टर्मिनल क्लियर न करें – संदेशों को बहने दें (स्ट्रीमिंग अनुभव)
        
        # प्रॉम्प्ट दिखाएँ
        console.print(f"[bold cyan]🔒 [{current_state}] मास्टर > [/]", end="")
        user_input = sys.stdin.readline().strip()
        if not user_input or user_input.lower() in ["exit", "quit"]:
            break
        
        # ===== 1. यदि पेंडिंग चैलेंज है =====
        if pending_challenge is not None:
            if user_input == pending_challenge["expected"]:
                current_state = STATE_UNLOCKED
                pending_challenge = None
                console.print("[green]✅ सिस्टम अनलॉक हो गया! अब आप सुरक्षित कमांड चला सकते हैं।[/]")
                # वॉइस फीडबैक (वैकल्पिक)
                subprocess.run(["termux-tts-speak", "सिस्टम अनलॉक हो गया"], capture_output=True)
            else:
                console.print("[red]❌ चैलेंज उत्तर गलत! सिस्टम लॉक रहेगा।[/]")
                pending_challenge = None
                subprocess.run(["termux-tts-speak", "गलत उत्तर"], capture_output=True)
            continue
        
        # ===== 2. यदि लॉक है और उपयोगकर्ता ने एक्टिवेशन सेंटेंस दर्ज किया =====
        if current_state == STATE_LOCKED and user_input.strip() == ACTIVATION_SENTENCE:
            q, exp = generate_challenge()
            pending_challenge = {"question": q, "expected": exp}
            console.print(f"[cyan]🔐 {q}[/]")
            subprocess.run(["termux-tts-speak", q], capture_output=True)
            continue
        
        # ===== 3. यदि लॉक है – सामान्य चैट (कोई कमांड नहीं) =====
        if current_state == STATE_LOCKED:
            with console.status("[bold blue]बुज्जी सोच रहा है..."):
                reply = ask_ai(user_input, env)
            console.print(f"\n[bold green]बुज्जी:[/] {reply}\n")
            continue
        
        # ===== 4. यदि अनलॉक है – चेक करें कि क्या उपयोगकर्ता कमांड देना चाहता है =====
        # सरल रूल: अगर इनपुट whitelist के किसी प्रीफिक्स से शुरू होता है, तो कमांड समझें
        is_cmd = any(user_input.strip().lower().startswith(cmd) for cmd in ALLOWED_COMMANDS)
        if is_cmd:
            # कमांड चलाएँ (लाइव आउटपुट दिखेगा)
            output = execute_command(user_input)
            # अगर आउटपुट बहुत लंबा है तो केवल सारांश दिखाएँ (वैकल्पिक)
            if len(output) > 500:
                console.print(f"[dim]आउटपुट {len(output)} अक्षरों का है। ऊपर देखें।[/]")
        else:
            # सामान्य बातचीत
            with console.status("[bold blue]बुज्जी सोच रहा है..."):
                reply = ask_ai(user_input, env)
            console.print(f"\n[bold green]बुज्जी:[/] {reply}\n")
        
        # थोड़ा विराम (स्ट्रीमिंग एहसास के लिए)
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]बुज्जी बंद हो रहा है। जय मास्टर माधव![/]")
        sys.exit(0)
