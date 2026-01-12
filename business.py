

import os
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import pandas as pd
from typing import List, Dict
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

RESULTS_FOLDER = "results/"

class GenAIBenchmarkJudge:
    """
    A judge system for evaluating GenAI tool responses using Claude via LangChain.
    """
    
    def __init__(self, api_key: str = None, provider: str = None):
        """
        Initialize the judge with specified model provider.
        
        Args:
            api_key: API key for the chosen provider (not needed for Ollama)
            provider: Model provider ("anthropic", "gemini", "groq", or "ollama")
        """
        # Get default provider from environment if not specified
        if provider is None:
            provider = os.getenv("DEFAULT_PROVIDER", "gemini")
        
        self.provider = provider.lower()
        
        if self.provider == "anthropic":
            if api_key:
                os.environ["ANTHROPIC_API_KEY"] = api_key
            self.llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=0.3,
                max_tokens=4000
            )
        elif self.provider == "gemini":
            # Get API key from parameter or environment variables
            api_key_to_use = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if not api_key_to_use:
                raise ValueError("Gemini API key not found. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
            
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.3,
                max_output_tokens=4000,
                google_api_key=api_key_to_use
            )
        elif self.provider == "groq":
            if api_key:
                os.environ["GROQ_API_KEY"] = api_key
            self.llm = ChatGroq(
                model="llama-3.1-70b-versatile",
                temperature=0.3,
                max_tokens=4000
            )
        elif self.provider == "ollama":
            # Ollama runs locally, no API key needed
            model_name = os.getenv("OLLAMA_MODEL", "mistral:latest")
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            
            self.model_name = model_name  # Store model name for reference
            self.llm = ChatOllama(
                model=model_name,
                temperature=0.3,
                base_url=base_url
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}. Choose from 'anthropic', 'gemini', 'groq', or 'ollama'")
        
        # Define the evaluation prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert judge evaluating GenAI tool responses across multiple metrics.

Your task is to evaluate responses from various GenAI tools against these metrics:

1. Truthfulness (Factual correctness, Internal consistency, Resistance to hallucination)
2. Creativity (Novel framing or synthesis, Non-obvious insights, Original examples or analogies)
3. Coherence & Reasoning Quality (Logical flow, Step-by-step reasoning, Absence of contradictions)
4. Utility/Actionability (Practical usefulness, Clarity for decision-making, Transferability to real-world tasks)

For each tool's response, provide:
- A score out of 1000 for each metric (use full range 0-1000 for maximum precision, e.g., 862, 745, 923)
- Brief reasoning for each score
- An overall score (average of all metrics, also out of 1000)

Format your response as valid JSON with this structure:
{{
    "evaluations": [
        {{
            "tool": "ToolName",
            "truthfulness": {{"score": XXX, "reasoning": "..."}},
            "creativity": {{"score": XXX, "reasoning": "..."}},
            "coherence": {{"score": XXX, "reasoning": "..."}},
            "utility": {{"score": XXX, "reasoning": "..."}},
            "overall_score": XXX,
            "notes": "..."
        }}
    ],
    "winner": "ToolName",
    "winner_reasoning": "...",
    "ranking": ["Tool1", "Tool2", ...]
}}"""),
            ("human", """Question: {question}

Tool Responses:
{responses}

Please evaluate these responses according to the metrics defined above.""")
        ])
        
        # Create the chain
        self.chain = self.prompt_template | self.llm | StrOutputParser()
        
        # Create enhanced prompt template that includes judge's own answer
        self.enhanced_prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert judge evaluating GenAI tool responses across multiple metrics.

Your task has two parts:
1. First, provide your own answer to the question for reference only
2. Then evaluate only the provided tool responses (do NOT evaluate your own answer)

EVALUATION METRICS:
1. Truthfulness (Factual correctness, Internal consistency, Resistance to hallucination)
2. Creativity (Novel framing or synthesis, Non-obvious insights, Original examples or analogies)
3. Coherence & Reasoning Quality (Logical flow, Step-by-step reasoning, Absence of contradictions)
4. Utility/Actionability (Practical usefulness, Clarity for decision-making, Transferability to real-world tasks)

For each tool response (excluding your own), provide:
- A score out of 1000 for each metric (use full range 0-1000 for maximum precision, e.g., 862, 745, 923)
- Brief reasoning for each score
- An overall score (average of all metrics, also out of 1000)

IMPORTANT: 
- Do NOT include yourself in the evaluations or ranking. Only evaluate the provided tool responses.
- You MUST respond with valid JSON only. Do not include any text before or after the JSON.
- Do not use markdown code blocks or any formatting around the JSON.

Format your response as valid JSON with this EXACT structure:
{{
    "judge_answer": "Your comprehensive answer to the question for reference only...",
    "evaluations": [
        {{
            "tool": "ToolName",
            "truthfulness": {{"score": XXX, "reasoning": "Brief explanation..."}},
            "creativity": {{"score": XXX, "reasoning": "Brief explanation..."}},
            "coherence": {{"score": XXX, "reasoning": "Brief explanation..."}},
            "utility": {{"score": XXX, "reasoning": "Brief explanation..."}},
            "overall_score": XXX,
            "notes": "Additional notes if needed"
        }}
    ],
    "winner": "ToolName",
    "winner_reasoning": "Explanation of why this tool won...",
    "ranking": ["Tool1", "Tool2", "Tool3"]
}}"""),
            ("human", """Question: {question}

Tool Responses:
{responses}

Please first provide your own comprehensive answer to this question for reference, then evaluate only the provided tool responses (do not evaluate your own answer) according to the metrics defined above. 

RESPOND WITH VALID JSON ONLY - NO OTHER TEXT.""")
        ])
        
        # Create enhanced chain that includes judge's own answer
        self.enhanced_chain = self.enhanced_prompt_template | self.llm | StrOutputParser()
    
    def get_judge_name(self) -> str:
        """
        Get the judge name for database storage.
        For Ollama, returns "Ollama - {model_name}", otherwise returns the provider name.
        """
        if self.provider == "ollama":
            model_name = getattr(self, 'model_name', os.getenv("OLLAMA_MODEL", "ollama"))
            return f"Ollama - {model_name}"
        return self.provider
    
    def _handle_gemini_error(self, error):
        """
        Handle specific Gemini API errors and return user-friendly messages.
        
        Args:
            error: The exception that occurred
            
        Returns:
            Dictionary with error type and user message
        """
        error_str = str(error).lower()
        
        if "429" in error_str or "quota" in error_str or "rate" in error_str:
            return {
                "error_type": "quota_exceeded",
                "user_message": "Gemini model limit reached, visit us back next time"
            }
        elif "403" in error_str or "leaked" in error_str:
            return {
                "error_type": "api_key_leaked", 
                "user_message": "Gemini model limit reached, visit us back next time"
            }
        elif "401" in error_str or "unauthorized" in error_str:
            return {
                "error_type": "invalid_key",
                "user_message": "Invalid API key provided"
            }
        else:
            return {
                "error_type": "general_error",
                "user_message": f"Gemini API error: {str(error)}"
            }
        
        # Define the evaluation prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert judge evaluating GenAI tool responses across multiple metrics.

Your task is to evaluate responses from various GenAI tools against these metrics:

1. Truthfulness (Factual correctness, Internal consistency, Resistance to hallucination)
2. Creativity (Novel framing or synthesis, Non-obvious insights, Original examples or analogies)
3. Coherence & Reasoning Quality (Logical flow, Step-by-step reasoning, Absence of contradictions)
4. Utility/Actionability (Practical usefulness, Clarity for decision-making, Transferability to real-world tasks)

For each tool's response, provide:
- A score out of 1000 for each metric (use full range 0-1000 for maximum precision, e.g., 862, 745, 923)
- Brief reasoning for each score
- An overall score (average of all metrics, also out of 1000)

