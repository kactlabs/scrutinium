import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage

# Load environment variables
load_dotenv()

def main():
    # Initialize the Gemini model
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.7
    )
    
    print("🤖 Gemini Chat Bot")
    print("Type 'quit' or 'exit' to end the conversation")
    print("-" * 50)
    
    # Chat loop
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            print("Goodbye! 👋")
            break
            
        if not user_input:
            continue
            
        try:
            # Create message and get response
            message = HumanMessage(content=user_input)
            response = llm.invoke([message])
            
            print(f"\nGemini: {response.content}")
            
        except Exception as e:
            print(f"Error: {e}")
            print("Please check your API key and internet connection.")

if __name__ == "__main__":
    main()