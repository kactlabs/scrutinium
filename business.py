

import os
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
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
    
    def __init__(self, api_key: str = None, provider: str = "anthropic"):
        """
        Initialize the judge with specified model provider.
        
        Args:
            api_key: API key for the chosen provider
            provider: Model provider ("anthropic", "gemini", or "groq")
        """
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
        else:
            raise ValueError(f"Unsupported provider: {provider}. Choose from 'anthropic', 'gemini', or 'groq'")
        
        # Define the evaluation prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert judge evaluating GenAI tool responses across multiple metrics.

Your task is to evaluate responses from various GenAI tools against these metrics:

1. Truthfulness (Factual correctness, Internal consistency, Resistance to hallucination)
2. Creativity (Novel framing or synthesis, Non-obvious insights, Original examples or analogies)
3. Coherence & Reasoning Quality (Logical flow, Step-by-step reasoning, Absence of contradictions)
4. Utility/Actionability (Practical usefulness, Clarity for decision-making, Transferability to real-world tasks)

For each tool's response, provide:
- A score out of 10 for each metric
- Brief reasoning for each score
- An overall score (average of all metrics)

Format your response as valid JSON with this structure:
{{
    "evaluations": [
        {{
            "tool": "ToolName",
            "truthfulness": {{"score": X, "reasoning": "..."}},
            "creativity": {{"score": X, "reasoning": "..."}},
            "coherence": {{"score": X, "reasoning": "..."}},
            "utility": {{"score": X, "reasoning": "..."}},
            "overall_score": X.X,
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
            rows.append({
                "Tool": eval_item["tool"],
                "Truthfulness": eval_item["truthfulness"]["score"],
                "Creativity": eval_item["creativity"]["score"],
                "Coherence & Reasoning": eval_item["coherence"]["score"],
                "Utility/Actionability": eval_item["utility"]["score"],
                "Overall Score": eval_item["overall_score"],
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
    # Example 1: Use Gemini (Free with API key)
    print("Using Gemini for evaluation...")
    judge = GenAIBenchmarkJudge(
        api_key=os.getenv("GEMINI_API_KEY"),  # Set your GEMINI_API_KEY environment variable
        provider="gemini"
    )
    
    # Example 2: Use Groq (Free with API key) - uncomment to use
    # print("Using Groq for evaluation...")
    # judge = GenAIBenchmarkJudge(
    #     api_key=os.getenv("GROQ_API_KEY"),  # Set your GROQ_API_KEY environment variable
    #     provider="groq"
    # )
    
    # Example 3: Use Anthropic Claude (requires paid API key) - uncomment to use
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