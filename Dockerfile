# Base image with Python
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY rocketleague_replay_coach/ ./rocketleague_replay_coach
COPY *.py . 
COPY *.sh .
COPY rattletrap .

# set env variables
# PLAYER_NAME, OPENAI_API_KEY, RL_REPLAY_DIR for all scripts

# Run the application
CMD ["bash", "replay_coach.sh"]