Format your response as valid JSON with this structure:
{{
    "evaluations": [
        {{
            "tool": "ToolName",
            "truthfulness": {{"score": XXX, "reasoning": "..."}},
            "creativity": {{"score": XXX, "reasoning": "..."}},
            "coherence": {{"score": XXX, "reasoning": "..."}},
            "utility": {{"score": XXX, "reasoning": "..."}},
            "overall_score": XXX,
            "notes": "..."
        }}
    ],
    "winner": "ToolName",
    "winner_reasoning": "...",
    "ranking": ["Tool1", "Tool2", ...]
}}"""),
            ("human", """Question: {question}

Tool Responses:
{responses}

Please evaluate these responses according to the metrics defined above.""")
        ])
        
        # Create the chain
        self.chain = self.prompt_template | self.llm | StrOutputParser()
    
    def format_responses(self, responses: Dict[str, str]) -> str:
        """
        Format tool responses for the prompt.
        
        Args:
            responses: Dictionary mapping tool names to their responses
            
        Returns:
            Formatted string of responses
        """
        formatted = []
        for tool, response in responses.items():
            formatted.append(f"--- {tool} ---\n{response}\n")
        return "\n".join(formatted)
    
    def evaluate(self, question: str, responses: Dict[str, str]) -> Dict:
        """
        Evaluate all tool responses for a given question.
        
        Args:
            question: The question that was asked
            responses: Dictionary mapping tool names to their responses
            
        Returns:
            Dictionary containing evaluation results
        """
        # Format responses
        formatted_responses = self.format_responses(responses)
        
        try:
            # Run the evaluation
            result = self.chain.invoke({
                "question": question,
                "responses": formatted_responses
            })
            
            # Parse JSON response
            try:
                # Some models wrap JSON in markdown code blocks
                if "```json" in result:
                    result = result.split("```json")[1].split("```")[0].strip()
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0].strip()
                
                evaluation_data = json.loads(result)
                return evaluation_data
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                print(f"Raw response: {result}")
                return {"error": "Failed to parse evaluation", "raw_response": result}
                
        except Exception as e:
            # Handle provider-specific errors
            if self.provider == "gemini":
                error_info = self._handle_gemini_error(e)
                return {
                    "error": error_info["user_message"],
                    "error_type": error_info["error_type"],
                    "provider": "gemini"
                }
            elif self.provider == "ollama":
                return {
                    "error": f"Ollama error: {str(e)}. Make sure Ollama is running locally.",
                    "error_type": "ollama_error",
                    "provider": "ollama"
                }
            else:
                return {"error": f"Evaluation failed: {str(e)}", "provider": self.provider}
    
    def evaluate_with_judge_answer(self, question: str, responses: Dict[str, str]) -> Dict:
        """
        Evaluate all tool responses including the judge's own answer to the question.
        
        Args:
            question: The question that was asked
            responses: Dictionary mapping tool names to their responses
            
        Returns:
            Dictionary containing evaluation results including judge's answer
        """
        # Format responses
        formatted_responses = self.format_responses(responses)
        
        try:
            # Run the enhanced evaluation that includes judge's own answer
            result = self.enhanced_chain.invoke({
                "question": question,
                "responses": formatted_responses
            })
            
            # Parse JSON response
            try:
                # Clean up the response - remove any markdown formatting
                cleaned_result = result.strip()
                
                # Remove markdown code blocks if present
                if "```json" in cleaned_result:
                    cleaned_result = cleaned_result.split("```json")[1].split("```")[0].strip()
                elif "```" in cleaned_result:
                    cleaned_result = cleaned_result.split("```")[1].split("```")[0].strip()
                
                # Try to find JSON content if there's extra text
                if not cleaned_result.startswith('{'):
                    # Look for JSON starting with {
                    json_start = cleaned_result.find('{')
                    if json_start != -1:
                        cleaned_result = cleaned_result[json_start:]
                        # Find the matching closing brace
                        brace_count = 0
                        json_end = -1
                        for i, char in enumerate(cleaned_result):
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    json_end = i + 1
                                    break
                        if json_end != -1:
                            cleaned_result = cleaned_result[:json_end]
                
                evaluation_data = json.loads(cleaned_result)
                return evaluation_data
                
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                print(f"Raw response: {result}")
                print(f"Cleaned response: {cleaned_result if 'cleaned_result' in locals() else 'N/A'}")
                
                # Return a fallback error response
                return {
                    "error": "Failed to parse evaluation - AI returned non-JSON response", 
                    "raw_response": result[:500] + "..." if len(result) > 500 else result,
                    "provider": self.provider
                }
                
        except Exception as e:
            # Handle provider-specific errors
            if self.provider == "gemini":
                error_info = self._handle_gemini_error(e)
                return {
                    "error": error_info["user_message"],
                    "error_type": error_info["error_type"],
                    "provider": "gemini"
                }
            elif self.provider == "ollama":
                return {
                    "error": f"Ollama error: {str(e)}. Make sure Ollama is running locally.",
                    "error_type": "ollama_error",
                    "provider": "ollama"
                }
            else:
                return {"error": f"Evaluation failed: {str(e)}", "provider": self.provider}
    
    def categorize_question(self, question: str) -> str:
        """
        Categorize a question into an appropriate category using LLM.
        
        Args:
            question: The question to categorize
            
        Returns:
            Category string determined by the LLM
        """
        # Define the categorization prompt template
        categorization_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert content categorizer. Your task is to categorize questions into appropriate topic categories.

Analyze the given question and provide a single, concise category name that best describes the main topic or domain of the question.

Guidelines:
- Use clear, descriptive category names (e.g., "artificial intelligence", "finance", "health", "science", "history", "sports", etc.)
- Choose the most specific and relevant category possible
- Use lowercase for consistency
- Prefer single words or short phrases (1-3 words maximum)
- If the question spans multiple topics, choose the primary/dominant topic

Examples:
- "How does machine learning work?" → "artificial intelligence"
- "What are the best investment strategies?" → "finance" 
- "Who won the World Cup in 2022?" → "sports"
- "How do vaccines work?" → "medicine"
- "What caused World War II?" → "history"
- "How to bake a chocolate cake?" → "cooking"

Respond with ONLY the category name, no explanations or additional text."""),
            ("human", "Categorize this question: {question}")
        ])
        
        # Create a simple chain for categorization
        categorization_chain = categorization_prompt | self.llm | StrOutputParser()
        
        try:
            # Get the category
            result = categorization_chain.invoke({"question": question})
            category = result.strip().lower()
            
            # Clean up the result (remove quotes, extra spaces, etc.)
            category = category.replace('"', '').replace("'", "").strip()
            
            # Ensure we have a valid category (not empty)
            if category and len(category) > 0:
                return category
            else:
                return "general"  # Fallback if empty
                
        except Exception as e:
            # Handle provider-specific errors for categorization
            if self.provider == "gemini":
                error_info = self._handle_gemini_error(e)
                print(f"Error categorizing question: {error_info['user_message']}")
            elif self.provider == "ollama":
                print(f"Error categorizing question: Ollama error - {str(e)}")
            else:
                print(f"Error categorizing question: {e}")
            return "general"  # Default fallback

    def create_results_table(self, evaluation_data: Dict) -> pd.DataFrame:
        """
        Create a pandas DataFrame from evaluation results.
        
        Args:
            evaluation_data: The evaluation results dictionary
            
        Returns:
            DataFrame with evaluation scores
        """
        if "error" in evaluation_data:
            return None
        
        rows = []
        for eval_item in evaluation_data.get("evaluations", []):
            # Convert scores from 1000-scale to 10-scale with 3 decimal places
            truthfulness_score = round(float(eval_item["truthfulness"]["score"]) / 100, 3)
            creativity_score = round(float(eval_item["creativity"]["score"]) / 100, 3)
            coherence_score = round(float(eval_item["coherence"]["score"]) / 100, 3)
            utility_score = round(float(eval_item["utility"]["score"]) / 100, 3)
            overall_score = round(float(eval_item["overall_score"]) / 100, 3)
            
            rows.append({
                "Tool": eval_item["tool"],
                "Truthfulness": truthfulness_score,
                "Creativity": creativity_score,
                "Coherence & Reasoning": coherence_score,
                "Utility/Actionability": utility_score,
                "Overall Score": overall_score,
                "Notes": eval_item.get("notes", "")
            })
        
        df = pd.DataFrame(rows)
        return df
    
    def print_detailed_report(self, evaluation_data: Dict):
        """
        Print a detailed evaluation report.
        
        Args:
            evaluation_data: The evaluation results dictionary
        """
        if "error" in evaluation_data:
            print(f"Error: {evaluation_data['error']}")
            return
        
        print("=" * 80)
        print("SCRUTINIUM: CROSS-GENAI BENCHMARKING EVALUATION REPORT")
        print("=" * 80)
        print()
        
        # Print table
        df = self.create_results_table(evaluation_data)
        if df is not None:
            print(df.to_string(index=False))
            print()
        
        # Print detailed reasoning for each tool
        print("\n" + "=" * 80)
        print("DETAILED ANALYSIS")
        print("=" * 80)
        
        for eval_item in evaluation_data.get("evaluations", []):
            print(f"\n### {eval_item['tool']} ###")
            print(f"Truthfulness ({eval_item['truthfulness']['score']}/10): {eval_item['truthfulness']['reasoning']}")
            print(f"Creativity ({eval_item['creativity']['score']}/10): {eval_item['creativity']['reasoning']}")
            print(f"Coherence ({eval_item['coherence']['score']}/10): {eval_item['coherence']['reasoning']}")
            print(f"Utility ({eval_item['utility']['score']}/10): {eval_item['utility']['reasoning']}")
            print(f"Overall: {eval_item['overall_score']}/10")
            if eval_item.get('notes'):
                print(f"Notes: {eval_item['notes']}")
        
        # Print winner and ranking
        print("\n" + "=" * 80)
        print("FINAL VERDICT")
        print("=" * 80)
        print(f"\n🏆 Winner: {evaluation_data.get('winner', 'N/A')}")
        print(f"\nReasoning: {evaluation_data.get('winner_reasoning', 'N/A')}")
        print(f"\nFull Ranking: {' > '.join(evaluation_data.get('ranking', []))}")
        print()


