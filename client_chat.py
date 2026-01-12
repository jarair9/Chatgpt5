import requests
import sys

API_URL = "http://127.0.0.1:5000"

class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def chat():
    print(f"\n{Colors.BOLD}--- Claila API Chat Client ---{Colors.RESET}")
    print(f"Connecting to: {API_URL}\n")
    print("Type 'exit' or 'quit' to close.\n")

    system_prompt = input(f"{Colors.BLUE}System Prompt (optional, press Enter to skip): {Colors.RESET}").strip()
    
    while True:
        try:
            user_input = input(f"\n{Colors.GREEN}You: {Colors.RESET}")
            if user_input.lower() in ['exit', 'quit']:
                print("\nGoodbye!")
                break
            
            if not user_input.strip():
                continue
                
            payload = {"message": user_input}
            if system_prompt:
                payload["system_prompt"] = system_prompt
                
            print("Thinking...", end="\r")
            
            try:
                response = requests.post(API_URL, json=payload, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    print(f"\r{Colors.BLUE}AI: {Colors.RESET}{data.get('response')}")
                    # Debug: print(f"Raw: {data}")
                else:
                    print(f"\r{Colors.BOLD}Error {response.status_code}:{Colors.RESET} {response.text}")
                    
            except requests.exceptions.Timeout:
                print(f"\r{Colors.BOLD}Error:{Colors.RESET} Request timed out.")
            except Exception as e:
                print(f"\r{Colors.BOLD}Error:{Colors.RESET} {str(e)}")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    chat()
