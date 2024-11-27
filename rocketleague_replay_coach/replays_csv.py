import os
from rattleplayer import RattlePlayer

# Path to the directory containing replay files
replay_dir = os.path.join(os.getcwd(), 'json')
csv_output_dir = os.path.join(os.getcwd(), 'csv')

if not os.path.exists(csv_output_dir):
    os.makedirs(csv_output_dir)

for replay_file in os.listdir(replay_dir):
    if replay_file.endswith(".json"):  
        replay_path = os.path.join(replay_dir, replay_file)
        
        try:

            rattleplayer = RattlePlayer(replay_path)
            csv_data = rattleplayer.generate_csv()
            csv_file_path = os.path.join(csv_output_dir, f"{os.path.splitext(replay_file)[0]}_{rattleplayer.game.game_playlist}_{rattleplayer.game.game_region}.csv")
            with open(csv_file_path, 'w') as csv_file:
                csv_file.write(csv_data)

            print(f"CSV for {replay_file} written to {csv_file_path}")

        except Exception as e:
            print(f"Error parsing {replay_file}: {str(e)}")


