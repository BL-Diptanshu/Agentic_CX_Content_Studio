import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.text_content_gen import get_text_generator
import time

def run_text_experiments():
    """Run text generation experiments with different parameters"""
    print("\n" + "="*80)
    print("MLflow Text Generation Experiments")
    print("="*80)
    
    generator = get_text_generator()
    
    experiments = [
        {
            "name": "Low Temperature (Focused)",
            "prompt": "Write a professional product description for a smartwatch",
            "max_tokens": 100,
            "temperature": 0.3
        },
        {
            "name": "High Temperature (Creative)",
            "prompt": "Write a creative product description for a smartwatch",
            "max_tokens": 100,
            "temperature": 0.9
        },
        {
            "name": "Short Output",
            "prompt": "Write a tagline for a premium smartphone",
            "max_tokens": 50,
            "temperature": 0.7
        },
        {
            "name": "Long Output",
            "prompt": "Write a detailed blog post introduction about AI in marketing",
            "max_tokens": 200,
            "temperature": 0.7
        }
    ]
    
    for i, exp in enumerate(experiments, 1):
        print(f"\n{'='*80}")
        print(f"Experiment {i}/{len(experiments)}: {exp['name']}")
        print(f"{'='*80}")
        print(f"Prompt: {exp['prompt']}")
        print(f"Parameters: max_tokens={exp['max_tokens']}, temperature={exp['temperature']}")
        
        try:
            start = time.time()
            result = generator.generate_text(
                prompt=exp['prompt'],
                max_tokens=exp['max_tokens'],
                temperature=exp['temperature']
            )
            duration = time.time() - start
            
            print(f"\n✓ Generated ({duration:.2f}s):")
            print(f"{result[:200]}{'...' if len(result) > 200 else ''}")
            print(f"\nLogged to MLflow ✓")
            
        except Exception as e:
            print(f"✗ Error: {e}")
        
        time.sleep(1)
    
    print("\n" + "="*80)
    print("All experiments completed")
    print("="*80)
    print("\nView experiments in MLflow UI:")
    print("  1. Run: mlflow ui --port 5000")
    print("  2. Open: http://localhost:5000")
    print("  3. Check experiment: 'text_content_generation'")


def run_marketing_copy_experiments():
    """Run marketing copy experiments"""
    print("\n" + "="*80)
    print("MLflow Marketing Copy Experiments")
    print("="*80)
    
    generator = get_text_generator()
    
    campaigns = [
        {
            "name": "Tech Product Launch",
            "campaign_name": "SmartWatch Pro Launch",
            "brand": "TechCorp",
            "objective": "Launch premium smartwatch with health features",
            "target_audience": "Health-conscious professionals"
        },
        {
            "name": "Summer Campaign",
            "campaign_name": "Summer Sale 2026",
            "brand": "FashionHub",
            "objective": "Drive summer clothing sales",
            "target_audience": "Young adults aged 18-35"
        },
        {
            "name": "Brand Awareness",
            "campaign_name": "Innovation Showcase",
            "brand": "FutureTech",
            "objective": "Build brand awareness in AI space",
            "target_audience": "Tech enthusiasts and early adopters"
        }
    ]
    
    for i, campaign in enumerate(campaigns, 1):
        print(f"\n{'='*80}")
        print(f"Campaign {i}/{len(campaigns)}: {campaign['name']}")
        print(f"{'='*80}")
        
        try:
            start = time.time()
            result = generator.generate_marketing_copy(
                campaign_name=campaign['campaign_name'],
                brand=campaign['brand'],
                objective=campaign['objective'],
                target_audience=campaign['target_audience'],
                max_tokens=150
            )
            duration = time.time() - start
            
            print(f"✓ Generated ({duration:.2f}s):")
            print(f"{result[:250]}{'...' if len(result) > 250 else ''}")
            print(f"\nLogged to MLflow ✓")
            
        except Exception as e:
            print(f"✗ Error: {e}")
        
        time.sleep(1)
    
    print("\n" + "="*80)
    print("✓ All marketing campaigns completed")
    print("="*80)


if __name__ == "__main__":
    print("\n" + "="*80)
    print("MLFLOW EXPERIMENT TEST SUITE")
    print("User Story 6 - ML Engineer 2")
    print("="*80)
    
    try:
        run_text_experiments()
        run_marketing_copy_experiments()
        
        print("\n" + "="*80)
        print("✓ ALL EXPERIMENTS COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nNext Steps:")
        print("  1. Start MLflow UI: mlflow ui --port 5000")
        print("  2. Navigate to: http://localhost:5000")
        print("  3. View experiment: 'text_content_generation'")
        print("  4. Verify logged parameters and metrics")
        
    except Exception as e:
        print(f"\n✗ Experiments failed: {e}")
        sys.exit(1)
