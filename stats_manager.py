import csv
import os
from datetime import datetime

class StatsManager:
    def __init__(self):
        self.game_id = 0
        self.records = []
        self.csv_file = 'game_stats.csv'
        self.ensure_csv_exists()
        self.load_last_game_id()  # Load the last Game_ID from CSV

    def load_last_game_id(self):
        """Load the highest Game_ID from the CSV file to ensure continuous numbering."""
        try:
            with open(self.csv_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['Game_ID']:
                        self.game_id = max(self.game_id, int(row['Game_ID']))
        except Exception as e:
            print(f"Error loading last game ID: {e}")
            self.game_id = 0

    def ensure_csv_exists(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['Game_ID', 'Steps', 'Time', 'Enemies_Encountered', 'Score', 'Levels_Completed', 'Result'])
                writer.writeheader()

    def record_game(self, steps, time_seconds, enemies, score, result, levels_completed=0):
        self.game_id += 1
        record = {
            "Game_ID": self.game_id,
            "Steps": steps,
            "Time": time_seconds,
            "Enemies_Encountered": enemies,
            "Score": score,
            "Levels_Completed": levels_completed,
            "Result": result
        }
        self.records.append(record)
        self.save_to_csv(record)
        return record

    def save_to_csv(self, record):
        try:
            with open(self.csv_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['Game_ID', 'Steps', 'Time', 'Enemies_Encountered', 'Score', 'Levels_Completed', 'Result'])
                writer.writerow(record)
        except Exception as e:
            print(f"Error saving to CSV: {e}")

    def get_stats_summary(self):
        if not self.records:
            return None
        wins = sum(1 for r in self.records if r['Result'] == 'Win')
        losses = len(self.records) - wins
        avg_steps = sum(r['Steps'] for r in self.records) / len(self.records)
        avg_time = sum(r['Time'] for r in self.records) / len(self.records)
        total_score = sum(r['Score'] for r in self.records)
        return {
            'total_games': len(self.records),
            'wins': wins,
            'losses': losses,
            'win_rate': wins / len(self.records) * 100 if self.records else 0,
            'avg_steps': avg_steps,
            'avg_time': avg_time,
            'total_score': total_score
        }
