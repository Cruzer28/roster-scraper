from flask import Flask, render_template, request, jsonify, send_file
import csv
import io
from scraper import RosterScraper

app = Flask(__name__)
scraper = RosterScraper()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/debug')
def debug():
    return render_template('debug.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    method = data.get('method')
    
    try:
        if method == 'url':
            url = data.get('url')
            roster_data = scraper.scrape_from_url(url)
        elif method == 'html':
            html_content = data.get('html')
            url = data.get('url', '')
            roster_data = scraper.scrape_from_html(html_content, url)
        else:
            return jsonify({'error': 'Invalid method'}), 400
        
        return jsonify({
            'success': True,
            'data': roster_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/export/csv', methods=['POST'])
def export_csv():
    data = request.json
    roster_data = data.get('roster_data')
    sport = data.get('sport', 'basketball')  # Default to basketball
    export_options = data.get('export_options', {})
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    if sport in ['baseball', 'softball']:
        # Baseball/Softball format - combined names, no season
        # Team info section
        writer.writerow(['Team Name', '', '', 'Record:', '', '', '', ''])
        writer.writerow(['Mascot:', '', '', 'Rank:', '', '', '', ''])
        writer.writerow(['Color 1:', '', '', 'Location:', '', '', '', ''])
        writer.writerow(['Color 2:', '', '', 'Logo:', '', '', '', ''])
        writer.writerow(['Color 3:', '', '', '', '', '', '', ''])
        writer.writerow(['', '', '', '', '', '', '', ''])
        
        # Coaches section (first 3 only) - combined names
        writer.writerow(['', 'Coaches', '', '', '', '', ''])
        writer.writerow(['Name', 'Title', 'Dropline 1', '', 'Dropline 2', '', ''])
        for coach in roster_data.get('coaches', [])[:3]:  # Limit to first 3
            full_name = coach.get('full_name', '') or f"{coach.get('first_name', '')} {coach.get('last_name', '')}".strip()
            writer.writerow([
                full_name,
                coach.get('title', ''),
                coach.get('dropline1', ''),
                '',
                coach.get('dropline2', ''),
                '', ''
            ])
        
        writer.writerow(['', '', '', '', '', '', ''])
        
        # Players section - Name in column A, Number in column B
        writer.writerow(['', 'PLAYERS', '', '', '', '', ''])
        
        # Simple header - no empty column between Name and #
        header = ['Name', '#', '', '', '', '', '']
        writer.writerow(header)
        
        for player in roster_data.get('players', []):
            full_name = player.get('full_name', '') or f"{player.get('first_name', '')} {player.get('last_name', '')}".strip()
            row = [
                full_name,
                player.get('number', '') if export_options.get('number', True) else '',
                '',
                '',
                '',
                '',
                ''
            ]
            writer.writerow(row)
    
    else:
        # Basketball format (original)
        writer.writerow(['Team Name', roster_data.get('team_name', ''), '', 'Location:', '', '', '', '', ''])
        writer.writerow(['Rank:', '', '', 'Logo:', '', '', '', '', ''])
        writer.writerow(['Color:', '', '', '', '', '', '', '', ''])
        writer.writerow(['', '', '', '', '', '', '', '', ''])
        
        # Write coaches (first 3 only)
        writer.writerow(['', 'Coaches', '', '', '', '', '', '', ''])
        writer.writerow(['Last Name', 'First Name', 'Title', 'Dropline 1', '', 'Dropline 2', '', '', ''])
        for coach in roster_data.get('coaches', [])[:3]:  # Limit to first 3
            writer.writerow([
                coach.get('last_name', ''),
                coach.get('first_name', ''),
                coach.get('title', ''),
                coach.get('dropline1', ''),
                '',
                coach.get('dropline2', ''),
                '', '', ''
            ])
        
        writer.writerow(['', '', '', '', '', '', '', '', ''])
        
        # Write players
        writer.writerow(['', 'PLAYERS', '', '', '', '', '', '', ''])
        
        header = []
        if export_options.get('number', True):
            header.append('#')
        header.extend(['First Name', 'Last Name'])
        if export_options.get('position', True):
            header.append('Pos')
        if export_options.get('year', True):
            header.append('Year')
        if export_options.get('height', True):
            header.append('Ht')
        if export_options.get('weight', True):
            header.append('Wt')
        if export_options.get('photo', True):
            header.append('Photo')
        
        while len(header) < 9:
            header.append('')
        
        writer.writerow(header)
        
        for player in roster_data.get('players', []):
            row = []
            if export_options.get('number', True):
                row.append(player.get('number', ''))
            row.extend([
                player.get('first_name', ''),
                player.get('last_name', '')
            ])
            if export_options.get('position', True):
                row.append(player.get('position', ''))
            if export_options.get('year', True):
                row.append(player.get('year', ''))
            if export_options.get('height', True):
                row.append(player.get('height', ''))
            if export_options.get('weight', True):
                row.append(player.get('weight', ''))
            if export_options.get('photo', True):
                row.append(player.get('photo', ''))
            
            while len(row) < 9:
                row.append('')
            
            writer.writerow(row)
    
    # Convert to bytes for download
    output.seek(0)
    csv_bytes = io.BytesIO(output.getvalue().encode('utf-8'))
    csv_bytes.seek(0)
    
    sport_name = sport.capitalize()
    return send_file(
        csv_bytes,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f"{roster_data.get('team_name', 'roster')}_{sport_name}_roster.csv"
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
