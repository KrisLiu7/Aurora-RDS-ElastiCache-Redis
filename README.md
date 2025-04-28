# Aurora-RDS-ElastiCache-Redis

# Data Caching System with Aurora and Redis

This repository contains the code and documentation for a hero data caching system implemented on AWS. The system uses Amazon Aurora MySQL for persistent storage and Amazon ElastiCache Redis for caching, with an AWS Lambda function handling data access.

## Overview

The system is designed to improve the performance of retrieving hero data by caching frequently accessed information in Redis. This reduces the load on the Aurora database and improves application responsiveness.

## Architecture

The system consists of the following components:

* **Amazon Aurora MySQL:** The primary database for storing hero data (ID, name, power, XP, color).
* **Amazon ElastiCache Redis:** An in-memory cache for storing frequently accessed hero data.
* **AWS Lambda Function (Python):** The application logic, handling read and write requests and interacting with both Aurora and Redis.

## Functionality

* **Read Operations (Lazy Loading):** When reading hero data, the Lambda function first checks the Redis cache. If the data is found (cache hit), it's returned directly. If not (cache miss), the data is retrieved from Aurora, stored in Redis, and then returned.
* **Write Operations (Write-Through Caching):** When writing new hero data, the Lambda function writes to both Aurora and Redis to ensure data consistency.

## Code Structure

The core logic is implemented in the `lambda_function.py` file. Key components include:

* **Database Interaction (DB Class):** Handles connections and queries to the Aurora MySQL database.
* **Redis Interaction:** Uses the `redis-py` library to connect to and interact with the ElastiCache Redis cluster.
* **`read()` function:** Implements the read logic with lazy loading.
* **`write()` function:** Implements the write logic with write-through caching.
* **`lambda_handler()` function:** The entry point for the Lambda function, handling incoming requests and orchestrating data access.

## Setup Instructions (Example - Adapt to your specific setup)

1.  **Create an Amazon Aurora MySQL database instance.**
2.  **Create an Amazon ElastiCache Redis cluster.**
3.  **Create an AWS Lambda function.**
4.  **Configure the Lambda function:**
    * Set environment variables for database connection details (DB\_HOST, DB\_USER, DB\_PASS, DB\_NAME, DB\_TABLE) and Redis URL (REDIS\_URL).
    * Upload the `lambda_function.py` code.
    * Configure the Lambda function's IAM role to allow access to Aurora and ElastiCache.
    * Configure the Lambda function's VPC settings to match the VPC of your Aurora and ElastiCache resources, if applicable.
5.  **Deploy and test the Lambda function.**

##  Troubleshooting

(You could include information about the `ssl_sslopt` error and the need for `redis.Redis.from_url(REDIS_URL, ssl=True)` if you want to be thorough)

##  Contributing

(Add your contribution guidelines if you plan to accept contributions)

## License

(Add your chosen license)
