import openai
import pandas as pd
import os
from openai import OpenAI
import numpy as np
import matplotlib
matplotlib.use('Agg')  # or 'Agg' for headless mode
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

player_the_name = os.getenv("PLAYER_NAME")

# Initialize OpenAI client
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)
intervalx = 1000

def read_csv(file_path, time_interval=25600):
    """Reads the CSV file and returns a time-based filtered sample."""
    df = pd.read_csv(file_path)
    
    # Sample rows based on a time interval
    df['time'] = df['time'] * 10000000  # if time is in seconds, convert to microseconds
    df['time'] = df['time'].astype(int)

    # Filter by specific time intervals
    filtered_df = df[df['time'] % time_interval == 0]

    return filtered_df.to_csv(index=False)

def format_data_for_prompt(filename,data_csv):
    """
    Formats the relevant player information from the CSV into a structured format
    that can be sent to the GPT API for coaching feedback.
    """
    base_name, _ = os.path.splitext(filename)

    # Split the filename by underscores
    parts = base_name.split('_')

    if parts[1] == 'heatseeker':
        prompt = f"""
        The following represents a heatseeker replay of Rocket League.  Everyone has full boost always, and the ball follows a heatseeking trajectory towards goal. It includes the players and the ball locations for a subset of timestamps during the match. (Note: every {intervalx}th timestamp has been filtered)
        Kindly analyze the match and provide heatseaker coaching feedback for {player_the_name}.

        {data_csv}
        """
        return prompt

    prompt = f"""
    The following represents a match replay of Rocket League. It includes the players and the ball locations for a subset of timestamps during the match. (Note: every {intervalx}th timestamp has been filtered)
    Kindly analyze the match and provide coaching feedback for {player_the_name}.

    {data_csv}
    """
    return prompt



def get_coaching_feedback(prompt):
    """Sends a prompt to the GPT-4 API and returns the feedback."""
    try:
        stream = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": prompt,
            }],
            model="gpt-4o",
            stream=True,
        )
        feedback = ''
        for chunk in stream:
            feedback += chunk.choices[0].delta.content or ""
        return feedback
    except Exception as e:
        print(f"Error while fetching feedback: {e}")
        return None

def generate_session_summary(all_feedback):
    """Generates an overview summary of the session's feedback using GPT-4."""
    try:
        # Combine all feedback from all matches into one single string
        prompt = f"Please provide a session-wide summary of the following coaching feedback for Rocket League matches:\n\n{all_feedback}"

        stream = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": prompt,
            }],
            model="gpt-4o",
            stream=True,
        )
        summary = ''
        for chunk in stream:
            summary += chunk.choices[0].delta.content or ""
        return summary
    except Exception as e:
        print(f"Error while generating session summary: {e}")
        return None

def plot_regular(filename):
    # Read the match data from CSV
    data = pd.read_csv("csv/" + filename)

    # Create a 3D plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    dataf = data #.head(7111)

    # Separate the players and the ball
    players = dataf[dataf['player_name'] != 'ball']  # All players
    ball = dataf[dataf['player_name'] == 'ball']    # Ball

    # Assign team colors and coached player
    orange_team = players[players['team'] == 0]
    blue_team = players[players['team'] == 1]
    coached_player = players[players['player_name'] == player_the_name]
    
    # Adjust the field and axis limits based on the Rocket League field size
    # Field size: x = ±4096, y = ±5120 (as per your data)
    field_length = 5200*2 #4002*2  # Field length (X-axis)
    field_width =  4000*2  # Field width (Y-axis)
    field_height = 2000  # Field height (Z-axis)

    # Scale the coordinates to match the game scale
    max_coordinate = 5200
    ax.set_xlim(-max_coordinate, max_coordinate)
    ax.set_ylim(-max_coordinate, max_coordinate)
    ax.set_zlim(0, field_height)


    # Outline the field in the plot (centered at origin)
    ax.plot([-field_width / 2, -field_width / 2], [-field_length / 2, field_length / 2], [0, 0], color='black', linewidth=2)  # Left side line
    ax.plot([-field_width / 2, field_width / 2], [-field_length / 2, -field_length / 2], [0, 0], color='black', linewidth=2)  # Bottom line
    ax.plot([field_width / 2, field_width / 2], [-field_length / 2, field_length / 2], [0, 0], color='black', linewidth=2)  # Right side line
    ax.plot([-field_width / 2, field_width / 2], [field_length / 2, field_length / 2], [0, 0], color='black', linewidth=2)  # Top line

    # Plot the goal areas (on both ends of the field)
    goal_width = 892*2  # Goal area depth along the X-axis
    goal_depth = 880
    ax.plot([-goal_width / 2, goal_width / 2], [-field_length/2, -field_length/2], [0,0],  color='red', linewidth=2)  
    ax.plot([-goal_width / 2, goal_width / 2], [-field_length/2-goal_depth, -field_length/2-goal_depth], [0,0],  color='red', linewidth=2)  
    ax.plot([-goal_width / 2, -goal_width / 2], [-field_length/2, -field_length/2-goal_depth], [0,0],  color='red', linewidth=2)  
    ax.plot([goal_width / 2, goal_width / 2], [-field_length/2, -field_length/2-goal_depth], [0,0],  color='red', linewidth=2)  
    ax.plot([-goal_width / 2, goal_width / 2], [field_length/2, field_length/2], [0,0],  color='red', linewidth=2)  
    ax.plot([-goal_width / 2, goal_width / 2], [field_length/2+goal_depth, field_length/2+goal_depth], [0,0],  color='red', linewidth=2)  
    ax.plot([-goal_width / 2, -goal_width / 2], [field_length/2, field_length/2+goal_depth], [0,0],  color='red', linewidth=2)  
    ax.plot([goal_width / 2, goal_width / 2], [field_length/2, field_length/2+goal_depth], [0,0],  color='red', linewidth=2)  

    # Plot the center line (midfield)
    ax.plot([-field_width / 2, field_width / 2], [0, 0], [0,0], color='blue', linewidth=2, linestyle='--')  # Center line

    # Boost Pad Locations (given coordinates for each pad)
    boost_pads = [
        [0.0, -4240.0, 70.0], [-1792.0, -4184.0, 70.0], [1792.0, -4184.0, 70.0],
        [-3072.0, -4096.0, 73.0], [3072.0, -4096.0, 73.0], [-940.0, -3308.0, 70.0],
        [940.0, -3308.0, 70.0], [0.0, -2816.0, 70.0], [-3584.0, -2484.0, 70.0],
        [3584.0, -2484.0, 70.0], [-1788.0, -2300.0, 70.0], [1788.0, -2300.0, 70.0],
        [-2048.0, -1036.0, 70.0], [0.0, -1024.0, 70.0], [2048.0, -1036.0, 70.0],
        [-3584.0, 0.0, 73.0], [-1024.0, 0.0, 70.0], [1024.0, 0.0, 70.0],
        [3584.0, 0.0, 73.0], [-2048.0, 1036.0, 70.0], [0.0, 1024.0, 70.0],
        [2048.0, 1036.0, 70.0], [-1788.0, 2300.0, 70.0], [1788.0, 2300.0, 70.0],
        [-3584.0, 2484.0, 70.0], [3584.0, 2484.0, 70.0], [0.0, 2816.0, 70.0],
        [-940.0, 3310.0, 70.0], [940.0, 3308.0, 70.0], [-3072.0, 4096.0, 73.0],
        [3072.0, 4096.0, 73.0], [-1792.0, 4184.0, 70.0], [1792.0, 4184.0, 70.0],
        [0.0, 4240.0, 70.0]
    ]

    # Plot the Boost Pads: Small pads in yellow and large pads in red
    for pad in boost_pads:
        if pad[2] == 73.0:  # Large boost pads
            ax.scatter(pad[0], pad[1], pad[2], c='gold', marker='.', s=150, label=None)
        else:  # Small boost pads
            ax.scatter(pad[0], pad[1], pad[2], c='gold', marker='.', s=80, label=None)


    # Plot the players in blue
    ax.scatter(blue_team['location_x'], blue_team['location_y'], blue_team['location_z'], 
            c='blue', label='Blue Team', s=2, alpha=0.05, marker='o')


    # Plot the players in orange
    ax.scatter(orange_team['location_x'], orange_team['location_y'], orange_team['location_z'], 
               c='orange', label='Orange Team', s=2, alpha=0.05, marker='o')

    
    # Plot the coached player in green
    ax.scatter(coached_player['location_x'], coached_player['location_y'], coached_player['location_z'], 
            c='purple', label=player_the_name, s=4, alpha=0.1, marker='o')


    # Plot the ball (smaller, gray color)
    ax.scatter(ball['location_x'], ball['location_y'], ball['location_z'], 
               c='gray', label='Ball', s=1, alpha=0.01, marker='o', edgecolors='black')
    
    # Labeling and title
    ax.set_xlabel('X Position (Field width)')
    ax.set_ylabel('Y Position (Field length)')
    ax.set_zlabel('Z Position (Height)')
    ax.set_title(f'3D Visualization of Rocket League Match: {filename}', fontsize=14)

    ax.grid(True)

    # Set view angle for better visualization
    ax.view_init(elev=30, azim=-60)

    # Add the legend to label the teams and ball
    ax.legend(loc='upper left')

    output_filename1 = f"output/player_locations_{filename}_1.png"
    plt.savefig(output_filename1)

    # Set the view to a top-down perspective
    ax.view_init(elev=90, azim=-90)
    output_filename2 = f"output/player_locations_{filename}_2.png"
    plt.savefig(output_filename2)

    plt.close(fig)
    
    return [output_filename1, output_filename2]


