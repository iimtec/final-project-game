#!/usr/bin/env python3
"""
Script to view and analyze game statistics from the CSV file.
Run this to see your gameplay data displayed nicely.
"""

import csv
import os
from stats_manager import StatsManager

def view_stats():
    stats_manager = StatsManager()
    
    print("\n" + "="*80)
    print("GAME STATISTICS SUMMARY")
    print("="*80 + "\n")
    
    if not os.path.exists(stats_manager.csv_file):
        print("No game data found yet. Play some games to generate stats!")
        return
    
    # Read CSV and display
    records = []
    try:
        with open(stats_manager.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                levels_completed = int(row.get('Levels_Completed', 0))
                print(f"Game #{row['Game_ID']:>3} | Levels: {levels_completed:>2} | Steps: {row['Steps']:>5} | Time: {row['Time']:>4}s | Enemies: {row['Enemies_Encountered']:>2} | Score: {row['Score']:>4} | Result: {row['Result']}")
    except Exception as e:
        print(f"Error reading stats: {e}")
        return
    
    if not records:
        print("No game records found.")
        return
    
    # Calculate summary
    print("\n" + "-"*80)
    print("SUMMARY STATISTICS")
    print("-"*80 + "\n")
    
    wins = sum(1 for r in records if r['Result'] == 'Win')
    losses = sum(1 for r in records if r['Result'] == 'Loss')
    win_rate = (wins / len(records) * 100) if records else 0
    
    avg_steps = sum(int(r['Steps']) for r in records) / len(records)
    avg_time = sum(int(r['Time']) for r in records) / len(records)
    avg_levels = sum(int(r['Levels_Completed']) for r in records) / len(records)
    total_score = sum(int(r['Score']) for r in records)
    
    print(f"Total Games Played:  {len(records)}")
    print(f"Wins (completed levels): {sum(1 for r in records if int(r['Levels_Completed']) > 0)}")
    print(f"Losses (no levels): {sum(1 for r in records if int(r['Levels_Completed']) == 0)}")
    print(f"Average Levels per Game: {avg_levels:.1f}")
    print(f"Average Steps:       {avg_steps:.0f}")
    print(f"Average Time:        {avg_time:.0f} seconds")
    print(f"Total Score:         {total_score}")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    view_stats()
