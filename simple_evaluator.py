"""
Simple Sales Pitch Evaluator

A streamlined multi-agent system that evaluates sales pitches against product brochures.
Uses OpenRouter for LLMs and HuggingFace API for embeddings.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.embedder.huggingface import HuggingfaceCustomEmbedder
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.models.openai import OpenAIChat
from agno.team import Team
from agno.vectordb.lancedb import LanceDb, SearchType

# Load environment variables
load_dotenv()


def read_full_pdf(pdf_path: str) -> str:
    """
    Read the complete PDF content as fallback.
    Use this if vector search doesn't retrieve enough information.
    """
    try:
        from pypdf import PdfReader
        
        reader = PdfReader(pdf_path)
        full_text = ""
        
        for page in reader.pages:
            full_text += page.extract_text() + "\n\n"
        
        return full_text
    except Exception as e:
        print(f"⚠️  Could not read PDF directly: {e}")
        return ""


def create_model() -> OpenAIChat:
    """Create OpenRouter-compatible model."""
    return OpenAIChat(
        id=os.getenv("MODEL_NAME", "anthropic/claude-3.5-sonnet"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        request_params={"temperature": 0.7, "max_tokens": 4096},
    )


def setup_knowledge(brochures_dir: str = "brochures") -> Knowledge:
    """Setup knowledge base with product brochures."""
    
    # Initialize vector database with HuggingFace embeddings API
    # Using HuggingFace API for embeddings
    print("\n🔧 Initializing HuggingFace embedder...")
    
    embedder = HuggingfaceCustomEmbedder(
        id="sentence-transformers/all-MiniLM-L6-v2",
        api_key=os.getenv("HUGGINGFACE_API_KEY"),
        dimensions=384,  # This model produces 384-dimensional embeddings
    )
    
    print("✅ HuggingFace embedder ready!\n")
    
    vector_db = LanceDb(
        uri="tmp/lancedb",
        table_name="product_brochures",
        search_type=SearchType.hybrid,
        embedder=embedder,
    )
    
    # Create PDF reader with optimized chunking for 9000-word PDFs
    # With 9000 words (~45,000 chars), we need good coverage
    pdf_reader = PDFReader(
        chunk=True,
        chunk_size=3000,  # Larger chunks for better context (~600 words per chunk)
        chunk_overlap=600,  # Substantial overlap to maintain context flow
    )
    
    # Create knowledge base
    knowledge = Knowledge(
        name="Product Brochures",
        vector_db=vector_db,
        max_results=25,  # Retrieve top 25 chunks for comprehensive coverage
    )
    
    # Load all PDF brochures with custom reader
    print("📚 Loading brochures...")
    for pdf_file in Path(brochures_dir).glob("*.pdf"):
        print(f"  - {pdf_file.name}")
        knowledge.add_content(
            path=str(pdf_file),
            name=pdf_file.stem,
            metadata={"filename": pdf_file.name, "type": "brochure"},
            reader=pdf_reader
        )
    
    print("✅ Knowledge base ready!\n")
    return knowledge


def create_agents(model: OpenAIChat, knowledge: Knowledge) -> list[Agent]:
    """Create evaluation agents."""
    
    agents = [
        Agent(
            name="Brochure Selector",
            role="Find the right product brochure",
            model=model,
            knowledge=knowledge,
            search_knowledge=True,
            read_chat_history=True,
            instructions=[
                "Identify which product is being discussed in the pitch",
                "Search knowledge base thoroughly for the matching brochure",
                "Return only ONE brochure that best matches",
                "Confirm the exact product name"
            ]
        ),
        
        Agent(
            name="Knowledge Analyzer",
            role="Extract comprehensive product information",
            model=model,
            knowledge=knowledge,
            search_knowledge=True,
            read_chat_history=True,
            instructions=[
                "Thoroughly read the COMPLETE product brochure",
                "Search multiple times to get ALL sections of the brochure",
                "Extract EVERY key feature, benefit, term, and condition",
                "Include ALL: premiums, coverage amounts, policy terms, riders, exclusions",
                "Note ALL disclaimers, eligibility criteria, and limitations",
                "Include pricing structure, tax benefits, and maturity benefits",
                "Provide a comprehensive and detailed summary - leave nothing out",
                "If information seems incomplete, search again with different queries"
            ]
        ),
        
        Agent(
            name="Pitch Evaluator",
            role="Score the pitch against complete product knowledge",
            model=model,
            read_chat_history=True,
            instructions=[
                "Compare pitch against the COMPLETE product knowledge provided",
                "Score out of 100 based on:",
                "  - Accuracy (30 pts): Are all facts correct?",
                "  - Completeness (25 pts): Are ALL key features covered?",
                "  - Clarity (15 pts): Is it easy to understand?",
                "  - Persuasiveness (15 pts): Is it compelling?",
                "  - Compliance (15 pts): Are disclaimers mentioned?",
                "Identify EVERYTHING that's missing, incorrect, or could be improved",
                "Be thorough and detailed in your evaluation"
            ]
        ),
        
        Agent(
            name="Feedback Generator",
            role="Provide detailed actionable feedback",
            model=model,
            read_chat_history=True,
            instructions=[
                "Highlight what was done well in the pitch",
                "Clearly identify ALL gaps, inaccuracies, or missing information",
                "Provide specific, actionable recommendations with examples",
                "Suggest exact phrases or points to add based on the complete brochure",
                "Organize feedback in a clear, structured format",
                "Be encouraging yet thoroughly honest in the assessment",
                "Include examples of how to improve each weak area"
            ]
        )
    ]
    
    return agents


def create_evaluation_team(model: OpenAIChat, agents: list[Agent], knowledge: Knowledge) -> Team:
    """Create coordinated evaluation team."""
    
    return Team(
        name="Sales Pitch Evaluation Team",
        model=model,
        members=agents,
        knowledge=knowledge,
        show_members_responses=True,
        read_chat_history=True,
    )


def evaluate_pitch(team: Team, pitch: str, product_hint: str = None) -> str:
    """Evaluate a sales pitch."""
    
    query = f"""
    Evaluate this sales pitch:
    
    {f'Product hint: {product_hint}' if product_hint else ''}
    
    PITCH:
    {pitch}
    
    Provide: score, breakdown, strengths, improvements, and recommendations.
    """
    
    print("🤖 Starting evaluation...\n" + "=" * 80)
    
    try:
        response = team.print_response(query, stream=True)
        print("\n" + "=" * 80)
        print("✅ Evaluation complete!")
        return response
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "rate limit" in error_msg.lower():
            print("\n❌ Rate limit exceeded. Wait and try again.")
        else:
            print(f"\n❌ Error: {error_msg}")
        raise


def get_user_pitch() -> tuple[str, str]:
    """
    Get sales pitch input from the user via console.
    
    Returns:
        Tuple of (pitch_text, product_hint)
    """
    print("\n" + "=" * 80)
    print("📝 ENTER YOUR SALES PITCH")
    print("=" * 80 + "\n")
    
    print("Instructions:")
    print("  1. Type or paste your sales pitch below")
    print("  2. Press Enter twice (empty line) when done")
    print("  3. Or type 'example' to use a sample pitch\n")
    
    print("-" * 80)
    
    # Collect multi-line pitch
    pitch_lines = []
    empty_count = 0
    
    while empty_count < 1:  # Stop after one empty line
        try:
            line = input()
            
            # Check for example request
            if line.strip().lower() == "example" and len(pitch_lines) == 0:
                return get_example_pitch()
            
            if line.strip() == "":
                empty_count += 1
                if empty_count >= 1:
                    break
            else:
                empty_count = 0
                pitch_lines.append(line)
                
        except (EOFError, KeyboardInterrupt):
            break
    
    pitch_text = "\n".join(pitch_lines).strip()
    
    if not pitch_text:
        print("\n⚠️  No pitch entered. Using example pitch instead.\n")
        return get_example_pitch()
    
    # Ask for product hint
    print("\n" + "-" * 80)
    print("\n💡 Optional: Enter a product hint to speed up matching")
    print("   Examples: 'term insurance', 'ULIP', 'savings plan'")
    print("   Or press Enter to skip\n")
    
    try:
        product_hint = input("Product hint: ").strip()
    except (EOFError, KeyboardInterrupt):
        product_hint = ""
    
    return pitch_text, product_hint if product_hint else None


def get_example_pitch() -> tuple[str, str]:
    """
    Return an example sales pitch for demonstration.
    
    Returns:
        Tuple of (pitch_text, product_hint)
    """
    example_pitch = """
    Hello! I'd like to tell you about our Kotak e-Term Plan.
    
    This is a pure term insurance policy that provides financial protection 
    for your family. Key benefits include:
    
    - High coverage at affordable premiums
    - Flexible policy terms from 5 to 30 years
    - Multiple death benefit payout options
    - Online purchase with instant policy issuance
    
    The policy ensures your family's financial security if something happens 
    to you. The premiums are very competitive, and you can buy it completely 
    online in just a few minutes!
    
    Would you like to know more about the coverage options?
    """
    
    return example_pitch.strip(), "term insurance"


def main():
    """Run the evaluator."""
    
    print("\n" + "=" * 80)
    print("🎯 SALES PITCH EVALUATOR")
    print("=" * 80 + "\n")
    
    # Initialize
    try:
        model = create_model()
        knowledge = setup_knowledge()
        agents = create_agents(model, knowledge)
        team = create_evaluation_team(model, agents, knowledge)
    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        return
    
    # Get pitch from user
    try:
        pitch, product_hint = get_user_pitch()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user.")
        return
    
    # Show what we're evaluating
    print("\n" + "=" * 80)
    print("📋 PITCH TO EVALUATE:")
    print("-" * 80)
    print(pitch)
    print("-" * 80)
    if product_hint:
        print(f"💡 Product hint: {product_hint}")
    print("=" * 80)
    
    # Evaluate
    try:
        evaluate_pitch(team, pitch, product_hint=product_hint)
    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
