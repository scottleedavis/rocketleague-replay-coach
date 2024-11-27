# rocketleague replay coach

#### **Rocket League Replay Coach**
A tool that interfaces with AI for analyzing Rocket League replays, offering insights into gameplay strategy, player performance, and goal scenarios. Ideal for casual players, competitive gamers, and coaches aiming to refine gameplay.

See an [example summary here.](examples/example_summary.md)

---

### **Docker Setup**

```
docker build -t rocketleague-replay-coach .
```

#### **Example**

```
docker run -e PLAYER_NAME="Ether Zephyr" -e OPENAI_API_KEY="YourAPIKey" -e RL_REPLAY_DIR="$(pwd)/examples"  rocketleague-replay-coach
```

### **Local Setup**

1. Clone the repository:
   ```bash
   git clone https://github.com/scottleedavis/rocketleague-replay-coach.git
   cd rocketleague-replay-coach
   ```
2. Install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   pip install -r requirements.txt

   ```
3. [rattletrap](https://github.com/tfausak/rattletrap) available on the $PATH (provided in this repo)


#### **Example**
```
export RL_REPLAY_DIR="$(pwd)/examples" 
export OPENAI_API_KEY="sk-proj-your-secet-openai-key"
export PLAYER_NAME="Ether Zephyr"
./replay_coach.sh
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