def plot_heatseeker(filename):
    # Read the match data from CSV
    data = pd.read_csv("csv/" + filename)

    # Create a 3D plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    dataf = data #.head(7111)

    # Separate the players and the ball
    players = dataf[dataf['player_name'] != 'ball']  # All players
    ball = dataf[dataf['player_name'] == 'ball']    # Ball

    # Assign team colors and coached player
    orange_team = players[players['team'] == 0]
    blue_team = players[players['team'] == 1]
    coached_player = players[players['player_name'] == player_the_name]
    
    # Adjust the field and axis limits based on the Rocket League field size
    # Field size: x = ±4096, y = ±5120 (as per your data)
    field_length = 5200*2*100 #4002*2  # Field length (
    field_width =  4000*2*100  # Field width 
    field_height = 2000 * 100 # Field height 

    # # Scale the coordinates to match the game scale
    max_coordinate = 5200 * 100
    ax.set_xlim(-max_coordinate, max_coordinate)
    ax.set_ylim(-max_coordinate, max_coordinate)
    ax.set_zlim(0, field_height)


    # Outline the field in the plot (centered at origin)
    ax.plot([-field_width / 2, -field_width / 2], [-field_length / 2, field_length / 2], [0, 0], color='black', linewidth=2)  # Left side line
    ax.plot([-field_width / 2, field_width / 2], [-field_length / 2, -field_length / 2], [0, 0], color='black', linewidth=2)  # Bottom line
    ax.plot([field_width / 2, field_width / 2], [-field_length / 2, field_length / 2], [0, 0], color='black', linewidth=2)  # Right side line
    ax.plot([-field_width / 2, field_width / 2], [field_length / 2, field_length / 2], [0, 0], color='black', linewidth=2)  # Top line

    # Plot the goal areas (on both ends of the field)
    goal_width = 892*2  # Goal area depth along the X-axis
    goal_depth = 880
    ax.plot([-goal_width / 2, goal_width / 2], [-field_length/2, -field_length/2], [0,0],  color='red', linewidth=2)  
    ax.plot([-goal_width / 2, goal_width / 2], [-field_length/2-goal_depth, -field_length/2-goal_depth], [0,0],  color='red', linewidth=2)  
    ax.plot([-goal_width / 2, -goal_width / 2], [-field_length/2, -field_length/2-goal_depth], [0,0],  color='red', linewidth=2)  
    ax.plot([goal_width / 2, goal_width / 2], [-field_length/2, -field_length/2-goal_depth], [0,0],  color='red', linewidth=2)  
    ax.plot([-goal_width / 2, goal_width / 2], [field_length/2, field_length/2], [0,0],  color='red', linewidth=2)  
    ax.plot([-goal_width / 2, goal_width / 2], [field_length/2+goal_depth, field_length/2+goal_depth], [0,0],  color='red', linewidth=2)  
    ax.plot([-goal_width / 2, -goal_width / 2], [field_length/2, field_length/2+goal_depth], [0,0],  color='red', linewidth=2)  
    ax.plot([goal_width / 2, goal_width / 2], [field_length/2, field_length/2+goal_depth], [0,0],  color='red', linewidth=2)  

    # # Plot the center line (midfield)
    ax.plot([-field_width / 2, field_width / 2], [0, 0], [0,0], color='blue', linewidth=2, linestyle='--')  # Center line

    # Plot the players in blue
    ax.scatter(blue_team['location_x'], blue_team['location_y'], blue_team['location_z'], 
            c='blue', label='Blue Team', s=2, alpha=0.05, marker='o')

    # Plot the players in orange
    ax.scatter(orange_team['location_x'], orange_team['location_y'], orange_team['location_z'], 
               c='orange', label='Orange Team', s=2, alpha=0.05, marker='o')

    # Plot the coached player in green
    ax.scatter(coached_player['location_x'], coached_player['location_y'], coached_player['location_z'], 
            c='purple', label=player_the_name, s=4, alpha=0.1, marker='o')


    # Plot the ball (smaller, gray color)
    # Plot the ball with a larger marker for smoother appearance
    ax.plot(ball['location_x'], ball['location_y'], ball['location_z'], 
            c='gray', label='Ball', marker=None, alpha=1, markeredgecolor='black')

    # ax.scatter(ball['location_x'], ball['location_y'], ball['location_z'], 
    #            c='gray', label='Ball', s=1, alpha=1, marker='o', edgecolors='black')
    
    # Labeling and title
    ax.set_xlabel('X Position (Field width)')
    ax.set_ylabel('Y Position (Field length)')
    ax.set_zlabel('Z Position (Height)')
    base_name, _ = os.path.splitext(filename)
    # Split the filename by underscores
    parts = base_name.split('_')
    ax.set_title(f'3D Visualization of Rocket League Match: {parts[1]} {parts[0]} {parts[2]}', fontsize=12)

    ax.grid(True)

    # Set view angle for better visualization
    ax.view_init(elev=30, azim=-60)

    # Add the legend to label the teams and ball
    ax.legend(loc='upper left')

    output_filename1 = f"output/player_locations_{filename}_1.png"
    plt.savefig(output_filename1)

    # Set the view to a top-down perspective
    ax.view_init(elev=90, azim=-90)
    output_filename2 = f"output/player_locations_{filename}_2.png"
    plt.savefig(output_filename2)

    plt.close(fig)
    
    return [output_filename1, output_filename2]


