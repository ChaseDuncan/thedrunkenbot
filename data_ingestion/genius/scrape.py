#!/usr/bin/env python3
"""
Genius Lyrics Scraper

Scrapes lyrics from Genius.com using the lyricsgenius library.
Designed to be extended with CSV-based artist/album/song specification.

Usage:
    create .env with GENIUS_ACCESS_TOKEN="your_token_here"
    python scrape.py

Requirements:
    pip install lyricsgenius pyyaml
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

try:
    import yaml
    from lyricsgenius import Genius
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Install with: pip install lyricsgenius pyyaml python-dotenv")
    sys.exit(1)

# Load environment variables from .env file
load_dotenv()


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('genius_scraper.log')
    ]
)
logger = logging.getLogger(__name__)


class GeniusScraper:
    """Scraper for Genius lyrics with configuration management."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize scraper with configuration."""
        self.config = self._load_config(config_path)
        self.genius = self._init_genius_client()
        self.output_dir = Path(__file__).parent / self.config['output_dir']
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Metadata tracking
        self.scrape_metadata = {
            'scrape_date': datetime.now().isoformat(),
            'config': self.config,
            'artists_scraped': [],
            'total_songs': 0,
            'errors': []
        }
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        config_file = Path(__file__).parent / config_path
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Loaded configuration from {config_file}")
        return config
    
    def _init_genius_client(self) -> Genius:
        """Initialize Genius API client."""
        # Try to get token from config, then environment variable
        api_token = self.config.get('api_token') or os.getenv('GENIUS_ACCESS_TOKEN')
        
        if not api_token:
            raise ValueError(
                "Genius API token not found. Set GENIUS_ACCESS_TOKEN environment "
                "variable or add 'api_token' to config.yaml"
            )
        
        genius = Genius(
            api_token,
            sleep_time=self.config.get('sleep_time', 0.5),
            timeout=self.config.get('timeout', 15),
            verbose=True,
            remove_section_headers=self.config.get('remove_section_headers', False),
            skip_non_songs=self.config.get('skip_non_songs', True),
            retries=3
        )
        
        logger.info("Initialized Genius API client")
        return genius
    
    def scrape_artist(self, artist_name: str) -> Optional[Dict]:
        """
        Scrape all (or max_songs) for a given artist.
        
        Args:
            artist_name: Name of the artist to scrape
            
        Returns:
            Dictionary with artist data and songs, or None if failed
        """
        logger.info(f"Starting scrape for artist: {artist_name}")
        
        try:
            max_songs = self.config.get('max_songs_per_artist')
            artist = self.genius.search_artist(
                artist_name,
                max_songs=max_songs,
                sort='popularity'
            )
            
            if not artist:
                logger.warning(f"Artist not found: {artist_name}")
                self.scrape_metadata['errors'].append({
                    'artist': artist_name,
                    'error': 'Artist not found'
                })
                return None
            
            logger.info(f"Found {len(artist.songs)} songs for {artist_name}")
            
            # Convert to serializable format
            artist_data = {
                'artist_name': artist.name,
                'artist_id': getattr(artist, '_id', None),
                'num_songs': len(artist.songs),
                'songs': []
            }
            
            for song in artist.songs:
                song_data = {
                    'title': song.title,
                    'song_id': getattr(song, 'id', None),
                    'url': song.url,
                    'lyrics': song.lyrics,
                    'album': getattr(song, 'album', None),
                    'year': getattr(song, 'year', None),
                    'featured_artists': [artist.name for artist in song.featured_artists] 
                        if hasattr(song, 'featured_artists') and song.featured_artists else [],
                    'writer_artists': [artist.name for artist in song.writer_artists] 
                        if hasattr(song, 'writer_artists') and song.writer_artists else [],
                }
                artist_data['songs'].append(song_data)
            
            # Update metadata
            self.scrape_metadata['artists_scraped'].append(artist_name)
            self.scrape_metadata['total_songs'] += len(artist.songs)
            
            return artist_data
            
        except Exception as e:
            logger.error(f"Error scraping {artist_name}: {e}", exc_info=True)
            self.scrape_metadata['errors'].append({
                'artist': artist_name,
                'error': str(e)
            })
            return None
    
    def save_artist_data(self, artist_data: Dict):
        """Save artist data to JSON file."""
        if not artist_data:
            return
        
        # Create artist-specific directory
        artist_name = artist_data['artist_name']
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in artist_name)
        artist_dir = self.output_dir / safe_name
        artist_dir.mkdir(exist_ok=True)
        
        # Save full artist data
        output_file = artist_dir / f"{safe_name}_complete.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(artist_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(artist_data['songs'])} songs to {output_file}")
        
        # Optionally save individual song files
        if self.config.get('save_individual_songs', False):
            for song in artist_data['songs']:
                safe_song_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in song['title'])
                song_file = artist_dir / f"{safe_song_name}.json"
                with open(song_file, 'w', encoding='utf-8') as f:
                    json.dump(song, f, indent=2, ensure_ascii=False)
    
    def save_metadata(self):
        """Save scraping metadata."""
        metadata_file = self.output_dir / "scrape_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.scrape_metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved scrape metadata to {metadata_file}")
    
    def run(self):
        """Run the complete scraping workflow."""
        logger.info("=" * 60)
        logger.info("Starting Genius lyrics scraping")
        logger.info("=" * 60)
        
        artists = self.config.get('artists', [])
        if not artists:
            logger.error("No artists specified in configuration")
            return
        
        logger.info(f"Will scrape {len(artists)} artists")
        
        for i, artist_name in enumerate(artists, 1):
            logger.info(f"\n[{i}/{len(artists)}] Processing: {artist_name}")
            
            artist_data = self.scrape_artist(artist_name)
            if artist_data:
                self.save_artist_data(artist_data)
        
        # Save final metadata
        self.save_metadata()
        
        # Summary
        logger.info("=" * 60)
        logger.info("Scraping complete!")
        logger.info(f"Artists scraped: {len(self.scrape_metadata['artists_scraped'])}")
        logger.info(f"Total songs: {self.scrape_metadata['total_songs']}")
        logger.info(f"Errors: {len(self.scrape_metadata['errors'])}")
        logger.info("=" * 60)


def main():
    """Main entry point."""
    try:
        scraper = GeniusScraper()
        scraper.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()