import logging
import asyncio
import json
import redis.asyncio as aioredis
from app.config import settings

logger = logging.getLogger("gigsurance-backend.redis")

class InMemoryPubSub:
    def __init__(self):
        self.subscribers = []
    
    def subscribe(self, callback):
        if callback not in self.subscribers:
            self.subscribers.append(callback)
        
    def unsubscribe(self, callback):
        if callback in self.subscribers:
            self.subscribers.remove(callback)
            
    async def publish(self, message):
        for callback in self.subscribers:
            try:
                callback(message)
            except Exception as e:
                logger.error(f"Error in pubsub callback: {e}")

class InMemoryPubSubAdapter:
    def __init__(self, pubsub_inst):
        self.pubsub_inst = pubsub_inst
        self.queue = asyncio.Queue()
        
    async def subscribe(self, channel):
        self.pubsub_inst.subscribe(self._on_message)
        
    def _on_message(self, message):
        self.queue.put_nowait(message)
        
    async def listen(self):
        while True:
            msg = await self.queue.get()
            yield {"type": "message", "data": msg}

class InMemoryRedis:
    def __init__(self):
        self.cache = {}
        self.pubsub_inst = InMemoryPubSub()
        logger.info("Initializing fallback In-Memory Redis client")
        
    async def get(self, key):
        return self.cache.get(key)
        
    async def setex(self, key, ttl, value):
        self.cache[key] = value
        return True
        
    async def publish(self, channel, message):
        await self.pubsub_inst.publish(message)
        return 1
        
    def pubsub(self):
        return InMemoryPubSubAdapter(self.pubsub_inst)

class PubSubProxy:
    def __init__(self, proxy):
        self.proxy = proxy
        self.real_pubsub = None
        self.fallback_pubsub = None
        self.is_fallback = False

    async def subscribe(self, channel):
        client = await self.proxy._get_client()
        self.is_fallback = self.proxy.use_fallback
        if self.is_fallback:
            self.fallback_pubsub = client.pubsub()
            await self.fallback_pubsub.subscribe(channel)
        else:
            try:
                self.real_pubsub = client.pubsub()
                await self.real_pubsub.subscribe(channel)
            except Exception:
                self.proxy.use_fallback = True
                self.is_fallback = True
                self.fallback_pubsub = self.proxy.fallback_client.pubsub()
                await self.fallback_pubsub.subscribe(channel)

    async def listen(self):
        if self.is_fallback:
            async for msg in self.fallback_pubsub.listen():
                yield msg
        else:
            try:
                async for msg in self.real_pubsub.listen():
                    yield msg
            except Exception:
                self.proxy.use_fallback = True
                self.is_fallback = True
                self.fallback_pubsub = self.proxy.fallback_client.pubsub()
                await self.fallback_pubsub.subscribe("dummy") # trigger subscribe
                async for msg in self.fallback_pubsub.listen():
                    yield msg

class RedisProxy:
    def __init__(self):
        self.real_client = aioredis.from_url(settings.redis_url, decode_responses=True)
        self.fallback_client = InMemoryRedis()
        self.use_fallback = False
        
    async def _get_client(self):
        if self.use_fallback:
            return self.fallback_client
        try:
            # Verify connectivity with 0.5s timeout
            await asyncio.wait_for(self.real_client.ping(), timeout=0.5)
            return self.real_client
        except Exception:
            logger.warning("Redis is unavailable. Falling back to In-Memory simulation.")
            self.use_fallback = True
            return self.fallback_client

    async def get(self, key):
        client = await self._get_client()
        try:
            return await client.get(key)
        except Exception:
            self.use_fallback = True
            return await self.fallback_client.get(key)

    async def setex(self, key, ttl, value):
        client = await self._get_client()
        try:
            return await client.setex(key, ttl, value)
        except Exception:
            self.use_fallback = True
            return await self.fallback_client.setex(key, ttl, value)

    async def publish(self, channel, message):
        client = await self._get_client()
        try:
            return await client.publish(channel, message)
        except Exception:
            self.use_fallback = True
            return await self.fallback_client.publish(channel, message)

    def pubsub(self):
        return PubSubProxy(self)

# Global singleton
redis_client = RedisProxy()
