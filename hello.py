"""
Sales Assist - AI-Powered Sales Pitch Evaluation System

A multi-agent system built with Agno v2 that evaluates sales pitches
against product brochures and provides scoring with detailed feedback.
"""

from sales_pitch_evaluator import SalesPitchEvaluator


def main():
    """Quick start guide for sales-assist"""
    print("\n" + "="*80)
    print("SALES-ASSIST: AI-Powered Pitch Evaluation System")
    print("="*80 + "\n")
    
    print("Welcome to Sales-Assist!")
    print("\nThis system uses a multi-agent architecture to:")
    print("  ✓ Identify the correct product brochure")
    print("  ✓ Analyze complete brochure content")
    print("  ✓ Score sales pitches out of 100")
    print("  ✓ Provide detailed feedback and recommendations")
    
    print("\n" + "-"*80)
    print("QUICK START")
    print("-"*80)
    
    print("\n1. Setup (first time only):")
    print("   pip install -e .")
    print("   copy .env.example .env")
    print("   # Edit .env and add your Gemini API key")
    
    print("\n2. Run the main evaluation system:")
    print("   python sales_pitch_evaluator.py")
    
    print("\n3. Try different examples:")
    print("   python examples.py")
    
    print("\n4. Use in your code:")
    print("   from sales_pitch_evaluator import SalesPitchEvaluator")
    print("   evaluator = SalesPitchEvaluator()")
    print("   evaluator.evaluate_pitch('Your pitch here...')")
    
    print("\n" + "-"*80)
    print("FEATURES")
    print("-"*80)
    
    print("\n🤖 Multi-Agent System:")
    print("   • Brochure Selector - Finds the right product")
    print("   • Knowledge Analyzer - Extracts key information")
    print("   • Pitch Evaluator - Scores the pitch")
    print("   • Feedback Generator - Provides improvements")
    
    print("\n📊 Scoring Criteria (100 points):")
    print("   • Accuracy: 30 points")
    print("   • Completeness: 25 points")
    print("   • Clarity: 15 points")
    print("   • Persuasiveness: 15 points")
    print("   • Compliance: 15 points")
    
    print("\n🔧 Powered by:")
    print("   • Agno v2 (Multi-agent framework)")
    print("   • Gemini 2.0 Flash (LLM)")
    print("   • LanceDB (Vector database)")
    print("   • OpenAI-compatible embeddings")
    
    print("\n" + "-"*80)
    print("BROCHURES IN DATABASE")
    print("-"*80 + "\n")
    
    import os
    from pathlib import Path
    
    brochures_dir = Path("brochures")
    if brochures_dir.exists():
        pdf_files = list(brochures_dir.glob("*.pdf"))
        if pdf_files:
            for i, pdf in enumerate(pdf_files, 1):
                print(f"   {i}. {pdf.stem}")
        else:
            print("   ⚠️  No PDF files found in brochures/ directory")
    else:
        print("   ⚠️  Brochures directory not found")
    
    print("\n" + "="*80)
    print("\nFor more information, see README.md")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
