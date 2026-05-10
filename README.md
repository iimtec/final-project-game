# MAZE RUNNER

## Project Description

Horror Maze Escape is a 2D horror-style maze escape game where players navigate through procedurally generated mazes while avoiding intelligent enemies. The game features progressive difficulty levels, collectible hint items, teleportation portals, and a comprehensive statistics system. Players must find the escape portal on each level to progress, with the ultimate goal of reaching level 5 and escaping the final maze.


---

## Installation

To clone this project:

```sh
git clone https://github.com/iimtec/final-project-game.git
cd final-project-game
```

To create and run Python Environment for this project:

**Windows:**
```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Mac:**
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Running Guide

After activating Python Environment of this project, you can process to run the game by:

**Windows:**
```bat
python main.py
```

**Mac:**
```sh
python3 main.py
```

---

## Tutorial / Usage

### **Getting Started:**
1. Run the game using the command above
2. The main menu will appear with game instructions
3. Click the **"START GAME"** button to begin playing

### **Game Controls:**
- **WASD** - Move around the maze
- **Z Key** - Toggle statistics view during gameplay
- **Mouse** - Click buttons on menu and game-over screens

### **Gameplay Basics:**
- **Objective:** Find the yellow escape portal and reach it to complete the level
- **Enemies:** Killer avatar represent enemies that will chase you if detected (range 200 pixels)
- **Fog of War:** Your visibility is limited to a circular radius around your character
- **Hint Items:** Purple diamond shapes reveal the direction to the escape door
- **Portals:** Cyan circles teleport you to random locations in the maze
- **Score:** Earn points by completing levels

### **Level Progression:**
- Progress through 5 increasingly difficult levels
- Each level has more enemies, reduced visibility and decrease the amount of hint items
- Level 5 features a special red-tinted exit door as the final escape route

### **Statistics:**
- Press **Z** during gameplay to view game statistics
- Press **view stats** button on main menu
- Track your steps, time, enemies encountered, score and result
- Statistics are automatically saved to `game_stats.csv` after each game

### **Game Over:**
- If caught by an enemy, the game ends and displays your final score
- Click **"Retry"** to start a new game
- Click **"Menu"** to return to the main menu
- Click **"Quit"** to exit the game

---

## Game Features

- **Procedurally Generated Mazes:** Unique, randomized maze layouts on each level created using depth-first search algorithm
- **5-Level Progression System:** Progressively challenging levels with increasing difficulty
- **Intelligent Enemy AI:** Multiple enemies with chase mechanics, detection ranges, and autonomous pathfinding
- **Fog of War System:** Dynamic visibility radius that decreases as you progress through levels
- **Teleportation Portals:** Random portals that transport players to different maze locations
- **Hint Items:** Collectible items that show directional arrows pointing to the escape portal
- **Sprite-Based Animation:** Smooth directional animations for player and enemy movement
- **Visual Effects:** Screen shake on enemy encounters, floating text feedback and glowing portal effects
- **Sound Effects:** Audio cues for heartbeat, teleportation, and game-over sound effect
- **Statistics Tracking:** Comprehensive game data recording including steps, time, enemies encountered, score and result
- **Statistics Visualization:** Interactive charts and graphs displaying performance metrics
- **Main Menu System:** Clean, intuitive menu with game instructions, start button, view stats button
- **Game-Over Menu:** Options to retry, return to menu, or quit

---

## Known Bugs

- There is a chance that the elements in the game spawn at the same places

---

## Unfinished Works

All features are implemented

---

## External Sources

**Sound:**
- Ambient music: https://youtu.be/xAO3x-Uhfoo?si=1sbyciBwffv3f9iG
- Heartbeat sound effect (Enemy nearby): https://youtu.be/TgZjYIPPe50?si=P78gjud7Oc195koT
- Screaming sound effect (Gameover): https://youtu.be/5fUAM0dR804?si=0O1P5jmFB9xEJzzL
- Teleport sound effect (Teleport portal): https://youtu.be/7ORuFBPthWQ?si=HDnBjlzZOHWQHVTL
- Escape portal sound effect (Escape portal): https://www.youtube.com/watch?v=rr5CMS2GtCY