# Usage with free provider
def main():
    # Example 1: Use Ollama (Local, Free)
    print("Using Ollama for evaluation...")
    judge = GenAIBenchmarkJudge(provider="ollama")
    
    # Example 2: Use Gemini (Free with API key) - uncomment to use
    # print("Using Gemini for evaluation...")
    # judge = GenAIBenchmarkJudge(
    #     api_key=os.getenv("GEMINI_API_KEY"),  # Set your GEMINI_API_KEY environment variable
    #     provider="gemini"
    # )
    
    # Example 3: Use Groq (Free with API key) - uncomment to use
    # print("Using Groq for evaluation...")
    # judge = GenAIBenchmarkJudge(
    #     api_key=os.getenv("GROQ_API_KEY"),  # Set your GROQ_API_KEY environment variable
    #     provider="groq"
    # )
    
    # Example 4: Use Anthropic Claude (requires paid API key) - uncomment to use
    # print("Using Claude for evaluation...")
    # judge = GenAIBenchmarkJudge(
    #     api_key=os.getenv("ANTHROPIC_API_KEY"),  # Set your ANTHROPIC_API_KEY environment variable
    #     provider="anthropic"
    # )
    
    # Define the question
    question = "Who was the first Canadian prime minister?"
    
    # Define responses from different tools
    responses = {
        "ChatGPT": """The first Prime Minister of Canada was Sir John A. Macdonald.
He assumed office on 1 July 1867, the day Canada became a self-governing Dominion following Confederation.
Key context:
* Served as Prime Minister from 1867–1873 and again from 1878–1891
* A principal architect of Canadian Confederation
* Played a central role in creating a strong federal government and expanding Canada westward
* Leader of the Conservative Party
In practical terms, Macdonald is widely regarded as the founding political leader of modern Canada.""",
        
        "Kimi": """**Sir John Alexander Macdonald** was the first prime minister of Canada, serving from 1867 to 1873 and again from 1878 to 1891. A key architect of Canadian Confederation, Macdonald led the new Dominion of Canada through its early years of expansion and nation-building.""",
        
        "DeepSeek": """The first Prime Minister of Canada was **Sir John A. Macdonald**. He took office on **July 1, 1867**, the day Canada became a self-governing dominion through Confederation.
Here are a few key points about him:
- He served as prime minister from **1867 to 1873** and again from **1878 to 1891**.
- He was a leading figure in the negotiations that led to Confederation, often called one of the **"Fathers of Confederation."**
- His government oversaw the expansion of Canada across the continent, including the construction of the **Canadian Pacific Railway**.
- His legacy is complex, as his policies also included the **Chinese Head Tax** and the establishment of the **residential school system**, which have had lasting negative impacts on Indigenous and Chinese communities.
So, while Sir John A. Macdonald is recognized as Canada's first prime minister, his historical legacy is both foundational and contested.""",
        
        "Qwen": """The first Prime Minister of Canada was Sir John A. Macdonald. He served as Prime Minister from July 1, 1867, when Canada became a self-governing dominion within the British Empire, until November 5, 1873, and then again from October 17, 1878, until his death on June 6, 1891.""",
        
        "Mistral": """The first Prime Minister of Canada was Sir John A. Macdonald. He served from July 1, 1867, when Canada became a self-governing dominion, until November 5, 1873, and again from October 17, 1878, to June 6, 1891. Macdonald played a key role in the Confederation of Canada and is often considered one of the country's founding fathers.""",
        
        "Gemini": """The first Prime Minister of Canada was Sir John A. Macdonald. He is widely regarded as the dominant figure of Canadian Confederation and the primary architect of the nation.

Overview of His Leadership
Sir John A. Macdonald served as Prime Minister for a total of nearly 19 years, making him the second longest-serving Prime Minister in Canadian history (after William Lyon Mackenzie King). He held the office during two distinct periods:
* First Term: July 1, 1867 – November 5, 1873
* Second Term: October 17, 1878 – June 6, 1891

Key Achievements and Legacy
Macdonald's leadership was defined by his vision of a transcontinental nation that was independent of the United States and closely tied to Great Britain.
* Architect of Confederation: He played a leading role in the Charlottetown, Quebec, and London Conferences that led to the creation of the Dominion of Canada on July 1, 1867.
* The Canadian Pacific Railway (CPR): He oversaw the massive project of building a transcontinental railroad, which was essential for bringing British Columbia into Confederation and physically uniting the country from East to West.
* National Policy: He implemented a system of high tariffs to protect Canadian manufacturing and promote economic growth.
* Establishment of the NWMP: In 1873, he established the North-West Mounted Police (the precursor to the RCMP) to bring law and order to the western territories.
* Expansion of Canada: During his time in office, Canada expanded significantly, adding Manitoba (1870), British Columbia (1871), and Prince Edward Island (1873).

Note on Modern Perspective: While Macdonald is celebrated as a nation-builder, his legacy is also the subject of contemporary debate and criticism regarding his policies toward Indigenous peoples (such as the residential school system) and the Chinese Immigration Act."""
    }
    
    # Run evaluation
    print(f"Running evaluation with {judge.provider.title()}...")
    evaluation_results = judge.evaluate(question, responses)
    
    # Print detailed report
    judge.print_detailed_report(evaluation_results)
    
    # Optionally save results to CSV
    df = judge.create_results_table(evaluation_results)
    if df is not None:
        df.to_csv(f"{RESULTS_FOLDER}genai_benchmark_results.csv", index=False)
        print("\n✓ Results saved to 'genai_benchmark_results.csv'")
    
    # Optionally save full evaluation to JSON
    with open(f"{RESULTS_FOLDER}genai_benchmark_full_results.json", "w") as f:
        json.dump(evaluation_results, f, indent=2)
        print("✓ Full evaluation saved to 'genai_benchmark_full_results.json'")


if __name__ == "__main__":
    main()