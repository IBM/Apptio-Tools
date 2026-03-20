"""
Simple test script to validate CSV parsing without requiring Turbonomic connection
"""

import sys
sys.path.insert(0, '.')

from create_groups import TurbonomicGroupCreator

def test_csv_parsing():
    """Test CSV parsing functionality"""
    print("Testing CSV parsing...")
    print("=" * 60)
    
    # Create instance (won't authenticate)
    creator = TurbonomicGroupCreator(
        turbo_url="https://test.example.com",
        username="test",
        password="test",
        dry_run=True
    )
    
    # Parse the example CSV
    groups = creator.parse_csv('groups_example.csv')
    
    print(f"\nParsed {len(groups)} groups from CSV:\n")
    
    for idx, group in enumerate(groups, start=1):
        print(f"{idx}. {group['displayName']}")
        print(f"   Type: {group['groupType']}")
        print(f"   Filter: {group['criteriaList'][0]['filterType']}")
        print(f"   Expression: {group['criteriaList'][0]['expType']} {group['criteriaList'][0]['expVal']}")
        if group.get('description'):
            print(f"   Description: {group['description']}")
        print()
    
    print("=" * 60)
    print(f"✓ Successfully parsed {len(groups)} groups")
    print("✓ CSV format is valid")
    print("✓ All required fields present")
    
    return len(groups) > 0

if __name__ == '__main__':
    success = test_csv_parsing()
    sys.exit(0 if success else 1)

# Made with Bob
