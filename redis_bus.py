import redis
import json
import logging
import os
import queue
import threading
from typing import Callable, Any, Dict, List

logger = logging.getLogger(__name__)

class LocalMemoryBus:
    """
    In-Memory Message Bus replacement for Redis.
    Allows running the swarm in a single Python process without external dependencies.
    """
    def __init__(self):
        self.channels: Dict[str, List[Callable]] = {}
        self.lock = threading.Lock()
        self.message_queue = queue.Queue()
        self.running = True
        
    def connect(self):
        logger.info("✅ Connected to Local Memory Bus")
        return True

    def publish(self, channel: str, message: Any):
        # Serialize to ensure simulation of real network behavior (and separation)
        if not isinstance(message, str):
            try:
                # Store as object for local, but safe copy recommended
                pass 
            except Exception as e:
                logger.error(f"❌ Failed to process message: {e}")
                return

        # Distribute immediately to subscribers (or queue if we want async)
        with self.lock:
            if channel in self.channels:
                for callback in self.channels[channel]:
                    # Call in a separate thread/loop or directly? 
                    # Directly is dangerous for blocking, so we'll just execute safely
                    try:
                        # We pass the raw message object for simplicity in local mode
                        callback(message)
                    except Exception as e:
                        logger.error(f"❌ Error in local subscriber: {e}")
        
        logger.debug(f"📤 [LocalBus] Published to {channel}")

    def subscribe(self, channel: str, callback: Callable[[Any], None]):
        with self.lock:
            if channel not in self.channels:
                self.channels[channel] = []
            self.channels[channel].append(callback)
        logger.info(f"Fg [LocalBus] Subscribed to {channel}")

    def listen_sync(self):
        # In this local model, callbacks are triggered on publish.
        # So we just sleep to keep the thread alive if it's the main loop.
        import time
        time.sleep(0.1)

class RedisBus:
    def __init__(self, host="redis", port=6379, db=0):
        self.host = os.getenv("REDIS_HOST", host)
        self.port = int(os.getenv("REDIS_PORT", port))
        self.db = int(os.getenv("REDIS_DB", db))
        self.redis = None
        self.pubsub = None

    def connect(self):
        try:
            self.redis = redis.Redis(host=self.host, port=self.port, db=self.db, decode_responses=True)
            self.redis.ping()
            logger.info(f"✅ Connected to Redis at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            return False

    def publish(self, channel: str, message: Any):
        if not self.redis:
            logger.warning("⚠️ Redis not connected, cannot publish")
            return
        
        if not isinstance(message, str):
            try:
                message = json.dumps(message)
            except Exception as e:
                logger.error(f"❌ Failed to serialize message: {e}")
                return

        self.redis.publish(channel, message)
        logger.debug(f"📤 Published to {channel}: {message[:50]}...")

    def subscribe(self, channel: str, callback: Callable[[Any], None]):
        if not self.redis:
            logger.warning("⚠️ Redis not connected, cannot subscribe")
            return

        if not self.pubsub:
            self.pubsub = self.redis.pubsub()

        def handler(message):
            if message['type'] == 'message':
                data = message['data']
                try:
                    # Try to parse JSON
                    data = json.loads(data)
                except json.JSONDecodeError:
                    pass # Keep as string
                
                callback(data)

        self.pubsub.subscribe(**{channel: handler})
        logger.info(f"Fg Subscribed to {channel}")
        
        # Start listener thread if not already running
        # For async usage we might need a different approach, but for now thread is okay for simple agents
        if not self.pubsub.connection:
             self.pubsub.run_in_thread(sleep_time=0.001)

    def listen_sync(self):
        """Blocking listen for main thread usage"""
        if not self.pubsub:
            return
            
        for message in self.pubsub.listen():
             pass # Handlers are called automatically via subscribe callback
