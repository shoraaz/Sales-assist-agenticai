"""
Quick Test Script for Competitive Evaluator

Tests the competitive evaluator with a sample pitch.
"""

from competitive_evaluator import (
    create_model,
    setup_knowledge,
    create_agents,
    create_evaluation_team,
    evaluate_pitch,
    get_available_plans,
    find_kotak_plan
)

def test_basic_functionality():
    """Test basic functions."""
    print("🧪 Testing basic functionality...\n")
    
    # Test 1: Available plans
    print("Test 1: Getting available plans...")
    plans = get_available_plans()
    for category, plan_list in plans.items():
        print(f"  {category}: {len(plan_list)} plans")
    print("✅ Test 1 passed\n")
    
    # Test 2: Find Kotak plan
    print("Test 2: Finding Kotak plan...")
    result = find_kotak_plan("guaranteed_income")
    if result:
        print(f"  Found: {result}")
        print("✅ Test 2 passed\n")
    else:
        print("  ❌ Plan not found\n")
    
    # Test 3: Find non-existent plan
    print("Test 3: Testing non-existent plan...")
    result = find_kotak_plan("xyz_nonexistent")
    if not result:
        print("  Correctly returned None for non-existent plan")
        print("✅ Test 3 passed\n")
    else:
        print("  ❌ Should have returned None\n")


def test_full_evaluation():
    """Test full evaluation flow with a sample pitch."""
    print("\n" + "="*60)
    print("🧪 FULL EVALUATION TEST")
    print("="*60 + "\n")
    
    # Sample pitch
    pitch = """
    Hello! Let me tell you about Kotak Get Assured Income Now (GAIN).
    
    This is a participating non-linked savings plan that offers:
    - Guaranteed income starting from the 1st policy month
    - Life cover until age 85
    - Three flexible plan options: Early Income, Paid-up Additions, and Premium Saver
    - Special benefits for female lives
    - Additional benefits for ECS/Auto debit premium payments
    - 6 optional riders for comprehensive coverage
    
    You can pay premiums for just 6, 8, 10, or 12 years and get benefits for life.
    Minimum annual premium is just ₹50,000 with no upper limit.
    
    This plan is perfect for those seeking guaranteed income with life protection.
    """
    
    plan_name = "Kotak_guaranteed_income"
    plan_type = "Guaranteed_income"
    
    print(f"Plan: {plan_name}")
    print(f"Type: {plan_type}")
    print(f"\nPitch:\n{pitch}")
    print("\n" + "-"*60 + "\n")
    
    # Ask if user wants improved pitch in test
    improve_choice = input("Test with improved pitch generation? (y/n): ").strip().lower()
    generate_improved = improve_choice == 'y'
    
    # Initialize system
    print("⚙️  Initializing evaluation system...")
    try:
        model = create_model()
        print("✅ Model created")
        
        knowledge = setup_knowledge()
        print("✅ Knowledge base loaded")
        
        agents = create_agents(model, knowledge)
        print(f"✅ {len(agents)} agents created")
        
        team = create_evaluation_team(agents)
        print("✅ Team assembled")
        
        # Evaluate
        print("\n🔍 Running evaluation...\n")
        if generate_improved:
            print("💡 Including improved pitch generation...\n")
        
        result = evaluate_pitch(team, pitch, plan_name, plan_type, generate_improved)
        
        # Display results
        print("\n" + "="*60)
        print("📊 EVALUATION RESULTS")
        print("="*60 + "\n")
        print(result)
        print("\n" + "="*60)
        print("✅ Full evaluation test completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 COMPETITIVE EVALUATOR TEST SUITE")
    print("="*60 + "\n")
    
    # Run basic tests
    test_basic_functionality()
    
    # Ask if user wants to run full evaluation
    print("\n" + "-"*60)
    response = input("Run full evaluation test? (y/n): ").strip().lower()
    
    if response == 'y':
        test_full_evaluation()
    else:
        print("\n✅ Basic tests completed. Skipping full evaluation.")
    
    print("\n👋 Test suite finished!\n")
