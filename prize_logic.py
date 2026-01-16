import random

def has_four(n):
    return '4' in str(n)

def solve_prizes(total, n_players):
    if n_players <= 0: return []
    if total < n_players * 100:
        print("Error: Total too low")
        return []
    
    # Heuristic distribution based on user example
    # User: 10000 for 6 -> 5000, 3000, 1000, 200...
    # Ratios approx: 50%, 30%, 10%, remainder split
    
    # distribution = [0] * n_players
    
    # Strategy:
    # 1. Assign min 100 to everyone
    # 2. Distribute remainder with a steep decay
    
    prizes = [100] * n_players
    remainder = total - (100 * n_players)
    
    # Weighted distribution for the surplus
    # Weights for 6 players: 50, 30, 10, 2, 1, 1 -> sum 94
    # Let's use a geometric-ish decay
    weights = []
    for i in range(n_players):
        # 1st gets big chunk, 2nd gets smaller...
        if i == 0: w = 50
        elif i == 1: w = 30
        elif i == 2: w = 10
        else: w = 2 # Low for the rest
        weights.append(w)
        
    weight_sum = sum(weights)
    
    current_distributed = 0
    surplus_prizes = [0] * n_players
    
    # Initial coarse distribution
    for i in range(n_players):
        share = int((weights[i] / weight_sum) * remainder)
        # Round to nearest 100 if possible for clean numbers? User examples are clean.
        # Let's try to keep things at 100 granularity first if total is large
        share = (share // 100) * 100 
        surplus_prizes[i] = share
        current_distributed += share
        
    # Distribute the rest of the remainder (due to rounding)
    leftover = remainder - current_distributed
    # Give to 1st, 2nd...
    idx = 0
    while leftover > 0:
        surplus_prizes[idx] += 100 # Keep 100 granularity
        leftover -= 100
        idx = (idx + 1) % n_players
        
    # Combine
    final_prizes = [p + s for p, s in zip(prizes, surplus_prizes)]
    
    # Sort descending
    final_prizes.sort(reverse=True)
    
    # Fix "4"s
    # If a number has 4, we must move amount to another.
    # While has_bad_numbers:
    #   Find bad number.
    #   Try to move +/- 100 to neighbor.
    #   If neighbor becomes bad, revert and try other direction.
    
    # Let's try a perturbation loop
    attempts = 0
    while attempts < 1000:
        bad_indices = [i for i, x in enumerate(final_prizes) if has_four(x)]
        if not bad_indices:
            break
            
        for i in bad_indices:
            # Try to give 100 to next person (or previous)
            # Preference: Give to previous (higher rank) if possible, or next.
            amount_to_move = 100
            
            # Try giving to rank-1 (higher)
            if i > 0:
                final_prizes[i] -= amount_to_move
                final_prizes[i-1] += amount_to_move
                if not has_four(final_prizes[i]) and not has_four(final_prizes[i-1]) and final_prizes[i-1] >= final_prizes[i]:
                    break # Fixed this one
                # Revert
                final_prizes[i] += amount_to_move
                final_prizes[i-1] -= amount_to_move
                
            # Try giving to rank+1 (lower)
            if i < n_players - 1:
                final_prizes[i] -= amount_to_move
                final_prizes[i+1] += amount_to_move
                 # Check strict sorting violation? User said 1st, 2nd.. maybe ties allowed?
                 # "第一名...第二名..." implies order.
                if not has_four(final_prizes[i]) and fixed_check(final_prizes):
                    break
                # Revert
                final_prizes[i] += amount_to_move
                final_prizes[i+1] -= amount_to_move
                
            # If still stuck, try adding 100? (Must take from someone)
            # Maybe just randomize small amounts?
            
            # Fallback: Just randomize small transfers
            target = (i + 1) % n_players
            final_prizes[i] -= 100
            final_prizes[target] += 100
            final_prizes.sort(reverse=True) # Re-sort to maintain order
            
        attempts += 1
        
    return final_prizes

def fixed_check(prizes):
    # Check strict descending (or equal) and no 4s
    for x in prizes:
        if has_four(x): return False
    return all(prizes[i] >= prizes[i+1] for i in range(len(prizes)-1))

# Test Cases
print("Test 1: 10000, 6")
res = solve_prizes(10000, 6)
print(res, "Sum:", sum(res), "No 4s:", all(not has_four(x) for x in res))

print("\nTest 2: 8888, 5")
res = solve_prizes(8888, 5)
print(res, "Sum:", sum(res), "No 4s:", all(not has_four(x) for x in res))

print("\nTest 3: 4444, 4 (Hard case)")
res = solve_prizes(4444, 4)
print(res, "Sum:", sum(res), "No 4s:", all(not has_four(x) for x in res))
