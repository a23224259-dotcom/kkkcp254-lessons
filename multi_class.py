#!/usr/bin/env python3
"""CBC multi-level Telegram scheduler. All times are East Africa Time (UTC+3)."""
import os, json, hashlib, datetime as dt, urllib.parse, urllib.request, urllib.error, textwrap
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm

EAT = dt.timezone(dt.timedelta(hours=3))
CHAT = os.environ.get("TG_CHAT_ID", "@KKKCP254")
TOKEN = os.environ["TG_BOT_TOKEN"]
STATE_FILE = "multi_class_state.json"
FOOTER = (
    "\n\n━━━━━━━━━━━━━━\n"
    "📢 JOIN AND SHARE: https://t.me/KKKCP254\n"
    "🔗 Why share the channel link? It helps classmates, parents and other learners discover free learning and revision support.\n"
    "📄 Why share the PDF? Learners can save it, read it again offline, revise at their own pace and use the worked examples for practice.\n"
    "🌱 Help the channel grow: invite more learners and teachers, share useful questions and learning resources, and suggest topics that should be covered. More participation helps build a richer learning community for everyone.\n"
    "❓ Questions or contributions? Telegram admin: @alexandermurithi0"
)

# Each entry is a short, age-appropriate learning unit. Add new entries to grow
# the no-repeat bank. The scheduler refuses to resend an identical post.
LEVELS = [
("Playgroup", [
("Colours", "Learners identify and name red, blue and yellow objects around them.", "Point to one red object, one blue object and one yellow object.", "Red, blue and yellow objects."),
("Counting 1-3", "Count three familiar objects together, touching each object once.", "Count: 🍎 🍎 🍎. How many apples are there?", "Three apples."),
("Shapes", "A circle is round. A square has four equal sides.", "Find one round object and one square-shaped object.", "Examples: a ball or plate; a square tile."),
("Big and small", "We can compare objects by size. One object may be bigger or smaller.", "Point to the bigger of two toys.", "The bigger toy is the one that takes up more space.")
]),
("PP1", [
("Counting 1-5", "Count objects in order: one, two, three, four, five.", "How many fingers are on one hand?", "Five fingers."),
("Letter sounds", "The letter m makes the /m/ sound as in mat and milk.", "Say the first sound in moon.", "The /m/ sound."),
("Healthy habits", "Wash hands with clean water and soap before eating and after using the toilet.", "When should we wash our hands?", "Before eating and after using the toilet."),
("Shapes", "A triangle has three straight sides and three corners.", "How many sides does a triangle have?", "Three sides.")
]),
("PP2", [
("Addition to 10", "Addition means putting groups together. 3 + 2 = 5.", "Work out 4 + 3.", "7."),
("Beginning sounds", "The word sun begins with the /s/ sound.", "Which sound begins the word fish?", "The /f/ sound."),
("Living things", "Plants and animals are living things. They need resources to live and grow.", "Name one thing a plant needs to grow.", "Water, air, light or suitable soil."),
("Time", "We use a clock to tell time. A day has morning, afternoon, evening and night.", "Which part of the day comes after morning?", "Afternoon.")
]),
("Grade 1", [
("Place value", "In 24, the digit 2 means two tens and the digit 4 means four ones.", "What is the value of 3 in 35?", "30."),
("Nouns", "A noun names a person, place, animal or thing.", "Identify the noun: The dog runs.", "Dog."),
("Plants", "Roots hold a plant in the soil and absorb water and minerals.", "State one function of roots.", "They absorb water and minerals or anchor the plant."),
("Addition", "Add ones first: 12 + 5 = 17.", "Calculate 13 + 4.", "17.")
]),
("Grade 2", [
("Subtraction", "Subtraction means taking away. 15 - 6 = 9.", "Calculate 18 - 7.", "11."),
("Verbs", "A verb is an action or doing word, such as run, read or write.", "Find the verb: Amina sings.", "Sings."),
("Water sources", "Water comes from sources such as rain, rivers, lakes, springs and wells.", "Name two sources of water.", "Any two correct sources."),
("Multiplication", "Multiplication is repeated addition. 3 × 4 means 4 + 4 + 4.", "Calculate 2 × 5.", "10.")
]),
("Grade 3", [
("Fractions", "A fraction shows equal parts of a whole. One half is written 1/2.", "If a shape is divided into 4 equal parts and 1 is shaded, what fraction is shaded?", "1/4."),
("Punctuation", "A sentence begins with a capital letter and ends with a suitable punctuation mark.", "Correct this: we live in kenya", "We live in Kenya."),
("Matter", "Matter has mass and occupies space. Solids, liquids and gases are states of matter.", "Name the state of water in ice.", "Solid."),
("Perimeter", "Perimeter is the total distance around a shape.", "A square has sides of 3 cm. Find its perimeter.", "4 × 3 = 12 cm.")
]),
("Grade 4", [
("Factors", "A factor divides a number exactly. Factors of 12 include 1, 2, 3, 4, 6 and 12.", "List all factors of 8.", "1, 2, 4 and 8."),
("Adjectives", "An adjective describes a noun, for example a tall tree.", "Identify the adjective: The bright sun shines.", "Bright."),
("Food groups", "A balanced diet contains different food groups in suitable proportions.", "Give one example of a protein-rich food.", "Beans, eggs, fish, milk or meat."),
("Area", "Area measures the surface covered by a shape. Rectangle area = length × width.", "Find the area of a rectangle 5 cm by 3 cm.", "15 cm².")
]),
("Grade 5", [
("Equivalent fractions", "Equivalent fractions have the same value. 1/2 = 2/4 = 3/6.", "Write 1/3 as an equivalent fraction with denominator 9.", "3/9."),
("Subject and predicate", "The subject tells who or what the sentence is about. The predicate tells what the subject does or is.", "Identify the subject: The pupils read quietly.", "The pupils."),
("Force", "A force is a push or a pull. Forces can change motion or shape.", "Give one example of a push.", "Pushing a door or trolley."),
("Decimals", "The first digit after the decimal point represents tenths.", "Write 7/10 as a decimal.", "0.7.")
]),
("Grade 6", [
("Percentages", "Percent means out of 100. 25% = 25/100 = 1/4.", "Find 10% of 250.", "25."),
("Direct speech", "Direct speech gives the exact words spoken and uses quotation marks.", "Punctuate: Mary said I am ready.", "Mary said, “I am ready.”"),
("Electric circuits", "A simple circuit needs a cell, connecting wires and a complete conducting path.", "What happens when a switch opens the circuit?", "The current stops flowing."),
("Volume", "Volume of a cuboid = length × width × height.", "Find the volume of a cuboid 4 cm × 3 cm × 2 cm.", "24 cm³.")
]),
("Grade 7", [
("Integers", "Integers include negative whole numbers, zero and positive whole numbers.", "Calculate -3 + 8.", "5."),
("Active and passive voice", "In active voice the subject performs the action. In passive voice the subject receives the action.", "Change to passive: The learner wrote a letter.", "A letter was written by the learner."),
("Heat transfer", "Heat moves by conduction, convection and radiation.", "Which method transfers heat through a metal spoon?", "Conduction."),
("Ratio", "A ratio compares quantities using the same units.", "Simplify 6:9.", "2:3.")
]),
("Grade 8", [
("Linear equations", "An equation remains balanced when the same operation is applied to both sides.", "Solve 3x + 2 = 14.", "3x = 12, so x = 4."),
("Reported speech", "Reported speech tells what someone said without quoting the exact words.", "Change: He said, “I am tired.”", "He said that he was tired."),
("Cells", "The cell is the basic structural and functional unit of living organisms.", "Name the organelle that controls most cell activities.", "The nucleus."),
("Simple interest", "Simple interest I = PRT/100, where P is principal, R is rate and T is time in years.", "Find interest on KSh 1,000 at 5% for 2 years.", "I = 1000 × 5 × 2 / 100 = KSh 100.")
]),
("Grade 9", [
("Pythagoras", "In a right-angled triangle, hypotenuse² = base² + height².", "Find the hypotenuse when the shorter sides are 6 cm and 8 cm.", "√(36 + 64) = 10 cm."),
("Chemical changes", "A chemical change forms one or more new substances and is often difficult to reverse.", "Give one sign of a chemical reaction.", "Gas formation, colour change, temperature change or precipitate."),
("Human respiration", "Aerobic respiration releases energy from glucose using oxygen.", "Name the gas used in aerobic respiration.", "Oxygen."),
("Data handling", "The mean is the sum of values divided by the number of values.", "Find the mean of 2, 4, 6 and 8.", "20 ÷ 4 = 5.")
]),
("Grade 10", [
("Quadratic equations", "A quadratic equation has the form ax² + bx + c = 0, where a is not zero.", "Solve x² - 5x + 6 = 0.", "(x - 2)(x - 3) = 0; x = 2 or x = 3."),
("Electricity", "Ohm’s law states that V = IR for a conductor at constant physical conditions.", "Find the current when V = 12 V and R = 4 Ω.", "I = V/R = 12/4 = 3 A."),
("Radioactivity", "Half-life is the time taken for half the undecayed radioactive nuclei in a sample to decay.", "A sample has 80 g and a half-life of 5 days. How much remains after 5 days?", "40 g."),
("Waves", "Wave speed v = frequency f × wavelength λ.", "Find the speed for f = 50 Hz and λ = 2 m.", "v = 50 × 2 = 100 m/s.")
]),
("Grade 11", [
("Trigonometry", "For a right triangle, sin θ = opposite/hypotenuse, cos θ = adjacent/hypotenuse and tan θ = opposite/adjacent.", "If opposite = 3 and hypotenuse = 5, find sin θ.", "sin θ = 3/5 = 0.6."),
("Organic chemistry", "A homologous series has the same functional group and general formula, with successive members differing by CH₂.", "What is the next alkane after ethane?", "Propane, C₃H₈."),
("Genetics", "An allele is an alternative form of a gene. Genotype describes the allele combination.", "For Tt × Tt, what is the probability of tt?", "1/4 or 25%."),
("Statistics", "The median is the middle value after data are arranged in order.", "Find the median of 3, 7, 2, 9, 5.", "Ordered data: 2, 3, 5, 7, 9. Median = 5.")
]),
("Form 4", [
("KCSE Mathematics: probability", "For equally likely outcomes, P(A) = number of favourable outcomes / total number of outcomes.", "A fair die is rolled. Find the probability of getting an even number.", "Favourable outcomes: 2, 4, 6. Probability = 3/6 = 1/2."),
("KCSE Physics: internal resistance", "For a cell, terminal voltage V = E - Ir when supplying current I through external resistance; r is internal resistance.", "A cell has E = 1.5 V, r = 0.2 Ω and I = 2 A. Find terminal voltage.", "V = 1.5 - (2 × 0.2) = 1.1 V."),
("KCSE Chemistry: mole calculations", "Moles n = mass / molar mass. Always calculate the correct molar mass first.", "Find moles in 9 g of water, H₂O (H=1, O=16).", "Molar mass = 18 g/mol; n = 9/18 = 0.5 mol."),
("KCSE Biology: genetics", "A monohybrid cross follows inheritance of one characteristic. A heterozygous cross often gives a 3:1 phenotype ratio under complete dominance.", "Cross Aa × Aa. State the genotype ratio.", "1 AA : 2 Aa : 1 aa.")
])
]


