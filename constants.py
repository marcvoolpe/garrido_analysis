COLS = {
    'comprehension_attempts': 'intro.1.player.comprehension_attempts',
    'retailer_choice': 'intro.1.group.retailer_choice',
    'supplier_choice': 'intro.1.group.supplier_choice',
    'payoff': 'experiment.1.player.payoff',
    'profit': 'experiment.1.player.profit',
    'role': 'participant.role',
    'first_mover': 'session.first_mover_role'
}

TN = [
    '1_C_Supplier_First_AI',
    '2_C_Supplier_First_Human',
    '3_B_Retailer_First_AI',
    '4_B_Retailer_First_Human',
    '5_A_Supplier_First_AI',
    '6_A_Supplier_First_Human',
    '7_C_Retailer_First_AI',
    '8_C_Retailer_First_Human',
    '9_B_Supplier_First_AI',
    '10_B_Supplier_First_Human',
    '11_A_Retailer_First_AI',
    '12_A_Retailer_First_Human'
]

PATH = "data/all_apps_wide_2026-02-04.csv"

CLASSES = ['A', 'B', 'C']
SUPERIOR = {'A': 'A',
            'B': 'NONE',
            'C': 'B'}
