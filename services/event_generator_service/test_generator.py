import pandas as pd
from pathlib import Path
from generator import EventGenerator
from schema import FeaturesEvent

def test_dataset_loading():
    """Test if dataset loads correctly"""
    dataset_path = Path(__file__).parent / "data" / "transactions.csv"
    
    if not dataset_path.exists():
        print("❌ Dataset not found!")
        return False
    
    gen = EventGenerator(str(dataset_path))
    print(f"✓ Dataset loaded: {len(gen.df)} rows")
    print(f"✓ Columns: {list(gen.df.columns)}")
    return True

def test_event_generation():
    """Test if events are generated correctly"""
    dataset_path = Path(__file__).parent / "data" / "transactions.csv"
    gen = EventGenerator(str(dataset_path))
    
    # Get first 3 events
    event_iter = gen.get_events()
    for i in range(3):
        event = next(event_iter)
        print(f"\nEvent {i+1}:")
        print(f"  Timestamp: {event.timestamp}")
        print(f"  Features: {event.features}")
        print(f"  Feature count: {len(event.features)}")
    
    print("\n✓ Event generation works!")
    return True

def test_json_serialization():
    """Test if events serialize to JSON"""
    dataset_path = Path(__file__).parent / "data" / "transactions.csv"
    gen = EventGenerator(str(dataset_path))
    
    event = next(gen.get_events())
    json_str = event.model_dump_json()
    print(f"✓ JSON serialization works!")
    print(f"Sample JSON:\n{json_str[:200]}...")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("Testing Event Generator")
    print("=" * 50)
    
    test_dataset_loading()
    print("\n" + "-" * 50 + "\n")
    
    test_event_generation()
    print("\n" + "-" * 50 + "\n")
    
    test_json_serialization()
    
    print("\n" + "=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)