# Additional original learning units to broaden every class bank.
EXTRA_TOPICS = {
"Playgroup": [
("Counting 4-5", "Count slowly from one to five while touching one object for each number. The last number said tells how many objects are in the group.", "Count: 🟠 🟠 🟠 🟠. How many objects?", "Four objects."),
("Same and different", "Objects are the same when they share a feature such as colour, shape or size. They are different when at least one feature is not alike.", "Are a spoon and a cup the same shape?", "No. A spoon and a cup have different shapes.")
],
"PP1": [
("Numbers 6-10", "Count forward from six to ten in the correct order. Match each number word to a group containing the same number of objects.", "What number comes after 8?", "9."),
("Rhyming words", "Rhyming words have the same or similar ending sound, such as cat and hat. Listen to the ending sound rather than the first letter.", "Which word rhymes with sun: run or sit?", "Run.")
],
"PP2": [
("Subtraction within 10", "Subtraction means removing some objects from a group and finding how many remain. Count the objects left after taking some away.", "There are 8 mangoes. 3 are eaten. How many remain?", "8 - 3 = 5 mangoes."),
("Parts of a plant", "A plant commonly has roots, a stem and leaves. Roots absorb water, the stem supports the plant and carries materials, while leaves make food using light.", "Which part of a plant absorbs water from the soil?", "The roots.")
],
"Grade 1": [
("Number patterns", "A number pattern follows a rule. To continue it, compare neighbouring numbers and identify what is added or taken away each time.", "Complete: 2, 4, 6, 8, __.", "10; add 2 each time."),
("Healthy food", "Different foods provide different nutrients. Fruits and vegetables provide vitamins and fibre; beans, eggs and fish provide protein; cereals provide energy.", "Name one food that helps the body grow and repair.", "Beans, eggs, fish, milk or another protein-rich food.")
],
"Grade 2": [
("Fractions: halves", "A half is one of two equal parts of a whole. The two parts must be equal in size for each to represent one half.", "A chapati is shared equally between 2 children. What fraction does each get?", "One half, written 1/2."),
("Adverbs", "An adverb gives more information about a verb, often telling how, when or where an action happens. In 'She sings sweetly', sweetly tells how she sings.", "Identify the adverb: The boy ran quickly.", "Quickly.")
],
"Grade 3": [
("Multiplication tables", "Multiplication is equal groups. For example, 4 × 3 means four groups of three, which is 3 + 3 + 3 + 3.", "Calculate 5 × 4 using repeated addition.", "4 + 4 + 4 + 4 + 4 = 20."),
("Evaporation", "Evaporation happens when a liquid changes into gas at its surface. Heat and moving air can make evaporation happen faster.", "What happens to a small puddle on a warm sunny day?", "Some water evaporates into the air.")
],
"Grade 4": [
("Prime and composite numbers", "A prime number has exactly two factors: 1 and itself. A composite number has more than two factors. The number 1 is neither prime nor composite.", "Is 15 prime or composite? Give a reason.", "Composite; its factors include 1, 3, 5 and 15."),
("Types of sentences", "A statement gives information, a question asks something, a command gives an instruction and an exclamation expresses strong feeling.", "Identify the sentence type: 'Please close the door.'", "A command (imperative sentence).")
],
"Grade 5": [
("Adding fractions", "To add fractions with the same denominator, add the numerators and keep the denominator. The parts must be equal-sized.", "Calculate 2/7 + 3/7.", "5/7."),
("Electric conductors and insulators", "Conductors allow electric current to pass through them easily; metals such as copper are common conductors. Insulators resist current; dry plastic and rubber are common examples.", "Is copper a conductor or an insulator?", "A conductor.")
],
"Grade 6": [
("Ratio in simplest form", "A ratio compares quantities. To simplify it, divide every term by the highest common factor. First express quantities in the same units.", "Simplify 12:18.", "Divide both terms by 6: 2:3."),
("The water cycle", "The water cycle is the continuous movement of water between Earth's surface and the atmosphere. Evaporation, condensation and precipitation are key processes.", "What is precipitation?", "Water falling from clouds as rain, snow or hail.")
],
"Grade 7": [
("Fractions, decimals and percentages", "Fractions, decimals and percentages can represent the same quantity. Convert a fraction to a decimal by division, then multiply by 100 to get a percentage.", "Convert 3/4 to a percentage.", "3 ÷ 4 = 0.75; 0.75 × 100 = 75%."),
("Density", "Density is mass per unit volume. The formula is density = mass ÷ volume. Use consistent units and include the unit in the answer.", "A block has mass 60 g and volume 20 cm³. Find its density.", "60 ÷ 20 = 3 g/cm³.")
],
"Grade 8": [
("Expanding brackets", "To expand a bracket, multiply the term outside by every term inside. Keep the signs of the terms correct.", "Expand 3(x + 4).", "3 × x + 3 × 4 = 3x + 12."),
("Photosynthesis", "Photosynthesis is the process by which green plants use light energy to make glucose from carbon dioxide and water, releasing oxygen. Chlorophyll absorbs light.", "Name two raw materials needed for photosynthesis.", "Carbon dioxide and water.")
],
"Grade 9": [
("Simultaneous equations", "Simultaneous equations are equations solved together because the same values satisfy both. Elimination removes one variable; substitution replaces a variable using an equivalent expression.", "Solve x + y = 7 and x - y = 1.", "Add the equations: 2x = 8, so x = 4. Then y = 3."),
("Acids and bases", "Acids produce hydrogen ions in aqueous solution; alkalis are soluble bases that produce hydroxide ions. Indicators help distinguish acidic, neutral and alkaline solutions.", "What colour does blue litmus turn in an acidic solution?", "Red.")
],
"Grade 10": [
("Capacitance", "Capacitance is the ability of a capacitor to store charge per unit potential difference. C = Q/V, where C is capacitance, Q is charge and V is potential difference.", "A capacitor stores 24 μC at 6 V. Find its capacitance.", "C = Q/V = 24/6 = 4 μF."),
("Radioactive decay calculations", "After each half-life, half of the undecayed nuclei remain. The remaining fraction after n half-lives is (1/2)^n. Decay of individual nuclei is random, but large samples show predictable patterns.", "A 160 g sample has a half-life of 3 hours. Find the mass after 6 hours.", "6 hours is 2 half-lives: 160 → 80 → 40 g.")
],
"Grade 11": [
("Differentiation", "Differentiation finds the rate at which a quantity changes. For a power term, d(x^n)/dx = nx^(n-1). Differentiate each term separately and keep constant coefficients.", "Differentiate y = 3x² + 4x - 7.", "dy/dx = 6x + 4."),
("Electrolysis", "Electrolysis uses electrical energy to drive a non-spontaneous chemical change in an electrolyte. Positive ions move to the cathode and negative ions move to the anode.", "Which electrode attracts positive ions?", "The cathode (negative electrode).")
],
"Form 4": [
("KCSE Mathematics: quadratic functions", "A quadratic function has the form y = ax² + bx + c, where a is not zero. Its graph is a parabola. The axis of symmetry is x = -b/(2a).", "Find the axis of symmetry for y = x² - 6x + 5.", "x = -(-6)/(2 × 1) = 3."),
("KCSE Physics: transformer", "A transformer changes alternating voltage by electromagnetic induction. For an ideal transformer, Vs/Vp = Ns/Np, where V is voltage and N is number of turns.", "A transformer has 500 primary turns and 100 secondary turns. If the primary voltage is 240 V, find the secondary voltage.", "Vs/240 = 100/500; Vs = 48 V."),
("KCSE Chemistry: rates of reaction", "Reaction rate describes how quickly reactants are used up or products are formed. Increasing temperature usually increases rate because particles move faster and a greater fraction have enough energy to react.", "State one way to increase the rate of reaction between a solid and a solution.", "Increase temperature, increase concentration, stir, or increase the solid's surface area."),
("KCSE Biology: ecology", "An ecosystem includes living organisms and the non-living environment interacting in an area. Producers make organic food, consumers feed on organisms and decomposers break down dead material.", "What is the role of decomposers in an ecosystem?", "They break down dead organisms and wastes, returning nutrients to the environment.")
]
}
for _level_name, _extra_bank in EXTRA_TOPICS.items():
    next(_bank for _name, _bank in LEVELS if _name == _level_name).extend(_extra_bank)


