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

async def _safe_create_index(collection, keys, **kwargs):
    try:
        await collection.create_index(keys, **kwargs)
    except Exception as e:
        print(f"⚠️  Index skipped on {collection.name}: {e}")


async def _create_indexes():
    await _safe_create_index(db.users, "email", unique=True)
    await _safe_create_index(db.users, "googleId", sparse=True)
    await _safe_create_index(db.profiles, "userId", unique=True)
    await _safe_create_index(db.resumes, [("userId", 1), ("isDefault", -1)])
    await _safe_create_index(db.jobsearches, "userId")
    # Partial unique: existing docs with sourceId=null would break a full unique index
    await _safe_create_index(
        db.jobs,
        [("userId", 1), ("sourceId", 1)],
        unique=True,
        name="userId_1_sourceId_1_partial",
        partialFilterExpression={"sourceId": {"$type": "string", "$gt": ""}},
    )
    await _safe_create_index(db.applications, "userId")
    # Existing DBs may already have a partial unique index with this auto name.
    await _safe_create_index(db.aievaluations, "userId")
    await _safe_create_index(db.automationruns, "userId")
    await _safe_create_index(db.automationlogs, [("userId", 1), ("createdAt", -1)])
    await _safe_create_index(db.notifications, [("userId", 1), ("read", 1)])
    await _safe_create_index(db.resumeversions, "userId")

def get_db():
    return db
