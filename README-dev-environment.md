# Development Environment Guide

### Understanding GitHub Copilot in This Lab

This Codespace has been configured with a *student-safe* version of GitHub Copilot.  
This is intentional and designed to support your learning in the **Cloud Development** module.

---

## 🎯 Why Copilot Is Configured This Way

In this module, you are assessed on your ability to:

- Understand and apply cloud-native development principles  
- Design and justify API structures  
- Implement cloud services, CI/CD pipelines, security patterns, etc.  
- Debug, reason about, and improve your own code  

These skills cannot be developed by simply accepting AI-generated solutions.  
For that reason:

### **Copilot Chat is enabled**

You can ask questions such as:

- “Why am I getting a 422 error?”  
- “What does this CI/CD step do?”  
- “How should I structure a cloud-native API project?”  
- “What does this error message mean?”  

Copilot Chat will *explain concepts*, *guide you*, and *help you reflect*,  
without generating complete assignment solutions.

### **Copilot Autocomplete (inline code suggestions) is disabled**

This prevents situations where Copilot writes large portions of your assignment for you.

You will still type your own code, reason through your design choices, and build the solution yourself.

---

## 🧭 What Copilot *Will* Do

Copilot will:

- Give high-level explanations  
- Offer conceptual guidance
- Suggest debugging steps  
- Comment on your code when you paste it into chat  
- Provide pseudocode or partial patterns (never full implementations)  
- Encourage good practice (testing, structure, documentation, security)  

This helps you understand the *why* and *how* behind cloud development.

---

## 🚫 What Copilot *Will Not* Do

To protect academic integrity—and to help you genuinely learn—it will **not**:

- Produce full, copy-pasteable solutions  
- Generate complete FastAPI routes
- Write working SQL schemas or ORM models for you  
- Produce a full deployment pipeline or infrastructure config  
- Complete assignment tasks on your behalf  

If you ask for a full solution, Copilot will redirect you toward understanding and solving the problem yourself.

---

## 📘 Why This Matters for Your Learning

The assignment and module learning outcomes require you to:

- **Explain, justify, and critique** your decisions  
- Understand cloud-native architecture, APIs, SDLC, and reliability principles  
- Build and explain how your own project works  
- Debug cloud-based applications independently  

If an AI wrote large parts of your project, you would struggle to:

- Document what it does  
- Justify your design decisions  
- Debug or extend it  
- Pass the module’s assessment  

This configuration ensures you build **real, employable development skills**.

---

## 🛠 How to Use Copilot Effectively

Here are examples of good questions to ask:

❓ *“What does this error mean?”*  
❓ *“Why would a POST request return 500?”*  
❓ *“What is the difference between PUT and PATCH?”*  
❓ *“How does JWT authentication typically work?”*  
❓ *“How should I structure my project folders for a clean FastAPI application?”*  
❓ *“What should a CI pipeline include for a Python API?”*  

Avoid asking Copilot to:

- Write an endpoint
- Build your database schema
- Solve your entire task  
- Write your report  

Because it is intentionally prevented from doing these things.

---

## 🧑‍💻 Your Development Environment Supports You — But You Are the Developer

You are expected to:

- Understand your own code  
- Justify your design choices  
- Demonstrate cloud-native reasoning  
- Describe how your API works  
- Debug and test your application  
- Meet SLA, security, and reliability expectations  

Copilot is here to help you **learn**, not to do the work for you.

---

## 🤖 Custom Agents for Specialised Help

In addition to Copilot Chat, this workspace includes **custom agents** that provide specialised guidance for different aspects of cloud development.

Each agent is tailored to help you learn and implement specific technologies while maintaining the same academic integrity principles.

### Available Agents

| Agent | Purpose | Good Questions |
|-------|---------|----------------|
| **FastAPI Agent** | REST API design, routing, validation, error handling, project structure | "Why am I getting a 422 error?" / "How should I structure my FastAPI project?" |
| **Database Agent** | SQL concepts, schema design, queries across multiple database engines | "How should my schema relate these entities?" / "Why does my query fail?" |
| **Testing Agent** | Unit/integration/API testing, pytest, test design patterns, test automation | "How should I test this endpoint?" / "What test cases should I write?" |
| **CI/CD Agent** | GitHub Actions workflows, pipeline design, automation, deployment gates | "How should my CI pipeline be structured?" / "Why did my workflow fail?" |
| **Git Agent** | Source control, branching, merging, conflicts, GitHub workflows | "How do I resolve this merge conflict?" / "How should I structure my commits?" |
| **Deployment Agent** | Deployment strategies, environment configuration, rollbacks, SLAs | "How does blue–green deployment work?" / "What environment variables do I need?" |
| **Postman Agent** | API testing tools, request building, environment management, test scripts | "How do I create a Postman collection?" / "How do I test authentication?" |

### How to Use Agents

Ask a custom agent a question directly in **Copilot Chat**. The agent will:

- Explain relevant concepts and principles
- Suggest approaches and design patterns
- Help you debug your own work
- Ask clarifying questions about your implementation
- Provide **pseudocode and partial examples** (never complete solutions)

**Example workflow:**

1. You have a FastAPI endpoint that's not working → Ask the **FastAPI Agent** to help you debug
2. Your database queries are complex → Ask the **Database Agent** about SQL structure
3. Your tests are failing → Ask the **Testing Agent** about test design
4. Your CI pipeline has an error → Ask the **CI/CD Agent** to help interpret the logs

---

## 📩 If You Need More Help

Your lecturer, tutor, and peers are part of your support network.  
Copilot and the custom agents are tools to help you **learn and reason** independently.

Use them **wisely**, **ethically**, and **actively** as part of your learning.

---
