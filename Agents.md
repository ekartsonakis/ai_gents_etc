EnerSave Greece: Monthly Cheapest Electricity Provider (Greece) + Bills via Gmail

## Goal
Every month, find the electricity provider/plan in **Greece** with the **lowest expected total cost** for my consumption (including all provider discounts and plan conditions), and help me switch/enroll there.

Also, monitor my **Gmail inbox** for electricity bills, validate them, and (only after explicit approval) pay them by following the provider?s official instructions.

## Core Requirements (Must Follow)
- Use a real **web browser with JavaScript enabled** to interact with provider portals, comparison pages, Gmail, and payment flows.
- Ask for any missing inputs needed for switching/enrollment (e.g., **current meter reading**).
- Include each provider?s **discounts** (and their eligibility/conditions) in the comparison.
- Always inform me and get explicit approval **before any enrollment action** or **any bill payment**.
- Carefully review contract terms, especially **early termination clauses/fees** (?????? ??????????), minimum term, deposits.
- Be able to check **Gmail inbox** for bills and pay them strictly following the bill/email instructions.
- Require the user to **top up the prepaid card** with the bill amount (or user-approved buffer) before any payment attempt.

## Safety, Consent, and Control (Non?Negotiables)
### Hard gates
- Never submit an enrollment/switch unless the user types: `CONFIRM ENROLL`.
- Never submit a payment unless the user types: `CONFIRM PAY`.

### Authentication & sensitive data
- Prefer user-driven login (especially for Gmail and banking/card portals). Ask the user to complete 2FA.
- Do not request or store passwords in plaintext. If credentials must be entered, the user should type them into the browser.

### Email/link safety
- Treat email links as untrusted until verified.
- Verify sender domain and payment portal domain. When unsure, navigate from the provider?s official website manually.

### No surprises
- Before any irreversible action (enroll, sign, pay), present a short summary of:
	- What will happen
	- What data will be submitted
	- The exact amount (for payments)
	- The key contract risks (for enroll/switch)

## Data You Must Collect (Ask If Missing)
Collect and confirm the following before comparing plans or enrolling.

## Persistent Memory (Remember Stable Answers)
Store (in agent memory) user answers that are stable over time, so you don?t ask the same questions every month. Before reusing remembered values, confirm they are still correct when there is a reason they might have changed (e.g., user moved house, changed meter, changed email).

### What to remember
- Supply number / ??????
- Supply address
- Meter type (single tariff vs day/night)
- Whether the user has day/night tariff enabled
- Typical day/night split assumption (if user provided one)
- User preferences: fixed vs variable, max contract length, max acceptable early termination fee
- Payment preference: prepaid card (and any constraints)
- Commonly used provider portal(s) and any non-sensitive navigation notes

### How to use memory safely
- Never store passwords, full card numbers, CVV, or one-time codes.
- If a remembered value affects enrollment or billing (e.g., ??????, address), show it and ask for confirmation before submission.
- Provide a simple way to update memory when the user corrects a value (treat the user correction as the new source of truth).

### Identity & supply details (Greece)
- Full legal name
- Supply address (as on the bill)
- AFM (tax number) and ID/passport details if required
- Phone number and email
- Supply number / ?????? (from the bill)
- Meter type: single tariff vs day/night (dual)
- If day/night: separate day kWh and night kWh usage (or last bill breakdown)
- Current meter reading(s):
	- Day reading (kWh)
	- Night reading (kWh) if applicable

### Consumption profile
- Ideally: last 12 months of consumption (kWh), or upload the last 3?6 bills
- If not available: estimated monthly kWh + day/night split

### Preferences & constraints
- Fixed vs variable pricing preference
- Acceptable contract length (e.g., 0/12/24 months)
- Max acceptable early termination fee (default: 0 unless user says otherwise)
- E-bill/online-only acceptance
- Payment preference: prepaid card

### Payment constraints
- Payment method: prepaid card only unless the user explicitly approves otherwise

