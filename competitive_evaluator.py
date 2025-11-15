"""
Competitive Sales Pitch Evaluator

Evaluates sales pitches by comparing Kotak plans against competitors' plans.
Uses extracted markdown files for fast, accurate comparisons.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.embedder.huggingface import HuggingfaceCustomEmbedder
from agno.models.openai import OpenAIChat
from agno.team import Team
from agno.vectordb.lancedb import LanceDb, SearchType

# Load environment variables
load_dotenv()


def create_model() -> OpenAIChat:
    """Create OpenRouter-compatible model."""
    return OpenAIChat(
        id=os.getenv("MODEL_NAME", "anthropic/claude-3.5-sonnet"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        request_params={"temperature": 0.7, "max_tokens": 4096},
    )


def setup_knowledge(plans_dir: str = "plans") -> Knowledge:
    """Setup knowledge base with extracted plan markdown files."""
    
    print("\n🔧 Initializing HuggingFace embedder...")
    
    embedder = HuggingfaceCustomEmbedder(
        id="sentence-transformers/all-MiniLM-L6-v2",
        api_key=os.getenv("HUGGINGFACE_API_KEY"),
        dimensions=384,
    )
    
    print("✅ HuggingFace embedder ready!\n")
    
    vector_db = LanceDb(
        uri="tmp/lancedb_plans",
        table_name="insurance_plans",
        search_type=SearchType.hybrid,
        embedder=embedder,
    )
    
    knowledge = Knowledge(
        name="Insurance Plans Database",
        vector_db=vector_db,
        max_results=20,  # Get top 20 relevant sections
    )
    
    # Load all markdown files from plans directory
    print("📚 Loading plan documents...")
    plans_path = Path(plans_dir)
    
    for category_dir in plans_path.iterdir():
        if not category_dir.is_dir():
            continue
            
        print(f"\n  Category: {category_dir.name}")
        for md_file in category_dir.glob("*.md"):
            print(f"    - {md_file.name}")
            
            # Extract company and plan type from filename
            company = md_file.stem.split('_')[0]
            plan_type = category_dir.name
            
            knowledge.add_content(
                path=str(md_file),
                name=f"{company} - {plan_type}",
                metadata={
                    "company": company,
                    "plan_type": plan_type,
                    "filename": md_file.name,
                    "category": category_dir.name
                }
            )
    
    print("\n✅ Knowledge base ready!\n")
    return knowledge


def get_available_plans(plans_dir: str = "plans") -> dict[str, list[str]]:
    """Get list of available plans by category."""
    plans = {}
    plans_path = Path(plans_dir)
    
    for category_dir in plans_path.iterdir():
        if not category_dir.is_dir():
            continue
        
        md_files = list(category_dir.glob("*.md"))
        plans[category_dir.name] = [f.stem for f in md_files]
    
    return plans


def find_kotak_plan(plan_name: str, plans_dir: str = "plans") -> Optional[str]:
    """Find if a Kotak plan exists matching the given name."""
    plans_path = Path(plans_dir)
    
    # Search all categories
    for category_dir in plans_path.iterdir():
        if not category_dir.is_dir():
            continue
        
        for md_file in category_dir.glob("*.md"):
            if md_file.stem.lower().startswith("kotak") and plan_name.lower() in md_file.stem.lower():
                return str(md_file)
    
    return None


def create_agents(model: OpenAIChat, knowledge: Knowledge) -> list[Agent]:
    """Create evaluation agents for competitive analysis."""
    
    agents = [
        Agent(
            name="Plan Finder",
            role="Find the Kotak plan and competitor plans in the same category",
            model=model,
            knowledge=knowledge,
            search_knowledge=True,
            read_chat_history=True,
            instructions=[
                "You search the knowledge base to find the relevant Kotak plan details",
                "Also identify competitor plans (HDFC, Axis, etc.) in the same category",
                "Extract key features, benefits, eligibility, and pricing from all plans",
                "Organize findings by company for easy comparison",
                "Note: All plan information is already extracted in markdown format"
            ],
        ),
        Agent(
            name="Pitch Evaluator",
            role="Evaluate the sales pitch against the Kotak plan details",
            model=model,
            read_chat_history=True,
            instructions=[
                "Evaluate the sales pitch for accuracy against Kotak plan features",
                "Check if all key benefits are mentioned correctly",
                "Verify eligibility criteria, premiums, and terms are accurate",
                "Identify any missing important features",
                "Score accuracy on scale of 1-10",
                "Provide detailed analysis of what's correct and what needs improvement"
            ],
        ),
        Agent(
            name="Competitive Analyzer",
            role="Find Kotak plan's competitive advantages over competitors",
            model=model,
            read_chat_history=True,
            instructions=[
                "IMPORTANT: Focus ONLY on where Kotak is BETTER than competitors",
                "For EACH competitor (HDFC, Axis, etc.), identify:",
                "  • What makes Kotak plan SUPERIOR (strong points only)",
                "  • Unique Kotak advantages not available in competitor plans",
                "  • Better pricing, terms, or value propositions in Kotak",
                "  • Specific features where Kotak outperforms",
                "DO NOT mention competitor advantages - be BIASED towards Kotak",
                "Present as separate sections per competitor with clear Kotak wins",
                "These are selling points for the sales rep to emphasize",
                "Format: 'VS [COMPETITOR]: Why Kotak is Better'"
            ],
        ),
        Agent(
            name="Feedback Generator",
            role="Generate comprehensive feedback and recommendations",
            model=model,
            read_chat_history=True,
            instructions=[
                "Provide an overall evaluation score (1-10)",
                "List specific strengths of the pitch",
                "List specific areas for improvement",
                "Suggest competitive talking points based on Kotak's advantages",
                "Provide example phrases to highlight Kotak's superiority",
                "Give actionable recommendations to improve the pitch",
                "Keep feedback practical and sales-oriented"
            ],
        ),
        Agent(
            name="Pitch Improver",
            role="Generate an improved version of the sales pitch",
            model=model,
            read_chat_history=True,
            instructions=[
                "Based on the evaluation and competitive analysis, create an IMPROVED pitch",
                "Include all accurate information from the original pitch",
                "Add missing key features that should be highlighted",
                "Incorporate Kotak's competitive advantages vs each competitor",
                "Use persuasive sales language and structure",
                "Emphasize unique selling points and differentiators",
                "Make it compelling, accurate, and customer-focused",
                "Keep it concise but comprehensive (300-500 words)",
                "Use the format: 'IMPROVED PITCH:' followed by the enhanced version"
            ],
        ),
    ]
    
    return agents


def create_evaluation_team(agents: list[Agent]) -> Team:
    """Create the evaluation team."""
    return Team(
        name="Competitive Pitch Evaluation Team",
        members=agents,  # Fixed: Changed 'agents' to 'members'
        model=create_model(),  # Added: Team needs a model
        instructions=[
            "Work together to evaluate the sales pitch comprehensively",
            "Plan Finder: First identify the Kotak plan and all competitors",
            "Pitch Evaluator: Assess accuracy against Kotak plan details",
            "Competitive Analyzer: Find ONLY Kotak advantages vs EACH competitor (biased towards Kotak)",
            "Feedback Generator: Synthesize findings into actionable feedback",
            "Pitch Improver: Create an improved pitch incorporating all insights",
            "Focus on Kotak's competitive strengths and superiority",
            "Provide practical insights for sales improvement"
        ],
    )


def evaluate_pitch(
    team: Team,
    pitch: str,
    plan_name: str,
    plan_type: Optional[str] = None,
    generate_improved: bool = False
) -> str:
    """Evaluate a sales pitch with competitive analysis."""
    
    improved_instruction = ""
    if generate_improved:
        improved_instruction = "\n5. Pitch Improver: Generate an IMPROVED version of the pitch incorporating all insights"
    
    context = f"""
