# 🧭 END-TO-END FLOW
## Guest Interactions + AI Actions + Hotel Operations
*(Updated with General Information Handling)*

---

## 1) COMPLETE GUEST JOURNEY (STEP BY STEP)

### Step 0 — Entry Point
* **Guest action:** * Scans QR in room
  * Opens chat from welcome email
  * Clicks “Guest Services” link
* **Agent actions:** * Greets guest
  * Detects language
  * Loads guest context (name, room, dates)
* **Agent message example:** > “Hello Mr. Menzel! Welcome to Itz’ana Resort. I’m here to help with anything you need. How may I assist you today?”

### Step 1 — Understand the request
* **Guest action:** Writes request in natural language.
  * *Examples:* * “Can I get extra towels?”
    * “The AC is not cooling”
    * “Book dinner for tonight”
    * “What time does the spa open?”
* **Agent internal actions:** * Detect intent
  * Classify category
  * Pull guest context

---

## 💡 IF THE REQUEST IS PURE INFORMATION
When the guest is only asking for hotel information, the Agent must:
1. Recognize that no operational task is required.
2. Answer directly and immediately.
3. Use the official Itz’ana knowledge base.
4. Provide concise, clear responses.
5. Offer help with reservations or actions.

### Examples of “General Information” requests:
* Spa hours
* Pool hours
* Restaurant hours
* Restaurant menus
* Available activities
* Transportation options
* Wi-Fi information
* Hotel policies
* Directions inside the property

### AGENT RULES FOR INFORMATION REQUESTS
If the `request type = INFORMATION`:
* **Do NOT** create a task.
* Answer immediately using verified hotel data.
* Offer next step if applicable.

### Example Responses
* **Guest:** “What are the spa hours?”
  * **Agent:** “The Itz’ana Spa is open daily from 9:00 AM to 7:00 PM. Would you like me to book a treatment for you?”
* **Guest:** “What restaurants are open tonight?”
  * **Agent:** “Tonight you can enjoy:<br>– The Great House Restaurant: 6:00 PM – 10:00 PM<br>– Biblio Bar & Lounge: 5:00 PM – 11:00 PM<br>Would you like me to reserve a table for you?”
* **Guest:** “Do you have a pool?”
  * **Agent:** “Yes! We have two pools available for guests:<br>– Main Pool: 7:00 AM – 9:00 PM<br>– Marina Pool: 8:00 AM – 8:00 PM<br>Towels are provided at both locations.”

### WHEN INFORMATION BECOMES A TASK
If during the conversation the guest asks to **ACT** on the information, the Agent converts it into a task.
* *Example:* Guest asks for hours → **INFORMATION**
* *Example:* Guest says “Book a table” → **TASK CREATION**

---

## 🛠️ BACK TO OPERATIONAL FLOW
If the request is **NOT** general information:

### Step 2 — Clarify only what is missing
* **Agent logic:** * Checks required fields for that request type.
  * Asks only necessary questions.
* *Examples:*
  * **Towels:** quantity + preferred time
  * **Restaurant:** time + number of guests
  * **Maintenance:** urgency + best time to enter room

### Step 3 — Confirm details
* **Guest action:** Provides missing info.
* **Agent action:** Repeats summary for confirmation.
* *Example:* > “Great, you’d like 4 extra towels delivered to room 204 at 3:00 PM. Correct?”

### Step 4 — Create Task + Send to Team
* **Agent internal actions:**
  * Creates structured task
  * Assigns priority
  * Routes to correct department
  * Sends notification to operational team
* **Agent confirmation to guest:** > “Done! I’ve sent your request to our Housekeeping team. You will receive the towels within the next 15 minutes.”

---

## 🔁 Step 5 — OPERATIONAL TEAM TASK MANAGEMENT

### 5A – Team Receives the Task
Possible channels:
* Opera / PMS task list
* Slack
* WhatsApp
* Monday.com
* Email ticket

### 5B – TEAM UPDATES TASK STATUS
Operational staff must be able to mark the task as:

| Status | Meaning |
| :--- | :--- |
| **NEW** | Just created |
| **IN PROGRESS** | Team is working on it |
| **ON THE WAY** | Service en route |
| **COMPLETED** | Request fulfilled |
| **STAND BY** | Waiting on guest |
| **ESCALATED** | Needs supervisor |
| **UNABLE TO COMPLETE** | Issue blocked |

#### Example updates:
* *“IN PROGRESS – technician assigned”*
* *“ON THE WAY – towels leaving laundry”*
* *“STAND BY – guest not in room”*
* *“COMPLETED – delivered at 14:12”*

### 5C – AI AGENT FEEDBACK LOOP
Agent notifies guest when status changes to:
* ON THE WAY
* COMPLETED
* STAND BY
* ESCALATED

### Step 6 — Follow-up & Closure
* **Agent confirms completion and asks:** > “Is there anything else I can assist you with today?”

---

## 2) KEY ACTIONS THE AI AGENT PERFORMS

### A) Guest-Facing
* Greet and identify
* Provide information instantly
* Understand intent
* Ask minimal questions
* Confirm expectations
* Provide ETA
* Give updates
* Close loop

### B) Operational Intelligence
* Intent classification
* Information vs Task decision
* Priority assignment
* Task creation
* Department routing
* Escalation rules
* Status monitoring

---

## 3) OPERATIONAL TASK TYPES + EXAMPLES

### A. HOUSEKEEPING
* **Guest:** “Extra towels please”
* **Flow:** Task created → Team changes to `IN PROGRESS` → Team changes to `COMPLETED`
* **Agent message:** “Your towels have been delivered.”

### B. MAINTENANCE
* **Guest:** “AC not working”
* **Flow:** Task created (High Priority) → Technician dispatched → Status updates → Completion confirmation

### C. F&B
* **Guest:** “I want room service”
* **Flow:** Order details collected → Task to kitchen → `ON THE WAY` → `COMPLETED`

### D. CONCIERGE
* **Guest:** “Book snorkeling”
* **Flow:** Task to concierge → Booking confirmed → Agent informs guest

### E. FRONT DESK
* **Guest:** “Late checkout?”
* **Flow:** Task to FD → Availability checked → Confirmation to guest

---

## 4) SLA & ESCALATION MATRIX

| Request Type | SLA |
| :--- | :--- |
| **Information** | Immediate |
| **Housekeeping** | 15 min |
| **Maintenance** | 30 min |
| **Room Service** | 30–45 min |
| **Concierge** | 10 min reply |

---

## 5) DAILY OPERATIONAL BENEFITS
* Instant answers for general info
* Structured tasks for operations
* Full visibility
* Measurable service quality
* No lost requests

### 🏆 FINAL RESULT
Three clear modes:
1. **Information** → Answer instantly
2. **Request** → Create task + notify team
3. *All within one seamless guest experience.*

---

### Next Steps & Templates Available:
* Create the exact knowledge base template (hours, menus, services) in JSON or Markdown for the chatbot.
* Build the routing matrix per department at Itz’ana.
* Design the status update screens for the team.