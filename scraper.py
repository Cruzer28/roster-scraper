import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin
import json

class RosterScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_from_url(self, url):
        """Scrape roster data directly from URL"""
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return self.scrape_from_html(response.text, url)
    
    def scrape_from_html(self, html_content, url=''):
        """Parse HTML content and extract roster data"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove common non-roster elements first
        for tag in soup.find_all(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()
        
        # Detect platform and use appropriate parser
        if 'sidearmdev' in html_content or 'sidearm' in html_content.lower():
            return self._parse_sidearm(soup, url)
        elif 'prestosports' in html_content.lower():
            return self._parse_presto(soup, url)
        else:
            # Generic parser
            return self._parse_generic(soup, url)
    
    def _parse_sidearm(self, soup, url):
        """Parse Sidearm Sports platform sites (like OK State)"""
        roster_data = {
            'team_name': '',
            'coaches': [],
            'players': [],
            'platform': 'sidearm'
        }
        
        # Extract team name from title
        title = soup.find('title')
        if title:
            title_text = title.text
            title_text = re.sub(r'\s*-\s*Roster.*', '', title_text, flags=re.I)
            title_text = re.sub(r'\s*-.*Athletics.*', '', title_text, flags=re.I)
            title_text = re.sub(r'\s*Roster.*', '', title_text, flags=re.I)
            title_text = re.sub(r'\s*\d{4}-?\d{0,2}\s*', '', title_text)  # Remove years like "2025-26"
            roster_data['team_name'] = title_text.strip()
        
        # Look for ALL person containers (both players and coaches)
        person_containers = soup.find_all(['div', 'li', 'article'], class_=re.compile(
            r'(roster[-_]?player|athlete[-_]?card|player[-_]?card|roster[-_]?card|s-person-card|person[-_]?card)',
            re.I
        ))
        
        if not person_containers:
            person_containers = soup.find_all(['div', 'li', 'article'], attrs={
                'data-player': True
            }) or soup.find_all(['div', 'li', 'article'], attrs={
                'data-athlete': True
            })
        
        # Extract all people, then separate based on whether they have a position
        seen_players = set()
        seen_coaches = set()
        
        for container in person_containers:
            person = self._extract_player_from_sidearm_card(container, url)
            
            if not person or not person.get('last_name'):
                continue
            
            # Filter out navigation/junk
            name_check = f"{person.get('first_name', '')} {person.get('last_name', '')}".lower()
            skip_keywords = ['news', 'schedule', 'stats', 'roster', 'jersey', 'number',
                           'related', 'more', 'view', 'profile', 'bio', 'back', 'forward',
                           'previous', 'next', 'game', 'media', 'social']
            
            if any(keyword in name_check for keyword in skip_keywords):
                continue
            
            if person.get('last_name', '').replace('#', '').strip().isdigit():
                continue
            
            # Decide if this is a player or coach based on position/number
            # For basketball: G/F/C positions indicate player
            # For baseball/softball: Having a jersey number indicates player
            has_basketball_position = person.get('position', '') in ['G', 'F', 'C', 'PG', 'SG', 'SF', 'PF', 'G/F', 'F/G', 'F/C']
            has_number = person.get('number', '').strip() != ''
            
            # Someone is a player if they have a basketball position OR a jersey number
            is_player = has_basketball_position or has_number
            
            if is_player:
                # This is a player
                player_key = f"{person.get('first_name', '').lower()}_{person.get('last_name', '').lower()}"
                if player_key not in seen_players:
                    seen_players.add(player_key)
                    roster_data['players'].append(person)
            else:
                # No player position = likely a coach/staff member
                # Convert to coach format and use their title/byline as position
                coach = {
                    'first_name': person.get('first_name', ''),
                    'last_name': person.get('last_name', ''),
                    'full_name': person.get('full_name', ''),
                    'title': person.get('position', ''),
                    'photo': person.get('photo', ''),
                    'dropline1': '',
                    'dropline2': ''
                }
                
                # Try to find their actual title in the container
                full_text = container.get_text()
                title_patterns = [
                    r'(HEAD COACH)',
                    r'(ASSISTANT COACH)',
                    r'(ASSOCIATE.*?COACH)',
                    r'(ASSISTANT.*?COACH)',
                    r'(.*?COACH)',  # Catch any other coach titles
                ]
                for pattern in title_patterns:
                    match = re.search(pattern, full_text, re.I)
                    if match:
                        coach['title'] = match.group(1).upper()
                        break
                
                # Only include if "COACH" is in their title and we have less than 3 coaches
                if 'COACH' in coach['title'].upper() and len(roster_data['coaches']) < 3:
                    coach_key = f"{coach['first_name'].lower()}_{coach['last_name'].lower()}"
                    if coach_key not in seen_coaches:
                        seen_coaches.add(coach_key)
                        roster_data['coaches'].append(coach)
        
        # Fallback to generic parser if no people found
        if not roster_data['players'] and not roster_data['coaches']:
            roster_data = self._parse_generic(soup, url)
            roster_data['platform'] = 'sidearm-fallback'
        
        return roster_data
    
    def _extract_player_from_sidearm_card(self, container, base_url):
        """Extract player info from a Sidearm roster card"""
        player = {
            'number': '',
            'first_name': '',
            'last_name': '',
            'full_name': '',  # Combined name for baseball/softball
            'position': '',
            'photo': '',
            'height': '',
            'weight': ''
        }
        
        full_text = container.get_text(separator=' ', strip=True)
        
        # Find name
        name_elem = container.find(['h3', 'h4', 'h5', 'a'], class_=re.compile(r'name', re.I))
        if not name_elem:
            name_elem = container.find(['h3', 'h4', 'h5', 'strong'])
        if not name_elem:
            name_elem = container.find('a', href=re.compile(r'/player/|/athlete/|/roster/', re.I))
        
        if name_elem:
            name_text = name_elem.get_text(strip=True)
            name_text = re.sub(r'^#?\d{1,3}\s*', '', name_text)
            name_parts = name_text.split()
            if len(name_parts) >= 2:
                player['first_name'] = name_parts[0]
                player['last_name'] = ' '.join(name_parts[1:])
                player['full_name'] = f"{player['first_name']} {player['last_name']}"
        
        # Find jersey number - try data attributes first
        if container.has_attr('data-number'):
            player['number'] = container['data-number']
        elif container.has_attr('data-jersey'):
            player['number'] = container['data-jersey']
        
        # Look for Sidearm's stamp element (where OK State hides jersey numbers)
        if not player['number']:
            stamp_elem = container.find('div', attrs={'data-test-id': 's-stamp__root'})
            if not stamp_elem:
                stamp_elem = container.find('div', class_=re.compile(r's-stamp'))
            
            if stamp_elem:
                stamp_text_elem = stamp_elem.find('span', class_=re.compile(r's-stamp__text'))
                if stamp_text_elem:
                    # Get text, remove "Jersey Number" label
                    stamp_text = stamp_text_elem.get_text(strip=True)
                    stamp_text = re.sub(r'Jersey Number\s*', '', stamp_text, flags=re.I)
                    # Extract just the number
                    number_match = re.search(r'\d{1,3}', stamp_text)
                    if number_match:
                        player['number'] = number_match.group()
        
        # Try finding number in specific elements
        if not player['number']:
            number_elem = container.find(class_=re.compile(r'(^|\s)number($|\s)|(^|\s)jersey($|\s)', re.I))
            if number_elem:
                number_text = number_elem.get_text(strip=True)
                number_match = re.search(r'\d{1,3}', number_text)
                if number_match:
                    player['number'] = number_match.group()
        
        # Search in spans with specific classes
        if not player['number']:
            spans = container.find_all('span')
            for span in spans:
                span_class = ' '.join(span.get('class', []))
                if 'number' in span_class.lower() or 'jersey' in span_class.lower():
                    num_match = re.search(r'\d{1,3}', span.get_text())
                    if num_match:
                        player['number'] = num_match.group()
                        break
        
        # Last resort - search in full text
        if not player['number']:
            number_patterns = [
                r'#(\d{1,3})\b',
                r'No\.?\s*(\d{1,3})\b',
                r'Jersey\s*(\d{1,3})\b',
            ]
            for pattern in number_patterns:
                match = re.search(pattern, full_text)
                if match:
                    player['number'] = match.group(1)
                    break
        
        # Find position
        position_patterns = [
            r'Position\s+([A-Z]{1,3}(?:/[A-Z]{1,3})?)\b',
            r'\b(G|F|C|PG|SG|SF|PF|G/F|F/G|F/C)\b',
            r'\b(Guard|Forward|Center)\b'
        ]
        
        for pattern in position_patterns:
            match = re.search(pattern, full_text)
            if match:
                pos = match.group(1)
                if pos == 'Guard':
                    pos = 'G'
                elif pos == 'Forward':
                    pos = 'F'
                elif pos == 'Center':
                    pos = 'C'
                player['position'] = pos
                break
        
        # Find academic year (Fr, So, Jr, Sr)
        year_match = re.search(r'Academic Year\s+(Fr\.?|So\.?|Jr\.?|Sr\.?)\b', full_text, re.I)
        if not year_match:
            year_match = re.search(r'\b(Freshman|Sophomore|Junior|Senior)\b', full_text, re.I)
        if not year_match:
            year_match = re.search(r'\b(Fr\.?|So\.?|Jr\.?|Sr\.?)\b', full_text)
        
        if year_match:
            year = year_match.group(1)
            # Normalize to abbreviation
            year_map = {
                'Freshman': 'Fr', 'Fr.': 'Fr',
                'Sophomore': 'So', 'So.': 'So',
                'Junior': 'Jr', 'Jr.': 'Jr',
                'Senior': 'Sr', 'Sr.': 'Sr'
            }
            player['year'] = year_map.get(year, year)
        
        # Find height - matches patterns like "6' 1''" or "6-1" or "Height 6' 1''"
        height_match = re.search(r"Height\s+(\d+['\"]?\s*\d+['\"]?)", full_text)
        if not height_match:
            height_match = re.search(r"(\d+['\"]?\s*-?\s*\d+['\"]?)", full_text)
        
        if height_match:
            player['height'] = height_match.group(1).strip()
        
        # Find weight - matches patterns like "175 lbs" or "Weight 175"
        weight_match = re.search(r"Weight\s+(\d+)\s*lbs?", full_text, re.I)
        if not weight_match:
            weight_match = re.search(r"(\d{3})\s*lbs?", full_text)
        
        if weight_match:
            player['weight'] = weight_match.group(1)
        
        # Find photo
        img = container.find('img')
        if img and img.get('src'):
            src = img['src']
            if 'placeholder' not in src.lower() and 'default' not in src.lower():
                player['photo'] = urljoin(base_url, src)
        
        return player
    
    def _extract_coach_from_card(self, container, base_url):
        """Extract coach info from a card"""
        coach = {
            'first_name': '',
            'last_name': '',
            'title': '',
            'dropline1': '',
            'dropline2': ''
        }
        
        # Find name
        name_elem = container.find(['h3', 'h4', 'h5', 'a', 'strong'])
        if name_elem:
            name_text = name_elem.get_text(strip=True)
            name_parts = name_text.split()
            if len(name_parts) >= 2:
                coach['first_name'] = name_parts[0]
                coach['last_name'] = ' '.join(name_parts[1:])
        
        # Find title
        title_elem = container.find(class_=re.compile(r'title|position|role', re.I))
        if title_elem:
            coach['title'] = title_elem.get_text(strip=True).upper()
        else:
            text = container.get_text()
            title_patterns = [
                r'(HEAD COACH)',
                r'(ASSISTANT COACH)',
                r'(ASSOCIATE.*COACH)',
                r'(DIRECTOR)',
            ]
            for pattern in title_patterns:
                match = re.search(pattern, text, re.I)
                if match:
                    coach['title'] = match.group(1).upper()
                    break
        
        return coach
    
    def _parse_presto(self, soup, url):
        """Parse Presto Sports platform sites"""
        roster_data = {
            'team_name': '',
            'coaches': [],
            'players': [],
            'platform': 'presto'
        }
        
        tables = soup.find_all('table', class_=re.compile(r'roster', re.I))
        for table in tables:
            rows = table.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 3:
                    player = {
                        'number': cols[0].text.strip() if len(cols) > 0 else '',
                        'first_name': '',
                        'last_name': '',
                        'position': cols[-1].text.strip() if len(cols) > 2 else '',
                        'photo': ''
                    }
                    
                    name_col = cols[1] if len(cols) > 1 else cols[0]
                    name = name_col.text.strip()
                    name_parts = name.split()
                    if len(name_parts) >= 2:
                        player['first_name'] = name_parts[0]
                        player['last_name'] = ' '.join(name_parts[1:])
                    
                    img = row.find('img')
                    if img and img.get('src'):
                        player['photo'] = urljoin(url, img['src'])
                    
                    if player['last_name']:
                        roster_data['players'].append(player)
        
        return roster_data
    
    def _parse_generic(self, soup, url):
        """Generic parser for unknown platforms"""
        roster_data = {
            'team_name': '',
            'coaches': [],
            'players': [],
            'platform': 'generic'
        }
        
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 2:
                for row in rows[1:]:
                    cols = row.find_all(['td', 'th'])
                    if len(cols) >= 2:
                        text_cols = [col.text.strip() for col in cols]
                        
                        number = ''
                        for col in text_cols:
                            if col.isdigit() and len(col) <= 3:
                                number = col
                                break
                        
                        name = max(text_cols, key=len) if text_cols else ''
                        name_parts = name.split()
                        
                        if len(name_parts) >= 2:
                            player = {
                                'number': number,
                                'first_name': name_parts[0],
                                'last_name': ' '.join(name_parts[1:]),
                                'position': '',
                                'photo': ''
                            }
                            roster_data['players'].append(player)
        
        return roster_data
