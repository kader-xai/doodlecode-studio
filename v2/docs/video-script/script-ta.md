# DoodleCode Studio v2 — தமிழ் narration script

> YouTube auto-dub-க்காக தயாரிக்கப்பட்ட ஸ்கிரிப்ட்.
> ஒவ்வொரு வரியும் சிறிய வாக்கியம், timing எளிதாக அமைய.
> மொத்த நீளம் சுமார் 4–5 நிமிடம்.

---

## 1. அறிமுகம் (0:00 – 0:20)

வணக்கம் நண்பர்களே, என் பெயர் [உங்கள் பெயர்],
இன்று உங்களுக்கு காட்டப் போவது DoodleCode Studio v2.

இது ஒரு doodle பாணி Python notebook,
ஆனால் presentation canvas-ஆகவும் வேலை செய்யும்.

ஒரே `.py` கோப்பில் code cells,
markdown, images, live browser pages,
மற்றும் doodle diagrams — எல்லாமே சேர்த்து இருக்கும்.

---

## 2. கேன்வாஸ் சுற்றுப்பயணம் (0:20 – 0:50)

App-ஐ திறந்தவுடன்,
doodle பாணி canvas ஒன்று தெரியும்.

மேலே toolbar-ல் எல்லா cell types-க்கும்
தனித்தனி button இருக்கும் —
Code, Text, Media, Browser, Draw, Diagram.

பின்னணியில் மென்மையான floating shapes,
அவற்றை ambient picker-ல் மாற்றலாம் —
geometry, nature, அல்லது science.

dark mode button-ல் theme உடனே மாறும்.

---

## 3. Code cell மற்றும் persistent kernel (0:50 – 1:30)

Code cell-ல் Python எழுதி,
▶ Run பொத்தானை அழுத்துங்கள்.

இது persistent kernel,
அதாவது ஒரு cell-ல் `x = 41` என்று எழுதினால்,
அடுத்த cell-ல் `print(x + 1)` கொடுத்தால் `42` வரும்.

variables-உம் imports-உம் தொடர்ந்து தாக்குப்பிடிக்கும் —
சரியான Jupyter notebook மாதிரி.

matplotlib graph-ஐ inline-ஆகவே காட்டும்.
`plt.show()` மட்டும் போட்டால்,
படம் cell-க்கு கீழே வந்துவிடும்.

புதிய package install செய்ய,
📦 Install button-ஐ click செய்யுங்கள்.
பெயரை type செய்து Install அழுத்தினால்,
kernel தானாக மறுதொடக்கம் ஆகி,
import உடனே வேலை செய்யும்.

---

## 4. Markdown, Media மற்றும் Browser (1:30 – 2:10)

Text cell-ல் markdown எழுதலாம் —
heading-க்கு `#`, bold-க்கு `**`,
list-க்கு `-`, அவ்வளவுதான்.

Media cell-ல் image URL,
அல்லது YouTube link போட்டால்,
embed தானாகவே உருவாகும்.

Browser cell-ல் live website-ஐ
canvas-க்குள் வைத்துக் கொள்ளலாம்.
B key அழுத்தினால் iframe-உடன் interact செய்யலாம்,
🛡 button-ல் proxy mode ஆரம்பமாகி,
Google போன்ற sites கூட load ஆகும்.

---

## 5. Whiteboard மற்றும் Diagrams (2:10 – 2:50)

Whiteboard cell-ல் pen, highlighter,
eraser tools இருக்கின்றன —
ஐந்து colors, மூன்று backgrounds-உடன்.

Diagram cell-ல் மூன்று styles உள்ளன.

முதலாவது **Doodle** —
`A --> B` எழுதினால் flowchart,
`Label: number` எழுதினால் bar chart,
இரண்டுமே ஒரே source-ல் சேர்ந்து வரும்.

இரண்டாவது **Mermaid** —
sequence, flowchart எல்லாமே வேலை செய்யும்.

மூன்றாவது **Math** —
LaTeX equation-ஐ KaTeX-உடன் render செய்யும்.

---

## 6. Callouts மற்றும் connection animation (2:50 – 3:20)

எந்த cell-ஐயும் select செய்து,
💬 Callouts button-ஐ click செய்யுங்கள்.
modal திறக்கும், அங்கே
text-உம் image-உம் இரண்டும் சேர்க்கலாம்.

callout bubbles cell-க்கு வலதுபுறம் stack ஆகும்,
ஒவ்வொரு bubble-க்கும் dashed line ஓடும்,
அந்த line-ல் dots flow ஆகி,
energy cell-லிருந்து callout நோக்கி பாயும் மாதிரி தோன்றும்.

---

## 7. Save மற்றும் Open (3:20 – 3:45)

Cmd+S அழுத்தினால் notebook silently save ஆகும் —
நீங்கள் எந்த `.py` கோப்பிலிருந்து திறந்தீர்களோ
அதே இடத்துக்கே எழுதப்படும்.

🆕 New, 📂 Open, 💾 Save As —
எல்லா options-உம் File menu-ல் உள்ளன.

localStorage-ல் autosave-உம் நடக்கும்,
எனவே browser refresh ஆனாலும்
உங்கள் வேலை அப்படியே இருக்கும்.

---

## 8. Presentation mode (3:45 – 4:25)

இனி மிக சுவாரசியமான feature — Presentation mode.

S key அழுத்தினால் cells slide-by-slide
பரந்து போய் அமையும்.

பின் F5 அல்லது Shift+P அழுத்தி
Present mode-க்கு செல்லுங்கள்.

வலது arrow அல்லது Space அடுத்த slide-க்கு,
இடது arrow பின் slide-க்கு.

இடையில் ஏதாவது விளக்க வேண்டுமென்றால்,
**P** key-ல் pen, **H** key-ல் highlighter,
**X** key-ல் fixed pen.
**E** அழுத்தினால் எல்லா ink-உம் அழியும்.

**R** key-ல் code cell live-ஆக run செய்யலாம் —
பார்வையாளர்கள் முன்பே.

**F** key-ல் fullscreen mode.

---

## 9. முடிவுரை (4:25 – 4:45)

அவ்வளவுதான், நண்பர்களே.

DoodleCode Studio v2 இப்போது
முழுமையாக open-source,
உங்கள் computer-லேயே ஓடும்.
உங்கள் data வெளியே செல்லாது.

Star போடுங்கள், fork செய்யுங்கள்,
உங்கள் projects-ஐ share செய்யுங்கள்.

பார்த்ததற்கு நன்றி,
அடுத்த video-ல் சந்திப்போம்.
Bye!
