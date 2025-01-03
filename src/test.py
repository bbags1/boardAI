from main import AIBoardMember

from main import AIBoardMember

def test_board_member():
    board_member = AIBoardMember()
    
    # Test presentation analysis
    test_presentation = """
    Our Q4 results show a 15% increase in revenue, but we're seeing increased competition 
    in our main market. We're proposing a $10M investment in R&D to develop new product lines.
    Customer acquisition costs have risen by 20% year-over-year.
    """
    
    print("=== Board Member Analysis ===")
    print(board_member.listen_to_presentation(test_presentation))
    
    print("\n=== Board Member Questions ===")
    print(board_member.ask_question("market competition and R&D investment"))

if __name__ == "__main__":
    test_board_member()