# Base image with Python
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY examples examples
COPY rocketleague_replay_coach/ ./rocketleague_replay_coach
COPY setup.py . 
COPY replay_coach.sh .
COPY rattletrap .
COPY schema.json .

ENV PATH=/app:$PATH

# Run the application
CMD ["bash", "replay_coach.sh"]