def plot_rocket_league_match(filename):

    base_name, _ = os.path.splitext(filename)
    # Split the filename by underscores
    parts = base_name.split('_')

    if parts[1] == 'heatseeker':
        return plot_heatseeker(filename)

    return plot_regular(filename)


def main():
    # Path to the directory containing replay files
    input_dir = os.path.join(os.getcwd(), 'csv')
    output_dir = os.path.join(os.getcwd(), 'output')

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    all_feedback = ""  # Variable to accumulate feedback from all matches
    
    # Loop through all .csv files in the input directory
    for csv_file in os.listdir(input_dir):
        if csv_file.endswith('.csv'):  # Only process .csv files
            csv_path = os.path.join(input_dir, csv_file)
            
            try:
                # Read the CSV and format the data for the prompt
                data = read_csv(csv_path)
                prompt = format_data_for_prompt(csv_file,data)
                images = plot_rocket_league_match(csv_file)
                images_md = "\n\n".join([f"![img]({image})" for image in images])

                print(f"Sending prompt to ChatGPT for {csv_file}")

                # Constructing the feedback string including the markdown and coaching feedback
                feedback = f"{images_md}\n\n" + get_coaching_feedback(prompt)
                
                if feedback:
                    print(f"Coaching Feedback for {csv_file}: \n{feedback}\n")
                    
                    # Append feedback to the accumulated all_feedback string
                    all_feedback += f"## Feedback for {csv_file}\n\n{feedback}\n\n"
                    
                    # Save the feedback as a .md file in the output directory
                    md_file_path = os.path.join(output_dir, f"{os.path.splitext(csv_file)[0]}.md")
                    with open(md_file_path, 'w') as md_file:
                        md_file.write(f"# Feedback for {csv_file}\n\n{feedback}")
                    print(f"Feedback saved to {md_file_path}\n")
                else:
                    print(f"No feedback received for {csv_file}.\n")
            
            except Exception as e:
                print(f"Error processing {csv_file}: {str(e)}")

    # After generating all coaching feedback files, generate the session-wide summary
    session_summary = generate_session_summary(all_feedback)
    
    if session_summary:
        # Write the session summary to a dedicated file
        session_summary_path = "session_summary.md"
        with open(session_summary_path, 'w') as summary_file:
            summary_file.write(f"# Session Summary\n\n{session_summary}\n\n{all_feedback}")
        print(f"Session summary saved to {session_summary_path}")
    else:
        print("Failed to generate session summary.")

# Run the main function
if __name__ == "__main__":
    main()
