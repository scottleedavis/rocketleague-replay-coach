# rocketleague replay coach

#### **Rocket League Replay Coach**
A tool that interfaces with AI for analyzing Rocket League replays, offering insights into gameplay strategy, player performance, and goal scenarios. Ideal for casual players, competitive gamers, and coaches aiming to refine gameplay.

---

### **Features**
- **Replay Analysis:** Parse Rocket League replays to extract detailed match statistics.
- **Goal Analysis:** Understand the factors behind goals, assists, and defensive plays.
- **Individual Insights:** Analyze player-specific contributions to identify strengths and weaknesses.
- **Integrations:** Extend functionality with tools like CARL for machine learning-driven insights.

---

### **Docker Setup**

```
docker build -t rocketleague-replay-coach .
```

#### **Example**

```
export RL_REPLAY_DIR="/mnt/c/Users/gamez/OneDrive/Documents/My Games/Rocket League/TAGame/DemosEpic/"
export OPENAI_API_KEY="sk-proj-your-secret-openai-key"
export PLAYER_NAME="Your Player Name"
docker run -e PLAYER_NAME="YourPlayerName" -e OPENAI_API_KEY="YourAPIKey" -e RL_REPLAY_DIR="/path/to/replays" rocketleague-replay-coach
```

### **Local Setup**

1. Clone the repository:
   ```bash
   git clone https://github.com/scottleedavis/rocketleague-replay-coach.git
   cd rocketleague-replay-coach
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt

   ```
3.    ...mention rattletrap needs to be on the path.


#### **Example**
```
export OPENAI_API_KEY="sk-proj-your-secet-openai-key"
export PLAYER_NAME="Ether Zephyr"
./replay_example.sh
```

### local replays
```
export RL_REPLAY_DIR="/mnt/c/Users/gamez/OneDrive/Documents/My Games/Rocket League/TAGame/DemosEpic/"
export OPENAI_API_KEY="sk-proj-your-secret-openai-key"
export PLAYER_NAME="Your Player Name"
./replay_coach.sh
```
---


### **Future Plans**
1. **Goal Play Analysis:** Develop in-depth algorithms for analyzing goal scenarios.
2. **Player Metrics:** Provide advanced metrics like reaction times, positioning heatmaps, and boost efficiency.
3. **Integrations:**
   - **CARL:** Leverage machine learning for playstyle recognition and predictive analysis.
   - **Third-Party Tools:** Export data for use in platforms like RLStats or Tracker.

---