Plan Name: {plan_name}
Plan Type: {plan_type if plan_type else "Not specified"}

Sales Pitch:
{pitch}

Please evaluate this pitch by:
1. Finding the Kotak plan details and competitor plans in the same category
2. Checking if the pitch accurately represents the Kotak plan
3. Comparing Kotak plan advantages - ONLY show where Kotak is BETTER than each competitor (biased towards Kotak)
4. Providing an overall score and actionable feedback{improved_instruction}

For competitive analysis, focus ONLY on Kotak's strengths and advantages over competitors.
DO NOT mention competitor advantages - this is for Kotak sales reps.
"""
    
    print("\n🤖 Evaluation in progress...\n")
    
    try:
        response = team.run(context, stream=False)
        return response.content if response else "No response generated"
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        return f"Evaluation failed: {str(e)}"


def get_user_pitch() -> tuple[str, str, Optional[str], bool]:
    """Get pitch and plan name from user."""
    
    print("\n" + "="*60)
    print("🎯 COMPETITIVE SALES PITCH EVALUATOR")
    print("="*60)
    
    # Show available plans
    print("\n📋 Available Plans by Category:")
    plans = get_available_plans()
    for category, plan_list in plans.items():
        print(f"\n  {category}:")
        for plan in plan_list:
            if plan.lower().startswith("kotak"):
                print(f"    ✓ {plan}")
    
    print("\n" + "-"*60)
    
    # Get plan name
    plan_name = input("\n📌 Enter Kotak plan name (e.g., 'Kotak_guaranteed_income'): ").strip()
    
    if not plan_name:
        print("\n⚠️  No plan name provided!")
        return "", "", None, False
    
    # Check if plan exists
    kotak_plan = find_kotak_plan(plan_name)
    if not kotak_plan:
        print(f"\n❌ Sorry, I don't have information about '{plan_name}'")
        print("\nPlease choose from the available Kotak plans listed above.")
        return "", "", None, False
    
    print(f"✅ Found plan: {Path(kotak_plan).stem}")
    
    # Determine plan type from path
    plan_type = Path(kotak_plan).parent.name
    
    print("\n" + "-"*60)
    print("📝 Enter your sales pitch (Type 'done' on a new line to finish):")
    print("-"*60 + "\n")
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip().lower() == 'done':
                break
            lines.append(line)
        except EOFError:
            break
    
    pitch = "\n".join(lines).strip()
    
    if not pitch:
        print("\n⚠️  No pitch provided!")
        return "", "", None, False
    
    # Ask if user wants improved pitch
    print("\n" + "-"*60)
    improve_choice = input("💡 Generate an improved pitch? (y/n): ").strip().lower()
    generate_improved = improve_choice == 'y'
    
    return pitch, plan_name, plan_type, generate_improved


def display_evaluation(result: str):
    """Display evaluation results in a formatted way."""
    print("\n" + "="*60)
    print("📊 EVALUATION RESULTS")
    print("="*60 + "\n")
    print(result)
    print("\n" + "="*60 + "\n")


def main():
    """Main execution function."""
    
    # Get pitch from user
    pitch, plan_name, plan_type, generate_improved = get_user_pitch()
    
    if not pitch or not plan_name:
        print("\n👋 Exiting...")
        return
    
    print("\n" + "="*60)
    print(f"🔍 Analyzing pitch for: {plan_name}")
    if plan_type:
        print(f"📂 Category: {plan_type}")
    if generate_improved:
        print("💡 Will generate improved pitch")
    print("="*60)
    
    # Initialize components
    print("\n⚙️  Initializing evaluation system...")
    model = create_model()
    knowledge = setup_knowledge()
    agents = create_agents(model, knowledge)
    team = create_evaluation_team(agents)
    
    # Evaluate
    result = evaluate_pitch(team, pitch, plan_name, plan_type, generate_improved)
    
    # Display results
    display_evaluation(result)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Evaluation cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
