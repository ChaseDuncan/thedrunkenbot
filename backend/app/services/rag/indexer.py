import re
import json
import logging
import os
from pathlib import Path

import chromadb
from chromadb.config import Settings
from app.services.rag.utils import chunker, embedder

logger = logging.getLogger(__name__)

class Indexer:
    def __init__(self, collection_name: str = "lyric_chunks", reset: bool = False):
        """
        Creates Indexer by initializing ChromaDB persistent client. Set reset to True to refresh indexing.

        :param collection_name: Name of collection to retrieve or create
        :param reset: Reset the collection if it exists
        """
        self.client = chromadb.PersistentClient(settings=Settings(anonymized_telemetry=False)) 

        if reset:
            try:
                self.client.delete_collection(name=collection_name)
            except:
                pass # Collection does not exist

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hsnw:space": "cosine"}
        )

    
    def _clean_lyrics(self, lyrics: str) -> str:
        """
        Cleans text of lyrics scraped from Genius. Strips section 
        markers, e.g., [Intro], [Verse 1], etc., and removes extra
        whitespace.

        :param lyrics: Raw lyric string
        :type lyrics: str
        :return: Cleaned lyric string
        :rtype: str
        """
        text = re.sub(r'\[.*?\]', '', lyrics)
        text = re.sub(r'\n\s*\n', '\n', text)
        return text.strip()



    def index_from_json(self, json_path: str):
        """
        Indexes json representing data from Genius downloaded using lyricsgenius library.
        
        :param json_path: Path to json of Genius data download
        :type json_path: str
        """
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            artist_name = data['artist_name']
            artist_slug = re.sub(r"\s", "-", artist_name)
            songs  = data['songs']
        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse {json_path}: {e}")
            return
        
        for song in songs:
            try:
                title = song["title"]
                title_slug = re.sub(r"\s", "-", title)
                lyrics = self._clean_lyrics(song["lyrics"])
                album_name = song.get("album", {}).get("name")
            
                if not lyrics.strip():
                    logger.warning(f"Skipping '{title}': empty lyrics after cleaning")
                    continue
                
                chunks = chunker.chunk(lyrics)
                chunked_texts = [chunk.text for chunk in chunks]
                embeddings = embedder.encode(chunked_texts)

                metadatas = [{"artist": artist_name,
                              "title": title,
                              "album": album_name,
                              }] * len(chunked_texts)
                
                ids = [f"{artist_slug}_{title_slug}_{i}" for i in range(len(chunked_texts))]
                self.collection.add(documents=chunked_texts,
                                embeddings=embeddings.tolist(),
                                metadatas=metadatas,
                                ids=ids)

            except KeyError as e:
                logger.warning(f"Skipping song in {json_path} because of missing key {e}")

    def index_dir(self, json_dir: str, recursive: bool = True):
        """
        Recursively indexes directory of Genius data that was scraped using lyricsgenius 

        :param json_dir: Path to json dir
        :param recursive: Indicates whether to recursively index subdirectories of json dir
        :type json_dir: str
        """
        json_dir = Path(json_dir)

        if recursive:
            json_files = json_dir.rglob("*.json")
        else:
            json_files = json_dir.glob("*.json")
        
        for json_file in json_files:
            logger.info(f"Indexing json file: {json_file}")
            self.index_from_json(json_file)
        
        logger.info(f"Indexing complete. Total chunks: {self.collection.count()}")
        

            