def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"last_date": "", "last_slot": -1, "level_index": {}, "sent_hashes": [], "first_media_stage": "pending"}

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": CHAT, "text": text, "disable_web_page_preview": "true"
    }).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.load(response)
    if not result.get("ok"):
        raise RuntimeError("Telegram did not confirm message delivery")


def telegram_upload(method, filepath, field_name, caption):
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    with open(filepath, "rb") as f:
        boundary = "----ChatGPTTelegramUploadBoundary"
        chunks = []
        def add_field(name, value):
            chunks.append(f"--{boundary}\r\n".encode())
            chunks.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
            chunks.append(str(value).encode("utf-8") + b"\r\n")
        add_field("chat_id", CHAT)
        add_field("caption", caption)
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(f'Content-Disposition: form-data; name="{field_name}"; filename="{os.path.basename(filepath)}"\r\n'.encode())
        mime = "image/png" if filepath.lower().endswith(".png") else "application/pdf"
        chunks.append(f"Content-Type: {mime}\r\n\r\n".encode())
        chunks.append(f.read())
        chunks.append(f"\r\n--{boundary}--\r\n".encode())
    req = urllib.request.Request(url, data=b"".join(chunks), headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=60) as response:
        result = json.load(response)
    if not result.get("ok"):
        raise RuntimeError(f"Telegram {method} did not confirm delivery")

