# BUCHI V11 – Elite AI Agent for Non-Rooted Android

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**BUCHI** एक अत्याधुनिक, सुरक्षित और ऑटोनॉमस **AI एजेंट फ्रेमवर्क** है जिसे विशेष रूप से Android पर **Termux** के भीतर चलाने के लिए बनाया गया है। यह बिना किसी **Root एक्सेस** के सीधे आपके डिवाइस को एक शक्तिशाली मल्टी-मॉडल एआई कर्नल में बदल देता है।

## 🚀 मुख्य विशेषताएँ (Why BUCHI?)

* **✅ No-Root Required:** पूरी तरह से सुरक्षित। बिना किसी छेड़छाड़ या Shizuku/ADB bridging के मानक Termux एनवायरनमेंट में चलता है।
* **🧠 Multi-Modal Intelligence:** केवल चैट नहीं! हार्डवेयर (टॉर्च, बैटरी) और ऐप्स (Deep-linking) को सीधे एआई कमांड से नियंत्रित करता है।
* **🛡️ Security Kernel:** 'एक्टिवेशन सेंटेंस' और गणितीय चुनौतियों के साथ एक अभेद्य सुरक्षा लॉक।
* **🔒 Sandboxed Execution:** व्हाइटलिस्ट आधारित सुरक्षित कमांड निष्पादन। कोई भी खतरनाक शेल मेटाकैरेक्टर सिस्टम को नुकसान नहीं पहुँचा सकता।
* **🔧 Self-Healing Engine:** गुम पैकेज का पता लगाना और उन्हें पृष्ठभूमि में स्वतः इंस्टॉल करना।
* **📡 Real-time Monitoring:** बैटरी, रैम, और तापमान का लाइव सिस्टम डेटा एक्सेस।

## 🛠 इंस्टॉलेशन

```bash
pkg update && pkg upgrade
pkg install python git
git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name
pip install -r requirements.txt
cp .env.example .env
nano .env   # अपनी GROQ_API_KEY और ACTIVATION_SENTENCE सेट करें
python buchi_core.py
