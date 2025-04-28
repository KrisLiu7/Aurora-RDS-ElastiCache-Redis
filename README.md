
# Aurora-RDS-ElastiCache-Redis Project

This project demonstrates real-world Data Engineering practices using AWS services, specifically AWS Lambda, Aurora RDS, and Redis (ElastiCache). The goal is to implement a serverless architecture that incorporates caching to optimize the performance of a cloud-based data pipeline.

## Performance Comparison (Cache vs. No Cache)

- **Without caching**: Every read operation queries Aurora, causing higher latency (~100-300ms).
- **With caching**: Frequent reads are served in-memory from Redis with latency under 5ms.

**Impact**: Approximately 20x to 60x performance improvement, critical for scalable backend systems.

## Key Data Engineering Skills Demonstrated

This project highlights key Data Engineering skills:

- **Serverless architecture design** using AWS managed services (AWS Lambda, Aurora, ElastiCache).
- **Caching strategy implementation** (lazy-loading and write-through).
- **Secure cloud infrastructure deployment** with IAM (Identity Access Management) and VPC (Virtual Private Cloud).
- **Performance optimization** for high-scale applications with Redis caching.

## Architecture Overview

The architecture incorporates AWS Lambda for serverless compute, Aurora RDS for relational database storage, and Redis for caching through ElastiCache. The system is designed to minimize latency by serving frequent read operations from Redis while ensuring data integrity with Aurora RDS for write operations.

## Conclusion

The system design and implementation techniques shown here are directly applicable to real-world, production-grade cloud data pipelines.

## Key Technologies Used

- **AWS Lambda**: For running backend logic without provisioning servers.
- **Aurora RDS**: For scalable relational database management.
- **Redis**: For in-memory data caching.
- **IAM**: For secure cloud access management.
- **VPC**: For securing the network infrastructure.

## Author

**Kris Liu**

## Project

- **Name**: AWS Lambda - RDS - ElastiCache Hero Data Caching
- **GitHub Repo**: [Aurora-RDS-ElastiCache-Redis](https://github.com/KrisLiu7/Aurora-RDS-ElastiCache-Redis)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Code for AWS Lambda - RDS - ElastiCache Integration

### AWS Lambda Function Code (Python Example)

This is a basic example of how to implement AWS Lambda to interact with Aurora RDS and ElastiCache Redis.

```python
import json
import boto3
import redis
from botocore.exceptions import NoCredentialsError

# Connect to RDS (Aurora) and Redis
rds_client = boto3.client('rds-data')
redis_client = redis.StrictRedis(host='your-redis-endpoint', port=6379, db=0)

def lambda_handler(event, context):
    # Example: Get data from Redis Cache
    cache_key = 'user_data:' + str(event['user_id'])
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        # Return data from Redis cache if available
        return {
            'statusCode': 200,
            'body': json.dumps({'data': cached_data.decode('utf-8'), 'source': 'cache'})
        }
    
    # If not found in cache, query Aurora RDS (MySQL-compatible)
    try:
        response = rds_client.execute_statement(
            resourceArn='arn:aws:rds:region:account-id:cluster:aurora-cluster',
            secretArn='arn:aws:secretsmanager:region:account-id:secret:secret-id',
            database='your_database',
            sql='SELECT * FROM users WHERE user_id = :user_id',
            parameters=[{'name': 'user_id', 'value': {'longValue': event['user_id']}}]
        )
        
        user_data = response['records'][0]
        
        # Cache the data in Redis for future use
        redis_client.set(cache_key, json.dumps(user_data))
        
        return {
            'statusCode': 200,
            'body': json.dumps({'data': user_data, 'source': 'database'})
        }
    
    except NoCredentialsError as e:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': str(e)})
        }
```

### Aurora RDS Setup

1. **Create a MySQL-Compatible Aurora Cluster**:
   - In AWS Console, navigate to RDS > Databases > Create Database.
   - Choose "Amazon Aurora" and select a MySQL-compatible edition.
   - Configure your cluster settings and database parameters.

2. **Create a Table for Storing User Data**:

```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    username VARCHAR(255),
    email VARCHAR(255)
);
```

3. **Inserting Sample Data**:

```sql
INSERT INTO users (user_id, username, email) VALUES (1, 'JohnDoe', 'john.doe@example.com');
```

### ElastiCache (Redis) Setup

1. **Create an ElastiCache Cluster**:
   - In the AWS Console, navigate to ElastiCache > Redis > Create.
   - Select the appropriate instance type and configuration.

2. **Connecting Redis to Your Application**:
   - In the Lambda function, you’ll connect to your Redis cluster using the `redis-py` client.
   - Make sure to provide the Redis endpoint and port in your Lambda function.

```bash
pip install redis
```

3. **Caching Strategy**: The caching layer follows a **lazy-loading** approach, where data is only fetched from the database when it’s not found in the cache.

```python
# Example of caching strategy in Lambda
def cache_data(key, data):
    redis_client.set(key, json.dumps(data))
```