def make_first_run_files():
    level, bank = LEVELS[0]
    title, explanation, question, answer = bank[0]
    poster_path = "welcome_learning_poster.png"
    pdf_path = "welcome_learning_pack.pdf"

    image = Image.new("RGB", (1080, 1350), "#10233f")
    draw = ImageDraw.Draw(image)
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular = ImageFont.truetype(regular_path, 42)
    bold = ImageFont.truetype(bold_path, 66)
    heading = ImageFont.truetype(bold_path, 48)
    draw.rounded_rectangle((55, 55, 1025, 1295), radius=42, fill="#f5f8ff")
    draw.rounded_rectangle((55, 55, 1025, 360), radius=42, fill="#174a78")
    draw.text((100, 105), "STUDENTS PREDICTIONS", font=heading, fill="white")
    draw.text((100, 175), "& REVISIONS", font=heading, fill="white")
    draw.text((100, 265), "DAILY LEARNING SERIES", font=regular, fill="#dcecff")
    draw.text((100, 425), "PLAYGROUP", font=bold, fill="#174a78")
    draw.text((100, 535), title, font=heading, fill="#172b4d")
    y = 640
    for line in textwrap.wrap(explanation, width=34):
        draw.text((100, y), line, font=regular, fill="#26364d")
        y += 62
    draw.rounded_rectangle((95, 930, 985, 1160), radius=28, fill="#e2efff")
    draw.text((130, 970), "TRY THIS", font=heading, fill="#174a78")
    for i, line in enumerate(textwrap.wrap(question, width=35)):
        draw.text((130, 1040 + i*52), line, font=regular, fill="#172b4d")
    draw.text((100, 1150), "Learn • Practise • Improve", font=heading, fill="#174a78")
    small = ImageFont.truetype(regular_path, 18)
    draw.text((100, 1200), "Channel: t.me/KKKCP254 | Share with other learners", font=small, fill="#172b4d")
    draw.text((100, 1235), "Questions? Telegram: @alexandermurithi0", font=small, fill="#172b4d")
    image.save(poster_path, "PNG")

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="PackTitle", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor("#174a78"), spaceAfter=12))
    styles.add(ParagraphStyle(name="PackHeading", parent=styles["Heading2"], textColor=colors.HexColor("#174a78"), spaceBefore=12))
    story = [
        Paragraph("STUDENTS PREDICTIONS AND REVISIONS", styles["PackTitle"]),
        Paragraph("Starter Learning Pack — Playgroup", styles["Heading2"]),
        Paragraph(f"<b>Topic:</b> {title}", styles["PackHeading"]),
        Paragraph(explanation, styles["BodyText"]),
        Spacer(1, 8*mm),
        Paragraph("Guided activity", styles["PackHeading"]),
        Paragraph(question, styles["BodyText"]),
        Paragraph(f"<b>Suggested response:</b> {answer}", styles["BodyText"]),
        Spacer(1, 8*mm),
        Paragraph("Learning activity for an adult and child", styles["PackHeading"]),
        Paragraph("Find safe, familiar objects together. Name their colours and sort them into groups. Encourage the child to say each colour aloud. Keep the activity playful and supervised.", styles["BodyText"]),
        Spacer(1, 8*mm),
        Paragraph("Revision reminder", styles["PackHeading"]),
        Paragraph("Repeat the activity using different familiar objects. Praise careful looking, listening and participation.", styles["BodyText"]),
        Spacer(1, 8*mm),
        Paragraph("<b>Channel:</b> https://t.me/KKKCP254", styles["BodyText"]),
        Paragraph("Please share this pack with classmates and friends so more learners can benefit.", styles["BodyText"]),
        Paragraph("<b>Questions? Contact the admin:</b>", styles["BodyText"]),
        Paragraph("Telegram: @alexandermurithi0", styles["BodyText"]),
    ]
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=18*mm, bottomMargin=18*mm)
    doc.build(story)
    return poster_path, pdf_path

