import json
import sys
import logging
import redis
import pymysql
import time
from urllib.parse import urlparse

DB_HOST = "kris-aurora-cluster.cluster-csfwoeoec4om.us-east-1.rds.amazonaws.com"
DB_USER = "admin"
DB_PASS = "AtThisbluedot123gz"
DB_NAME = "w5_cache_db"
DB_TABLE = "heroes"
REDIS_URL = "redis://master.w5-redis-cluster.dtqqmb.use1.cache.amazonaws.com:6379"
TTL = 60  # Time to Live for cached data (in seconds)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class DB:
    def __init__(self, **params):
        self.host = params.get('host')
        self.user = params.get('user')
        self.password = params.get('password')
        self.db = params.get('db')
        self.conn = None

    def connect(self):
        try:
            self.conn = pymysql.connect(host=self.host, user=self.user, password=self.password, db=self.db)
        except pymysql.Error as e:
            logger.error(f"ERROR: Could not connect to MySQL instance.\n{e}")
            sys.exit()
        return self.conn.cursor(pymysql.cursors.DictCursor)

    def query(self, sql):
        cursor = self.connect()
        cursor.execute(sql)
        results = cursor.fetchall()
        self.conn.close()
        return results

    def record(self, sql, values):
        cursor = self.connect()
        cursor.execute(sql, values)
        result = cursor.fetchone()
        self.conn.commit()
        self.conn.close()
        return result

    def get_idx(self, table_name):
        sql = f"SELECT MAX(id) as max_id FROM `{table_name}`"
        result = self.query(sql)
        if result and result[0]['max_id'] is not None:
            return result[0]['max_id'] + 1
        return 1

    def insert(self, idx, data, table_name):
        columns = ', '.join(f"`{key}`" for key in data.keys())
        placeholders = ', '.join('%s' for _ in data.values())
        values = list(data.values())
        sql = f"INSERT INTO `{table_name}` (`id`, {columns}) VALUES (%s, {placeholders})"
        return self.record(sql, [idx] + values)

def read(use_cache, xps, Database, Cache):
    start_time = time.time()
    results = []
    not_found_in_cache = []

    if use_cache:
        cached_results = Cache.mget([f"hero:{xp}" for xp in xps])
        for i, cached_result in enumerate(cached_results):
            if cached_result:
                results.append(json.loads(cached_result.decode('utf-8')))
            else:
                not_found_in_cache.append(xps[i])
    else:
        not_found_in_cache = xps

    if not_found_in_cache:
        sql = f"SELECT id, hero, power, name, xp, color FROM `{DB_TABLE}` WHERE id IN ({','.join(map(str, not_found_in_cache))})"
        db_results = Database.query(sql)
        results.extend(db_results)
        if use_cache and db_results:
            for hero in db_results:
                Cache.setex(f"hero:{hero['id']}", TTL, json.dumps(hero))

    duration = time.time() - start_time
    logger.info(f"Read operation took {duration:.4f} seconds")
    return results

def write(use_cache, sqls, Database, Cache):
    start_time = time.time()
    for data in sqls:
        idx = Database.get_idx(DB_TABLE)
        Database.insert(idx, data, DB_TABLE)
        if use_cache:
            Cache.setex(f"hero:{idx}", TTL, json.dumps(data))
    duration = time.time() - start_time
    logger.info(f"Write operation took {duration:.4f} seconds")
    return {"status": "success", "message": f"Wrote {len(sqls)} records"}

def lambda_handler(event, context):
    start_time = time.time()
    use_cache = event.get('USE_CACHE', False)
    request_type = event.get('REQUEST')
    Database = None
    Cache = None

    try:
        Database = DB(host=DB_HOST, user=DB_USER, password=DB_PASS, db=DB_NAME)
        parsed_url = urlparse(REDIS_URL)
        Cache = redis.Redis(host=parsed_url.hostname, port=parsed_url.port, ssl=True)
        Cache.ping() # Check Redis connection
        logger.info("Successfully connected to Redis")
    except redis.exceptions.ConnectionError as e:
        logger.error(f"ERROR: Could not connect to Redis instance.\n{e}")
        Database = DB(host=DB_HOST, user=DB_USER, password=DB_PASS, db=DB_NAME) # Fallback to DB only
        Cache = None
    except pymysql.Error as e:
        logger.error(f"ERROR: Could not connect to MySQL instance during handler initialization.\n{e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Could not connect to database'})
        }

    result = []
    if request_type == 'read':
        xps = event.get('xps', [])
        result = read(use_cache, xps, Database, Cache)
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    elif request_type == 'write':
        sqls = event.get('sqls', [])
        result = write(use_cache, sqls, Database, Cache)
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid REQUEST type'})
        }

    total_duration = time.time() - start_time
    logger.info(f"Lambda function execution time: {total_duration:.4f} seconds")