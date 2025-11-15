"""
Quick Start Helper

Choose which evaluator to use based on your needs.
"""

import sys
from pathlib import Path


def show_menu():
    """Display main menu."""
    print("\n" + "="*60)
    print("🚀 SALES PITCH EVALUATOR - QUICK START")
    print("="*60 + "\n")
    
    print("Which evaluator do you want to use?\n")
    
    print("1️⃣  Simple Evaluator (simple_evaluator.py)")
    print("   • Uses PDF brochures from 'brochures/' folder")
    print("   • Processes full PDF documents (9000 words avg)")
    print("   • 5-agent system with PDF analysis")
    print("   • Good for: Initial PDF exploration\n")
    
    print("2️⃣  Competitive Evaluator (competitive_evaluator.py) ⭐ RECOMMENDED")
    print("   • Uses extracted markdown from 'plans/' folder")
    print("   • Pre-processed data (150-250 lines per plan)")
    print("   • 4-agent system (faster)")
    print("   • Detailed per-competitor comparisons")
    print("   • Shows strong points separately for each competitor")
    print("   • User selects plan, validates if exists")
    print("   • Good for: Production use, competitive analysis\n")
    
    print("3️⃣  Test Suite (test_competitive.py)")
    print("   • Test competitive evaluator functionality")
    print("   • Verify all components working\n")
    
    print("4️⃣  View Documentation")
    print("   • Read detailed guides and comparisons\n")
    
    print("5️⃣  Exit\n")
    
    print("="*60)


def run_simple_evaluator():
    """Launch simple evaluator."""
    print("\n🚀 Launching Simple Evaluator...\n")
    import simple_evaluator
    simple_evaluator.main()


def run_competitive_evaluator():
    """Launch competitive evaluator."""
    print("\n🚀 Launching Competitive Evaluator...\n")
    import competitive_evaluator
    competitive_evaluator.main()


def run_tests():
    """Launch test suite."""
    print("\n🧪 Launching Test Suite...\n")
    import test_competitive
    # test_competitive runs automatically


def show_docs():
    """Show available documentation."""
    print("\n" + "="*60)
    print("📚 DOCUMENTATION")
    print("="*60 + "\n")
    
    docs = {
        "COMPETITIVE_EVALUATOR_README.md": "Complete guide to competitive evaluator",
        "SCRIPT_COMPARISON.md": "Detailed comparison between evaluators",
        "IMPLEMENTATION_SUMMARY.md": "Implementation overview and features",
        "SIMPLIFICATION.md": "Original simplification documentation",
    }
    
    print("Available documentation files:\n")
    for doc, desc in docs.items():
        if Path(doc).exists():
            print(f"  ✅ {doc}")
            print(f"     {desc}\n")
        else:
            print(f"  ❌ {doc} (not found)\n")
    
    print("Open any of these files to read detailed documentation.")
    print("\n" + "="*60)
    input("\nPress Enter to return to main menu...")


def main():
    """Main menu loop."""
    while True:
        show_menu()
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            try:
                run_simple_evaluator()
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("\nPress Enter to continue...")
        
        elif choice == "2":
            try:
                run_competitive_evaluator()
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("\nPress Enter to continue...")
        
        elif choice == "3":
            try:
                run_tests()
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("\nPress Enter to continue...")
        
        elif choice == "4":
            show_docs()
        
        elif choice == "5":
            print("\n👋 Goodbye!\n")
            sys.exit(0)
        
        else:
            print("\n❌ Invalid choice. Please enter 1-5.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!\n")
    except Exception as e:
        print(f"\n\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