def send_first_run_media(state):
    stage = state.get("first_media_stage", "pending")
    if stage == "complete":
        return
    poster, pdf = make_first_run_files()
    if stage == "pending":
        telegram_upload("sendPhoto", poster, "photo", "📌 Welcome poster — Playgroup learning series." + FOOTER)
        state["first_media_stage"] = "poster_sent"
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        stage = "poster_sent"
    if stage == "poster_sent":
        telegram_upload("sendDocument", pdf, "document", "📄 Starter PDF learning pack — Playgroup." + FOOTER)
        state["first_media_stage"] = "complete"
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

def make_post(level, item, seq, phase):
    title, explanation, question, answer = item

    # Turn each bank item into a structured teaching note rather than a
    # one-line reminder. Keep the language and task appropriate to the level.
    if level in ("Playgroup", "PP1", "PP2", "Grade 1", "Grade 2", "Grade 3"):
        level_guidance = (
            "Read the note with a learner. Demonstrate using familiar objects, "
            "say the key words aloud, and let the learner try the activity. "
            "Repeat with different examples and encourage complete answers."
        )
    elif level in ("Grade 4", "Grade 5", "Grade 6"):
        level_guidance = (
            "Read each idea carefully, underline the key words, and explain "
            "the concept in your own words. Use the worked activity to check "
            "understanding before attempting the independent task."
        )
    else:
        level_guidance = (
            "Make concise study notes, define the key terms, show every "
            "calculation or reasoning step, and include units where required. "
            "After studying the worked activity, attempt a similar question "
            "without looking at the answer."
        )

    if phase == 0:
        return (
            f"📘 {level} — DETAILED LEARNING NOTES\n"
            f"Topic: {title}\n"
            f"Learning focus: Understand the meaning of {title.lower()}, "
            f"explain the main idea, and apply it to a question.\n\n"
            f"1. MEANING AND INTRODUCTION\n{explanation}\n\n"
            f"2. EXPLANATION\n"
            f"{explanation} This idea is important because it helps us "
            f"describe, recognise or solve problems involving {title.lower()}. "
            f"Always identify the information given and what the question "
            f"requires before answering.\n\n"
            f"3. IMPORTANT POINTS TO REMEMBER\n"
            f"• Learn the meaning of the key term in the topic.\n"
            f"• Pay attention to the words and quantities given in a question.\n"
            f"• Use the correct rule, method or scientific idea.\n"
            f"• Show clear working and check that the answer addresses the question.\n\n"
            f"4. WORKED EXAMPLE\n"
            f"Question: {question}\n"
            f"Approach: First identify what is being asked. Next use the "
            f"definition or method explained in the notes. Finally state the "
            f"answer clearly.\n"
            f"Answer: {answer}\n\n"
            f"5. LEARNER ACTIVITY\n"
            f"Try the worked question again without looking at the answer. "
            f"Explain aloud how you reached your answer, then create another "
            f"example from your home, school or surroundings where possible.\n\n"
            f"6. QUICK QUIZ\n{question}\n"
            f"Answer and explanation: {answer}\n\n"
            f"7. STUDY GUIDANCE\n{level_guidance}\n"
            f"Learning series item {seq + 1}." + FOOTER
        )

    return (
        f"📝 {level} — DETAILED REVISION NOTES AND PRACTICE\n"
        f"Topic: {title}\n\n"
        f"1. QUICK REVIEW\n{explanation}\n\n"
        f"2. KEY IDEAS\n"
        f"• State the meaning of the main term.\n"
        f"• Explain the concept using your own words.\n"
        f"• Identify the relevant facts, rule, formula or steps.\n"
        f"• Check the final answer for accuracy and completeness.\n\n"
        f"3. GUIDED REVISION QUESTION\n{question}\n"
        f"How to answer: Identify what is required, select the relevant "
        f"idea or method from the notes, show the steps clearly, and write "
        f"the final answer.\n"
        f"Suggested answer: {answer}\n\n"
        f"4. INDEPENDENT PRACTICE\n"
        f"Answer the question again without looking at the suggested answer. "
        f"Then write one new question on {title.lower()} and exchange it "
        f"with a classmate.\n\n"
        f"5. QUICK QUIZ\n{question}\n"
        f"Answer: {answer}\n\n"
        f"6. REVISION CHECKLIST\n"
        f"□ I can define the key term.\n"
        f"□ I can explain the main idea.\n"
        f"□ I can answer a question on this topic and explain my method.\n"
        f"Practice series item {seq + 1}." + FOOTER
    )


