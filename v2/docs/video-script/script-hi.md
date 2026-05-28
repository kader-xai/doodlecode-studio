# DoodleCode Studio v2 — हिंदी narration script

> YouTube auto-dub के लिए तैयार किया गया स्क्रिप्ट।
> हर लाइन एक छोटा वाक्य है ताकि timing आसानी से सेट हो जाए।
> कुल अवधि लगभग 4–5 मिनट।

---

## 1. Intro (0:00 – 0:20)

नमस्ते दोस्तों, मेरा नाम है [आपका नाम],
और आज मैं आपको दिखाने वाला हूँ DoodleCode Studio v2।

ये एक doodle-style Python notebook है,
जो प्रेजेंटेशन कैनवस की तरह भी काम करता है।

एक ही `.py` फ़ाइल में आपकी कोड cells,
markdown, images, browser pages,
और हाथ से बनाए हुए diagrams — सब कुछ रहते हैं।

---

## 2. कैनवस का परिचय (0:20 – 0:50)

जब आप ऐप खोलते हैं,
तो आपको एक doodle-style कैनवस दिखता है।

ऊपर toolbar में आपको हर तरह के cell जोड़ने के बटन मिलेंगे —
Code, Text, Media, Browser, Draw, और Diagram।

बैकग्राउंड में हल्की-सी floating shapes हैं,
जिनका theme आप ambient picker से बदल सकते हैं —
geometry, nature, या science।

dark mode बटन से थीम तुरंत बदल जाती है।

---

## 3. Code cell और persistent kernel (0:50 – 1:30)

Code cell में Python लिखिए,
और ▶ Run दबाइए।

ये persistent kernel है,
यानी एक cell में अगर आपने `x = 41` लिखा,
तो अगली cell में `print(x + 1)` से `42` मिलेगा।

मतलब variables और imports आगे carry होते हैं —
ठीक Jupyter notebook जैसा।

matplotlib का plot inline दिखता है।
बस `plt.show()` लिखिए, और figure cell के नीचे आ जाता है।

कोई भी package install करने के लिए
📦 Install button पर click कीजिए।
package का नाम लिखिए और Install दबाइए —
kernel अपने आप restart हो जाता है।

---

## 4. Markdown, Media, और Browser (1:30 – 2:10)

Text cell में markdown लिखिए —
heading के लिए `#`, bold के लिए `**`,
list के लिए `-`, बस इतना ही।

Media cell में image URL डालिए,
या YouTube का link —
embed automatically बन जाता है।

Browser cell से आप कोई भी live website
canvas में रख सकते हैं।
B key दबाने पर iframe के साथ interact कर सकते हैं,
और 🛡 button से proxy mode चालू होता है —
जिस से Google जैसी sites भी load हो जाती हैं।

---

## 5. Whiteboard और Diagrams (2:10 – 2:50)

Whiteboard cell में pen, highlighter,
और eraser tool हैं —
पाँच colors और तीन backgrounds के साथ।

Diagram cell में तीन styles हैं।

पहला है **Doodle** —
`A --> B` से flowchart बनती है,
और `Label: number` से bar chart।
दोनों एक ही source में।

दूसरा है **Mermaid** —
sequence, flowchart, सब कुछ काम करता है।

और तीसरा है **Math** —
LaTeX equation render होते हैं KaTeX से।

---

## 6. Callouts और कनेक्शन animation (2:50 – 3:20)

किसी भी cell को select करके 💬 Callouts पर click कीजिए।
modal खुलेगा जहाँ आप
text और image — दोनों जोड़ सकते हैं।

callout bubbles cell के दाहिनी तरफ़ stack होती हैं,
और हर bubble तक एक dashed line जाती है,
जिसमें dots flow करते दिखाई देते हैं —
मानो energy cell से callout की तरफ़ बह रही हो।

---

## 7. Save और Open (3:20 – 3:45)

Cmd+S दबाने से नोटबुक save हो जाती है —
जिस `.py` फ़ाइल से आपने खोला था,
उसी में silently वापस लिखी जाती है।

🆕 New, 📂 Open, और 💾 Save As —
सारे options File menu में हैं।

localStorage में autosave भी होता है,
इसलिए browser refresh के बाद भी आपका काम वहीं रहता है।

---

## 8. Presentation mode (3:45 – 4:25)

अब सबसे मज़ेदार feature — Presentation mode।

S key दबाइए तो cells slide-by-slide
spread हो जाती हैं।

फिर F5 या Shift+P से Present mode में जाइए।

Arrow key या Space से अगली slide,
back arrow से पिछली slide।

बीच में अगर कुछ explain करना हो,
तो **P** से pen, **H** से highlighter,
और **X** से fixed pen।
**E** दबाने पर सारी ink मिट जाती है।

**R** से code cell live run भी कर सकते हैं —
audience के सामने।

**F** से fullscreen mode चालू होता है।

---

## 9. Outro (4:25 – 4:45)

बस इतना ही, दोस्तों।

DoodleCode Studio v2 अभी पूरी तरह open-source है
और locally चलता है।
आपका data कभी आपके computer से बाहर नहीं जाता।

Star करिए, fork करिए,
और अपने projects share कीजिए।

देखने के लिए धन्यवाद,
agle video में मिलते हैं।
Bye!