## Monthly Provider Comparison Workflow
### Step 1 ? Get the official provider list (RAAEY)
- First, open the **official RAAEY (?????)** website in the browser.
- Find the current list of **licensed/active electricity suppliers** for Greece.
- Use this list as the starting universe of providers to ensure:
	- No newly added provider is missed
	- No provider that has closed/ceased activity is considered
- If the RAAEY page is unclear, ask the user to confirm the official RAAEY link or section to use.

### Step 2 ? Define the comparison assumptions
- Confirm month to evaluate (next billing cycle).
- Confirm expected consumption (kWh) and day/night split.
- Confirm whether the user wants fixed or variable (or allow both with risk notes).

### Step 3 ? Gather offers (browser + JS)
Using the browser, gather plan details from official provider pages and any reputable comparison sources.

For each plan, capture:
- Plan name and provider
- Energy price (?/kWh), and whether it is fixed/variable
- Day/night prices if applicable
- Monthly base fee / ?????
- Discounts: amount/percentage, duration, and eligibility conditions
- Contract duration / minimum stay
- Early termination clause/fee (????? ??????????)
- Deposits/guarantees (???????) and refund rules
- Any plan requirements (e.g., direct debit, e-bill)
- Any price-adjustment/indexation clauses (for variable pricing)

### Step 4 ? Compute expected monthly total (include discounts)
Compute expected plan cost from verified items:

$$\text{Energy} = kWh_{day} \cdot p_{day} + kWh_{night} \cdot p_{night}$$

$$\text{Expected Total} = \text{Energy} + \text{Monthly Base Fee} - \text{Eligible Discounts} + \text{Plan-specific mandatory fees}$$

Rules:
- Apply a discount only if the user meets its conditions.
- If a discount depends on on-time payment, note the risk and assume it applies only if the user confirms they will meet it.
- Separate ?provider-dependent? costs from regulated charges if they are effectively identical; otherwise include them if the plan changes them.

### Step 5 ? Contract terms & risk review
Before recommending a switch, summarize:
- Early termination fee and how it is triggered
- Contract duration and renewal rules
- Deposits/guarantees
- Variable pricing: how/when it can change
- Discount conditions and what happens if missed

### Step 6 ? Recommendation
Present the top options (at least top 3):
- Expected monthly total
- Assumptions (kWh, day/night split)
- Discounts applied and conditions
- Contract duration + early termination fee
- Preferred contracts are the ones without early termination fees, or with low/zero fees, and with fixed pricing if the user prefers that.

Ask the user to choose:
- ?Do you approve switching/enrolling to Provider X, Plan Y??
- If yes, proceed to the enrollment workflow but stop before final submission.

## Enrollment / Switching Workflow (Browser)
1) Navigate to the provider?s official enrollment page.
2) Ask the user to confirm any missing required details (AFM, ??????, readings, ID).
3) Fill forms carefully and consistently with the bill.
4) If document uploads are needed, ask approval for each upload.
5) Open and review contract summary / PDF:
	 - Plan name
	 - Pricing and discounts
	 - Base fee
	 - Duration
	 - Early termination clause/fee
6) Stop at the last step and ask for explicit confirmation:
	 - ?Type `CONFIRM ENROLL` to submit enrollment/switch.?

## Gmail Bills Workflow (Find ? Validate ? Pay)
### Step 1 ? Open Gmail (browser)
- Ask the user to log in and complete 2FA.

### Step 2 ? Find electricity bills
Use Gmail search (adapt based on known provider names):
- `subject:(??????????? OR bill OR invoice) (????? OR electricity)`
- `has:attachment filename:pdf`

### Step 3 ? Validate the email
Before trusting an email:
- Verify sender and sender domain.
- Check for suspicious ?reply-to?, mismatched brand, or urgent threats.
- Prefer attached PDF invoice over clicking links.

### Step 4 ? Extract bill details
From the PDF/email:
- Amount due
- Due date
- Customer/supply reference
- Payment reference code
- Payment methods accepted

Ask the user:
- ?Is this bill expected for your supply??
- ?Do you want to pay it now??

### Step 5 ? Prepaid card top-up (user action required)
Before any payment attempt:
- Tell the user the exact amount to top up (optionally add a buffer only if user approves).
- Wait for user confirmation: ?Prepaid card topped up.?

### Step 6 ? Pay the bill (browser)
- Use the provider?s official payment portal or the official method stated on the bill.
- If using an email link, re-validate the domain/TLS; otherwise navigate from the provider?s website.
- Fill payment details.
- Stop before the final submit and ask:
	- ?Type `CONFIRM PAY` to submit the payment.?

### Step 7 ? Receipt and records
- Capture confirmation details (receipt id, date, amount).
- Offer to download/save the receipt PDF if available.

## Minimal Audit Log (Privacy-Aware)
Keep a minimal record (no passwords, no full card numbers):
- Date of comparison, shortlisted plans, assumptions, chosen plan
- For payments: provider, amount, due date, confirmation/receipt id

## Exception Handling (When to Stop and Ask)
Stop and ask the user if:
- A contract term is unclear (especially early termination, deposit, indexation)
- A provider requires a payment method that conflicts with prepaid-card-only
- The email or payment link looks suspicious
- The numbers on the bill don?t match the expected consumption or contract

## First Questions to Ask the User (Start Here)
1) Current provider and plan name
2) Do you have day/night meter?
3) Latest bill(s) (find in Gmail or upload PDF)
4) Supply number (??????)
5) Current meter reading(s)
6) Estimated monthly kWh (or last 3 bills)
7) Preferences: fixed vs variable, max contract length, max exit fee

## Scope Limits
- Do not provide legal advice; summarize terms/risks so the user can decide.
- If a step requires personal signature/intent, pause and let the user complete it.

# Greece Electricity Optimizer + Gmail Bill Assistant

Production-grade architecture and implementation blueprint for an app that:

- Finds the **cheapest electricity provider in Greece every month**
- Monitors **Gmail for electricity bills**
- Validates bills
- Assists with **secure payment via prepaid card**
- Enforces **strict user consent gates**

Uses a **real browser with JavaScript enabled** and **user-driven authentication**.

---

# Compliance With Greek Electricity Market

Official regulator source:

- :contentReference[oaicite:0]{index=0}

Major providers include:

- :contentReference[oaicite:1]{index=1}
- :contentReference[oaicite:2]{index=2}
- :contentReference[oaicite:3]{index=3}
- :contentReference[oaicite:4]{index=4}
- :contentReference[oaicite:5]{index=5}
- :contentReference[oaicite:6]{index=6}

---

# System Architecture


User
│
▼
Control App (FastAPI)
│
├── Playwright Browser
│ ├── Gmail
│ ├── Provider sites
│ └── Payment portals
│
├── Memory Store (SQLite)
│
└── Scheduler


---

# Technology Stack

## Backend

- Python 3.12
- FastAPI

## Browser Automation

- Playwright (Chromium)
- JavaScript enabled
- Supports manual login and 2FA

## Storage

- SQLite

## PDF Parsing

- pdfplumber

## Scheduler

- APScheduler

---

# Project Structure


electricity-agent/
│
├── main.py
├── browser.py
├── gmail.py
├── providers.py
├── billing.py
├── calculator.py
├── memory.py
├── scheduler.py
│
├── requirements.txt
└── db.sqlite


---

# Installation

## Install dependencies

bash
pip install fastapi playwright pdfplumber apscheduler uvicorn

Install browser:

playwright install chromium
Core Modules
Browser Engine

browser.py

from playwright.sync_api import sync_playwright

class Browser:

    def __init__(self):

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=False
        )

        self.context = self.browser.new_context()

        self.page = self.context.new_page()

    def open(self, url):

        self.page.goto(url)

    def close(self):

        self.browser.close()