def make_post_media(level, item, seq, phase, message):
    """Create a fresh topic poster and complete PDF pack for every scheduled post."""
    title, explanation, question, answer = item
    poster_path = "daily_learning_poster.png"
    pdf_path = "daily_learning_pack.pdf"

    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular = ImageFont.truetype(regular_path, 34)
    bold = ImageFont.truetype(bold_path, 48)
    image = Image.new("RGB", (1080, 1350), "#10233f")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((42, 42, 1038, 1308), radius=38, fill="#f5f8ff")
    draw.rounded_rectangle((42, 42, 1038, 315), radius=38, fill="#174a78")
    draw.text((82, 92), "STUDENTS PREDICTIONS", font=bold, fill="white")
    draw.text((82, 158), "& REVISIONS", font=bold, fill="white")
    draw.text((82, 245), f"{level.upper()} • DAILY LEARNING", font=regular, fill="#dcecff")

    y = 365
    draw.text((82, y), title[:38], font=bold, fill="#174a78")
    y += 92
    draw.text((82, y), "KEY NOTES", font=bold, fill="#174a78")
    y += 68
    for line in textwrap.wrap(explanation, width=43)[:5]:
        draw.text((82, y), line, font=regular, fill="#26364d")
        y += 48

    y += 28
    draw.rounded_rectangle((75, y, 1005, y + 360), radius=26, fill="#e2efff")
    draw.text((110, y + 30), "WORKED QUESTION", font=bold, fill="#174a78")
    qy = y + 100
    for line in textwrap.wrap("Question: " + question, width=43)[:3]:
        draw.text((110, qy), line, font=regular, fill="#172b4d")
        qy += 48
    qy += 12
    draw.text((110, qy), "ANSWER", font=bold, fill="#174a78")
    qy += 62
    for line in textwrap.wrap(answer, width=43)[:2]:
        draw.text((110, qy), line, font=regular, fill="#172b4d")
        qy += 46
    draw.text((82, 1240), "Learn • Practise • Improve  |  t.me/KKKCP254",
              font=regular, fill="#174a78")
    image.save(poster_path, "PNG")

    if "DejaVuLearning" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("DejaVuLearning", regular_path))
    pdf_style = ParagraphStyle(
        name="DailyPackBody", fontName="DejaVuLearning", fontSize=9.5,
        leading=14, textColor=colors.HexColor("#172b4d"), spaceAfter=8
    )
    story = [
        Paragraph(f"<b>{level} — {title}</b>", styles_for_daily_pack()["Title"]),
        Paragraph("Complete daily learning and revision pack", pdf_style),
        Spacer(1, 5*mm),
        Preformatted(message.encode("cp1252", errors="replace").decode("cp1252"), ParagraphStyle(
            name="DailyPackText", fontName="DejaVuLearning", fontSize=8.5,
            leading=12, textColor=colors.HexColor("#172b4d"), splitLongWords=1
        ))
    ]
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=17*mm,
                            leftMargin=17*mm, topMargin=16*mm, bottomMargin=16*mm)
    doc.build(story)
    return poster_path, pdf_path


