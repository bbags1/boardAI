from main import AdvisoryBoard

def test_advisory_board():
    # Create board and add advisors
    board = AdvisoryBoard()
    board.add_advisor("legal")
    board.add_advisor("financial")
    board.add_advisor("technology")
    
    # Test topic for discussion
    topic = """
    Our company is considering acquiring a competing AI startup for $50M.
    The startup has valuable patents but is currently operating at a loss.
    They have some pending litigation regarding data privacy.
    """
    
    # Test individual analysis
    print("=== INDIVIDUAL LEGAL ANALYSIS ===")
    print(board.get_individual_analysis(topic, "legal"))
    print("\n")
    
    # Test group discussion
    print("=== GROUP DISCUSSION ===")
    print(board.facilitate_discussion(topic, ["legal", "financial", "technology"]))

if __name__ == "__main__":
    test_advisory_board()