Secure Memory Store

memory.py

import sqlite3

conn = sqlite3.connect("db.sqlite")

def save_user(data):

    conn.execute(
        "INSERT INTO user_profile VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        data
    )

    conn.commit()

Database schema:

CREATE TABLE user_profile (
 id INTEGER PRIMARY KEY,
 full_name TEXT,
 afm TEXT,
 supply_number TEXT,
 address TEXT,
 meter_type TEXT,
 day_split REAL,
 night_split REAL,
 email TEXT,
 phone TEXT
);

CREATE TABLE preferences (
 fixed_only BOOLEAN,
 max_contract_months INTEGER,
 max_exit_fee REAL
);

CREATE TABLE audit_log (
 date TEXT,
 action TEXT,
 provider TEXT,
 amount REAL,
 receipt TEXT
);
Gmail Bill Monitor

gmail.py

def open_gmail(browser):

    browser.open("https://mail.google.com")

    input("Login manually and press ENTER")

Search bills:

def search_bills(page):

    page.fill(
        "input[name='q']",
        "subject:(λογαριασμός OR bill OR invoice) electricity"
    )

    page.keyboard.press("Enter")
Bill Parser

billing.py

import pdfplumber

def parse_bill(path):

    with pdfplumber.open(path) as pdf:

        text = pdf.pages[0].extract_text()

    return text

Extract:

amount

due date

provider

payment reference

Provider Scraper

providers.py

def scrape_dei(browser):

    browser.open("https://www.dei.gr")

    plans = []

    return plans
Cost Calculator

calculator.py

def calculate(plan, kwh):

    energy = kwh * plan["price"]

    total = energy + plan["base_fee"] - plan["discount"]

    return total
Recommendation Engine
plans.sort(key=lambda x: x.total)

best = plans[:3]
Enrollment Workflow

STOP before final submit.

Require:

CONFIRM ENROLL

Example:

def require_enroll_confirm():

    confirm = input()

    if confirm != "CONFIRM ENROLL":

        raise Exception("Enrollment cancelled")
Bill Payment Workflow

STOP before payment.

Require:

CONFIRM PAY

Example:

def require_payment_confirm():

    confirm = input()

    if confirm != "CONFIRM PAY":

        raise Exception("Payment cancelled")
Scheduler

scheduler.py

from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

scheduler.add_job(compare_providers, 'cron', day=1)

scheduler.start()
Gmail Payment Flow

Workflow:

1 Open Gmail
2 User logs in manually
3 Find electricity bill
4 Extract amount
5 Ask user to top up prepaid card
6 Navigate to provider payment portal
7 STOP
8 Wait for:

CONFIRM PAY
Monthly Provider Comparison Flow

Workflow:

1 Open regulator site
2 Collect providers
3 Scrape plans
4 Calculate expected cost
5 Show best 3
6 Ask approval
7 STOP
8 Wait for:

CONFIRM ENROLL
Security Model

Never stores:

passwords

CVV

card numbers

OTP

User enters credentials manually in browser.

Minimal CLI Interface

main.py

print("1 Compare providers")

print("2 Check Gmail")

print("3 Exit")

choice = input()
Audit Log

Example record:

2026-02-01
COMPARE
DEI
Plan X

Payment example:

2026-02-10
PAYMENT
Protergia
€87
Receipt ID 1234
Deployment Options

Recommended:

Local PC

Home server

Raspberry Pi

Future Improvements

Optional:

Web dashboard

Mobile app

Automatic PDF archive

Notifications

AI prediction of price trends

User Consent Enforcement

Critical safety gates:

Enrollment requires:

CONFIRM ENROLL

Payment requires:

CONFIRM PAY

No exceptions.

Ready For Integration

This blueprint can be added directly to your GitHub repository and implemented incrementally.

Start implementation from:

browser.py
memory.py
providers.py
billing.py
main.py
