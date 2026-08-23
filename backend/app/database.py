from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGODB_URI, MONGODB_DB

client: AsyncIOMotorClient = None
db = None

async def connect_db():
    global client, db
    client = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)
    db = client[MONGODB_DB]
    try:
        await _create_indexes()
        print(f"✅ Connected to MongoDB: {MONGODB_DB}")
    except Exception as e:
        print(f"⚠️  MongoDB connection issue: {e}")
        print(f"⚠️  Server will start but database operations will fail until MongoDB is available.")

async def disconnect_db():
    global client
    if client:
        client.close()
        print("✅ MongoDB disconnected")

async def _create_indexes():
    await db.users.create_index("email", unique=True)
    await db.users.create_index("googleId", sparse=True)
    await db.profiles.create_index("userId", unique=True)
    await db.resumes.create_index([("userId", 1), ("isDefault", -1)])
    await db.jobsearches.create_index("userId")
    await db.jobs.create_index([("userId", 1), ("sourceId", 1)], unique=True)
    await db.applications.create_index("userId")
    await db.applications.create_index([("userId", 1), ("jobId", 1)])
    await db.aievaluations.create_index("userId")
    await db.automationruns.create_index("userId")
    await db.automationlogs.create_index([("userId", 1), ("createdAt", -1)])
    await db.notifications.create_index([("userId", 1), ("read", 1)])
    await db.resumeversions.create_index("userId")

def get_db():
    return db