def styles_for_daily_pack():
    pack_styles = getSampleStyleSheet()
    if "DailyPackTitle" not in pack_styles:
        pack_styles.add(ParagraphStyle(
            name="DailyPackTitle", parent=pack_styles["Title"],
            fontName="DejaVuLearning", alignment=TA_CENTER,
            textColor=colors.HexColor("#174a78"), spaceAfter=12
        ))
    return {"Title": pack_styles["DailyPackTitle"]}


def send_post_bundle(level, media_item, seq, phase, message):
    """Every run sends a topic poster, a PDF pack, and the full text lesson."""
    poster, pdf = make_post_media(level, media_item, seq, phase, message)
    telegram_upload(
        "sendPhoto", poster, "photo",
        f"{level} poster: {media_item[0]} | Daily learning series"
    )
    print(f"Poster uploaded for {level}: {media_item[0]}")
    telegram_upload(
        "sendDocument", pdf, "document",
        f"{level} PDF notes, worked question and revision activity: {media_item[0]}"
    )
    print(f"PDF uploaded for {level}: {media_item[0]}")
    send_message(message)
    print(f"Text lesson sent for {level}: {media_item[0]}")


def generate_ai_lesson(level, item, seq, phase):
    """Generate an original, detailed lesson with the OpenAI Responses API."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("OPENAI_API_KEY is not set; using the existing prepared lesson bank.")
        return None

    title, explanation, question, answer = item
    phase_name = "learning notes" if phase == 0 else "revision notes"
    prompt = (
        "Create a high-quality, original Kenyan school learning post. "
        "Return ONLY valid JSON with exactly these string fields: "
        "title, explanation, question, answer, lesson_text. "
        "The lesson_text must be detailed, clearly sectioned, and suitable "
        "for a Telegram post and a printable PDF. Include definitions, "
        "step-by-step explanations, important points, at least one fully "
        "worked example with reasoning, learner practice, and a short quiz "
        "with answers. Use correct age-appropriate language and the Kenyan "
        "CBC/CBE or KCSE context where relevant. Never claim questions are "
        "leaked, guaranteed, or official predictions. Do not invent facts; "
        "if a topic is uncertain, state the limitation. Keep content safe "
        "for school learners. Do not request personal information. "
        "For Playgroup to PP2, make activities simple and adult-supervised. "
        "Avoid repeating generic filler. "
        f"Class: {level}. Post type: {phase_name}. "
        f"Topic seed: {title}. Existing curriculum hint: {explanation}. "
        f"Example question seed: {question}. Reference answer: {answer}. "
        f"Sequence number for variety: {seq + 1}. "
        "The JSON title should be concise; explanation should be 1-3 "
        "sentences; question and answer should match the worked example. "
        "The lesson_text should not include contact details or channel links."
    )
    payload = {
        "model": os.environ.get("OPENAI_MODEL", "gpt-6.2-sol"),
        "input": [
            {"role": "system", "content": "You are a careful, encouraging Kenyan school tutor. Produce accurate, original educational material."},
            {"role": "user", "content": prompt}
        ],
        "max_output_tokens": 1800
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            result = json.load(response)
        output_text = result.get("output_text", "")
        if not output_text:
            parts = []
            for output in result.get("output", []):
                for part in output.get("content", []):
                    if part.get("type") == "output_text":
                        parts.append(part.get("text", ""))
            output_text = "\n".join(parts)
        generated = json.loads(output_text)
        ai_title = str(generated["title"]).strip()[:100]
        ai_explanation = str(generated["explanation"]).strip()
        ai_question = str(generated["question"]).strip()
        ai_answer = str(generated["answer"]).strip()
        lesson_text = str(generated["lesson_text"]).strip()
        if not all((ai_title, ai_explanation, ai_question, ai_answer, lesson_text)):
            raise ValueError("AI response contained an empty required field")
        media_item = (ai_title, ai_explanation, ai_question, ai_answer)
        message = f"📘 {level} — {phase_name.upper()}\nTopic: {ai_title}\n\n{lesson_text}" + FOOTER
        return message, media_item
    except Exception as exc:
        print(f"AI lesson generation failed; using prepared lesson bank: {type(exc).__name__}: {exc}")
        return None


def main():
    now = dt.datetime.now(EAT)
    mins = now.hour * 60 + now.minute
    slot = mins // 30  # 0..47: one slot every 30 minutes, 24 hours a day
    # GitHub scheduled jobs can start late. Use the current EAT slot and
    # rely on last_slot plus the content hash to prevent duplicate deliveries.
    manual_test = os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch"

    state = load_state()
    today = now.date().isoformat()

    # A manual Run workflow is a genuine delivery test. It uses a separate
    # rotating class pointer and does not consume or mark a scheduled time slot.
    if manual_test:
        level_index = int(state.get("manual_level_index", 0)) % len(LEVELS)
        phase = 0
    else:
        if state.get("last_date") == today and slot <= state.get("last_slot", -1):
            print(f"Slot {slot + 1} already processed; no duplicate sent.")
            return
        level_index = slot % len(LEVELS)
        phase = (slot // len(LEVELS)) % 2  # alternates learning / revision

    # On the very first successful run, deliver the poster first, then the PDF.
    if state.get("first_media_stage", "pending") != "complete":
        send_first_run_media(state)

    level, bank = LEVELS[level_index]
    seq = int(state.setdefault("level_index", {}).get(level, 0))
    item = bank[seq % len(bank)]
    generated = generate_ai_lesson(level, item, seq, phase)
    if generated:
        message, media_item = generated
    else:
        message = make_post(level, item, seq, phase)
        media_item = item
    digest = hashlib.sha256(message.encode("utf-8")).hexdigest()
    seen = set(state.setdefault("sent_hashes", []))
    if digest in seen:
        raise RuntimeError(f"Duplicate content blocked for {level}; add fresh content to its bank.")
    send_post_bundle(level, media_item, seq, phase, message)
    seen.add(digest)
    state["sent_hashes"] = list(seen)
    state["level_index"][level] = seq + 1
    if manual_test:
        state["manual_level_index"] = (level_index + 1) % len(LEVELS)
    else:
        state["last_date"] = today
        state["last_slot"] = slot
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    if manual_test:
        print(f"Manual delivery test sent: {level} learning post.")
    else:
        print(f"Sent slot {slot + 1}/48: {level} ({'learning' if phase == 0 else 'revision'}).")

if __name__ == "__main__":
    main()
