import requests  # Used for HTTP requests to Ollama and as agent API client
from backend.core.context_manager import ContextManager

# Query Ollama LLM with a prompt and model
# Returns the generated response as a string
def query_ollama(prompt, model="gemma3:4b"):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",  # Ollama API endpoint
            json={
                "model": model,  # Model name
                "prompt": prompt,  # User/system prompt
                "stream": False  # No streaming, get full response
            },
            timeout=10
        )
        return response.json()["response"]  # Extract response text
    except Exception as e:
        print(f"Ollama connection failed: {e}")
        return None

# Query Ollama LLM with a prompt, context, and model
# Returns the generated response as a string
def query_ollama_with_context(prompt, context="", model="gemma3:4b"):
    try:
        full_prompt = f"""
Previous conversation context:
{context}

Current request:
{prompt}

Please provide a response that considers the conversation history above.
"""
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": full_prompt,
                "stream": False
            },
            timeout=10
        )
        return response.json()["response"]
    except Exception as e:
        print(f"Ollama connection failed: {e}")
        return None

def get_fallback_healthcare_response(symptom):
    """Provide fallback healthcare advice when Ollama is not available"""
    symptom_lower = symptom.lower()
    
    if any(word in symptom_lower for word in ['headache', 'head', 'migraine']):
        return """Based on your headache symptoms, here are some general recommendations:

**Immediate Relief:**
- Rest in a quiet, dark room
- Stay hydrated (drink plenty of water)
- Try over-the-counter pain relievers like acetaminophen or ibuprofen
- Apply a cold or warm compress to your forehead

**When to Seek Medical Attention:**
- Severe headache that comes on suddenly
- Headache with fever and stiff neck
- Headache after head injury
- Headache with confusion or vision changes

**Prevention Tips:**
- Maintain regular sleep patterns
- Manage stress through relaxation techniques
- Avoid known triggers (certain foods, bright lights, loud noises)

**Important Disclaimer:** This is general advice only. If your headache is severe, persistent, or accompanied by other concerning symptoms, please consult a healthcare professional immediately."""
    
    elif any(word in symptom_lower for word in ['fever', 'temperature', 'hot']):
        return """For fever management, here are some recommendations:

**Home Care:**
- Rest and stay hydrated
- Take acetaminophen or ibuprofen as directed
- Use cool compresses or take a lukewarm bath
- Monitor your temperature regularly

**When to Seek Medical Attention:**
- Fever above 103°F (39.4°C)
- Fever lasting more than 3 days
- Fever with severe headache, rash, or confusion
- Fever in infants under 3 months

**Important Disclaimer:** This is general advice only. If your fever is high or persistent, please consult a healthcare professional."""
    
    elif any(word in symptom_lower for word in ['cough', 'cold', 'sore throat']):
        return """For respiratory symptoms, here are some recommendations:

**Home Care:**
- Rest and stay hydrated
- Use honey for cough relief (adults and children over 1 year)
- Gargle with warm salt water for sore throat
- Use a humidifier to add moisture to the air

**When to Seek Medical Attention:**
- Difficulty breathing or shortness of breath
- Cough with blood or colored mucus
- Symptoms lasting more than 10 days
- High fever with respiratory symptoms

**Important Disclaimer:** This is general advice only. If you have difficulty breathing or severe symptoms, please consult a healthcare professional immediately."""
    
    else:
        return f"""Thank you for sharing your symptoms: "{symptom}"

**General Health Recommendations:**
- Stay hydrated and get adequate rest
- Maintain a balanced diet
- Exercise regularly as tolerated
- Monitor your symptoms and note any changes

**When to Seek Medical Attention:**
- Severe or worsening symptoms
- Symptoms that interfere with daily activities
- New or unusual symptoms
- Symptoms lasting longer than expected

**Important Disclaimer:** I am an AI assistant and cannot provide medical diagnoses. This information is for educational purposes only and should not replace professional medical advice. Please consult a qualified healthcare provider for proper evaluation and treatment of your symptoms.

If you have specific concerns about your health, please provide more details about your symptoms, and I can offer more targeted general advice."""

# Suggest a healthcare plan based on a symptom
# Returns a dictionary with the advice string
def suggest_advice(symptom, context_list=None):
    if context_list is None:
        context_list = []
    cm = ContextManager()
    context_str = cm.format_context_for_agent(context_list)
    prompt_str = f"You are a healthcare assistant. Based on the user's symptom and conversation history, provide advice.\n\n{context_str}\nCurrent Symptom: {symptom}\nPlease provide a general answer and suggest next steps, considering any previous discussions."
    output = query_ollama(prompt_str, model="gemma3:4b")
    
    # If Ollama fails, use fallback response
    if output is None:
        output = get_fallback_healthcare_response(symptom)
    
    return {
        "success": True,
        "data": output,
        "agent": "healthcare_agent",
        "command": "suggest_advice"
    }

# Standard API entry point for this agent
# Handles all API calls for this agent
def run_command_with_context(command, params, context_list=None):
    if context_list is None:
        context_list = []
    if command == "suggest_advice":
        return suggest_advice(params.get("symptom", ""), context_list)
    else:
        return {
            "success": False,
            "error": f"Unknown command: {command}",
            "agent": "healthcare_agent",
            "command": command
        }

def run_command(command, params):
    return run_command_with_context(command, params, [])
