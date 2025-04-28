# AWS Hero Data Caching System with Aurora and Redis

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![AWS Cloud](https://img.shields.io/badge/AWS-Cloud-orange)](https://aws.amazon.com)
[![Python](https://img.shields.io/badge/Python-3.9-blue)](https://www.python.org)

## Overview

This project implements a hero data caching system on AWS to improve the performance of retrieving hero information from an Amazon Aurora MySQL database. By leveraging Amazon ElastiCache Redis as a caching layer, frequently accessed hero data is stored in-memory, reducing database load and enhancing application responsiveness. The system utilizes an AWS Lambda function written in Python to handle data access, implementing both lazy loading for reads and write-through caching for updates.

## Architecture

The architecture of the Hero Data Caching System is illustrated below:

| Component             | Description                                                                 | AWS Service          |
| --------------------- | --------------------------------------------------------------------------- | ---------------------- |
| **Data Storage** | Persistent storage for hero data (ID, name, power, XP, color).             | Amazon Aurora MySQL    |
| **Caching Layer** | In-memory data store for frequently accessed hero data.                     | Amazon ElastiCache Redis |
| **Application Logic** | Handles read and write requests, interacts with Aurora and Redis.          | AWS Lambda (Python)    |

The interaction flow is as follows:

**Read Operations (Lazy Loading):**

1.  A request to read hero data by ID is received by the Lambda function.
2.  The function checks the Redis cache for the requested data.
3.  **Cache Hit:** If the data is found in Redis, it is returned directly.
4.  **Cache Miss:** If the data is not found in Redis, the function queries Aurora, stores the retrieved data in Redis (with a TTL), and then returns it.

**Write Operations (Write-Through Caching):**

1.  A request to write new hero data is received by the Lambda function.
2.  The function first writes the data to the Aurora database.
3.  The function then immediately writes the same data to the Redis cache to ensure consistency.
4.  A success response is returned.

## Code Structure

The project's codebase is organized as follows:
