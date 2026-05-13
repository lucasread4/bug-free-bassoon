from flask import Flask, render_template, request, jsonify, session
import requests
import os
from datetime import datetime
import secrets
from functools import wraps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# API Configuration - Read from environment variable
API_BASE_URL = "https://api.balldontlie.io/fifa/worldcup/v1"
API_KEY = os.environ.get('FIFA_API_KEY')

# Check if API key is set
if not API_KEY:
    print("⚠️ WARNING: FIFA_API_KEY environment variable not set!")
    print("Please create a .env file with: FIFA_API_KEY=your_api_key_here")

# API Headers
headers = {'Authorization': API_KEY} if API_KEY else {}from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import os
import json
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Sample data (same as your HTML version)
SAMPLE_PLAYERS = [
    {"name": "Lionel Messi", "position": "Forward", "club": "Inter Miami"},
    {"name": "Cristiano Ronaldo", "position": "Forward", "club": "Al Nassr"},
    {"name": "Kylian Mbappé", "position": "Forward", "club": "Real Madrid"},
    {"name": "Erling Haaland", "position": "Forward", "club": "Man City"},
    {"name": "Neymar Jr", "position": "Forward", "club": "Al Hilal"},
    {"name": "Mohamed Salah", "position": "Forward", "club": "Liverpool"},
    {"name": "Kevin De Bruyne", "position": "Midfielder", "club": "Man City"},
    {"name": "Jude Bellingham", "position": "Midfielder", "club": "Real Madrid"},
    {"name": "Rodri", "position": "Midfielder", "club": "Man City"},
    {"name": "Pedri", "position": "Midfielder", "club": "Barcelona"},
    {"name": "Virgil van Dijk", "position": "Defender", "club": "Liverpool"},
    {"name": "Ruben Dias", "position": "Defender", "club": "Man City"},
    {"name": "Antonio Rüdiger", "position": "Defender", "club": "Real Madrid"},
    {"name": "Alphonso Davies", "position": "Defender", "club": "Bayern"},
    {"name": "Thibaut Courtois", "position": "Goalkeeper", "club": "Real Madrid"},
    {"name": "Alisson Becker", "position": "Goalkeeper", "club": "Liverpool"},
    {"name": "Ederson", "position": "Goalkeeper", "club": "Man City"},
    {"name": "Manuel Neuer", "position": "Goalkeeper", "club": "Bayern"},
    {"name": "Bukayo Saka", "position": "Midfielder", "club": "Arsenal"},
    {"name": "Victor Osimhen", "position": "Forward", "club": "Napoli"},
    {"name": "Jamal Musiala", "position": "Midfielder", "club": "Bayern"},
    {"name": "Rafael Leão", "position": "Forward", "club": "Milan"},
    {"name": "William Saliba", "position": "Defender", "club": "Arsenal"},
    {"name": "Mike Maignan", "position": "Goalkeeper", "club": "Milan"},
    {"name": "Federico Chiesa", "position": "Forward", "club": "Juventus"},
    {"name": "Declan Rice", "position": "Midfielder", "club": "Arsenal"},
    {"name": "Theo Hernández", "position": "Defender", "club": "Milan"},
    {"name": "Kim Min-jae", "position": "Defender", "club": "Bayern"},
    {"name": "Florian Wirtz", "position": "Midfielder", "club": "Leverkusen"},
    {"name": "Lautaro Martínez", "position": "Forward", "club": "Inter"},
    {"name": "Khvicha Kvaratskhelia", "position": "Midfielder", "club": "Napoli"}
]

def initialize_session():
    """Initialize or reset session data"""
    if 'players' not in session:
        # Add unique IDs to players
        players = []
        for idx, player in enumerate(SAMPLE_PLAYERS):
            player_copy = player.copy()
            player_copy['id'] = f"p_{datetime.now().timestamp()}_{idx}_{player['name'].replace(' ', '')}"
            players.append(player_copy)
        session['players'] = players
        session['drafted_ids'] = []
        session['history'] = []
        session['is_custom_data'] = False

@app.route('/')
def index():
    initialize_session()
    return render_template('index.html')

@app.route('/api/players', methods=['GET'])
def get_players():
    """Get all players with draft status"""
    initialize_session()
    players = session.get('players', [])
    drafted_ids = session.get('drafted_ids', [])
    
    # Mark drafted status
    for player in players:
        player['drafted'] = player['id'] in drafted_ids
    
    return jsonify({
        'players': players,
        'drafted_ids': drafted_ids,
        'is_custom_data': session.get('is_custom_data', False)
    })

@app.route('/api/draft', methods=['POST'])
def draft_player():
    """Draft a player"""
    data = request.json
    player_id = data.get('player_id')
    
    if not player_id:
        return jsonify({'error': 'No player ID provided'}), 400
    
    players = session.get('players', [])
    drafted_ids = session.get('drafted_ids', [])
    
    # Check if player exists and not already drafted
    player_exists = any(p['id'] == player_id for p in players)
    if not player_exists or player_id in drafted_ids:
        return jsonify({'error': 'Invalid or already drafted player'}), 400
    
    # Save to history
    history = session.get('history', [])
    history.append(drafted_ids.copy())
    if len(history) > 30:
        history.pop(0)
    session['history'] = history
    
    # Add to drafted
    drafted_ids.append(player_id)
    session['drafted_ids'] = drafted_ids
    session.modified = True
    
    return jsonify({'success': True, 'drafted_ids': drafted_ids})

@app.route('/api/remove', methods=['POST'])
def remove_player():
    """Remove a player from draft"""
    data = request.json
    player_id = data.get('player_id')
    
    if not player_id:
        return jsonify({'error': 'No player ID provided'}), 400
    
    drafted_ids = session.get('drafted_ids', [])
    
    if player_id not in drafted_ids:
        return jsonify({'error': 'Player not in draft'}), 400
    
    # Save to history
    history = session.get('history', [])
    history.append(drafted_ids.copy())
    if len(history) > 30:
        history.pop(0)
    session['history'] = history
    
    # Remove from drafted
    drafted_ids.remove(player_id)
    session['drafted_ids'] = drafted_ids
    session.modified = True
    
    return jsonify({'success': True, 'drafted_ids': drafted_ids})

@app.route('/api/undo', methods=['POST'])
def undo():
    """Undo last draft action"""
    history = session.get('history', [])
    
    if not history:
        return jsonify({'error': 'Nothing to undo'}), 400
    
    previous_state = history.pop()
    session['drafted_ids'] = previous_state
    session['history'] = history
    session.modified = True
    
    return jsonify({'success': True, 'drafted_ids': previous_state})

@app.route('/api/reset', methods=['POST'])
def reset_draft():
    """Reset entire draft"""
    session['drafted_ids'] = []
    session['history'] = []
    session.modified = True
    
    return jsonify({'success': True})

@app.route('/api/load_sample', methods=['POST'])
def load_sample():
    """Load sample data"""
    # Reset players to sample data
    players = []
    for idx, player in enumerate(SAMPLE_PLAYERS):
        player_copy = player.copy()
        player_copy['id'] = f"p_{datetime.now().timestamp()}_{idx}_{player['name'].replace(' ', '')}"
        players.append(player_copy)
    
    session['players'] = players
    session['drafted_ids'] = []
    session['history'] = []
    session['is_custom_data'] = False
    session.modified = True
    
    return jsonify({'success': True})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload and process CSV/Excel file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    
    # Get column mapping from form data
    name_col = request.form.get('name_col', '')
    pos_col = request.form.get('pos_col', '')
    club_col = request.form.get('club_col', '')
    
    try:
        # Read file based on extension
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        # Get headers
        headers = df.columns.tolist()
        
        # If no mapping provided, return headers for mapping UI
        if not name_col:
            return jsonify({
                'headers': headers,
                'preview': df.head(5).to_dict('records'),
                'row_count': len(df)
            })
        
        # Apply mapping
        if name_col not in df.columns:
            return jsonify({'error': f'Column "{name_col}" not found'}), 400
        
        # Process players
        players = []
        for idx, row in df.iterrows():
            name = str(row[name_col]).strip() if pd.notna(row[name_col]) else None
            if not name or name == 'nan':
                continue
            
            # Get position
            position = "Midfielder"
            if pos_col and pos_col in df.columns and pd.notna(row[pos_col]):
                position_raw = str(row[pos_col]).strip()
                # Normalize position
                pos_lower = position_raw.lower()
                pos_map = {
                    "fw": "Forward", "forward": "Forward", "st": "Forward",
                    "mf": "Midfielder", "midfielder": "Midfielder",
                    "df": "Defender", "defender": "Defender", "cb": "Defender",
                    "gk": "Goalkeeper", "goalkeeper": "Goalkeeper"
                }
                if pos_lower in pos_map:
                    position = pos_map[pos_lower]
                elif position_raw.startswith('F'):
                    position = "Forward"
                elif position_raw.startswith('M'):
                    position = "Midfielder"
                elif position_raw.startswith('D'):
                    position = "Defender"
                elif position_raw.startswith('G'):
                    position = "Goalkeeper"
            
            # Get club
            club = "Unknown Club"
            if club_col and club_col in df.columns and pd.notna(row[club_col]):
                club = str(row[club_col]).strip()
            
            players.append({
                'name': name,
                'position': position,
                'club': club,
                'id': f"p_{datetime.now().timestamp()}_{idx}_{name.replace(' ', '')}"
            })
        
        if not players:
            return jsonify({'error': 'No valid players found after mapping'}), 400
        
        # Update session
        session['players'] = players
        session['drafted_ids'] = []
        session['history'] = []
        session['is_custom_data'] = True
        session.modified = True
        
        return jsonify({
            'success': True,
            'player_count': len(players),
            'players': players
        })
        
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
