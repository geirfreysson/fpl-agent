"""
Fantasy Premier League Data Collector

This script collects data from FPL API endpoints and stores it locally.
It's designed to run once every 24 hours to avoid overloading the API.
"""

import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FPLDataCollector:
    def __init__(self, data_dir: str = "fpl_data/fpl_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.base_url = "https://fantasy.premierleague.com/api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def _should_update_data(self, filename: str) -> bool:
        """Check if data should be updated (once per 24 hours)"""
        filepath = self.data_dir / filename
        if not filepath.exists():
            return True
            
        # Check if file is older than 24 hours
        file_time = datetime.fromtimestamp(filepath.stat().st_mtime)
        return datetime.now() - file_time > timedelta(hours=24)
    
    def _fetch_json(self, url: str) -> Optional[Dict]:
        """Fetch JSON data from URL with error handling"""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def _save_json(self, data: Dict, filename: str) -> None:
        """Save JSON data to file"""
        filepath = self.data_dir / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved: {filepath}")
    
    def collect_bootstrap_static(self) -> bool:
        """Collect main FPL data (teams, players, gameweeks, etc.)"""
        filename = "bootstrap_static.json"
        if not self._should_update_data(filename):
            logger.info(f"Bootstrap static data is up to date")
            return True
            
        data = self._fetch_json(f"{self.base_url}/bootstrap-static/")
        if data:
            self._save_json(data, filename)
            return True
        return False
    
    def collect_fixtures(self) -> bool:
        """Collect all fixtures for the season"""
        filename = "fixtures.json"
        if not self._should_update_data(filename):
            logger.info(f"Fixtures data is up to date")
            return True
            
        data = self._fetch_json(f"{self.base_url}/fixtures/")
        if data:
            self._save_json(data, filename)
            return True
        return False
    
    def collect_current_gameweek_live(self) -> bool:
        """Collect live data for current gameweek"""
        # First get bootstrap data to find current gameweek
        bootstrap_file = self.data_dir / "bootstrap_static.json"
        if not bootstrap_file.exists():
            logger.error("Bootstrap data not found. Run collect_bootstrap_static first.")
            return False
            
        with open(bootstrap_file, 'r') as f:
            bootstrap_data = json.load(f)
        
        # Find current gameweek
        current_gw = None
        for event in bootstrap_data.get('events', []):
            if event.get('is_current', False):
                current_gw = event.get('id')
                break
        
        if not current_gw:
            logger.warning("Could not find current gameweek")
            return False
            
        filename = f"gameweek_{current_gw}_live.json"
        if not self._should_update_data(filename):
            logger.info(f"Current gameweek live data is up to date")
            return True
            
        data = self._fetch_json(f"{self.base_url}/event/{current_gw}/live/")
        if data:
            self._save_json(data, filename)
            return True
        return False
    
    def collect_player_summaries(self, limit: int = 150) -> bool:
        """Collect detailed player summaries (limited to avoid API overload)"""
        # Get bootstrap data to find player IDs
        bootstrap_file = self.data_dir / "bootstrap_static.json"
        if not bootstrap_file.exists():
            logger.error("Bootstrap data not found. Run collect_bootstrap_static first.")
            return False
            
        with open(bootstrap_file, 'r') as f:
            bootstrap_data = json.load(f)
        
        players = bootstrap_data.get('elements', [])
        
        # Sort players by total points to get the most relevant ones
        players.sort(key=lambda x: x.get('total_points', 0), reverse=True)
        
        # Limit to top players to avoid overwhelming the API
        top_players = players[:limit]
        
        filename = "player_summaries.json"
        if not self._should_update_data(filename):
            logger.info(f"Player summaries data is up to date")
            return True
        
        player_summaries = {}
        for i, player in enumerate(top_players):
            player_id = player.get('id')
            if player_id:
                logger.info(f"Fetching player {i+1}/{len(top_players)}: {player.get('web_name', 'Unknown')}")
                
                data = self._fetch_json(f"{self.base_url}/element-summary/{player_id}/")
                if data:
                    player_summaries[player_id] = data
                    
                # Rate limiting - wait between requests
                time.sleep(0.5)
        
        if player_summaries:
            self._save_json(player_summaries, filename)
            return True
        return False
    
    def collect_recent_gameweeks_live(self, num_gameweeks: int = 5) -> bool:
        """Collect live data for recent gameweeks"""
        # Get bootstrap data to find recent gameweeks
        bootstrap_file = self.data_dir / "bootstrap_static.json"
        if not bootstrap_file.exists():
            logger.error("Bootstrap data not found. Run collect_bootstrap_static first.")
            return False
            
        with open(bootstrap_file, 'r') as f:
            bootstrap_data = json.load(f)
        
        # Find recent finished gameweeks
        recent_gws = []
        for event in bootstrap_data.get('events', []):
            if event.get('finished', False):
                recent_gws.append(event.get('id'))
        
        # Get the last num_gameweeks
        recent_gws = recent_gws[-num_gameweeks:]
        
        success = True
        for gw in recent_gws:
            filename = f"gameweek_{gw}_live.json"
            if not self._should_update_data(filename):
                logger.info(f"Gameweek {gw} live data is up to date")
                continue
                
            data = self._fetch_json(f"{self.base_url}/event/{gw}/live/")
            if data:
                self._save_json(data, filename)
            else:
                success = False
                
            # Rate limiting
            time.sleep(0.5)
        
        return success
    
    def collect_all_data(self) -> bool:
        """Collect all FPL data"""
        logger.info("Starting FPL data collection...")
        
        success = True
        
        # Collect bootstrap data first (contains all basic info)
        if not self.collect_bootstrap_static():
            logger.error("Failed to collect bootstrap static data")
            success = False
        
        # Collect fixtures
        if not self.collect_fixtures():
            logger.error("Failed to collect fixtures data")
            success = False
        
        # Collect current gameweek live data
        if not self.collect_current_gameweek_live():
            logger.error("Failed to collect current gameweek live data")
            success = False
        
        # Collect recent gameweeks live data
        if not self.collect_recent_gameweeks_live():
            logger.error("Failed to collect recent gameweeks live data")
            success = False
        
        # Collect player summaries for top players
        if not self.collect_player_summaries():
            logger.error("Failed to collect player summaries")
            success = False
        
        if success:
            logger.info("FPL data collection completed successfully")
        else:
            logger.warning("FPL data collection completed with some errors")
        
        return success

def main():
    """Main function to run data collection"""
    collector = FPLDataCollector()
    collector.collect_all_data()

if __name__ == "__main__":
    main()