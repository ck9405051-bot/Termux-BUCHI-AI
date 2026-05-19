# BUCHI Framework – Elite AI Agent for Termux

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

एक पूर्ण, सुरक्षित, और अनुकूलन योग्य AI एजेंट फ्रेमवर्क Termux के लिए।  
**लॉक/अनलॉक आर्किटेक्चर, Groq AI, सेल्फ-हीलिंग, और सुरक्षित कमांड निष्पादन** के साथ।

## ✨ विशेषताएँ

- 🔒 **लॉक/अनलॉक** – अपना गुप्त सूत्र और गणितीय चैलेंज से सुरक्षा।
- 🤖 **Groq AI (LLaMA 3.3 70B)** – वास्तविक बुद्धिमान बातचीत।
- 🛡️ **सुरक्षित कमांड निष्पादन** – व्हाइटलिस्ट + शेल मेटाकैरेक्टर ब्लॉकिंग।
- 🔧 **सेल्फ-हीलिंग** – गुम पैकेज स्वतः इंस्टॉल करता है।
- 📺 **लाइव कमांड आउटपुट** – रियल-टाइम में देखें क्या हो रहा है।
- 🧠 **स्थानीय चैट इतिहास** – बातचीत की निरंतरता बनी रहती है।
- 📡 **सेंसर** – बैटरी, रैम, तापमान लाइव दिखाता है।

## 🚀 इंस्टॉलेशन

```bash
pkg update && pkg upgrade
pkg install python
pip install -r requirements.txt
cp .env.example .env
nano .env   # अपनी API key और एक्टिवेशन सेंटेंस डालें
python buchi_core.py
