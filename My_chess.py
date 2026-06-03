import subprocess
import os

def talk(cmd, process):
    process.stdin.write(cmd + "\n")
    process.stdin.flush()

def get_ai_move(process):
    talk("go movetime 1000", process)
    while True:
        line = process.stdout.readline().strip()
        if line.startswith("bestmove"):
            return line.split()[1]

def start_game():
    # LOOK HERE: This name MUST be exactly what you see in your folder[cite: 1]
    engine_name = "stockfish-windows-x86-64-avx2.exe" 
    
    if not os.path.exists(engine_name):
        print(f"ERROR: I can't find '{engine_name}' in this folder!")
        print("Make sure this script and the stockfish file are in the same place.")
        return

    try:
        engine = subprocess.Popen(
            engine_name,
            universal_newlines=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            bufsize=1
        )
    except Exception as e:
        print(f"The engine failed to start: {e}")
        return

    talk("uci", engine)
    talk("isready", engine)
    
    moves = []
    print("--- GAME STARTED ---")
    print("Type a move like e2e4 and press Enter.")

    while True:
        move = input("\nYour move: ")
        if move.lower() in ['quit', 'exit']: break
        moves.append(move)

        # Update Stockfish with the current move list[cite: 1]
        talk("position startpos moves " + " ".join(moves), engine)
        
        print("AI is thinking...")
        ai_move = get_ai_move(engine)
        moves.append(ai_move)
        
        print(f"AI played: {ai_move}")
        print(f"Full history: {' '.join(moves)}")

if __name__ == "__main__":
    start_game()
